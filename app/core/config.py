from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "Document Intelligence & Question Extraction Service"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Security & Auth
    SECRET_KEY: str = "pragati_bharati_super_secure_document_intelligence_secret_key_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Primary PostgreSQL Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/doc_intelligence"
    DATABASE_URL_SYNC: str = "postgresql+psycopg://postgres:postgres@localhost:5432/doc_intelligence"
    
    # SQLite Fallback (Zero-config local mode when Postgres isn't running)
    SQLITE_FALLBACK_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/storage/dev_database.db"
    SQLITE_SYNC_URL: str = f"sqlite:///{BASE_DIR}/storage/dev_database.db"

    # Redis Queue & Distributed State
    REDIS_URL: str = "redis://localhost:6379/0"

    # External AI & Vision Service (Gemini API)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # File Ingestion & Storage Limits
    MAX_UPLOAD_SIZE_MB: int = 25
    UPLOAD_DIR: str = str(BASE_DIR / "storage" / "uploads")
    EXTRACTED_DIR: str = str(BASE_DIR / "storage" / "extracted")
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "png", "jpg", "jpeg"]

settings = Settings()
