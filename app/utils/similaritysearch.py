# search_utils.py

from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List

def similarity_search(
    db: Session,
    video_id: str,
    query_embedding: List[float],
    top_k: int = 5
) -> List[str]:
    result = db.execute(
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