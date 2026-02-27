import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from app.main import app
from app.database import get_db

# ─────────────────────────────────────────────
# FIX 1: Correct patch path
# Your router does: from app.services.video_service import VideoService
# So patch must target: "app.services.video_service.VideoService"
# NOT "app.api.process_video.VideoService"
# ─────────────────────────────────────────────

PATCH_PATH = "app.services.video_service.VideoService"


# ─────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────

@pytest.fixture
def mock_db():
    """Mock SQLAlchemy session — prevents real DB calls."""
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    return db


@pytest.fixture
def client(mock_db):
    """TestClient with DB dependency overridden."""
    app.dependency_overrides[get_db] = lambda: mock_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def valid_payload():
    return {"video_id": "jNQXAC9IVRw"}


@pytest.fixture
def success_response():
    return {
        "video_id": "jNQXAC9IVRw",
        "cached": False,
        "chunk_count": 5,
        "message": "Video processed successfully."
    }


@pytest.fixture
def cached_response():
    return {
        "video_id": "jNQXAC9IVRw",
        "cached": True,
        "chunk_count": 0,
        "message": "Video already processed."
    }


# ─────────────────────────────────────────────
# Happy Path Tests
# ─────────────────────────────────────────────

class TestProcessVideoSuccess:

    @patch(PATCH_PATH)
    def test_process_new_video(self, mock_service_class, client, valid_payload, success_response):
        """Should return 200 for a new video."""
        mock_service_class.return_value.process_video.return_value = success_response

        response = client.post("/process_video/", json=valid_payload)

        assert response.status_code == 200
        assert response.json()["video_id"] == "jNQXAC9IVRw"
        assert response.json()["cached"] is False
        assert response.json()["chunk_count"] == 5
        assert response.json()["message"] == "Video processed successfully."

    @patch(PATCH_PATH)
    def test_process_cached_video(self, mock_service_class, client, valid_payload, cached_response):
        """Should return 200 with cached=True for already processed video."""
        mock_service_class.return_value.process_video.return_value = cached_response

        response = client.post("/process_video/", json=valid_payload)

        assert response.status_code == 200
        assert response.json()["cached"] is True
        assert response.json()["chunk_count"] == 0
        assert response.json()["message"] == "Video already processed."

    @patch(PATCH_PATH)
    def test_service_called_with_correct_video_id(self, mock_service_class, client, valid_payload, success_response):
        """Should pass video_id correctly to service."""
        mock_instance = mock_service_class.return_value
        mock_instance.process_video.return_value = success_response

        client.post("/process_video/", json=valid_payload)

        mock_instance.process_video.assert_called_once_with(
            video_id="jNQXAC9IVRw"
        )

    @patch(PATCH_PATH)
    def test_different_video_ids(self, mock_service_class, client):
        """Should handle any valid video_id string."""
        mock_service_class.return_value.process_video.return_value = {
            "video_id": "abc123XYZ99",
            "cached": False,
            "chunk_count": 8,
            "message": "Video processed successfully."
        }

        response = client.post("/process_video/", json={"video_id": "abc123XYZ99"})

        assert response.status_code == 200
        assert response.json()["video_id"] == "abc123XYZ99"


# ─────────────────────────────────────────────
# Validation Tests
# ─────────────────────────────────────────────

class TestProcessVideoValidation:

    def test_missing_video_id(self, client):
        """Should return 422 when video_id is missing."""
        response = client.post("/process_video/", json={})
        assert response.status_code == 422

    def test_null_video_id(self, client):
        """Should return 422 when video_id is null."""
        response = client.post("/process_video/", json={"video_id": None})
        assert response.status_code == 422

    def test_empty_body(self, client):
        """Should return 422 for empty body."""
        response = client.post("/process_video/", json={})
        assert response.status_code == 422

    def test_get_method_not_allowed(self, client):
        """GET should return 405."""
        response = client.get("/process_video/")
        assert response.status_code == 405

    def test_put_method_not_allowed(self, client):
        """PUT should return 405."""
        response = client.put("/process_video/", json={"video_id": "jNQXAC9IVRw"})
        assert response.status_code == 405

    @patch(PATCH_PATH)
    def test_extra_fields_ignored(self, mock_service_class, client, success_response):
        """Pydantic should ignore unknown fields."""
        mock_service_class.return_value.process_video.return_value = success_response

        response = client.post("/process_video/", json={
            "video_id": "jNQXAC9IVRw",
            "youtube_url": "https://youtube.com/watch?v=jNQXAC9IVRw",
            "language": "en"
        })
        assert response.status_code == 200


