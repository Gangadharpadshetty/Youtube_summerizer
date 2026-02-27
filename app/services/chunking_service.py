
from app.utils.chunking import chunk_transcript

class ChunkingService:
    def chunk(self, text: str) -> list[str]:
        chunks = chunk_transcript(text)  # delegates to util
        if not chunks:
            raise ValueError("No chunks produced")
        return chunks