"""ChromaDB vector store client and retriever factory for the RAG pipeline."""

import logging

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from backend.config import settings

logger = logging.getLogger(__name__)


def get_embeddings() -> OpenAIEmbeddings:
    """Return an OpenAI-compatible embedding client pointing at OpenRouter."""
    if not settings.openrouter_api_key:
        raise RuntimeError("OPENROUTER_API_KEY not set")

    return OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_base=settings.openrouter_base_url,
        openai_api_key=settings.openrouter_api_key,
    )


def get_vectorstore() -> Chroma:
    """Return the persistent ChromaDB vector store for the configured collection."""
    embeddings = get_embeddings()
    return Chroma(
        persist_directory=settings.chroma_persist_dir,
        collection_name=settings.collection_name,
        embedding_function=embeddings,
    )


def get_retriever(
    k: int | None = None,
    score_threshold: float | None = None,
) -> Chroma:
    """Return a Chroma retriever with similarity-score thresholding.

    Args:
        k: Number of documents to retrieve. Defaults to ``settings.retriever_k``.
        score_threshold: Minimum similarity score to include a document.
            Defaults to ``settings.similarity_threshold``.

    Returns:
        A Chroma retriever configured with ``similarity_score_threshold``.
    """
    vectorstore = get_vectorstore()
    search_kwargs: dict = {
        "k": k if k is not None else settings.retriever_k,
    }
    search_kwargs["score_threshold"] = (
        score_threshold
        if score_threshold is not None
        else settings.similarity_threshold
    )

    return vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs=search_kwargs,
    )
