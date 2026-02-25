import sys
from pathlib import Path

# Ensure project root is importable when running tests from workspace
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi import HTTPException
from unittest.mock import patch

from app.services import youtube_service as ys


def test_extract_video_id_valid():
    url = "https://www.youtube.com/watch?v=ABCDEFGHIJK"
    assert ys.extract_video_id(url) == "ABCDEFGHIJK"


def test_extract_video_id_invalid():
    with pytest.raises(HTTPException):
        ys.extract_video_id("https://example.com/watch")


@patch("app.services.youtube_service.YouTubeTranscriptApi")
def test_fetch_transcript_success(mock_api):
    mock_api.get_transcript.return_value = [
        {"text": " Hello", "start": 0.0, "duration": 1.0, "language": "en"},
        {"text": "world ", "start": 1.0, "duration": 1.0},
    ]
    cleaned, lang = ys.fetch_transcript("ABCDEFGHIJK")
    assert "Hello world" == cleaned
    assert lang == "en"


@patch("app.services.youtube_service.YouTubeTranscriptApi")
def test_fetch_transcript_failure(mock_api):
    mock_api.get_transcript.side_effect = Exception("no")
    with pytest.raises(HTTPException):
        ys.fetch_transcript("ABCDEFGHIJK")
