from vector_store_utils import bulk_insert_chunks
from search_utils import similarity_search

class VectorStoreService:
    def __init__(self, db: Session):
        self.db = db

    def bulk_insert_chunks(self, video_id, chunks, embeddings):
        bulk_insert_chunks(self.db, video_id, chunks, embeddings)

    def similarity_search(self, video_id, query_embedding, top_k=5):
        return similarity_search(self.db, video_id, query_embedding, top_k)