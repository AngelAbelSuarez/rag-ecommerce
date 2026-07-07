"""Tests for the RAG chain assembly."""

import asyncio

import pytest
from langchain_core.runnables import RunnableSerializable

from rag import NO_CONTEXT_ANSWER, SYSTEM_PROMPT, build_chain, stream_answer


@pytest.fixture
def no_api_key(monkeypatch):
    """Simulate a missing NVIDIA_API_KEY."""
    monkeypatch.setattr("rag.settings.nvidia_api_key", "")


@pytest.fixture
def fake_api_key(monkeypatch):
    """Simulate a configured NVIDIA_API_KEY."""
    monkeypatch.setattr("rag.settings.nvidia_api_key", "fake-key-for-tests")


def test_build_chain_returns_runnable(fake_api_key):
    """build_chain returns a LangChain RunnableSerializable."""
    chain = build_chain()
    assert isinstance(chain, RunnableSerializable)


def test_stream_answer_raises_when_key_missing(no_api_key):
    """stream_answer raises RuntimeError when the API key is not set."""

    async def _consume():
        async for _ in stream_answer("¿cómo hago un envío?"):
            pass

    with pytest.raises(RuntimeError, match="NVIDIA_API_KEY not set"):
        asyncio.run(_consume())


def test_system_prompt_contains_brand_and_language():
    """The system prompt names the brand and mandates Spanish."""
    assert "BimBam Buy" in SYSTEM_PROMPT
    assert "español" in SYSTEM_PROMPT


def test_no_context_answer_is_fallback_string():
    """NO_CONTEXT_ANSWER is the polite fallback returned on empty context."""
    assert isinstance(NO_CONTEXT_ANSWER, str)
    assert len(NO_CONTEXT_ANSWER) > 0
    assert "canales oficiales" in NO_CONTEXT_ANSWER
