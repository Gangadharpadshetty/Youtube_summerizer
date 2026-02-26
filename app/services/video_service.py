from sqlalchemy.orm import Session

from app.services.transcript_service import TranscriptService
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import VectorStoreService
from app.services.encryption_service import EncryptionService
from app.repositories.video_repository import VideoRepository


class VideoService:

    def __init__(self, db: Session, fernet_key: str):
        self.db = db
        self.repo = VideoRepository(db)
        self.encryption = EncryptionService(fernet_key)
        self.embedding = EmbeddingService()
        self.vector_store = VectorStoreService(db)

    def process_video(self, video_id: str) -> dict:

        existing = self.repo.get_by_video_id(video_id)
        if existing:
            return {
                "video_id": video_id,
                "cached": True,
                "chunk_count": 0,
                "message": "Video already processed."
            }

        transcript_text, language = TranscriptService.fetch(video_id)

        encrypted_transcript = self.encryption.encrypt(transcript_text)

        self.repo.create_video(video_id, encrypted_transcript, language)

        chunks = ChunkingService.chunk_text(transcript_text)

        embeddings = self.embedding.batch_embed(chunks)

        self.vector_store.bulk_insert_chunks(
            video_id,
            chunks,
            embeddings
        )

        return {
            "video_id": video_id,
            "cached": False,
            "chunk_count": len(chunks),
            "message": "Video processed successfully."
        }