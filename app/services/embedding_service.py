import os
import requests
from typing import List


class EmbeddingService:

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.endpoint = "https://api.openai.com/v1/embeddings"
        self.model = "text-embedding-3-small"

    def embed(self, text: str) -> List[float]:

        response = requests.post(
            self.endpoint,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "input": text
            },
            timeout=30
        )

        if response.status_code != 200:
            raise ValueError("Embedding generation failed.")

        return response.json()["data"][0]["embedding"]

    def batch_embed(self, texts: List[str]) -> List[List[float]]:
        return [self.embed(text) for text in texts]