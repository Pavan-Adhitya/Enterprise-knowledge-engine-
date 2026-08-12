import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application Settings managed via Environment Variables."""
    
    PROJECT_NAME: str = "Enterprise Knowledge Engine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # LLM Settings
    GEMINI_API_KEY: str = ""
    DEFAULT_LLM_MODEL: str = "gemini-2.0-flash"
    EMBEDDING_MODEL: str = "models/embedding-001"
    
    # Storage Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    CHROMA_PERSIST_DIR: str = "./storage/vector_db"
    UPLOAD_DIR: str = "./storage/uploads"
    DATABASE_URL: str = "sqlite+aiosqlite:///./storage/app.db"
    
    # RAG Tuning Default Values
    DEFAULT_CHUNK_SIZE: int = 768
    DEFAULT_CHUNK_OVERLAP: int = 100
    DEFAULT_TOP_K: int = 4
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def chroma_path(self) -> Path:
        p = Path(self.CHROMA_PERSIST_DIR)
        return p if p.is_absolute() else self.BASE_DIR / p

    @property
    def uploads_path(self) -> Path:
        p = Path(self.UPLOAD_DIR)
        return p if p.is_absolute() else self.BASE_DIR / p


settings = Settings()
