from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app import ChatRequest, HealthResponse, _sse_event, app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr("app.settings.nvidia_api_key", "")
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def client_with_key(monkeypatch):
    monkeypatch.setattr("app.settings.nvidia_api_key", "fake-key")
    monkeypatch.setattr("app.settings.nvidia_base_url", "https://fake.api.com/v1")
    with TestClient(app) as test_client:
        yield test_client


# ---------------------------------------------------------------------------
# Existing tests
# ---------------------------------------------------------------------------

def test_health_returns_503_when_no_api_key(client):
    response = client.get("/api/health")
    assert response.status_code == 503


def test_health_response_contains_status_and_vectorstore(client):
    response = client.get("/api/health")
    data = response.json()["detail"]
    assert "status" in data
    assert "vectorstore" in data


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
    response = HealthResponse(status="healthy", vectorstore="connected", llm="available")
    assert response.status == "healthy"
    assert response.vectorstore == "connected"
    assert response.llm == "available"


# ---------------------------------------------------------------------------
# _sse_event
# ---------------------------------------------------------------------------

def test_sse_event_without_event_name():
    result = _sse_event("hola mundo")
    assert result == "data: hola mundo\n\n"


def test_sse_event_with_event_name():
    result = _sse_event('{"done": true}', event_name="error")
    assert result == 'event: error\ndata: {"done": true}\n\n'


def test_sse_event_multiline_payload():
    result = _sse_event("line1\nline2")
    assert result == "data: line1\ndata: line2\n\n"


# ---------------------------------------------------------------------------
# Health — 200 cuando todo funciona / 503 degradado
# ---------------------------------------------------------------------------

def test_health_returns_200_when_connected(monkeypatch):
    monkeypatch.setattr("app.settings.nvidia_api_key", "fake-key")
    monkeypatch.setattr("app.settings.pinecone_api_key", "fake-pinecone-key")
    monkeypatch.setattr("app.settings.pinecone_index_name", "test-index")

    mock_stats = MagicMock()
    mock_stats.namespaces = {"": MagicMock(vector_count=5)}
    mock_idx = MagicMock()
    mock_idx.describe_index_stats.return_value = mock_stats
    mock_pc = MagicMock()
    mock_pc.Index.return_value = mock_idx
    monkeypatch.setattr("app.Pinecone", lambda **kw: mock_pc)

    with TestClient(app) as c:
        response = c.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["vectorstore"] == "connected"
    assert data["llm"] == "available"


def test_health_returns_degraded_when_vectorstore_fails(monkeypatch):
    monkeypatch.setattr("app.settings.nvidia_api_key", "fake-key")
    monkeypatch.setattr("app.settings.pinecone_api_key", "fake-pinecone-key")
    monkeypatch.setattr("app.settings.pinecone_index_name", "test-index")

    monkeypatch.setattr("app.Pinecone", MagicMock(side_effect=RuntimeError("Pinecone down")))

    with TestClient(app) as c:
        response = c.get("/api/health")

    assert response.status_code == 503
    data = response.json()["detail"]
    assert data["vectorstore"] == "disconnected"
    assert data["status"] == "degraded"


# ---------------------------------------------------------------------------
# Chat endpoint
# ---------------------------------------------------------------------------

def test_chat_returns_500_when_no_api_key(client):
    response = client.post("/api/chat", json={"message": "hola"})
    assert response.status_code == 500
    assert "NVIDIA_API_KEY" in response.json()["detail"]


def test_chat_streams_response_with_key(client_with_key):
    async def fake_stream(_question):
        yield "uno"
        yield "dos"
        yield "[DONE]"

    with patch("app.stream_answer", new=fake_stream):
        response = client_with_key.post("/api/chat", json={"message": "hola"})

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
    body = response.text
    assert "data: uno" in body
    assert "data: [DONE]" in body


# ---------------------------------------------------------------------------
# _stream_response (helper interno)
# ---------------------------------------------------------------------------

def test_stream_response_yields_error_on_runtime_error(monkeypatch):
    from app import _stream_response

    async def failing_stream(_question):
        raise RuntimeError("error interno")
        yield  # pragma: no cover

    monkeypatch.setattr("app.stream_answer", failing_stream)

    async def collect():
        parts = []
        async for part in _stream_response("test"):
            parts.append(part)
        return "".join(parts)

    import asyncio

    output = asyncio.run(collect())
    assert "event: error" in output
    assert "congestionado" in output


def test_stream_response_yields_error_on_generic_exception(monkeypatch):
    from app import _stream_response

    async def failing_stream(_question):
        raise ValueError("unexpected")
        yield  # pragma: no cover

    monkeypatch.setattr("app.stream_answer", failing_stream)

    async def collect():
        parts = []
        async for part in _stream_response("test"):
            parts.append(part)
        return "".join(parts)

    import asyncio

    output = asyncio.run(collect())
    assert "event: error" in output
    assert "inesperado" in output



