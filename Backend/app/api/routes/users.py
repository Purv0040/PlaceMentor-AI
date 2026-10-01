from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserModel(BaseModel):
    """MongoDB user document model."""

    model_config = ConfigDict(
        populate_by_name=True
    )

    id: Optional[str] = Field(
        default=None,
        alias="_id",
    )

    email: EmailStr

    hashed_password: str

    full_name: str

    is_active: bool = True

    is_onboarded: bool = False

    created_at: datetime = Field(
        default_factory=utc_now
    )

    updated_at: datetime = Field(
        default_factory=utc_now
    )