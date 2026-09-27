from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ProgressModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str = Field(...)
    roadmap_id: Optional[str] = Field(default=None)
    total_tasks: int = Field(default=0)
    completed_tasks: int = Field(default=0)
    pending_tasks: int = Field(default=0)
    skipped_tasks: int = Field(default=0)
    completion_percentage: float = Field(default=0.0)
    roadmap_completion_percentage: float = Field(default=0.0)
    weekly_completion: List[Dict[str, Any]] = Field(default_factory=list)
    daily_completion: List[Dict[str, Any]] = Field(default_factory=list)
    skill_progress: Dict[str, float] = Field(default_factory=dict)
    current_streak: int = Field(default=0)
    longest_streak: int = Field(default=0)
    last_active_date: Optional[str] = Field(default=None)
    completed_milestones: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
