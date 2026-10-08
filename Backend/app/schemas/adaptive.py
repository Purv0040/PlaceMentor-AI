from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AdaptiveRecalculateRequestSchema(BaseModel):
    roadmap_id: Optional[str] = Field(None, example="6ac7c44e1a747247b448c61b", description="Target roadmap ID")
    force: bool = Field(False, description="Force fresh recalculation bypassing cached unapplied recommendations")


class AdaptiveApplyRequestSchema(BaseModel):
    adaptation_id: Optional[str] = Field(None, example="67a5b3ef1248...", description="Specific adaptation event ID to apply")
    roadmap_id: Optional[str] = Field(None, example="6ac7c44e1a747247b448c61b", description="Roadmap ID to apply latest adaptation to")
    accept_changes: bool = Field(True, description="Whether to accept and apply the proposed task schedule adjustments")


class AdaptationChangeSchema(BaseModel):
    type: str = Field(..., example="rebalance", description="Type of change: rebalance, reschedule, acceleration, workload_reduction")
    description: str = Field(..., example="Rescheduled 2 overdue topics into upcoming catch-up window.", description="Human readable description")


class AdaptationEventResponseSchema(BaseModel):
    id: str = Field(..., example="67a5b3ef1248")
    user_id: str = Field(..., example="6ac7c02e25e58bec74d40f09")
    roadmap_id: str = Field(..., example="6ac7c44e1a747247b448c61b")
    trigger: str = Field(..., example="routine_check", description="Trigger category: routine_check, overdue_tasks, repeated_skipped_tasks, fast_progress")
    recommendation: str = Field(..., example="Roadmap schedule is optimal and balanced.")
    reason: str = Field(..., example="Your learning pace matches the target roadmap trajectory.")
    affected_skills: List[str] = Field(default_factory=list, example=[])
    changes: List[Dict[str, Any]] = Field(default_factory=list, example=[])
    applied: bool = Field(False, example=False)
    lifecycle_status: str = Field("pending", example="pending", description="Lifecycle state: pending, applied, superseded, informational")
    is_actionable: bool = Field(False, example=False, description="Whether this recommendation contains actionable adjustments awaiting application")
    created_at: datetime = Field(..., example="2026-10-08T22:50:00Z")
    applied_at: Optional[datetime] = Field(None, example=None)
    superseded_at: Optional[datetime] = Field(None, example=None)


class AdaptiveMetricsSchema(BaseModel):
    roadmap_id: Optional[str] = Field(None, example="6ac7c44e1a747247b448c61b")
    total_tasks: int = Field(0, example=180)
    total_completed: int = Field(0, example=0)
    total_pending: int = Field(0, example=180)
    total_skipped: int = Field(0, example=0)
    total_overdue: int = Field(0, example=0)
    completion_rate: float = Field(0.0, example=0.0)
    current_streak: int = Field(0, example=0)


class AdaptiveSummaryResponseSchema(BaseModel):
    status: str = Field("balanced", example="balanced", description="Current roadmap status: balanced, needs_rebalance, ahead_of_schedule")
    has_pending_recommendation: bool = Field(False, example=False, description="True if an actionable adaptation recommendation is awaiting application")
    latest_recommendation: Optional[AdaptationEventResponseSchema] = None
    metrics: AdaptiveMetricsSchema = Field(default_factory=AdaptiveMetricsSchema)


class AdaptiveApplyResponseSchema(BaseModel):
    status: str = Field(..., example="success", description="Status of the application: 'success', 'already_applied', 'dismissed'")
    applied_event: Optional[AdaptationEventResponseSchema] = Field(None, description="The adaptation event details after processing")
    message: str = Field(..., example="Roadmap schedule and daily tasks successfully rebalanced.", description="Result message")



