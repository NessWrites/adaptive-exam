from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """
    Application settings.
    Loaded from environment variables and .env file.
    """

    # Core
    DATABASE_URL: str = Field(..., description="PostgreSQL connection URL")
    DEBUG: bool = False

    # Exam configuration
    N_ADAPTIVE_QUESTIONS: int = Field(default=40, ge=1)

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra = "ignore"
    )


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings instance.
    Safe to use across the application.
    """
    return Settings()

