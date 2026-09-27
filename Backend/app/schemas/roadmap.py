from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class RoadmapTaskSchema(BaseModel):
    id: str
    day: int
    category: str
    title: str
    description: str
    estimated_minutes: int
    difficulty: str = "Intermediate"
    priority: str = "High"
    skill: str
    status: str = "pending"


class RoadmapPhaseSchema(BaseModel):
    phase_number: int
    name: str
    day_range: str
    start_day: int
    end_day: int
    goal: str
    tasks: List[RoadmapTaskSchema] = []


class WeeklyGoalSchema(BaseModel):
    week_number: int
    objective: str
    skills: List[str] = []
    tasks: List[str] = []
    expected_outcome: str
    estimated_effort: str
    completion_percentage: float = 0.0


class RoadmapGenerateRequestSchema(BaseModel):
    target_role: Optional[str] = Field(default=None, description="Target role name (defaults to student profile target role)")
    available_minutes_per_day: int = Field(default=120, ge=30, le=480)
    force_regenerate: bool = Field(default=False)


class RoadmapUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    available_minutes_per_day: Optional[int] = None


class RoadmapMilestoneSchema(BaseModel):
    title: str
    description: str
    week_number: int


class RoadmapResponseSchema(BaseModel):
    id: str
    roadmap_id: str
    user_id: str
    target_role: str
    title: str
    description: Optional[str] = None
    summary: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    duration_days: int = 90
    available_minutes_per_day: int = 120
    total_estimated_hours: float = 0.0
    phases: List[RoadmapPhaseSchema] = []
    weekly_goals: List[WeeklyGoalSchema] = []
    milestones: List[RoadmapMilestoneSchema] = []
    status: str = "active"
    progress: float = 0.0
    analysis_version: int = 1
    created_at: datetime
    updated_at: datetime


class RoadmapSummaryResponseSchema(BaseModel):
    roadmap_id: str
    target_role: str
    total_days: int = 90
    current_day: int = 1
    phases_count: int = 3
    progress_percentage: float = 0.0
    status: str = "active"
    current_phase_name: Optional[str] = None


# Alias for backward compatibility
RoadmapMilestone = RoadmapMilestoneSchema
RoadmapResponse = RoadmapResponseSchema
