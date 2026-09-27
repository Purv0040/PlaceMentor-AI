import json
from typing import List, Union, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application settings loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # Application settings
    APP_NAME: str = "AI Placement Copilot"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    

    # Database settings - supports both MONGODB_URL and MONGODB_URI
    MONGODB_URL: Optional[str] = None
    MONGODB_URI: str = "mongodb://localhost:27017/placementor"
    MONGODB_DATABASE: str = "placementor"

    # Cache settings
    REDIS_URL: str = "redis://localhost:6379"

    # External AI microservice
    AI_SERVICE_URL: str = "http://localhost:8001"

    # GitHub API Configuration
    GITHUB_API_URL: str = "https://api.github.com"
    GITHUB_TOKEN: Optional[str] = None

    # LeetCode API Configuration
    LEETCODE_API_URL: str = "https://leetcode.com/graphql"

    # Security & JWT settings
    JWT_SECRET_KEY: str = "change_this_to_a_secure_local_secret_key_1234567890"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # File uploads
    UPLOAD_DIR: str = "uploads"
    MAX_RESUME_SIZE_MB: int = 5

    # CORS origins
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:5173"]

    def get_mongo_uri(self) -> str:
        """Returns the effective MongoDB connection string (preferring MONGODB_URL)."""
        return self.MONGODB_URL or self.MONGODB_URI

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:5173"]


settings = Settings()
