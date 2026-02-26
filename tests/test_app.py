import pytest
from unittest.mock import patch


# -----------------------------
# HEALTH CHECK
# -----------------------------

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# -----------------------------
# INVALID YOUTUBE URL
# -----------------------------

def test_invalid_youtube_url(client):
    response = client.post(
        "/process-video",
        json={
            "youtube_url": "invalid_url",
            "telegram_id": "user1",
            "language": "English"
        }
    )

    assert response.status_code == 400
    assert "Invalid YouTube URL" in response.json()["detail"]


# -----------------------------
# NO TRANSCRIPT AVAILABLE
# -----------------------------

@patch("app.services.transcript_service.TranscriptService.fetch_transcript")
def test_no_transcript_available(mock_transcript, client):
    mock_transcript.return_value = None

    response = client.post(
        "/process-video",
        json={
            "youtube_url": "https://youtube.com/watch?v=abcdefghijk",
            "telegram_id": "user1",
            "language": "English"
        }
    )

    assert response.status_code == 400
    assert "Transcript not available" in response.json()["detail"]


# -----------------------------
# VERY LONG TRANSCRIPT
# -----------------------------

@patch("app.services.transcript_service.TranscriptService.fetch_transcript")
def test_long_transcript(mock_transcript, client):
    mock_transcript.return_value = "This is a long transcript. " * 1000

    response = client.post(
        "/process-video",
        json={
            "youtube_url": "https://youtube.com/watch?v=abcdefghijk",
            "telegram_id": "user1",
            "language": "English"
        }
    )

    assert response.status_code == 200
    assert "video_id" in response.json()


# -----------------------------
# ASK WITHOUT ACTIVE VIDEO
# -----------------------------

def test_ask_without_session(client):
    response = client.post(
        "/retrieve-chunks",
        json={
            "telegram_id": "new_user",
            "question": "What is pricing?",
            "language": "English"
        }
    )

    assert response.status_code == 400
    assert "No active video found" in response.json()["detail"]


# -----------------------------
# QUESTION NOT COVERED
# -----------------------------

@patch("app.services.rag_service.RAGService.retrieve_relevant_chunks")
def test_question_not_covered(mock_rag, client):
    mock_rag.return_value = []

    # First process video
    client.post(
        "/process-video",
        json={
            "youtube_url": "https://youtube.com/watch?v=abcdefghijk",
            "telegram_id": "user1",
            "language": "English"
        }
    )

    response = client.post(
        "/retrieve-chunks",
        json={
            "telegram_id": "user1",
            "question": "What about quantum physics?",
            "language": "English"
        }
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "This topic is not covered in the video."


# -----------------------------
# MULTI-LANGUAGE SUPPORT
# -----------------------------

@patch("app.services.openclaw_service.call_summarize_skill")
def test_multilanguage_summary(mock_summary, client):
    mock_summary.return_value = "यह वीडियो का सारांश है।"

    response = client.post(
        "/process-video",
        json={
            "youtube_url": "https://youtube.com/watch?v=abcdefghijk",
            "telegram_id": "user2",
            "language": "Hindi"
        }
    )

    assert response.status_code == 200
    assert "video_id" in response.json()


# -----------------------------
# MULTIPLE USERS SESSION ISOLATION
# -----------------------------

def test_multiple_users(client):

    # User 1
    client.post(
        "/process-video",
        json={
            "youtube_url": "https://youtube.com/watch?v=video11111",
            "telegram_id": "user1",
            "language": "English"
        }
    )

    # User 2
    client.post(
        "/process-video",
        json={
            "youtube_url": "https://youtube.com/watch?v=video22222",
            "telegram_id": "user2",
            "language": "English"
        }
    )

    response1 = client.post(
        "/retrieve-chunks",
        json={
            "telegram_id": "user1",
            "question": "What is discussed?",
            "language": "English"
        }
    )

    response2 = client.post(
        "/retrieve-chunks",
        json={
            "telegram_id": "user2",
            "question": "What is discussed?",
            "language": "English"
        }
    )

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response1.json() != response2.json()