from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, ConfigDict


class RoadmapTaskSchema(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True
    )

    id: str

    day: int = Field(
        ...,
        ge=1,
        le=90,
    )

    category: str

    title: str

    description: str

    estimated_minutes: int = Field(
        ...,
        ge=10,
        le=480,
    )

    difficulty: str = "Intermediate"

    priority: str = "High"

    skill: str

    status: str = "pending"


class RoadmapPhaseSchema(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True
    )

    phase_number: int = Field(
        ...,
        ge=1,
        le=3,
    )

    name: str

    day_range: str

    start_day: int = Field(
        ...,
        ge=1,
        le=90,
    )

    end_day: int = Field(
        ...,
        ge=1,
        le=90,
    )

    goal: str

    tasks: List[RoadmapTaskSchema] = Field(
        default_factory=list
    )


class WeeklyGoalSchema(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True
    )

    week_number: int = Field(
        ...,
        ge=1,
        le=13,
    )

    objective: str

    skills: List[str] = Field(
        default_factory=list
    )

    tasks: List[str] = Field(
        default_factory=list
    )

    expected_outcome: str

    estimated_effort: str

    completion_percentage: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
    )


class RoadmapGenerateRequestSchema(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True
    )

    target_role: Optional[str] = Field(
        default=None,
        description=(
            "Target role. If omitted, "
            "the student's profile target role is used."
        ),
    )

    available_minutes_per_day: int = Field(
        default=120,
        ge=30,
        le=480,
        description=(
            "Available learning minutes per day."
        ),
    )

    force_regenerate: bool = Field(
        default=False,
        description=(
            "Force creation of a new roadmap "
            "even when an active roadmap exists."
        ),
    )


class RoadmapUpdateSchema(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True
    )

    title: Optional[str] = Field(
        default=None,
        min_length=1,
    )

    description: Optional[str] = None

    status: Optional[str] = Field(
        default=None,
        description=(
            "active, completed, archived, superseded"
        ),
    )

    available_minutes_per_day: Optional[int] = Field(
        default=None,
        ge=30,
        le=480,
    )


class RoadmapMilestoneSchema(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True
    )

    title: str

    description: str

    week_number: int = Field(
        ...,
        ge=1,
        le=13,
    )


class RoadmapResponseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

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

    phases: List[RoadmapPhaseSchema] = Field(
        default_factory=list
    )

    weekly_goals: List[WeeklyGoalSchema] = Field(
        default_factory=list
    )

    milestones: List[RoadmapMilestoneSchema] = Field(
        default_factory=list
    )

    status: str = "active"

    progress: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
    )

    analysis_version: int = 1

    created_at: datetime

    updated_at: datetime


class RoadmapSummaryResponseSchema(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True
    )

    roadmap_id: Optional[str] = None

    target_role: str = "Not Set"

    total_days: int = 90

    current_day: int = 1

    phases_count: int = 0

    progress_percentage: float = 0.0

    status: str = "none"

    current_phase_name: Optional[str] = None


RoadmapMilestone = RoadmapMilestoneSchema

RoadmapResponse = RoadmapResponseSchema