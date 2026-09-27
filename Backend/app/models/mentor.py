from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MentorConversationModel(BaseModel):
    """MongoDB document model for mentor_conversations collection."""
    conversation_id: str = Field(..., description="Unique conversation identifier")
    user_id: str = Field(..., description="Authenticated student user ID")
    title: str = Field(default="New Placement Session", description="Conversation title")
    status: str = Field(default="active", description="active or archived")
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    last_message_at: Optional[datetime] = Field(default_factory=utc_now)


class MentorMessageModel(BaseModel):
    """MongoDB document model for mentor_messages collection."""
    message_id: str = Field(..., description="Unique message identifier")
    conversation_id: str = Field(..., description="Conversation ID reference")
    user_id: str = Field(..., description="Authenticated student user ID")
    role: str = Field(..., description="user or assistant")
    content: str = Field(..., description="Message text content")
    intent: Optional[str] = Field(default="general_placement", description="Detected intent category")
    context_sources: List[str] = Field(default_factory=list, description="Telemetry sources used for answer")
    evidence: List[str] = Field(default_factory=list, description="Factual evidence extracted from student context")
    suggested_actions: List[Dict[str, Any]] = Field(default_factory=list, description="Actionable routes/tasks")
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=utc_now)
