"""Application configuration.

Pydantic BaseSettings loads from environment variables (or .env file). All
secrets stay out of source. See `.env.example` for the full list.
"""
from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    APP_NAME: str = "AI Content Verification System"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_LOG_LEVEL: str = "INFO"

    # Security
    JWT_SECRET: str = Field(..., min_length=32)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TTL_MINUTES: int = 15
    JWT_REFRESH_TTL_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_cors(cls, v):
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    # Database
    DATABASE_URL: str = "sqlite:///./acvs.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Rate limits
    RATE_LIMIT_GLOBAL: str = "60/minute"
    RATE_LIMIT_SCAN: str = "5/minute"

    # AI Engine
    AI_ENGINE_URL: str = ""
    AI_ENGINE_TIMEOUT: int = 30

    # Upload limits
    MAX_TEXT_LENGTH: int = 50_000
    MAX_IMAGE_MB: int = 10
    MAX_AUDIO_MB: int = 50
    MAX_VIDEO_MB: int = 100

    # Retention
    UPLOAD_AUTO_DELETE_SECONDS: int = 300

    @property
    def is_prod(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor — import once, reuse everywhere."""
    return Settings()
