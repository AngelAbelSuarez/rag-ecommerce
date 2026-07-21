
import logging
import os

from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings

from config import settings

logger = logging.getLogger(__name__)


def get_embeddings() -> NVIDIAEmbeddings:

    if not settings.nvidia_api_key:
        raise RuntimeError("NVIDIA_API_KEY not set")
    return NVIDIAEmbeddings(
        model=settings.embedding_model,
        nvidia_api_key=settings.nvidia_api_key,
        base_url=settings.nvidia_base_url,
        truncate="NONE",
    )


def get_vectorstore():

    if not settings.pinecone_api_key:
        raise RuntimeError("PINECONE_API_KEY not set")
    os.environ.setdefault("PINECONE_API_KEY", settings.pinecone_api_key)

    embeddings = get_embeddings()
    from langchain_pinecone import PineconeVectorStore

    return PineconeVectorStore.from_existing_index(
        index_name=settings.pinecone_index_name,
        embedding=embeddings,
        namespace=settings.pinecone_namespace,
    )


def get_retriever(
    k: int | None = None,
    score_threshold: float | None = None,
):

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
