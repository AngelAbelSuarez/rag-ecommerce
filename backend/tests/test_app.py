from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app import ChatRequest, HealthResponse, _sse_event, app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr("app._auto_ingest", lambda: None)
    monkeypatch.setattr("app.settings.nvidia_api_key", "")
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def client_with_key(monkeypatch):
    monkeypatch.setattr("app._auto_ingest", lambda: None)
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
    response = HealthResponse(status="healthy", chromadb="connected", llm="available")
    assert response.status == "healthy"
    assert response.chromadb == "connected"
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
# _collection_has_data
# ---------------------------------------------------------------------------

def test_collection_has_data_returns_true(monkeypatch):
    mock_vs = MagicMock()
    mock_vs._collection.count.return_value = 5
    monkeypatch.setattr("app.get_vectorstore", lambda: mock_vs)
    from app import _collection_has_data

    assert _collection_has_data() is True


def test_collection_has_data_returns_false_on_empty(monkeypatch):
    mock_vs = MagicMock()
    mock_vs._collection.count.return_value = 0
    monkeypatch.setattr("app.get_vectorstore", lambda: mock_vs)
    from app import _collection_has_data

    assert _collection_has_data() is False


def test_collection_has_data_returns_false_on_exception(monkeypatch):
    monkeypatch.setattr(
        "app.get_vectorstore",
        MagicMock(side_effect=RuntimeError("ChromaDB not reachable")),
    )
    from app import _collection_has_data

    assert _collection_has_data() is False


# ---------------------------------------------------------------------------
# _auto_ingest
# ---------------------------------------------------------------------------

@patch("ingest.ingest")
def test_auto_ingest_skips_when_data_exists(mock_ingest, monkeypatch):
    monkeypatch.setattr("app._collection_has_data", lambda: True)
    from app import _auto_ingest

    result = _auto_ingest()
    assert result is None
    mock_ingest.assert_not_called()


@patch("ingest.ingest", return_value=(1, 5))
def test_auto_ingest_calls_ingest_when_empty(mock_ingest, monkeypatch):
    monkeypatch.setattr("app._collection_has_data", lambda: False)
    from app import _auto_ingest

    result = _auto_ingest()
    assert result == (1, 5)
    mock_ingest.assert_called_once()


@patch("ingest.ingest")
def test_auto_ingest_handles_system_exit(mock_ingest, monkeypatch):
    monkeypatch.setattr("app._collection_has_data", lambda: False)
    mock_ingest.side_effect = SystemExit(1)
    from app import _auto_ingest

    result = _auto_ingest()
    assert result is None


# ---------------------------------------------------------------------------
# Health — 200 cuando todo funciona / 503 degradado
# ---------------------------------------------------------------------------

def test_health_returns_200_when_connected(monkeypatch):
    monkeypatch.setattr("app.settings.nvidia_api_key", "fake-key")
    mock_vs = MagicMock()
    mock_vs._collection.count.return_value = 5
    monkeypatch.setattr("app.get_vectorstore", lambda: mock_vs)

    with TestClient(app) as c:
        response = c.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["chromadb"] == "connected"
    assert data["llm"] == "available"


def test_health_returns_degraded_when_chromadb_fails(monkeypatch):
    monkeypatch.setattr("app.settings.nvidia_api_key", "fake-key")
    monkeypatch.setattr("app._auto_ingest", lambda: None)
    monkeypatch.setattr(
        "app.get_vectorstore",
        MagicMock(side_effect=RuntimeError("ChromaDB down")),
    )

    with TestClient(app) as c:
        response = c.get("/api/health")

    assert response.status_code == 503
    data = response.json()["detail"]
    assert data["chromadb"] == "disconnected"
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


# ---------------------------------------------------------------------------
# Lifespan — auto_ingest runs on startup
# ---------------------------------------------------------------------------

def test_lifespan_runs_auto_ingest(monkeypatch):
    triggered = False

    def track_ingest():
        nonlocal triggered
        triggered = True

    monkeypatch.setattr("app._auto_ingest", track_ingest)
    monkeypatch.setattr("app.settings.nvidia_api_key", "")

    with TestClient(app) as _c:
        pass

    assert triggered
