"""
Pydantic schemas for the Daily Task Engine.
Defines prioritized daily task items, request payloads, and the complete TodayTasksResponse output.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas.student import StudentProfile
from app.schemas.skills import StudentIntelligenceProfile, ProfileBuildRequest
from app.schemas.skill_gap import SkillGapAnalysis
from app.schemas.roadmap import PersonalizedRoadmap, RoadmapTask


class TodayTaskItem(BaseModel):
    """A single prioritized preparation task for today."""
    id: str = Field(..., description="Unique task identifier (e.g. 'task_d10_1')")
    title: str = Field(..., description="Short task title")
    category: str = Field(
        ...,
        description="Task category (e.g., 'DSA', 'Backend', 'Frontend', 'AI/ML', 'DevOps', 'Projects', 'Resume', 'GitHub', 'Communication', 'Interview')"
    )
    estimated_minutes: int = Field(..., ge=5, le=480, description="Estimated duration in minutes")
    priority: str = Field(..., description="Task priority: 'High', 'Medium', 'Low'")
    reason: str = Field(..., description="Clear rationale explaining why this task was prioritized for today")
    skill: str = Field(..., description="Target skill or topic (e.g. 'Python', 'Arrays', 'FastAPI', 'System Design')")
    source_roadmap_day: int = Field(..., ge=1, le=90, description="Day number in the 90-day roadmap where this task originated")
    status: str = Field("pending", description="Task completion status: 'pending', 'completed', 'in_progress'")


class TodayTasksResponse(BaseModel):
    """
    Complete output for POST /api/ai/tasks/today.
    """
    target_role: str = Field(..., description="Target placement role")
    current_day: int = Field(..., ge=1, le=90, description="Current day number in prep plan (1 to 90)")
    available_time: int = Field(..., description="Available study time budget for today in minutes")
    total_scheduled_minutes: int = Field(..., description="Sum of estimated minutes across all scheduled today tasks")
    tasks: List[TodayTaskItem] = Field(default_factory=list, description="Prioritized list of tasks for today")
    overdue_rescheduled_count: int = Field(0, description="Count of overdue/missed tasks carried over into today's plan")
    completed_count_so_far: int = Field(0, description="Count of tasks completed by student so far")
    summary: str = Field(..., description="Executive summary of today's prep plan")
    reasoning: List[str] = Field(default_factory=list, description="Key reasoning points driving today's task selection")


class TodayTasksRequest(BaseModel):
    """
    Input payload for POST /api/ai/tasks/today.
    """
    roadmap: Optional[Any] = Field(None, description="Pre-computed PersonalizedRoadmap or dict")
    current_day: int = Field(1, ge=1, le=90, description="Current day number in preparation plan (1 to 90)")
    completed_tasks: List[str] = Field(default_factory=list, description="IDs of tasks completed so far")
    missed_tasks: List[str] = Field(default_factory=list, description="IDs of missed/overdue tasks from previous days")
    available_time: int = Field(120, ge=15, le=480, description="Available study minutes for today")
    target_role: Optional[str] = Field("Backend Developer", description="Target placement role")
    skill_gaps: Optional[Any] = Field(None, description="Pre-computed SkillGapAnalysis or dict")
    upcoming_priorities: List[str] = Field(default_factory=list, description="Explicit upcoming priorities or topics")
    profile_request: Optional[ProfileBuildRequest] = Field(None, description="Raw build request if profile/roadmap is not supplied")
