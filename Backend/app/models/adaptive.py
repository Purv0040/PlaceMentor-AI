from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AdaptationEventModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str = Field(...)
    roadmap_id: str = Field(...)
    trigger: str = Field(..., description="e.g. 'routine_check', 'repeated_skipped_tasks', 'fast_progress', 'overdue_tasks'")
    recommendation: str = Field(...)
    reason: str = Field(...)
    affected_skills: List[str] = Field(default_factory=list)
    changes: List[Dict[str, Any]] = Field(default_factory=list)
    applied: bool = Field(default=False)
    lifecycle_status: str = Field(default="pending", description="Lifecycle state: pending, applied, superseded, informational")
    is_actionable: bool = Field(default=False, description="True if recommendation contains pending actionable changes")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    applied_at: Optional[datetime] = None
    superseded_at: Optional[datetime] = None

    class Config:
        populate_by_name = True

