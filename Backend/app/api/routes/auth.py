from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Registration request."""

    email: EmailStr

    password: str = Field(
        ...,
        min_length=6,
        max_length=72,
    )

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )


class LoginRequest(BaseModel):
    """Login request."""

    email: EmailStr

    password: str = Field(
        ...,
        min_length=6,
        max_length=72,
    )


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""

    refresh_token: str = Field(
        ...,
        min_length=1,
    )


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"