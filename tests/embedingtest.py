import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from app.services.embedding_service import EmbeddingService


@pytest.fixture
def service():
    with patch("embedding_service.SentenceTransformer") as mock_st:
        mock_model = MagicMock()
        mock_st.return_value = mock_model
        svc = EmbeddingService()
        svc._mock_model = mock_model
        yield svc


class TestInit:

    def test_default_model(self):
        with patch("embedding_service.SentenceTransformer") as mock_st:
            EmbeddingService()
            mock_st.assert_called_once_with("all-MiniLM-L6-v2")

    def test_custom_model(self):
        with patch("embedding_service.SentenceTransformer") as mock_st:
            EmbeddingService(model_name="all-mpnet-base-v2")
            mock_st.assert_called_once_with("all-mpnet-base-v2")


class TestEmbed:

    def test_returns_list_of_floats(self, service):
        fake_vector = np.array([0.1, 0.2, 0.3])
        service._mock_model.encode.return_value = fake_vector

        result = service.embed("hello world")

        assert isinstance(result, list)
        assert all(isinstance(v, float) for v in result)

    def test_correct_values(self, service):
        fake_vector = np.array([0.1, 0.2, 0.3])
        service._mock_model.encode.return_value = fake_vector

        result = service.embed("hello world")

        assert result == pytest.approx([0.1, 0.2, 0.3])

    def test_calls_encode_with_text(self, service):
        service._mock_model.encode.return_value = np.array([0.0])

        service.embed("test input")

        service._mock_model.encode.assert_called_once_with("test input")

    def test_empty_string(self, service):
        service._mock_model.encode.return_value = np.array([0.0, 0.0])

        result = service.embed("")

        assert isinstance(result, list)

    def test_output_dimensionality(self, service):
        fake_vector = np.random.rand(384)
        service._mock_model.encode.return_value = fake_vector

        result = service.embed("some text")

        assert len(result) == 384


class TestBatchEmbed:

    def test_returns_list_of_lists(self, service):
        fake_matrix = np.array([[0.1, 0.2], [0.3, 0.4]])
        service._mock_model.encode.return_value = fake_matrix

        result = service.batch_embed(["hello", "world"])

        assert isinstance(result, list)
        assert all(isinstance(row, list) for row in result)

    def test_correct_values(self, service):
        fake_matrix = np.array([[0.1, 0.2], [0.3, 0.4]])
        service._mock_model.encode.return_value = fake_matrix

        result = service.batch_embed(["hello", "world"])

        assert result == pytest.approx([[0.1, 0.2], [0.3, 0.4]])

    def test_calls_encode_with_all_texts(self, service):
        service._mock_model.encode.return_value = np.array([[0.0], [0.0]])
        texts = ["first", "second"]

        service.batch_embed(texts)

        service._mock_model.encode.assert_called_once_with(texts)

    def test_single_item_batch(self, service):
        service._mock_model.encode.return_value = np.array([[0.5, 0.6]])

        result = service.batch_embed(["only one"])

        assert len(result) == 1
        assert result[0] == pytest.approx([0.5, 0.6])

    def test_empty_batch(self, service):
        service._mock_model.encode.return_value = np.array([]).reshape(0, 384)

        result = service.batch_embed([])

        assert result == []

    def test_output_shape(self, service):
        n, dim = 5, 384
        service._mock_model.encode.return_value = np.random.rand(n, dim)

        result = service.batch_embed([f"text {i}" for i in range(n)])

        assert len(result) == n
        assert all(len(row) == dim for row in result)


class TestIntegration:
    """Runs against the real model — skipped in CI unless marked."""

    @pytest.mark.integration
    def test_embed_real_output(self):
        svc = EmbeddingService()
        result = svc.embed("integration test")

        assert isinstance(result, list)
        assert len(result) == 384
        assert all(isinstance(v, float) for v in result)

    @pytest.mark.integration
    def test_similar_texts_closer_than_dissimilar(self):
        svc = EmbeddingService()
        e1 = np.array(svc.embed("cat"))
        e2 = np.array(svc.embed("kitten"))
        e3 = np.array(svc.embed("spaceship"))

        sim_close = np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2))
        sim_far = np.dot(e1, e3) / (np.linalg.norm(e1) * np.linalg.norm(e3))

        assert sim_close > sim_far