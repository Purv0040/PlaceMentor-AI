from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class NotificationModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    notification_id: str
    user_id: str
    type: str = "system"  # achievement, task, roadmap, streak, interview, communication, readiness, skill_gap, system
    title: str
    message: str
    priority: str = "normal"  # low, normal, high
    read: bool = False
    action_type: Optional[str] = None
    action_id: Optional[str] = None
    action_route: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    read_at: Optional[datetime] = None

    class Config:
        populate_by_name = True


class NotificationPreferencesModel(BaseModel):
    user_id: str
    task_reminders: bool = True
    achievement_notifications: bool = True
    roadmap_notifications: bool = True
    interview_notifications: bool = True
    general_notifications: bool = True
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
