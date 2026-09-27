from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class RoadmapTaskItemModel(BaseModel):
    id: str = Field(..., description="Unique task identifier in roadmap")
    day: int = Field(..., ge=1, le=90)
    category: str = Field(...)
    title: str = Field(...)
    description: str = Field(...)
    estimated_minutes: int = Field(..., ge=10, le=480)
    difficulty: str = Field("Intermediate")
    priority: str = Field("High")
    skill: str = Field(...)
    status: str = Field("pending")


class RoadmapPhaseModel(BaseModel):
    phase_number: int = Field(..., ge=1, le=3)
    name: str = Field(...)
    day_range: str = Field(...)
    start_day: int = Field(...)
    end_day: int = Field(...)
    goal: str = Field(...)
    tasks: List[RoadmapTaskItemModel] = Field(default_factory=list)


class WeeklyGoalModel(BaseModel):
    week_number: int = Field(..., ge=1, le=13)
    objective: str = Field(...)
    skills: List[str] = Field(default_factory=list)
    tasks: List[str] = Field(default_factory=list)
    expected_outcome: str = Field(...)
    estimated_effort: str = Field(...)
    completion_percentage: float = Field(default=0.0)


class RoadmapModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    roadmap_id: Optional[str] = Field(default=None)
    user_id: str
    target_role: str
    title: str = Field(default="90-Day Placement Preparation Roadmap")
    description: Optional[str] = Field(default=None)
    summary: Optional[str] = Field(default=None)
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = Field(default=None)
    duration_days: int = Field(default=90)
    available_minutes_per_day: int = Field(default=120)
    total_estimated_hours: float = Field(default=0.0)
    phases: List[RoadmapPhaseModel] = Field(default_factory=list)
    weekly_goals: List[WeeklyGoalModel] = Field(default_factory=list)
    all_tasks: List[RoadmapTaskItemModel] = Field(default_factory=list)
    milestones: List[Dict[str, Any]] = Field(default_factory=list)
    status: str = Field(default="active", description="'active', 'completed', 'archived', 'superseded'")
    progress: float = Field(default=0.0)
    analysis_version: int = Field(default=1)
    validation_report: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
