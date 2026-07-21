
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


_BACKEND_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _BACKEND_DIR.parent


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=_BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    nvidia_api_key: str = ""
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"

    embedding_model: str = "nvidia/nv-embed-v1"
    chat_model: str = "nvidia/llama-3.1-nemotron-nano-vl-8b-v1"

    pinecone_api_key: str = ""
    pinecone_index_name: str = "bimbam-docs"
    pinecone_namespace: str = "bimbam_docs"

    documents_dir: str = ""
    chunk_size: int = 600
    chunk_overlap: int = 80

    retriever_k: int = 4
    similarity_threshold: float = 0.0

    log_level: str = "INFO"
    request_timeout: float = 30.0

    @property
    def documents_path(self) -> Path:

        if self.documents_dir:
            return Path(self.documents_dir)
        return _PROJECT_ROOT / "documents"




settings = Settings()
