
import pytest
from fastapi.testclient import TestClient

from app import ChatRequest, HealthResponse, app


@pytest.fixture
def client(monkeypatch):

    monkeypatch.setattr("app._auto_ingest", lambda: None)
    monkeypatch.setattr("app.settings.nvidia_api_key", "")
    with TestClient(app) as test_client:
        yield test_client


def test_health_returns_503_when_no_api_key(client):

    response = client.get("/api/health")
    assert response.status_code == 503


def test_health_response_contains_status_and_chromadb(client):

    response = client.get("/api/health")
    data = response.json()["detail"]

    assert "status" in data
    assert "chromadb" in data


def test_chat_empty_message_returns_422(client):

    response = client.post("/api/chat", json={"message": ""})
    assert response.status_code == 422


def test_chat_request_model_accepts_message_and_optional_conversation_id():

    req = ChatRequest(message="hola")
    assert req.message == "hola"
    assert req.conversation_id is None

    req_with_id = ChatRequest(message="hola", conversation_id="abc-123")
    assert req_with_id.conversation_id == "abc-123"


def test_health_response_model_has_required_fields():

    response = HealthResponse(
        status="healthy",
        chromadb="connected",
        llm="available",
    )
    assert response.status == "healthy"
    assert response.chromadb == "connected"
    assert response.llm == "available"