# ─────────────────────────────────────────────
# Error Handling Tests
# ─────────────────────────────────────────────

class TestProcessVideoErrors:

    @patch(PATCH_PATH)
    def test_value_error_returns_400(self, mock_service_class, client, valid_payload):
        """Should return 400 for ValueError."""
        mock_service_class.return_value.process_video.side_effect = ValueError("Invalid video ID")

        response = client.post("/process_video/", json=valid_payload)

        assert response.status_code == 400
        assert "Invalid video ID" in response.json()["detail"]

    @patch(PATCH_PATH)
    def test_sqlalchemy_error_returns_503(self, mock_service_class, client, valid_payload):
        """Should return 503 for SQLAlchemyError."""
        mock_service_class.return_value.process_video.side_effect = SQLAlchemyError("DB down")

        response = client.post("/process_video/", json=valid_payload)

        assert response.status_code == 503
        assert response.json()["detail"] == "Database error"

    @patch(PATCH_PATH)
    def test_http_422_passthrough(self, mock_service_class, client, valid_payload):
        """Should pass through 422 from service."""
        mock_service_class.return_value.process_video.side_effect = HTTPException(
            status_code=422, detail="Transcript unavailable"
        )

        response = client.post("/process_video/", json=valid_payload)

        assert response.status_code == 422
        assert response.json()["detail"] == "Transcript unavailable"

    @patch(PATCH_PATH)
    def test_http_404_passthrough(self, mock_service_class, client, valid_payload):
        """Should pass through 404 from service."""
        mock_service_class.return_value.process_video.side_effect = HTTPException(
            status_code=404, detail="Video not found"
        )

        response = client.post("/process_video/", json=valid_payload)

        assert response.status_code == 404
        assert response.json()["detail"] == "Video not found"

    @patch(PATCH_PATH)
    def test_http_502_passthrough(self, mock_service_class, client, valid_payload):
        """Should pass through 502 from service."""
        mock_service_class.return_value.process_video.side_effect = HTTPException(
            status_code=502, detail="Failed to fetch transcript from YouTube"
        )

        response = client.post("/process_video/", json=valid_payload)

        assert response.status_code == 502
        assert response.json()["detail"] == "Failed to fetch transcript from YouTube"

    @patch(PATCH_PATH)
    def test_unexpected_exception_returns_500(self, mock_service_class, client, valid_payload):
        """Should return 500 for unexpected exceptions."""
        mock_service_class.return_value.process_video.side_effect = RuntimeError("Crash")

        response = client.post("/process_video/", json=valid_payload)

        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"


# ─────────────────────────────────────────────
# Response Schema Tests
# ─────────────────────────────────────────────

class TestProcessVideoResponseSchema:

    @patch(PATCH_PATH)
    def test_response_has_all_four_fields(self, mock_service_class, client, valid_payload, success_response):
        mock_service_class.return_value.process_video.return_value = success_response
        data = client.post("/process_video/", json=valid_payload).json()

        assert "video_id" in data
        assert "cached" in data
        assert "chunk_count" in data
        assert "message" in data

    @patch(PATCH_PATH)
    def test_video_id_is_string(self, mock_service_class, client, valid_payload, success_response):
        mock_service_class.return_value.process_video.return_value = success_response
        data = client.post("/process_video/", json=valid_payload).json()
        assert isinstance(data["video_id"], str)

    @patch(PATCH_PATH)
    def test_cached_is_boolean(self, mock_service_class, client, valid_payload, success_response):
        mock_service_class.return_value.process_video.return_value = success_response
        data = client.post("/process_video/", json=valid_payload).json()
        assert isinstance(data["cached"], bool)

    @patch(PATCH_PATH)
    def test_chunk_count_is_integer(self, mock_service_class, client, valid_payload, success_response):
        mock_service_class.return_value.process_video.return_value = success_response
        data = client.post("/process_video/", json=valid_payload).json()
        assert isinstance(data["chunk_count"], int)

    @patch(PATCH_PATH)
    def test_message_is_string(self, mock_service_class, client, valid_payload, success_response):
        mock_service_class.return_value.process_video.return_value = success_response
        data = client.post("/process_video/", json=valid_payload).json()
        assert isinstance(data["message"], str)

    @patch(PATCH_PATH)
    def test_video_id_matches_request(self, mock_service_class, client, valid_payload, success_response):
        mock_service_class.return_value.process_video.return_value = success_response
        data = client.post("/process_video/", json=valid_payload).json()
        assert data["video_id"] == valid_payload["video_id"]