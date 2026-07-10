from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document
from reportlab.pdfgen import canvas

from ingest import (
    _extract_with_pdfplumber,
    _extract_with_pypdf,
    ingest,
    load_pdf,
    main,
    split_documents,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_pdf(path: Path, pages: list[str]) -> None:
    c = canvas.Canvas(str(path))
    for text in pages:
        if text:
            c.drawString(100, 700, text)
        c.showPage()
    c.save()


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    path = tmp_path / "sample.pdf"
    _make_pdf(path, ["Página uno con información de envío.", "Página dos con detalles de garantía."])
    return path


@pytest.fixture
def empty_page_pdf(tmp_path: Path) -> Path:
    path = tmp_path / "empty.pdf"
    _make_pdf(path, [""])
    return path


# ---------------------------------------------------------------------------
# Tests existentes
# ---------------------------------------------------------------------------

def test_load_pdf_returns_documents_with_source(sample_pdf: Path):
    docs = load_pdf(sample_pdf)
    assert isinstance(docs, list)
    assert len(docs) == 2
    for doc in docs:
        assert isinstance(doc, Document)
        assert doc.metadata["source"] == sample_pdf.name
        assert isinstance(doc.metadata["page"], int)
        assert doc.metadata["page"] > 0


def test_split_documents_chunks_smaller_than_chunk_size(monkeypatch):
    monkeypatch.setattr("ingest.settings.chunk_size", 80)
    monkeypatch.setattr("ingest.settings.chunk_overlap", 10)

    long_text = " ".join(["palabra"] * 200)
    docs = [Document(page_content=long_text, metadata={"source": "test"})]
    chunks = split_documents(docs)
    assert len(chunks) > 0
    assert all(len(chunk.page_content) <= 80 for chunk in chunks)


def test_extract_with_pypdf_handles_empty_page(empty_page_pdf: Path):
    docs = _extract_with_pypdf(empty_page_pdf)
    assert isinstance(docs, list)
    assert len(docs) == 1
    assert docs[0].page_content == ""
    assert docs[0].metadata["source"] == empty_page_pdf.name


# ---------------------------------------------------------------------------
# _extract_with_pdfplumber
# ---------------------------------------------------------------------------

def test_extract_with_pdfplumber(sample_pdf: Path):
    docs = _extract_with_pdfplumber(sample_pdf)
    assert isinstance(docs, list)
    assert len(docs) == 2
    assert "información de envío" in docs[0].page_content.lower()
    assert docs[0].metadata["source"] == sample_pdf.name
    assert docs[0].metadata["page"] == 1


def test_extract_with_pdfplumber_handles_empty_page(empty_page_pdf: Path):
    docs = _extract_with_pdfplumber(empty_page_pdf)
    assert len(docs) == 1
    assert docs[0].page_content == ""


# ---------------------------------------------------------------------------
# load_pdf — fallback y edge cases
# ---------------------------------------------------------------------------

def test_load_pdf_falls_back_to_pdfplumber_when_pypdf_fails(tmp_path: Path):
    path = tmp_path / "corrupt.pdf"
    _make_pdf(path, ["contenido"])

    with patch("ingest._extract_with_pypdf", side_effect=RuntimeError("pypdf error")):
        with patch("ingest._extract_with_pdfplumber") as mock_plumber:
            mock_plumber.return_value = [
                Document(page_content="ok", metadata={"source": path.name, "page": 1}),
            ]
            docs = load_pdf(path)

    assert len(docs) == 1
    mock_plumber.assert_called_once_with(path)


def test_load_pdf_raises_when_both_fail(tmp_path: Path):
    path = tmp_path / "bad.pdf"
    _make_pdf(path, ["nada"])

    with patch("ingest._extract_with_pypdf", side_effect=RuntimeError("pypdf error")):
        with patch("ingest._extract_with_pdfplumber", side_effect=RuntimeError("plumber error")):
            with pytest.raises(RuntimeError, match="Could not read"):
                load_pdf(path)


def test_load_pdf_defaults_page_when_missing(tmp_path: Path):
    path = tmp_path / "nopage.pdf"
    _make_pdf(path, ["test"])

    with patch("ingest._extract_with_pypdf") as mock_pypdf:
        mock_pypdf.return_value = [
            Document(page_content="test", metadata={"source": "nopage.pdf"}),
        ]
        docs = load_pdf(path)

    assert docs[0].metadata["page"] == 1


def test_load_pdf_handles_non_int_page(tmp_path: Path):
    path = tmp_path / "strpage.pdf"
    _make_pdf(path, ["test"])

    with patch("ingest._extract_with_pypdf") as mock_pypdf:
        mock_pypdf.return_value = [
            Document(page_content="test", metadata={"source": "strpage.pdf", "page": "three"}),
        ]
        docs = load_pdf(path)

    assert docs[0].metadata["page"] == 1


# ---------------------------------------------------------------------------
# ingest()
# ---------------------------------------------------------------------------

def test_ingest_raises_when_dir_not_found(monkeypatch):
    monkeypatch.setattr("ingest.settings.documents_dir", "/nonexistent")
    with pytest.raises(SystemExit):
        ingest()


def test_ingest_raises_when_no_pdfs(tmp_path: Path, monkeypatch):
    monkeypatch.setattr("ingest.settings.documents_dir", str(tmp_path))
    with pytest.raises(SystemExit):
        ingest()


def test_ingest_success(tmp_path: Path, monkeypatch):
    pdf_path = tmp_path / "test.pdf"
    _make_pdf(pdf_path, ["Página uno", "Página dos"])

    monkeypatch.setattr("ingest.settings.documents_dir", str(tmp_path))
    monkeypatch.setattr("ingest.settings.chunk_size", 500)
    monkeypatch.setattr("ingest.settings.chunk_overlap", 50)
    monkeypatch.setattr("ingest.settings.chroma_persist_dir", str(tmp_path / "chroma"))
    monkeypatch.setattr("ingest.settings.collection_name", "test_collection")

    mock_vs = MagicMock()
    monkeypatch.setattr("ingest.get_vectorstore", lambda: mock_vs)

    files, chunks = ingest()
    assert files == 1
    assert chunks > 0
    mock_vs.delete_collection.assert_called_once()
    mock_vs.add_documents.assert_called_once()


def test_ingest_skips_failing_pdf(tmp_path: Path, monkeypatch):
    good = tmp_path / "good.pdf"
    _make_pdf(good, ["bueno"])

    bad = tmp_path / "bad.pdf"
    _make_pdf(bad, ["malo"])

    monkeypatch.setattr("ingest.settings.documents_dir", str(tmp_path))
    monkeypatch.setattr("ingest.settings.chunk_size", 500)
    monkeypatch.setattr("ingest.settings.chunk_overlap", 0)
    monkeypatch.setattr("ingest.settings.chroma_persist_dir", str(tmp_path / "chroma"))
    monkeypatch.setattr("ingest.settings.collection_name", "test")

    original_load = load_pdf

    def flaky_load(path: Path):
        if "bad" in path.name:
            raise RuntimeError("corrupto")
        return original_load(path)

    monkeypatch.setattr("ingest.load_pdf", flaky_load)

    mock_vs = MagicMock()
    monkeypatch.setattr("ingest.get_vectorstore", lambda: mock_vs)

    files, chunks = ingest()
    # ingest() returns len(pdf_paths) — ambos archivos, uno falló
    assert files == 2
    assert chunks > 0


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------

def test_main_exits_when_no_api_key(monkeypatch):
    monkeypatch.setattr("ingest.settings.nvidia_api_key", "")
    with pytest.raises(SystemExit):
        main()


def test_main_success(monkeypatch, tmp_path):
    monkeypatch.setattr("ingest.settings.nvidia_api_key", "fake-key")

    pdf_path = tmp_path / "doc.pdf"
    _make_pdf(pdf_path, ["contenido"])

    monkeypatch.setattr("ingest.settings.documents_dir", str(tmp_path))
    monkeypatch.setattr("ingest.settings.chunk_size", 500)
    monkeypatch.setattr("ingest.settings.chunk_overlap", 0)
    monkeypatch.setattr("ingest.settings.chroma_persist_dir", str(tmp_path / "chroma"))
    monkeypatch.setattr("ingest.settings.collection_name", "test")

    mock_vs = MagicMock()
    monkeypatch.setattr("ingest.get_vectorstore", lambda: mock_vs)

    main()  # no debe levantar SystemExit


def test_main_handles_generic_exception(monkeypatch):
    monkeypatch.setattr("ingest.settings.nvidia_api_key", "fake-key")

    def broken_ingest():
        raise ValueError("unexpected error")

    monkeypatch.setattr("ingest.ingest", broken_ingest)

    with pytest.raises(SystemExit):
        main()
