
from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from typing import Any

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableSerializable
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config import settings
from store import get_retriever

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Sos un asistente de atención al cliente de BimBam Buy, un e-commerce LATAM. "
    "Usá SOLO la información del contexto para responder. "
    "Si no encontrás la respuesta, decí que no tenés esa información y sugerí al "
    "cliente que consulte los canales oficiales. "
    "Respondé en español, claro, amable y directo."
)

NO_CONTEXT_ANSWER = (
    "No tengo información suficiente para responder esa consulta. "
    "Te sugiero contactar a BimBam Buy a través de sus canales oficiales para "
    "recibir asistencia personalizada."
)

MAX_RETRIES = 3


def _format_context(docs: list[Document]) -> str:

    if not docs:
        return ""

    parts: list[str] = []
    for doc in docs:
        source = doc.metadata.get("source", "documento desconocido")
        page = doc.metadata.get("page", "?")
        parts.append(f"Documento {source} (pág {page}):\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def _retrieve_and_format(inputs: dict[str, Any]) -> dict[str, str]:

    question = inputs["question"]
    retriever = get_retriever(
        k=settings.retriever_k,
        score_threshold=settings.similarity_threshold,
    )
    docs = retriever.invoke(question)
    return {
        "question": question,
        "context": _format_context(docs),
    }


def build_chain() -> RunnableSerializable[dict[str, Any], str]:

    llm = ChatNVIDIA(
        model=settings.chat_model,
        api_key=settings.nvidia_api_key,
        base_url=settings.nvidia_base_url,
        temperature=0.3,
        timeout=settings.request_timeout,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            (
                "human",
                "Contexto:\n{context}\n\nPregunta: {question}\n\nRespuesta:",
            ),
        ]
    )

    return RunnableLambda(_retrieve_and_format) | prompt | llm | StrOutputParser()


async def stream_answer(
    question: str,
    history: list[tuple[str, str]] | None = None,
) -> AsyncIterator[str]:

    del history  # reserved for future session support

    if not settings.nvidia_api_key:
        logger.error("NVIDIA_API_KEY not set")
        raise RuntimeError("Backend misconfiguration: NVIDIA_API_KEY not set")

    chain = build_chain()

    async for attempt in AsyncRetrying(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type((RuntimeError,)),
        reraise=True,
    ):
        with attempt:
            try:
                context = ""
                async for token in chain.astream({"question": question}):
                    context += token
                    yield token
                if not context.strip():
                    yield NO_CONTEXT_ANSWER
                return
            except Exception as exc:
                error_message = str(exc).lower()
                if "429" in error_message or "rate limit" in error_message:
                    logger.warning(
                        "NVIDIA API rate limit for query '%s': %s",
                        question,
                        exc,
                    )
                    raise RuntimeError(f"NVIDIA API rate limit: {exc}") from exc
                logger.exception("LLM generation failed for query '%s'", question)
                raise

    yield NO_CONTEXT_ANSWER
