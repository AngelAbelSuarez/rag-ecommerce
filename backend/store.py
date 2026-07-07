"""ChromaDB vector store client and retriever factory for the RAG pipeline.

Uses the official ``langchain_nvidia_ai_endpoints`` package for embeddings
instead of LangChain's built-in OpenAI wrapper, because NVIDIA's embedding
API requires vendor-specific parameters (``input_type``, ``truncate``) that
the official package handles internally.
"""

import logging

from langchain_chroma import Chroma
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings

from config import settings

logger = logging.getLogger(__name__)


def get_embeddings() -> NVIDIAEmbeddings:
    """Return an NVIDIA-compatible embedding instance."""
    if not settings.nvidia_api_key:
        raise RuntimeError("NVIDIA_API_KEY not set")
    return NVIDIAEmbeddings(
        model=settings.embedding_model,
        nvidia_api_key=settings.nvidia_api_key,
        base_url=settings.nvidia_base_url,
        truncate="NONE",
    )


def get_vectorstore() -> Chroma:
    """Return the persistent ChromaDB vector store for the configured collection."""
    embeddings = get_embeddings()
    return Chroma(
        persist_directory=str(settings.chroma_path),
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
