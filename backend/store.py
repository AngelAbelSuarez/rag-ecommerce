
import logging

from langchain_chroma import Chroma
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


def get_vectorstore() -> Chroma:

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
