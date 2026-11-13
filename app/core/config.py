from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    app_name: str = "Agentic RAG"
    openrouter_api_key: str = "OPENROUTER_API_KEY"
    openrouter_model: str = "openrouter/free"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    qdrant_path: str = "./data/qdrant"
    collection_name: str = "document_chunks"
    chunk_size: int = 900
    chunk_overlap: int = 150
    top_k: int = 12
    max_feedback_rounds: int = 2
    max_upload_mb: int = 20

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def absolute_qdrant_path(self) -> str:
        p = Path(self.qdrant_path)
        return str(p if p.is_absolute() else ROOT_DIR / p)

settings = Settings()
