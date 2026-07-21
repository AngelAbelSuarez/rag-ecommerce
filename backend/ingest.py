
import logging
import os
import sys
import time
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone

from config import settings
from store import get_vectorstore

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(levelname)s: %(message)s",
)


def _extract_with_pypdf(path: Path) -> list[Document]:

    from pypdf import PdfReader

    reader = PdfReader(str(path), strict=False)
    docs: list[Document] = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        docs.append(
            Document(
                page_content=text,
                metadata={"source": path.name, "page": page_number},
            )
        )
    return docs


def _extract_with_pdfplumber(path: Path) -> list[Document]:

    import pdfplumber

    docs: list[Document] = []
    with pdfplumber.open(str(path)) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            docs.append(
                Document(
                    page_content=text,
                    metadata={"source": path.name, "page": page_number},
                )
            )
    return docs


def load_pdf(path: Path) -> list[Document]:

    try:
        docs = _extract_with_pypdf(path)
    except Exception as exc:
        logger.warning("pypdf failed for %s: %s; trying pdfplumber", path.name, exc)
        try:
            docs = _extract_with_pdfplumber(path)
        except Exception as fallback_exc:
            raise RuntimeError(
                f"Could not read {path.name}: {fallback_exc}"
            ) from fallback_exc

    for doc in docs:
        doc.metadata["source"] = path.name
        page = doc.metadata.get("page")
        if page is None:
            page = doc.metadata.get("page_number", 1)
        try:
            doc.metadata["page"] = int(page)
        except (TypeError, ValueError):
            doc.metadata["page"] = 1

    return docs


def split_documents(docs: list[Document]) -> list[Document]:

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " "],
        length_function=len,
    )
    return splitter.split_documents(docs)


def ingest() -> tuple[int, int]:

    docs_dir = settings.documents_path
    if not docs_dir.is_dir():
        logger.error("Documents directory not found: %s", docs_dir)
        raise SystemExit(1)

    pdf_paths = sorted(docs_dir.glob("*.pdf"))
    if not pdf_paths:
        logger.error("No PDFs found in %s", docs_dir.resolve())
        raise SystemExit(1)

    all_chunks: list[Document] = []
    for path in pdf_paths:
        try:
            logger.info("Processing %s", path.name)
            docs = load_pdf(path)
            chunks = split_documents(docs)
            for chunk in chunks:
                chunk.metadata["source"] = path.name
            all_chunks.extend(chunks)
            logger.info("  -> %d pages, %d chunks", len(docs), len(chunks))
        except Exception as exc:
            logger.error("Failed to process %s: %s", path.name, exc)
            continue

    if not all_chunks:
        logger.error("No chunks produced from any PDF")
        raise SystemExit(1)

    logger.info("Embedding %d chunks into Pinecone...", len(all_chunks))

    os.environ.setdefault("PINECONE_API_KEY", settings.pinecone_api_key)
    pc = Pinecone(api_key=settings.pinecone_api_key)
    idx = pc.Index(settings.pinecone_index_name)
    try:
        idx.delete(namespace=settings.pinecone_namespace, delete_all=False)
        logger.info("Deleted existing namespace '%s'", settings.pinecone_namespace)
    except Exception as exc:
        logger.info("Namespace '%s' did not exist or could not be deleted: %s", settings.pinecone_namespace, exc)

    vectorstore = get_vectorstore()
    vectorstore.add_documents(all_chunks)

    logger.info(
        "Ingestion complete: %d files, %d chunks persisted to Pinecone index '%s' namespace '%s'",
        len(pdf_paths),
        len(all_chunks),
        settings.pinecone_index_name,
        settings.pinecone_namespace,
    )
    return len(pdf_paths), len(all_chunks)


def main() -> None:
    if not settings.nvidia_api_key:
        logger.error("NVIDIA_API_KEY not set")
        sys.exit(1)
    if not settings.pinecone_api_key:
        logger.error("PINECONE_API_KEY not set")
        sys.exit(1)

    start = time.perf_counter()
    try:
        files, chunks = ingest()
        elapsed = time.perf_counter() - start
        logger.info("Done in %.2fs (%d files, %d chunks)", elapsed, files, chunks)
    except SystemExit:
        raise
    except Exception as exc:
        logger.exception("Ingestion failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
