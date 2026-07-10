from __future__ import annotations

import os
from pathlib import Path

from config import Settings


def test_chroma_path_resolves_relative_to_backend():
    settings = Settings(chroma_persist_dir="mi_chroma")
    chroma_path = settings.chroma_path

    assert isinstance(chroma_path, Path)
    assert chroma_path.name == "mi_chroma"
    assert chroma_path.parent.name == "backend"


def test_chroma_path_uses_chroma_persist_dir():
    settings = Settings(chroma_persist_dir="data/vector_store")
    chroma_path = settings.chroma_path

    assert chroma_path.name == "vector_store"
    assert chroma_path.parent.name == "data"
    assert chroma_path.parent.parent.name == "backend"


def test_documents_path_defaults_to_project_root_documents(monkeypatch):
    monkeypatch.delenv("DOCUMENTS_DIR", raising=False)
    settings = Settings(documents_dir="")
    path = settings.documents_path

    assert path.name == "documents"
    assert (path.parent / "backend").is_dir()


def test_documents_path_uses_documents_dir():
    settings = Settings(documents_dir="/custom/path/docs")
    assert str(settings.documents_path) == os.path.normpath("/custom/path/docs")
