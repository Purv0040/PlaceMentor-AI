from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class DailyTaskModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    task_id: str = Field(..., description="Unique task identifier")
    user_id: str = Field(...)
    roadmap_id: Optional[str] = Field(default=None)
    date: str = Field(..., description="YYYY-MM-DD date string")
    day_number: int = Field(default=1, ge=1, le=90)
    title: str = Field(...)
    description: str = Field(...)
    category: str = Field(...)
    skill: str = Field(...)
    priority: str = Field("HIGH", description="'HIGH', 'MEDIUM', 'LOW'")
    estimated_minutes: int = Field(default=60)
    actual_minutes: Optional[int] = Field(default=None)
    difficulty: str = Field(default="Intermediate")
    status: str = Field(default="pending", description="'pending', 'in_progress', 'completed', 'skipped'")
    completion_percentage: float = Field(default=0.0)
    completed_at: Optional[datetime] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    resource: Optional[Dict[str, Any]] = Field(default=None)
    route: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
