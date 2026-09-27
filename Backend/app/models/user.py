from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserModel(BaseModel):
    """MongoDB User document model."""
    id: Optional[str] = Field(default=None, alias="_id")
    email: EmailStr
    hashed_password: str
    full_name: str
    is_active: bool = True
    is_onboarded: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
