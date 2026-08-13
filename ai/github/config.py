"""Configuration module for GitHub Analyzer using Pydantic Settings."""

from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """GitHub Analyzer application configuration."""

    APP_NAME: str = "AI Placement Copilot - GitHub Analyzer"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    HOST: str = "0.0.0.0"
    PORT: int = 8001

    # GitHub API Credentials
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_API_TOKEN: Optional[str] = None

    # CORS Settings
    CORS_ORIGINS: List[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def token(self) -> Optional[str]:
        """Returns the active GitHub API token."""
        return self.GITHUB_TOKEN or self.GITHUB_API_TOKEN


settings = Settings()
