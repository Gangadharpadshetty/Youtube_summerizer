import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.base import Base
from app.database.session import get_db
from app.models import Video, Chunk


# ----------------------------
# Test Database Setup
# ----------------------------

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# ----------------------------
# Mock Services
# ----------------------------

@pytest.fixture(autouse=True)
def mock_services(monkeypatch):
    """
    Mock transcript + embeddings to avoid real API calls
    """

    # Mock transcript fetch
    def fake_fetch(video_id):
        return "Artificial intelligence is transforming industries.", "English"

    monkeypatch.setattr(
        "app.services.transcript_service.TranscriptService.fetch",
        fake_fetch
    )

    # Mock embeddings
    def fake_embed(self, text):
        return [0.1] * 1536

    def fake_batch_embed(self, texts):
        return [[0.1] * 1536 for _ in texts]

    monkeypatch.setattr(
        "app.services.embedding_service.EmbeddingService.embed",
        fake_embed
    )

    monkeypatch.setattr(
        "app.services.embedding_service.EmbeddingService.batch_embed",
        fake_batch_embed
    )


# ----------------------------
# HEALTH TEST
# ----------------------------

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ----------------------------
# PROCESS VIDEO TEST
# ----------------------------

def test_process_video_success():
    response = client.post(
        "/process_video/",
        json={"video_id": "abc123xyz00"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["video_id"] == "abc123xyz00"
    assert data["cached"] is False
    assert data["chunk_count"] > 0


def test_process_video_cached():
    # First call
    client.post("/process_video/", json={"video_id": "cached123456"})

    # Second call
    response = client.post(
        "/process_video/",
        json={"video_id": "cached123456"}
    )

    assert response.status_code == 200
    assert response.json()["cached"] is True


# ----------------------------
# RETRIEVE CHUNKS TEST
# ----------------------------

def test_retrieve_chunks_success():
    # First process video
    client.post("/process_video/", json={"video_id": "ragvideo123"})

    response = client.post(
        "/retrieve_chunks/",
        json={
            "video_id": "ragvideo123",
            "question": "What is artificial intelligence?",
            "top_k": 3
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert data["video_id"] == "ragvideo123"
    assert isinstance(data["chunks"], list)
    assert len(data["chunks"]) <= 3


def test_retrieve_chunks_invalid_video():
    response = client.post(
        "/retrieve_chunks/",
        json={
            "video_id": "nonexistent",
            "question": "Hello?",
            "top_k": 3
        }
    )

    # Depending on your service logic
    assert response.status_code in [200, 400]


# ----------------------------
# EDGE CASE TESTS
# ----------------------------

def test_invalid_video_id():
    response = client.post(
        "/process_video/",
        json={"video_id": ""}
    )

    assert response.status_code in [400, 422]


def test_invalid_top_k():
    response = client.post(
        "/retrieve_chunks/",
        json={
            "video_id": "abc",
            "question": "Test",
            "top_k": 100
        }
    )

    assert response.status_code == 422