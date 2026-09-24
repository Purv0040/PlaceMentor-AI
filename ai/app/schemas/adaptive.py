"""
Pydantic schemas for the Adaptive Roadmap Engine.
Defines student progress, performance payloads, adaptive thresholds, roadmap adjustments, request and response schemas.
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas.skills import ProfileBuildRequest
from app.schemas.roadmap import PersonalizedRoadmap, RoadmapTask


class AdaptiveThresholds(BaseModel):
    """Configurable thresholds for detecting student preparation states."""
    ahead_completion_pct: float = Field(90.0, ge=0.0, le=100.0, description="Completion rate threshold for AHEAD state (>= 90%)")
    on_track_completion_pct: float = Field(80.0, ge=0.0, le=100.0, description="Completion rate threshold for ON_TRACK state (>= 80%)")
    behind_completion_pct: float = Field(50.0, ge=0.0, le=100.0, description="Completion rate threshold for BEHIND state (50-79%)")
    struggling_completion_pct: float = Field(50.0, ge=0.0, le=100.0, description="Completion rate threshold for STRUGGLING state (< 50%)")
    struggling_dsa_accuracy_pct: float = Field(40.0, ge=0.0, le=100.0, description="DSA accuracy threshold trigger for STRUGGLING state (< 40%)")
    improving_delta_pct: float = Field(15.0, ge=0.0, le=100.0, description="Completion rate improvement delta trigger for IMPROVING state (>= +15%)")


class RoadmapAdjustment(BaseModel):
    """Explaining a single adaptation edit made to a roadmap task while maintaining complete audit lineage."""
    id: str = Field(..., description="Unique adjustment ID (e.g. 'adj_1001')")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO timestamp when adaptation occurred"
    )
    action_type: str = Field(
        ...,
        description="Type of change: 'difficulty_reduced', 'prerequisite_injected', 'task_rescheduled', 'workload_reduced', 'task_accelerated', 'difficulty_increased'"
    )
    reason: str = Field(..., description="Explainable rationale for the adaptation")
    old_task: Optional[Dict[str, Any]] = Field(None, description="Original state of the task prior to edit")
    new_task: Optional[Dict[str, Any]] = Field(None, description="New state of the task after edit")
    impact_description: str = Field(..., description="Summary of how this adjustment impacts student preparation trajectory")


class StudentProgressPayload(BaseModel):
    """Information about actual student behavior and completed work."""
    completed_tasks: List[str] = Field(default_factory=list, description="IDs of tasks completed by student")
    missed_tasks: List[str] = Field(default_factory=list, description="IDs of tasks missed/skipped by student")
    completion_rate: float = Field(..., ge=0.0, le=100.0, description="Overall completion percentage (0.0 to 100.0)")
    current_day: int = Field(1, ge=1, le=90, description="Current day in the prep plan (1 to 90)")
    recent_completion_rate: Optional[float] = Field(None, ge=0.0, le=100.0, description="Recent completion rate (e.g. past 7 days)")
    previous_completion_rate: Optional[float] = Field(None, ge=0.0, le=100.0, description="Previous period completion rate for trend detection")


class StudentPerformancePayload(BaseModel):
    """Information about performance metrics, DSA accuracy, time availability, and skill gaps."""
    available_time: int = Field(120, ge=15, le=480, description="Daily available study time in minutes")
    dsa_performance: Optional[Dict[str, Any]] = Field(None, description="DSA performance metrics e.g. {'accuracy': 65.0, 'weak_topics': ['Dynamic Programming']}")
    skill_gaps: Optional[List[str]] = Field(default_factory=list, description="List of detected high-priority skill gaps")
    readiness_history: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Historical readiness scores over time")
    upcoming_deadlines: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Upcoming deadlines or interview dates")


class AdaptiveRoadmapResponse(BaseModel):
    """
    Output payload for POST /api/ai/roadmap/adapt.
    """
    target_role: str = Field(..., description="Target placement role")
    detected_state: str = Field(..., description="Detected state: 'ON_TRACK', 'BEHIND', 'AHEAD', 'STRUGGLING', 'IMPROVING'")
    state_description: str = Field(..., description="Transparent explanation of detected state based on thresholds")
    adaptation_summary: str = Field(..., description="Executive summary of all roadmap adjustments made")
    original_plan: PersonalizedRoadmap = Field(..., description="Original un-modified roadmap for non-destructive lineage")
    current_plan: PersonalizedRoadmap = Field(..., description="Updated roadmap reflecting all current adjustments")
    adjustments: List[RoadmapAdjustment] = Field(default_factory=list, description="Audit log of all adjustments made")
    thresholds_used: AdaptiveThresholds = Field(..., description="Threshold configuration used for state detection")


class AdaptiveRoadmapRequest(BaseModel):
    """
    Input payload for POST /api/ai/roadmap/adapt.
    """
    roadmap: Optional[Any] = Field(None, description="Pre-computed PersonalizedRoadmap or dict")
    progress: StudentProgressPayload = Field(..., description="Student progress payload")
    performance: Optional[StudentPerformancePayload] = Field(default_factory=StudentPerformancePayload, description="Student performance payload")
    thresholds: Optional[AdaptiveThresholds] = Field(None, description="Custom thresholds for state detection")
    target_role: Optional[str] = Field("Backend Developer", description="Target placement role if not in roadmap")
    profile_request: Optional[ProfileBuildRequest] = Field(None, description="Raw profile build request if roadmap is not provided")
