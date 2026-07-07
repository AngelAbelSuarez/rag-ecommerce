"""Tests for the PDF ingestion pipeline."""

from pathlib import Path

import pytest
from langchain_core.documents import Document
from reportlab.pdfgen import canvas

from ingest import _extract_with_pypdf, load_pdf, split_documents


def _make_pdf(path: Path, pages: list[str]) -> None:
    """Create a minimal PDF with one page per text entry."""
    c = canvas.Canvas(str(path))
    for text in pages:
        if text:
            c.drawString(100, 700, text)
        c.showPage()
    c.save()


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """PDF with two non-empty pages."""
    path = tmp_path / "sample.pdf"
    _make_pdf(
        path,
        [
            "Página uno con información de envío.",
            "Página dos con detalles de garantía.",
        ],
    )
    return path


@pytest.fixture
def empty_page_pdf(tmp_path: Path) -> Path:
    """PDF with a single empty page."""
    path = tmp_path / "empty.pdf"
    _make_pdf(path, [""])
    return path


def test_load_pdf_returns_documents_with_source(sample_pdf: Path):
    """load_pdf returns Documents with source metadata."""
    docs = load_pdf(sample_pdf)

    assert isinstance(docs, list)
    assert len(docs) == 2
    for doc in docs:
        assert isinstance(doc, Document)
        assert doc.metadata["source"] == sample_pdf.name
        assert isinstance(doc.metadata["page"], int)
        assert doc.metadata["page"] > 0


def test_split_documents_chunks_smaller_than_chunk_size(monkeypatch):
    """split_documents produces chunks that fit within the configured size."""
    monkeypatch.setattr("ingest.settings.chunk_size", 80)
    monkeypatch.setattr("ingest.settings.chunk_overlap", 10)

    long_text = " ".join(["palabra"] * 200)
    docs = [Document(page_content=long_text, metadata={"source": "test"})]
    chunks = split_documents(docs)

    assert len(chunks) > 0
    assert all(len(chunk.page_content) <= 80 for chunk in chunks)


def test_extract_with_pypdf_handles_empty_page(empty_page_pdf: Path):
    """_extract_with_pypdf returns an empty Document for a blank page."""
    docs = _extract_with_pypdf(empty_page_pdf)

    assert isinstance(docs, list)
    assert len(docs) == 1
    assert docs[0].page_content == ""
    assert docs[0].metadata["source"] == empty_page_pdf.name
