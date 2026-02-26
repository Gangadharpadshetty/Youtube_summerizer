from pydantic import BaseModel, Field
from typing import List


class RetrieveChunksRequest(BaseModel):
    video_id: str
    question: str
    top_k: int = Field(default=5, ge=1, le=20)


class RetrieveChunksResponse(BaseModel):
    video_id: str
    chunks: List[str]