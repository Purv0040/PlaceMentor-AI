from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class NotificationResponseSchema(BaseModel):
    id: str = Field(..., example="notif_123")
    notification_id: str = Field(..., example="notif_123")
    user_id: str = Field(..., example="user_123")
    type: str = Field(..., example="achievement")
    title: str = Field(..., example="Achievement Unlocked!")
    message: str = Field(..., example="You earned the 14-Day Consistency Master badge.")
    priority: str = Field("normal", example="normal")
    read: bool = Field(False, example=False)
    action_type: Optional[str] = Field(None, example="achievement")
    action_id: Optional[str] = Field(None, example="ach-1")
    action_route: Optional[str] = Field(None, example="/tasks")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[Any] = Field(None, example="2026-09-27T21:00:00Z")
    read_at: Optional[Any] = Field(None, example=None)


class NotificationUnreadCountSchema(BaseModel):
    unread_count: int = Field(..., example=3)


class NotificationPreferencesSchema(BaseModel):
    task_reminders: bool = Field(True, example=True)
    achievement_notifications: bool = Field(True, example=True)
    roadmap_notifications: bool = Field(True, example=True)
    interview_notifications: bool = Field(True, example=True)
    general_notifications: bool = Field(True, example=True)
