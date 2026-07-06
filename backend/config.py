"""Centralized configuration for the BimBam chatbot backend.

Loads values from environment variables and an optional ``.env`` file placed
next to the backend entry point.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.

    All fields can be overridden via environment variables or a ``.env`` file.
    Variable names are the snake_case equivalents of the field names, e.g.
    ``OPENROUTER_API_KEY``.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # OpenRouter
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Models
    embedding_model: str = "llama-nemotron-embed-vl-1b-v2:free"
    chat_model: str = "nvidia/nemotron-3-ultra"

    # Vector store
    chroma_persist_dir: str = "chroma_db"
    collection_name: str = "bimbam_docs"

    # Ingestion
    documents_dir: str = "documents"
    chunk_size: int = 600
    chunk_overlap: int = 80

    # Retrieval
    retriever_k: int = 4
    similarity_threshold: float = 0.3

    # Runtime
    log_level: str = "INFO"
    request_timeout: float = 30.0


settings = Settings()
