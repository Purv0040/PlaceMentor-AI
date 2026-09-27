from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AdaptiveRecalculateRequestSchema(BaseModel):
    roadmap_id: Optional[str] = None
    force: bool = False


class AdaptiveApplyRequestSchema(BaseModel):
    adaptation_id: Optional[str] = None
    roadmap_id: Optional[str] = None
    accept_changes: bool = True


class AdaptationEventResponseSchema(BaseModel):
    id: str
    user_id: str
    roadmap_id: str
    trigger: str
    recommendation: str
    reason: str
    affected_skills: List[str] = []
    changes: List[Dict[str, Any]] = []
    applied: bool = False
    created_at: datetime


class AdaptiveSummaryResponseSchema(BaseModel):
    status: str = "balanced"  # "balanced", "needs_rebalance", "ahead_of_schedule"
    has_pending_recommendation: bool = False
    latest_recommendation: Optional[AdaptationEventResponseSchema] = None
    metrics: Dict[str, Any] = {}
