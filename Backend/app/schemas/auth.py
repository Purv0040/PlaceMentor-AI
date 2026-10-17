from typing import Any
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Minimum 6 characters")
    full_name: str = Field(..., min_length=2, description="Candidate's full name")

    @model_validator(mode="before")
    @classmethod
    def normalize_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Accept 'name' or 'fullName' if 'full_name' is missing
            if not data.get("full_name"):
                if data.get("name"):
                    data["full_name"] = data["name"]
                elif data.get("fullName"):
                    data["full_name"] = data["fullName"]

            # Trim string values if provided
            if isinstance(data.get("email"), str):
                data["email"] = data["email"].strip()
            if isinstance(data.get("full_name"), str):
                data["full_name"] = data["full_name"].strip()
        return data

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        return v

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        cleaned = v.strip() if isinstance(v, str) else ""
        if len(cleaned) < 2:
            raise ValueError("Full name must be at least 2 characters long.")
        return cleaned


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class GoogleAuthRequest(BaseModel):
    credential: str = Field(..., description="Google ID token from Google Sign-In")
