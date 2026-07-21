from __future__ import annotations

import os
from pathlib import Path

from config import Settings


def test_pinecone_defaults(monkeypatch):
    monkeypatch.setenv("PINECONE_API_KEY", "")
    settings = Settings()
    assert settings.pinecone_index_name == "bimbam-docs"
    assert settings.pinecone_namespace == "bimbam_docs"


def test_pinecone_fields_from_env(monkeypatch):
    monkeypatch.setenv("PINECONE_API_KEY", "pcsk-xxx")
    monkeypatch.setenv("PINECONE_INDEX_NAME", "my-index")
    monkeypatch.setenv("PINECONE_NAMESPACE", "my-ns")
    settings = Settings()
    assert settings.pinecone_api_key == "pcsk-xxx"
    assert settings.pinecone_index_name == "my-index"
    assert settings.pinecone_namespace == "my-ns"


def test_documents_path_defaults_to_project_root_documents(monkeypatch):
    monkeypatch.delenv("DOCUMENTS_DIR", raising=False)
    settings = Settings(documents_dir="")
    path = settings.documents_path

    assert path.name == "documents"
    assert (path.parent / "backend").is_dir()


def test_documents_path_uses_documents_dir():
    settings = Settings(documents_dir="/custom/path/docs")
    assert str(settings.documents_path) == os.path.normpath("/custom/path/docs")
