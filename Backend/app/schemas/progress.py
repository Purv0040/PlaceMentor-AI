from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


class WeeklyCompletionSchema(BaseModel):
    week: int
    start_date: str
    end_date: str
    total: int = 0
    completed: int = 0
    pending: int = 0
    skipped: int = 0
    percentage: float = 0.0


class ProgressResponseSchema(BaseModel):
    id: Optional[str] = None

    user_id: str
    roadmap_id: Optional[str] = None

    total_tasks: int = 0
    completed_tasks: int = 0
    pending_tasks: int = 0
    skipped_tasks: int = 0

    completion_percentage: float = 0.0
    roadmap_completion_percentage: float = 0.0

    weekly_completion: List[WeeklyCompletionSchema] = Field(
        default_factory=list
    )

    daily_completion: List[Dict[str, Any]] = Field(
        default_factory=list
    )

    skill_progress: Dict[str, float] = Field(
        default_factory=dict
    )

    current_streak: int = 0
    longest_streak: int = 0

    last_active_date: Optional[str] = None

    completed_milestones: List[str] = Field(
        default_factory=list
    )

    updated_at: datetime


class ProgressSummaryResponseSchema(BaseModel):
    user_id: str

    total_tasks: int
    completed_tasks: int

    completion_percentage: float

    current_streak: int
    longest_streak: int

    roadmap_completion_percentage: float

    top_skills_completed: List[str] = Field(
        default_factory=list
    )


class StreakResponseSchema(BaseModel):
    current_streak: int
    longest_streak: int

    last_active_date: Optional[str] = None

    is_active_today: bool = False


ProgressResponse = ProgressResponseSchema