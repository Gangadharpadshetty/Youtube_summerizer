from pydantic import BaseModel, Field

class ProcessVideoRequest(BaseModel):
    video_id: str = Field(..., min_length=1, description="YouTube video ID")  # ← add min_length=1

class ProcessVideoResponse(BaseModel):
    video_id: str
    cached: bool
    chunk_count: int
    message: str