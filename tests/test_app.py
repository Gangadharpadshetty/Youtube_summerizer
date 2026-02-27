from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
import logging

from app.services.transcript_service import TranscriptService
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import VectorStoreService
from app.repositories.video_repository import VideoRepository

logger = logging.getLogger(__name__)


class VideoService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = VideoRepository(db)
        self.embedding = EmbeddingService()
        self.vector_store = VectorStoreService(db)

    def process_video(self, video_id: str) -> dict:

        # Check cache
        try:
            existing = self.repo.get_by_video_id(video_id)
            if existing:
                return {
                    "video_id": video_id,
                    "cached": True,
                    "chunk_count": 0,
                    "message": "Video already processed."
                }
        except SQLAlchemyError as e:
            logger.error(f"Database error checking video {video_id}: {e}")
            raise HTTPException(status_code=503, detail="Database unavailable")

        # Fetch transcript
        try:
            transcript_text, language = TranscriptService.fetch(video_id)
        except ValueError as e:
            logger.warning(f"Transcript not available for {video_id}: {e}")
            raise HTTPException(status_code=422, detail=f"Transcript unavailable: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to fetch transcript for {video_id}: {e}")
            raise HTTPException(status_code=502, detail="Failed to fetch transcript from YouTube")

        # Save video record
        try:
            self.repo.create_video(video_id, transcript_text, language)
        except SQLAlchemyError as e:
            logger.error(f"Failed to save video {video_id}: {e}")
            raise HTTPException(status_code=503, detail="Failed to save video to database")

        # Chunk transcript
        try:
            chunks = ChunkingService.chunk_text(transcript_text)
            if not chunks:
                raise ValueError("Chunking produced no output")
        except ValueError as e:
            logger.warning(f"Chunking failed for {video_id}: {e}")
            raise HTTPException(status_code=422, detail="Transcript could not be chunked")
        except Exception as e:
            logger.error(f"Unexpected chunking error for {video_id}: {e}")
            raise HTTPException(status_code=500, detail="Chunking error")

        # Generate embeddings
        try:
            embeddings = self.embedding.batch_embed(chunks)
            if not embeddings:
                raise ValueError("Embedding returned empty result")
        except ValueError as e:
            logger.warning(f"Embedding failed for {video_id}: {e}")
            raise HTTPException(status_code=422, detail="Failed to generate embeddings")
        except Exception as e:
            logger.error(f"Embedding service error for {video_id}: {e}")
            raise HTTPException(status_code=502, detail="Embedding service unavailable")

        # Store vectors
        try:
            self.vector_store.bulk_insert_chunks(video_id, chunks, embeddings)
        except SQLAlchemyError as e:
            logger.error(f"Vector store insert failed for {video_id}: {e}")
            raise HTTPException(status_code=503, detail="Failed to store embeddings")
        except Exception as e:
            logger.error(f"Unexpected vector store error for {video_id}: {e}")
            raise HTTPException(status_code=500, detail="Vector store error")

        logger.info(f"Video {video_id} processed successfully — {len(chunks)} chunks")

        return {
            "video_id": video_id,
            "cached": False,
            "chunk_count": len(chunks),
            "message": "Video processed successfully."
        }