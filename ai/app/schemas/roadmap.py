"""
Pydantic schemas for the 90-Day Personalized Roadmap Generator.
Defines daily tasks, phase structures, validation reports, and the complete PersonalizedRoadmap output.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas.student import StudentProfile
from app.schemas.skills import StudentIntelligenceProfile, ProfileBuildRequest
from app.schemas.skill_gap import SkillGapAnalysis
from app.schemas.readiness import PlacementReadinessAnalysis


class RoadmapTask(BaseModel):
    """A single actionable daily preparation task."""
    id: str = Field(..., description="Unique task identifier (e.g. 'task_d1_1', 'task_d45_2')")
    day: int = Field(..., ge=1, le=90, description="Day number (1 to 90)")
    category: str = Field(
        ...,
        description="Task category: 'DSA', 'Backend', 'Frontend', 'AI/ML', 'Data Science', 'Databases', 'DevOps', 'Cloud', 'CS Fundamentals', 'Projects', 'Resume', 'GitHub', 'Communication', 'Interview'"
    )
    title: str = Field(..., description="Short task title")
    description: str = Field(..., description="Detailed, actionable learning or coding instructions")
    estimated_minutes: int = Field(..., ge=10, le=480, description="Estimated duration in minutes")
    difficulty: str = Field(..., description="Task difficulty: 'Beginner', 'Intermediate', 'Advanced'")
    priority: str = Field(..., description="Task priority: 'High', 'Medium', 'Low'")
    skill: str = Field(..., description="Target skill or topic (e.g. 'Python', 'Arrays', 'FastAPI', 'System Design')")
    status: str = Field("pending", description="Task completion status: 'pending', 'completed', 'in_progress'")


class RoadmapPhase(BaseModel):
    """A 30-day phase block within the 90-day preparation roadmap."""
    phase_number: int = Field(..., ge=1, le=3, description="Phase number (1, 2, or 3)")
    name: str = Field(..., description="Phase name (e.g. 'Phase 1: Foundation')")
    day_range: str = Field(..., description="Day range string (e.g. 'Days 1-30')")
    start_day: int = Field(..., ge=1, le=90)
    end_day: int = Field(..., ge=1, le=90)
    goal: str = Field(..., description="Primary high-level milestone and goal for this phase")
    tasks: List[RoadmapTask] = Field(default_factory=list, description="Tasks scheduled within this phase")


class PersonalizedRoadmap(BaseModel):
    """
    Complete validated 90-Day Personalized Roadmap output.
    """
    target_role: str = Field(..., description="Target placement role name")
    total_days: int = Field(90, description="Total days in roadmap")
    available_minutes_per_day: int = Field(..., description="Daily study time budget in minutes")
    total_estimated_hours: float = Field(..., description="Total cumulative hours across all 90 days")
    phases: List[RoadmapPhase] = Field(default_factory=list, description="List of 3 phases covering Days 1-90")
    all_tasks: List[RoadmapTask] = Field(default_factory=list, description="Flat list of all tasks across 90 days")
    summary: str = Field(..., description="Strategic executive summary of the 90-day roadmap")
    validation_report: Dict[str, Any] = Field(
        default_factory=dict,
        description="Python post-validation results confirming time budget, prerequisite sequence, and schema integrity"
    )


class RoadmapGenerateRequest(BaseModel):
    """Input payload for POST /api/ai/roadmap/generate."""
    target_role: str = Field("Backend Developer", description="Target placement role")
    available_minutes_per_day: int = Field(120, ge=30, le=480, description="Available daily study time in minutes")
    profile: Optional[Any] = Field(None, description="Pre-computed StudentIntelligenceProfile or dict")
    skill_gaps: Optional[Any] = Field(None, description="Pre-computed SkillGapAnalysis or dict")
    readiness: Optional[Any] = Field(None, description="Pre-computed PlacementReadinessAnalysis or dict")
    profile_request: Optional[ProfileBuildRequest] = Field(None, description="Raw build request if profile is not supplied")
