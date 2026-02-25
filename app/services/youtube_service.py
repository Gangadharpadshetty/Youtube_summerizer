import re
from youtube_transcript_api import YouTubeTranscriptApi
from fastapi import HTTPException


def extract_video_id(url: str) -> str:
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    return match.group(1)


def fetch_transcript(video_id: str):
    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Transcript not available for this video"
        )
        

    full_text = " ".join([entry["text"] for entry in transcript_data])

    # Clean whitespace
    cleaned_text = " ".join(full_text.split())

    language = transcript_data[0].get("language", "unknown")

    return cleaned_text, language
