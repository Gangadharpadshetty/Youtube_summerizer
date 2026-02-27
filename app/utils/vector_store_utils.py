# vector_store_utils.py

from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List

def bulk_insert_chunks(
    db: Session,
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

    db.execute(
        text("""
            INSERT INTO chunks (video_id, chunk_index, content, embedding)
            VALUES (:video_id, :chunk_index, :content, :embedding)
        """),
        values
    )

    db.commit()

def build_index(db: Session, table_name='chunks', vector_column='embedding'):
    """
    Create a vector index on the specified table and column using pgvector.
    """
    index_name = f"{table_name}_{vector_column}_idx"
    sql = f"""
    CREATE INDEX IF NOT EXISTS {index_name}
    ON {table_name}
    USING ivfflat ( {vector_column} vector_l2_ops )
    """
    db.execute(text(sql))
    db.commit()