from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, ConfigDict


class RoadmapTaskItemModel(BaseModel):
    """
    Individual task inside a roadmap.
    """

    model_config = ConfigDict(
        populate_by_name=True
    )

    id: str = Field(
        ...,
        description="Unique task identifier in roadmap",
    )

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

    difficulty: str = Field(
        default="Intermediate"
    )

    priority: str = Field(
        default="High"
    )

    skill: str

    status: str = Field(
        default="pending"
    )


class RoadmapPhaseModel(BaseModel):
    """
    One of the three roadmap phases.
    """

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

    tasks: List[RoadmapTaskItemModel] = Field(
        default_factory=list
    )


class WeeklyGoalModel(BaseModel):
    """
    Weekly roadmap goal.
    """

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


class RoadmapModel(BaseModel):
    """
    MongoDB roadmap document model.
    """

    model_config = ConfigDict(
        populate_by_name=True
    )

    id: Optional[str] = Field(
        default=None,
        alias="_id",
    )

    roadmap_id: Optional[str] = None

    user_id: str

    target_role: str

    title: str = Field(
        default="90-Day Placement Preparation Roadmap"
    )

    description: Optional[str] = None

    summary: Optional[str] = None

    start_date: datetime = Field(
        default_factory=datetime.utcnow
    )

    end_date: Optional[datetime] = None

    duration_days: int = Field(
        default=90,
        ge=1,
        le=365,
    )

    available_minutes_per_day: int = Field(
        default=120,
        ge=30,
        le=480,
    )

    total_estimated_hours: float = Field(
        default=0.0,
        ge=0.0,
    )

    phases: List[RoadmapPhaseModel] = Field(
        default_factory=list
    )

    weekly_goals: List[WeeklyGoalModel] = Field(
        default_factory=list
    )

    all_tasks: List[RoadmapTaskItemModel] = Field(
        default_factory=list
    )

    milestones: List[Dict[str, Any]] = Field(
        default_factory=list
    )

    status: str = Field(
        default="active"
    )

    progress: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
    )

    analysis_version: int = Field(
        default=1,
        ge=1,
    )

    validation_report: Dict[str, Any] = Field(
        default_factory=dict
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow
    )