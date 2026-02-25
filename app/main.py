from fastapi import FastAPI
from pydantic import BaseModel
from app.services import youtube_service as ys

app = FastAPI(title="YouTube Video Transcriptor API")


class TranscriptRequest(BaseModel):
    youtube_url: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/transcript")
def get_transcript(request: TranscriptRequest):
    video_id = extract_video_id(request.youtube_url)
    transcript, language = fetch_transcript(video_id)

    return {
        "video_id": video_id,
        "language": language,
        "transcript": transcript
    }