from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List


class VectorStoreService:

    def __init__(self, db: Session):
        self.db = db

    def bulk_insert_chunks(
        self,
        video_id: str,
        chunks: List[str],
        embeddings: List[List[float]],
    ):

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
                INSERT INTO chunks (video_id, chunk_index, content, embedding)
                VALUES (:video_id, :chunk_index, :content, :embedding)
            """),
            values
        )

        self.db.commit()

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

        return [row[0] for row in result.fetchall()]