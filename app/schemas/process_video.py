from pydantic import BaseModel, Field


class ProcessVideoRequest(BaseModel):
    video_id: str = Field(..., description="YouTube video ID")


class ProcessVideoResponse(BaseModel):
    video_id: str
    cached: bool
    chunk_count: int
    message: str