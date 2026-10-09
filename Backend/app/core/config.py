import json
from typing import List, Optional, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # ========================================================
    # APPLICATION
    # ========================================================

    APP_NAME: str = "AI Placement Copilot"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # ========================================================
    # MONGODB
    # ========================================================

    MONGODB_URL: Optional[str] = None

    MONGODB_URI: str = (
        "mongodb://localhost:27017/placementor"
    )

    MONGODB_DATABASE: str = "placementor"

    # ========================================================
    # REDIS
    # ========================================================

    REDIS_URL: str = "redis://localhost:6379"

    # ========================================================
    # AI SERVICE
    # ========================================================

    AI_SERVICE_URL: str = "http://localhost:8001"

    # ========================================================
    # GITHUB
    # ========================================================

    GITHUB_API_URL: str = "https://api.github.com"
    GITHUB_TOKEN: Optional[str] = None

    # ========================================================
    # GOOGLE OAUTH
    # ========================================================

    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None


    # ========================================================
    # LEETCODE
    # ========================================================

    LEETCODE_API_URL: str = (
        "https://leetcode.com/graphql"
    )

    # ========================================================
    # JWT
    # ========================================================

    JWT_SECRET_KEY: str = (
        "default_secret_key_for_development_and_ci_testing_32bytes"
    )
    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ========================================================
    # UPLOADS
    # ========================================================

    UPLOAD_DIR: str = "uploads"
    MAX_RESUME_SIZE_MB: int = 5

    # ========================================================
    # CORS
    # ========================================================

    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]

    # ========================================================
    # MONGODB URI
    # ========================================================

    def get_mongo_uri(self) -> str:
        """
        Return the effective MongoDB URI.

        MONGODB_URL takes priority when provided.
        """
        return self.MONGODB_URL or self.MONGODB_URI

    # ========================================================
    # CORS VALIDATOR
    # ========================================================

    @field_validator(
        "CORS_ORIGINS",
        mode="before",
    )
    @classmethod
    def assemble_cors_origins(
        cls,
        value: Union[str, List[str]],
    ) -> List[str]:

        if isinstance(value, list):
            return value

        if isinstance(value, str):

            value = value.strip()

            if value.startswith("[") and value.endswith("]"):
                try:
                    parsed = json.loads(value)

                    if isinstance(parsed, list):
                        return parsed

                except json.JSONDecodeError:
                    pass

            return [
                item.strip()
                for item in value.split(",")
                if item.strip()
            ]

        return ["http://localhost:5173"]


settings = Settings()