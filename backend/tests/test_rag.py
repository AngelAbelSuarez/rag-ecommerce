from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.documents import Document
from langchain_core.runnables import RunnableSerializable

from rag import (
    GREETING_ANSWER,
    NO_CONTEXT_ANSWER,
    SYSTEM_PROMPT,
    _format_context,
    _is_greeting,
    _retrieve_and_format,
    build_chain,
    stream_answer,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def no_api_key(monkeypatch):
    monkeypatch.setattr("rag.settings.nvidia_api_key", "")


@pytest.fixture
def fake_api_key(monkeypatch):
    monkeypatch.setattr("rag.settings.nvidia_api_key", "fake-key-for-tests")


# ---------------------------------------------------------------------------
# Tests existentes
# ---------------------------------------------------------------------------

def test_build_chain_returns_runnable(fake_api_key):
    chain = build_chain()
    assert isinstance(chain, RunnableSerializable)


def test_stream_answer_raises_when_key_missing(no_api_key):
    async def _consume():
        async for _ in stream_answer("¿cómo hago un envío?"):
            pass

    with pytest.raises(RuntimeError, match="NVIDIA_API_KEY not set"):
        asyncio.run(_consume())


def test_system_prompt_contains_brand_and_language():
    assert "BimBam Buy" in SYSTEM_PROMPT
    assert "español" in SYSTEM_PROMPT


def test_no_context_answer_is_fallback_string():
    assert isinstance(NO_CONTEXT_ANSWER, str)
    assert len(NO_CONTEXT_ANSWER) > 0
    assert "canales oficiales" in NO_CONTEXT_ANSWER


def test_greeting_answer_is_string():
    assert isinstance(GREETING_ANSWER, str)
    assert len(GREETING_ANSWER) > 0
    assert "BimBam Buy" in GREETING_ANSWER


# ---------------------------------------------------------------------------
# _is_greeting
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "hola",
        "Hola",
        "HOLA!",
        "buenas",
        "buen dia",
        "buenos días",
        "buenas tardes",
        "buenas noches",
        "hello",
        "hi",
        "hey",
        "qué tal",
        "que tal",
        "como estas",
        "cómo estás",
        "cómo está",
        "cómo están",
        "cómo va",
        "como te va",
        "cómo andan",
        "good morning",
        "good afternoon",
        "good evening",
    ],
)
def test_is_greeting_returns_true(text):
    assert _is_greeting(text)


@pytest.mark.parametrize(
    "text",
    [
        "hola necesito ayuda con un envío",
        "buenas, cómo hago una devolución",
        "qué tal, consulta sobre garantía",
        "cristianismo",
        "cuáles son los métodos de pago",
        "cómo trackear mi pedido",
        "",
        "   ",
    ],
)
def test_is_greeting_returns_false(text):
    assert not _is_greeting(text)


# ---------------------------------------------------------------------------
# _format_context
# ---------------------------------------------------------------------------

def test_format_context_empty():
    assert _format_context([]) == ""


def test_format_context_with_docs():
    docs = [
        Document(
            page_content="Información de envío",
            metadata={"source": "manual.pdf", "page": 3},
        ),
        Document(
            page_content="Detalles de garantía",
            metadata={"source": "garantia.pdf", "page": 1},
        ),
    ]
    result = _format_context(docs)
    assert "manual.pdf" in result
    assert "pág 3" in result
    assert "Información de envío" in result
    assert "garantia.pdf" in result


def test_format_context_with_default_metadata():
    docs = [
        Document(page_content="Solo texto", metadata={}),
    ]
    result = _format_context(docs)
    assert "documento desconocido" in result
    assert "?" in result


# ---------------------------------------------------------------------------
# _retrieve_and_format
# ---------------------------------------------------------------------------

def test_retrieve_and_format(fake_api_key, monkeypatch):
    fake_docs = [
        Document(page_content="Info de envío", metadata={"source": "faq.pdf", "page": 1}),
    ]
    mock_retriever = MagicMock()
    mock_retriever.invoke.return_value = fake_docs
    monkeypatch.setattr("rag.get_retriever", lambda **kw: mock_retriever)
    monkeypatch.setattr("rag.settings.retriever_k", 4)
    monkeypatch.setattr("rag.settings.similarity_threshold", 0.0)

    result = _retrieve_and_format({"question": "¿cómo envío?"})
    assert result["question"] == "¿cómo envío?"
    assert "Info de envío" in result["context"]
    assert "faq.pdf" in result["context"]


# ---------------------------------------------------------------------------
# stream_answer — retry en rate limit
# ---------------------------------------------------------------------------

def test_stream_answer_retries_on_rate_limit(fake_api_key, monkeypatch):
    """429 → reintenta 2 veces → agota intentos → RuntimeError."""
    chain_attempts = 0

    class FakeChain:
        async def astream(self, _inputs):
            nonlocal chain_attempts
            chain_attempts += 1
            raise RuntimeError("429 Too Many Requests")
            yield  # pragma: no cover

    monkeypatch.setattr("rag.build_chain", lambda: FakeChain())
    monkeypatch.setattr("rag.MAX_RETRIES", 2)
    monkeypatch.setattr("rag.settings.request_timeout", 5.0)

    async def collect():
        async for _ in stream_answer("¿consulta?"):
            pass

    with pytest.raises(RuntimeError, match="NVIDIA API rate limit"):
        asyncio.run(collect())

    assert chain_attempts == 2


def test_stream_answer_returns_no_context_when_empty(fake_api_key, monkeypatch):
    """Cadena devuelve string vacío → yields NO_CONTEXT_ANSWER."""

    class EmptyChain:
        async def astream(self, _inputs):
            yield ""

    monkeypatch.setattr("rag.build_chain", lambda: EmptyChain())
    monkeypatch.setattr("rag.settings.request_timeout", 5.0)

    async def collect():
        tokens = []
        async for token in stream_answer("¿consulta?"):
            tokens.append(token)
        return "".join(tokens)

    result = asyncio.run(collect())
    assert result == NO_CONTEXT_ANSWER


def test_stream_answer_passes_on_non_429(fake_api_key, monkeypatch):
    """Error no-429 se relanza sin reintentar."""

    class FailingChain:
        async def astream(self, _inputs):
            raise ValueError("algo explotó")
            yield  # pragma: no cover — never reached

    monkeypatch.setattr("rag.build_chain", lambda: FailingChain())
    monkeypatch.setattr("rag.MAX_RETRIES", 1)
    monkeypatch.setattr("rag.settings.request_timeout", 5.0)

    async def collect():
        tokens = []
        async for token in stream_answer("¿consulta?"):
            tokens.append(token)
        return "".join(tokens)

    with pytest.raises(ValueError, match="algo explotó"):
        asyncio.run(collect())


def test_stream_answer_returns_greeting_for_hola(fake_api_key, monkeypatch):
    """Saludo puro → GREETING_ANSWER sin invocar build_chain."""

    chain_called = False

    def _fake_build():
        nonlocal chain_called
        chain_called = True
        return MagicMock()

    monkeypatch.setattr("rag.build_chain", _fake_build)

    async def collect():
        tokens = []
        async for token in stream_answer("hola"):
            tokens.append(token)
        return "".join(tokens)

    result = asyncio.run(collect())
    assert result == GREETING_ANSWER
    assert not chain_called, "build_chain no debe invocarse para saludos"


# ---------------------------------------------------------------------------
# build_chain no necesita API key para construirse
# ---------------------------------------------------------------------------

def test_build_chain_does_not_raise_without_key():
    chain = build_chain()
    assert isinstance(chain, RunnableSerializable)
