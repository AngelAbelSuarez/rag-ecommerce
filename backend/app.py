
from __future__ import annotations

import json
import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pinecone import Pinecone
from pydantic import BaseModel, Field

from config import settings
from rag import stream_answer

logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):

    message: str = Field(..., min_length=1, description="User question")
    conversation_id: str | None = Field(
        default=None,
        description="Optional client-side conversation id (reserved for future use)",
    )


class HealthResponse(BaseModel):

    status: str
    vectorstore: str
    llm: str | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001

    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(levelname)s: %(message)s",
    )

    yield


app = FastAPI(
    title="BimBam Chatbot API",
    description="RAG chatbot runtime for BimBam Buy",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
async def health() -> HealthResponse:

    vectorstore_status = "connected"
    llm_status = "available" if settings.nvidia_api_key else "unavailable"

    try:
        os.environ.setdefault("PINECONE_API_KEY", settings.pinecone_api_key)
        pc = Pinecone(api_key=settings.pinecone_api_key)
        idx = pc.Index(settings.pinecone_index_name)
        stats = idx.describe_index_stats()
        count = sum(ns.vector_count for ns in stats.namespaces.values()) if stats.namespaces else 0
        logger.debug("Pinecone health check: %d vectors", count)
    except Exception as exc:
        logger.warning("vector store health check failed: %s", exc)
        vectorstore_status = "disconnected"

    status = "healthy" if vectorstore_status == "connected" else "degraded"
    if llm_status != "available":
        status = "degraded"

    response = HealthResponse(
        status=status,
        vectorstore=vectorstore_status,
        llm=llm_status,
    )

    if vectorstore_status == "connected" and llm_status == "available":
        return response

    raise HTTPException(
        status_code=503,
        detail=response.model_dump(),
    )


def _sse_event(payload: str, event_name: str | None = None) -> str:

    lines = []
    if event_name:
        lines.append(f"event: {event_name}")
    for line in payload.splitlines():
        lines.append(f"data: {line}")
    lines.append("")
    lines.append("")
    return "\n".join(lines)


async def _stream_response(question: str) -> AsyncIterator[str]:

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
