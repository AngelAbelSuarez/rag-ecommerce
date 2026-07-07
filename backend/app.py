"""FastAPI runtime for the BimBam chatbot.

Exposes a health endpoint and a streaming chat endpoint backed by the RAG
chain.  If ChromaDB is empty at startup, the offline ingestion pipeline is run
automatically so the first query can succeed.
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from config import settings
from rag import stream_answer
from store import get_vectorstore

logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    """Body for POST /api/chat."""

    message: str = Field(..., min_length=1, description="User question")
    conversation_id: str | None = Field(
        default=None,
        description="Optional client-side conversation id (reserved for future use)",
    )


class HealthResponse(BaseModel):
    """Response model for GET /api/health."""

    status: str
    chromadb: str
    llm: str | None = None


def _collection_has_data() -> bool:
    """Return True if the ChromaDB collection contains at least one document."""
    try:
        vectorstore = get_vectorstore()
        count = vectorstore._collection.count()
        return count > 0
    except Exception as exc:
        logger.warning("Could not determine ChromaDB document count: %s", exc)
        return False


def _auto_ingest() -> tuple[int, int] | None:
    """Run the offline ingestion pipeline if ChromaDB is empty."""
    from ingest import ingest as _ingest

    if _collection_has_data():
        logger.info("ChromaDB already contains data; skipping auto-ingestion")
        return None

    logger.info("ChromaDB is empty; running auto-ingestion")
    try:
        return _ingest()
    except SystemExit as exc:
        # ingest.py raises SystemExit on fatal config/data errors.
        logger.error("Auto-ingestion failed with exit code %s", exc.code)
        return None


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """Application lifespan: configure logging and ingest data if needed."""
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(levelname)s: %(message)s",
    )

    # Run ingestion in a thread so the event loop is not blocked by pdf parsing.
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _auto_ingest)

    yield


app = FastAPI(
    title="BimBam Chatbot API",
    description="RAG chatbot runtime for BimBam Buy",
    version="0.2.0",
    lifespan=lifespan,
)

# Open CORS for local development.  Tighten origins before production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Return the health status of ChromaDB and the LLM provider."""
    chromadb_status = "connected"
    llm_status = "available" if settings.nvidia_api_key else "unavailable"

    try:
        vectorstore = get_vectorstore()
        count = vectorstore._collection.count()
        logger.debug("ChromaDB health check: %d documents", count)
    except Exception as exc:
        logger.warning("ChromaDB health check failed: %s", exc)
        chromadb_status = "disconnected"

    status = "healthy" if chromadb_status == "connected" else "degraded"
    if llm_status != "available":
        status = "degraded"

    response = HealthResponse(
        status=status,
        chromadb=chromadb_status,
        llm=llm_status,
    )

    if chromadb_status == "connected" and llm_status == "available":
        return response

    raise HTTPException(
        status_code=503,
        detail=response.model_dump(),
    )


def _sse_event(payload: str, event_name: str | None = None) -> str:
    """Format a single SSE frame."""
    lines = []
    if event_name:
        lines.append(f"event: {event_name}")
    for line in payload.splitlines():
        lines.append(f"data: {line}")
    lines.append("")
    lines.append("")
    return "\n".join(lines)


async def _stream_response(question: str) -> AsyncIterator[str]:
    """Yield SSE frames for a RAG answer."""
    try:
        async for token in stream_answer(question):
            yield _sse_event(token)
        yield _sse_event("[DONE]")
    except RuntimeError as exc:
        logger.error("Streaming failed for query '%s': %s", question, exc)
        error_payload = json.dumps(
            {"message": "El servicio está congestionado, intentá de nuevo en unos segundos"}
        )
        yield _sse_event(error_payload, event_name="error")
    except Exception as exc:
        logger.exception("Unexpected error streaming answer for '%s'", question)
        error_payload = json.dumps(
            {"message": "Ocurrió un error inesperado. Intentá de nuevo más tarde."}
        )
        yield _sse_event(error_payload, event_name="error")


@app.post("/api/chat")
async def chat(request: Request, body: ChatRequest) -> StreamingResponse:
    """Stream a RAG-generated answer via SSE."""
    if not settings.nvidia_api_key:
        logger.error("NVIDIA_API_KEY not set; refusing /api/chat request")
        raise HTTPException(
            status_code=500,
            detail="Backend misconfiguration: NVIDIA_API_KEY not set",
        )

    logger.info(
        "Chat request: conversation_id=%s message='%s'",
        body.conversation_id,
        body.message,
    )

    return StreamingResponse(
        _stream_response(body.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
