from typing import List
from sentence_transformers import SentenceTransformer


class EmbeddingService:

    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()

    def batch_embed(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts).tolist()