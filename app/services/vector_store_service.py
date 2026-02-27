from fastapi.params import Depends

from app.utils.vector_store_utils import bulk_insert_chunks, build_index
from app.utils.similaritysearch import similarity_search
from app.database import get_db
class VectorStoreService:
    def __init__(self, db: Depends(get_db)):
        self.db = db
        self.index = None  # Initialize the index attribute

    def bulk_insert_chunks(self, video_id, chunks, embeddings):
        bulk_insert_chunks(self.db, video_id, chunks, embeddings)

    def build_index(self, embeddings):
        """
        Build or update the index with the provided embeddings.
        """
        self.index = build_index(embeddings)

    def similarity_search(self, video_id, query_embedding, top_k=5):
        if self.index is None:
            # Optionally, build the index here if not built yet
            # Or handle the case where index is not available
            raise ValueError("Index is not built yet. Please build the index before searching.")
        return similarity_search(self.db, video_id, query_embedding, top_k)