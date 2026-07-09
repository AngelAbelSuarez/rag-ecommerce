
from unittest.mock import MagicMock, patch

import pytest
from langchain_chroma import Chroma
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings

from store import get_embeddings, get_retriever, get_vectorstore


@pytest.fixture
def no_api_key(monkeypatch):

    monkeypatch.setattr("store.settings.nvidia_api_key", "")


@pytest.fixture
def fake_api_key(monkeypatch):

    monkeypatch.setattr("store.settings.nvidia_api_key", "fake-key-for-tests")


def test_get_embeddings_returns_nvidia_embeddings(fake_api_key):

    embeddings = get_embeddings()
    assert isinstance(embeddings, NVIDIAEmbeddings)


def test_get_embeddings_raises_when_key_empty(no_api_key):

    with pytest.raises(RuntimeError, match="NVIDIA_API_KEY not set"):
        get_embeddings()


def test_get_vectorstore_returns_chroma(fake_api_key, tmp_path, monkeypatch):

    monkeypatch.setattr("store.settings.chroma_persist_dir", str(tmp_path / "chroma"))
    vectorstore = get_vectorstore()
    assert isinstance(vectorstore, Chroma)


def test_get_retriever_uses_defaults(fake_api_key, tmp_path, monkeypatch):

    monkeypatch.setattr("store.settings.chroma_persist_dir", str(tmp_path / "chroma"))
    monkeypatch.setattr("store.settings.retriever_k", 4)
    monkeypatch.setattr("store.settings.similarity_threshold", 0.25)

    retriever = get_retriever()
    assert retriever.search_kwargs["k"] == 4
    assert retriever.search_kwargs["score_threshold"] == 0.25


def test_get_retriever_allows_overrides(fake_api_key, tmp_path, monkeypatch):

    monkeypatch.setattr("store.settings.chroma_persist_dir", str(tmp_path / "chroma"))

    retriever = get_retriever(k=10, score_threshold=0.5)
    assert retriever.search_kwargs["k"] == 10
    assert retriever.search_kwargs["score_threshold"] == 0.5
