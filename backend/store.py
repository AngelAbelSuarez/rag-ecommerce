"""ChromaDB vector store client and retriever factory for the RAG pipeline.

Uses a direct OpenAI client (not LangChain's OpenAIEmbeddings) to work around
compatibility issues between LangChain's token-based batching and OpenRouter's
embedding API.
"""

import logging
from typing import Any

from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from openai import OpenAI

from config import settings

logger = logging.getLogger(__name__)


class OpenRouterEmbeddings(Embeddings):
    """LangChain-compatible embeddings wrapper around the raw OpenAI client.

    Sends plain text (not token IDs) so that OpenRouter's free embedding
    models work correctly.
    """

    def __init__(self, **kwargs: Any) -> None:
        self.client = OpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            **kwargs,
        )
        self.model = settings.embedding_model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of documents."""
        response = self.client.embeddings.create(
            model=self.model, input=texts, encoding_format="float"
        )
        return [item.embedding for item in response.data]

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query string."""
        response = self.client.embeddings.create(
            model=self.model, input=[text], encoding_format="float"
        )
        return response.data[0].embedding


def get_embeddings() -> OpenRouterEmbeddings:
    """Return an OpenRouter-compatible embedding instance."""
    if not settings.openrouter_api_key:
        raise RuntimeError("OPENROUTER_API_KEY not set")
    return OpenRouterEmbeddings()


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
