
from unittest.mock import MagicMock

import pytest
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings

from store import get_embeddings, get_retriever, get_vectorstore


@pytest.fixture
def no_api_key(monkeypatch):

    monkeypatch.setattr("store.settings.nvidia_api_key", "")


@pytest.fixture
def fake_api_key(monkeypatch):

    monkeypatch.setattr("store.settings.nvidia_api_key", "fake-key-for-tests")


@pytest.fixture
def fake_pinecone_key(fake_api_key, monkeypatch):

    monkeypatch.setattr("store.settings.pinecone_api_key", "fake-pinecone-key")


def test_get_embeddings_returns_nvidia_embeddings(fake_api_key):

    embeddings = get_embeddings()
    assert isinstance(embeddings, NVIDIAEmbeddings)


def test_get_embeddings_raises_when_key_empty(no_api_key):

    with pytest.raises(RuntimeError, match="NVIDIA_API_KEY not set"):
        get_embeddings()


def test_get_vectorstore_returns_pinecone(fake_pinecone_key, monkeypatch):

    mock_instance = MagicMock()
    mock_pinecone_class = MagicMock()
    mock_pinecone_class.from_existing_index.return_value = mock_instance
    monkeypatch.setattr("langchain_pinecone.PineconeVectorStore", mock_pinecone_class)

    result = get_vectorstore()
    assert result is mock_instance
    mock_pinecone_class.from_existing_index.assert_called_once()


def test_get_retriever_uses_defaults(fake_pinecone_key, monkeypatch):

    mock_retriever = MagicMock()
    mock_retriever.search_kwargs = {"k": 4, "score_threshold": 0.25}
    mock_instance = MagicMock()
    mock_instance.as_retriever.return_value = mock_retriever
    mock_pinecone_class = MagicMock()
    mock_pinecone_class.from_existing_index.return_value = mock_instance
    monkeypatch.setattr("langchain_pinecone.PineconeVectorStore", mock_pinecone_class)

    monkeypatch.setattr("store.settings.retriever_k", 4)
    monkeypatch.setattr("store.settings.similarity_threshold", 0.25)

    retriever = get_retriever()
    assert retriever.search_kwargs["k"] == 4
    assert retriever.search_kwargs["score_threshold"] == 0.25


def test_get_retriever_allows_overrides(fake_pinecone_key, monkeypatch):

    mock_retriever = MagicMock()
    mock_retriever.search_kwargs = {"k": 10, "score_threshold": 0.5}
    mock_instance = MagicMock()
    mock_instance.as_retriever.return_value = mock_retriever
    mock_pinecone_class = MagicMock()
    mock_pinecone_class.from_existing_index.return_value = mock_instance
    monkeypatch.setattr("langchain_pinecone.PineconeVectorStore", mock_pinecone_class)

    retriever = get_retriever(k=10, score_threshold=0.5)
    assert retriever.search_kwargs["k"] == 10
    assert retriever.search_kwargs["score_threshold"] == 0.5
