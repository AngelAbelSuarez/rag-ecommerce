"""Centralized configuration for the BimBam chatbot backend.

Loads values from environment variables and an optional ``.env`` file.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


# The directory containing this config.py file (backend/)
_BACKEND_DIR = Path(__file__).resolve().parent
# The project root (parent of backend/)
_PROJECT_ROOT = _BACKEND_DIR.parent


class Settings(BaseSettings):
    """Application settings.

    All fields can be overridden via environment variables or a ``.env`` file
    placed in the ``backend/`` directory.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # OpenRouter
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Models
    embedding_model: str = "llama-nemotron-embed-vl-1b-v2:free"
    chat_model: str = "nvidia/nemotron-3-ultra-550b-a55b:free"

    # Vector store (relative to backend/)
    chroma_persist_dir: str = "chroma_db"
    collection_name: str = "bimbam_docs"

    # Ingestion (documents/ is at project root)
    documents_dir: str = ""
    chunk_size: int = 600
    chunk_overlap: int = 80

    # Retrieval
    retriever_k: int = 4
    similarity_threshold: float = 0.0

    # Runtime
    log_level: str = "INFO"
    request_timeout: float = 30.0

    @property
    def documents_path(self) -> Path:
        """Return the absolute path to the documents directory."""
        if self.documents_dir:
            return Path(self.documents_dir)
        return _PROJECT_ROOT / "documents"

    @property
    def chroma_path(self) -> Path:
        """Return the absolute path to the ChromaDB persistence directory."""
        return _BACKEND_DIR / self.chroma_persist_dir


settings = Settings()
