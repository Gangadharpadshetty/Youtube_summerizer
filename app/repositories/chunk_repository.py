from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List


class ChunkRepository:
    def __init__(self, db: Session):
        self.db = db

    # ----------------------------------
    # BULK INSERT CHUNKS
    # ----------------------------------
    def bulk_insert(
        self,
        video_id: str,
        chunks: List[str],
        embeddings: List[List[float]]
    ) -> None:

        if len(chunks) != len(embeddings):
            raise ValueError("Chunks and embeddings count mismatch.")

        values = [
            {
                "video_id": video_id,
                "chunk_index": idx,
                "content": chunk,
                "embedding": embedding,
            }
            for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings))
        ]

        self.db.execute(
            text("""
                INSERT INTO chunks (
                    video_id,
                    chunk_index,
                    content,
                    embedding
                )
                VALUES (
                    :video_id,
                    :chunk_index,
                    :content,
                    :embedding
                )
            """),
            values
        )

        self.db.commit()

    # ----------------------------------
    # SIMILARITY SEARCH (pgvector)
    # ----------------------------------
    def similarity_search(
        self,
        video_id: str,
        query_embedding: List[float],
        top_k: int = 5
    ) -> List[str]:

        result = self.db.execute(
            text("""
                SELECT content
                FROM chunks
                WHERE video_id = :video_id
                ORDER BY embedding <-> :embedding
                LIMIT :top_k
            """),
            {
                "video_id": video_id,
                "embedding": query_embedding,
                "top_k": top_k
            }
        )

        rows = result.fetchall()
        return [row[0] for row in rows]

    # ----------------------------------
    # DELETE BY VIDEO (optional cleanup)
    # ----------------------------------
    def delete_by_video(self, video_id: str) -> None:

        self.db.execute(
            text("""
                DELETE FROM chunks
                WHERE video_id = :video_id
            """),
            {"video_id": video_id}
        )

        self.db.commit()