from typing import List


class ChunkingService:

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 800, overlap: int = 200) -> List[str]:

        words = text.split()
        chunks = []

        start = 0
        while start < len(words):
            end = start + chunk_size
            chunk = words[start:end]
            chunks.append(" ".join(chunk))
            start += chunk_size - overlap

        return chunks