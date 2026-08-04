"""Configuration module for AI Resume Analyzer using Pydantic Settings."""

import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """Application Settings loaded from environment variables or defaults."""

    # Application Information
    APP_NAME: str = "AI Placement Copilot - Resume Analyzer"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Upload Rules
    MAX_UPLOAD_SIZE_MB: int = 5
    ALLOWED_EXTENSIONS: List[str] = ["pdf"]
    UPLOAD_DIR: Path = BASE_DIR / "uploads"

    # Data & Model Configuration
    SKILLS_CSV_PATH: Path = BASE_DIR / "data" / "skills.csv"
    SPACY_MODEL: str = "en_core_web_sm"

    # ATS Scoring Weight Definitions (Total 100)
    WEIGHT_ESSENTIAL_SECTIONS: int = 30
    WEIGHT_TECHNICAL_SKILLS: int = 30
    WEIGHT_PROJECTS_EXPERIENCE: int = 20
    WEIGHT_CONTACT_INFO: int = 10
    WEIGHT_STRUCTURE: int = 10

    # CORS Settings
    CORS_ORIGINS: List[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def init_directories(self) -> None:
        """Ensure necessary runtime directories exist."""
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.SKILLS_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.init_directories()
