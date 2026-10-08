from datetime import datetime, timezone
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


class DailyTaskModel(BaseModel):
    id: Optional[str] = Field(
        default=None,
        alias="_id",
    )

    task_id: str = Field(
        ...,
        description="Unique task identifier",
    )

    user_id: str

    roadmap_id: Optional[str] = None

    date: str = Field(
        ...,
        description="YYYY-MM-DD date string",
    )

    day_number: int = Field(
        default=1,
        ge=1,
        le=365,
    )

    title: str
    description: str
    category: str
    skill: str

    priority: str = Field(
        default="HIGH",
        description="'HIGH', 'MEDIUM', 'LOW'",
    )

    estimated_minutes: int = Field(
        default=60,
        ge=1,
        le=1440,
    )

    actual_minutes: Optional[int] = Field(
        default=None,
        ge=0,
        le=1440,
    )

    difficulty: str = Field(
        default="Intermediate",
    )

    status: str = Field(
        default="pending",
        description="'pending', 'in_progress', 'completed', 'skipped'",
    )

    completion_percentage: float = Field(
        default=0.0,
        ge=0,
        le=100,
    )

    completed_at: Optional[datetime] = None

    notes: Optional[str] = None

    resource: Optional[Dict[str, Any]] = None

    route: Optional[str] = None

    created_at: datetime = Field(
        default_factory=_now_utc
    )

    updated_at: datetime = Field(
        default_factory=_now_utc
    )

    class Config:
        populate_by_name = True