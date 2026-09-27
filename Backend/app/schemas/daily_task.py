from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DailyTaskCreateSchema(BaseModel):
    title: str = Field(...)
    description: str = Field(...)
    category: str = Field(...)
    skill: str = Field(...)
    priority: str = Field(default="HIGH", description="'HIGH', 'MEDIUM', 'LOW'")
    estimated_minutes: int = Field(default=60, ge=10, le=480)
    difficulty: str = Field(default="Intermediate")
    date: Optional[str] = Field(default=None, description="YYYY-MM-DD")
    day_number: Optional[int] = Field(default=1)
    resource: Optional[Dict[str, Any]] = None


class DailyTaskUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    skill: Optional[str] = None
    priority: Optional[str] = None
    estimated_minutes: Optional[int] = None
    actual_minutes: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class DailyTaskStatusUpdateSchema(BaseModel):
    status: str = Field(..., description="'pending', 'in_progress', 'completed', 'skipped'")
    actual_minutes: Optional[int] = None
    notes: Optional[str] = None


class DailyTaskCompleteSchema(BaseModel):
    actual_minutes: Optional[int] = Field(default=None)
    notes: Optional[str] = Field(default=None)


class DailyTaskSkipSchema(BaseModel):
    reason: Optional[str] = Field(default=None)


class DailyTaskResponseSchema(BaseModel):
    id: str
    task_id: str
    user_id: str
    roadmap_id: Optional[str] = None
    date: str
    day_number: int
    title: str
    description: str
    category: str
    skill: str
    priority: str
    estimated_minutes: int
    actual_minutes: Optional[int] = None
    difficulty: str
    status: str
    completion_percentage: float = 0.0
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None
    resource: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class TodayTasksResponseSchema(BaseModel):
    date: str
    day_number: int
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    estimated_total_minutes: int
    tasks: List[DailyTaskResponseSchema] = []
