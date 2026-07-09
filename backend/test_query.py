
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
import textwrap

from config import settings
from rag import stream_answer
from store import get_vectorstore

logger = logging.getLogger(__name__)


def _collection_has_data() -> bool:

    try:
        vectorstore = get_vectorstore()
        return vectorstore._collection.count() > 0
    except Exception as exc:
        logger.warning("Could not read ChromaDB collection: %s", exc)
        return False


def _ensure_ingested() -> None:

    if _collection_has_data():
        return

    print("ChromaDB está vacío. Ejecutando ingestión...")
    from backend import ingest

    try:
        files, chunks = ingest.ingest()
        print(f"Ingestión completa: {files} archivos, {chunks} chunks.")
    except SystemExit as exc:
        print("La ingestión falló. Verificá los logs y la configuración.")
        sys.exit(exc.code)


async def _run_query(question: str) -> str:

    answer_parts: list[str] = []
    async for token in stream_answer(question):
        answer_parts.append(token)
    return "".join(answer_parts)


def _print_answer(question: str, answer: str) -> None:

    print()
    print("=" * 60)
    print(f"Pregunta: {question}")
    print("=" * 60)
    print()
    print(textwrap.fill(answer, width=80))
    print()


async def _interactive_mode() -> None:

    print("BimBam RAG Tester — escribí tu pregunta o 'salir' para terminar.")
    while True:
        try:
            question = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nChau!")
            break

        if not question or question.lower() in {"salir", "exit", "quit"}:
            print("Chau!")
            break

        answer = await _run_query(question)
        _print_answer(question, answer)


def main() -> int:

    parser = argparse.ArgumentParser(
        description="Test the BimBam chatbot RAG pipeline."
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Pregunta a responder (omití para modo interactivo)",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Modo interactivo",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(levelname)s: %(message)s",
    )

    if not settings.nvidia_api_key:
        print(
            "ERROR: NVIDIA_API_KEY no está configurada.",
            file=sys.stderr,
        )
        return 1

    _ensure_ingested()

    if args.interactive or args.query is None:
        asyncio.run(_interactive_mode())
    else:
        answer = asyncio.run(_run_query(args.query))
        _print_answer(args.query, answer)

    return 0


if __name__ == "__main__":
    sys.exit(main())
