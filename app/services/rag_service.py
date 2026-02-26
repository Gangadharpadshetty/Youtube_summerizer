import logging
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import  VectorStoreService
from app.models.chunk import Chunk


logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.75


def retrieve_relevant_chunks(
    video_id: str,
    question: str,
    db: Session,
    top_k: int = 5
) -> List[str]:

    if not question.strip():
        raise ValueError("Question cannot be empty")

    # Ensure index exists
    vector_store_service = VectorStoreService(db)
    vector_store_service.build_index(video_id)

    embedding_service = EmbeddingService()
    query_vector = embedding_service.batch_embed(question)

    search_results = vector_store_service.search(video_id, query_vector, top_k)

    if not search_results:
        logger.info("No similar chunks found")
        return []

    filtered_ids = [
        chunk_id
        for chunk_id, score in search_results
        if score >= SIMILARITY_THRESHOLD
    ]

    if not filtered_ids:
        logger.info("No chunks above similarity threshold")
        return []

    stmt = select(Chunk.chunk_text).where(
        Chunk.id.in_(filtered_ids)
    )

    rows = db.execute(stmt).scalars().all()

    logger.info(f"Retrieved {len(rows)} relevant chunks")

    return rows