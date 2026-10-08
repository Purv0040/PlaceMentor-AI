from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, ConfigDict


# ============================================================
# TASKS TEST RESPONSE
# ============================================================

class TasksTestResponseSchema(BaseModel):
    status: str
    module: str


# ============================================================
# CREATE TASK
# ============================================================

class DailyTaskCreateSchema(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        description="Task title",
    )

    description: str = Field(
        ...,
        min_length=1,
        description="Task description",
    )

    category: str = Field(
        ...,
        min_length=1,
        description="Task category",
    )

    skill: str = Field(
        ...,
        min_length=1,
        description="Skill associated with the task",
    )

    priority: str = Field(
        default="HIGH",
        description="Task priority: HIGH, MEDIUM, or LOW",
    )

    estimated_minutes: int = Field(
        default=60,
        ge=1,
        le=1440,
        description="Estimated task duration in minutes",
    )

    difficulty: str = Field(
        default="Intermediate",
        min_length=1,
        description="Task difficulty",
    )

    date: Optional[str] = Field(
        default=None,
        description="Task date in YYYY-MM-DD format",
    )

    day_number: Optional[int] = Field(
        default=1,
        ge=1,
        le=365,
        description="Roadmap day number",
    )

    notes: Optional[str] = Field(
        default=None,
        description="Optional task notes",
    )

    resource: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional learning resource",
    )


# ============================================================
# UPDATE TASK
# ============================================================

class DailyTaskUpdateSchema(BaseModel):
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        description="Updated task title",
    )

    description: Optional[str] = Field(
        default=None,
        min_length=1,
        description="Updated task description",
    )

    category: Optional[str] = Field(
        default=None,
        min_length=1,
        description="Updated task category",
    )

    skill: Optional[str] = Field(
        default=None,
        min_length=1,
        description="Updated task skill",
    )

    priority: Optional[str] = Field(
        default=None,
        description="Updated priority",
    )

    difficulty: Optional[str] = Field(
        default=None,
        min_length=1,
        description="Updated difficulty",
    )

    estimated_minutes: Optional[int] = Field(
        default=None,
        ge=1,
        le=1440,
        description="Updated estimated duration",
    )

    actual_minutes: Optional[int] = Field(
        default=None,
        ge=0,
        le=1440,
        description="Actual time spent in minutes",
    )

    status: Optional[str] = Field(
        default=None,
        description=(
            "Task status: pending, in_progress, "
            "completed, or skipped"
        ),
    )

    notes: Optional[str] = Field(
        default=None,
        description="Updated task notes",
    )

    resource: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Updated learning resource",
    )


# ============================================================
# STATUS UPDATE
# ============================================================

class DailyTaskStatusUpdateSchema(BaseModel):
    status: str = Field(
        ...,
        description=(
            "Task status: pending, in_progress, "
            "completed, or skipped"
        ),
    )

    actual_minutes: Optional[int] = Field(
        default=None,
        ge=0,
        le=1440,
        description="Actual time spent in minutes",
    )

    notes: Optional[str] = Field(
        default=None,
        description="Optional status update notes",
    )


# ============================================================
# COMPLETE TASK
# ============================================================

class DailyTaskCompleteSchema(BaseModel):
    actual_minutes: Optional[int] = Field(
        default=None,
        ge=0,
        le=1440,
        description="Actual time spent in minutes",
    )

    notes: Optional[str] = Field(
        default=None,
        description="Optional completion notes",
    )


# ============================================================
# SKIP TASK
# ============================================================

class DailyTaskSkipSchema(BaseModel):
    reason: Optional[str] = Field(
        default=None,
        description="Optional reason for skipping the task",
    )


# ============================================================
# TASK RESPONSE
# ============================================================

class DailyTaskResponseSchema(BaseModel):
    """
    Standard API response for a daily task.
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    id: str
    task_id: str
    user_id: str

    roadmap_id: Optional[str] = None

    date: str
    day_number: int = 1

    title: str
    description: str
    category: str
    skill: str

    priority: str

    estimated_minutes: int
    actual_minutes: Optional[int] = None

    difficulty: str

    status: str

    completion_percentage: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
    )

    completed_at: Optional[datetime] = None

    notes: Optional[str] = None

    resource: Optional[Dict[str, Any]] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ============================================================
# TODAY TASKS RESPONSE
# ============================================================

class TodayTasksResponseSchema(BaseModel):
    """
    Response containing today's task summary and tasks.
    """

    date: str
    day_number: int = Field(
        default=1,
        ge=1,
    )

    total_tasks: int = Field(
        default=0,
        ge=0,
    )

    completed_tasks: int = Field(
        default=0,
        ge=0,
    )

    pending_tasks: int = Field(
        default=0,
        ge=0,
    )

    estimated_total_minutes: int = Field(
        default=0,
        ge=0,
    )

    tasks: List[DailyTaskResponseSchema] = Field(
        default_factory=list
    )