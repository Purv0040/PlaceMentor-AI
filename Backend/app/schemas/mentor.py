from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class MentorConversationCreateSchema(BaseModel):
    title: Optional[str] = Field(default=None, example="DSA & System Design Prep", description="Optional conversation title")


class MentorConversationResponseSchema(BaseModel):
    id: str = Field(..., example="67a5b3ef1248")
    conversation_id: str = Field(..., example="conv_user_123_1791481...")
    user_id: str = Field(..., example="user_123")
    title: str = Field(..., example="DSA & System Design Prep")
    status: str = Field("active", example="active", description="Conversation status: 'active' or 'archived'")
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None


class MentorMessageCreateSchema(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        example="What tasks should I focus on today for my backend developer preparation?",
        description="Student query text",
    )

    @field_validator("message")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Message cannot be empty or whitespace only.")
        return v.strip()


class MentorMessageResponseSchema(BaseModel):
    id: str = Field(..., example="msg_123")
    message_id: str = Field(..., example="msg_ai_1791481...")
    conversation_id: str = Field(..., example="conv_user_123_1791481...")
    user_id: str = Field(..., example="user_123")
    role: str = Field(..., example="assistant", description="Message author role: 'user' or 'assistant'")
    content: str = Field(..., example="Based on your 90-day roadmap, today you should focus on Dynamic Programming.")
    intent: Optional[str] = Field("general_placement", example="dsa")
    context_sources: List[str] = Field(default_factory=list, example=["profile", "readiness", "today_tasks"])
    evidence: List[str] = Field(default_factory=list, example=["Target Role: Backend Developer", "Readiness Score: 78/100"])
    suggested_actions: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = Field(0.9, ge=0.0, le=1.0, example=0.92)
    created_at: datetime


class MentorConversationDetailResponseSchema(MentorConversationResponseSchema):
    messages: List[MentorMessageResponseSchema] = Field(default_factory=list)


class MentorAskSchema(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        example="How can I improve my placement readiness score?",
        description="Quick mentor query text",
    )
    conversation_id: Optional[str] = Field(default=None, example="conv_user_123_1791481...", description="Optional existing conversation ID")

    @field_validator("message")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Message cannot be empty or whitespace only.")
        return v.strip()


class MentorResponseSchema(BaseModel):
    answer: str = Field(..., example="Your readiness score is 78/100. Focus on resolving your Dynamic Programming gap.")
    intent: str = Field("general_placement", example="readiness")
    context_sources: List[str] = Field(default_factory=list, example=["profile", "readiness"])
    evidence: List[str] = Field(default_factory=list, example=["Target Role: Backend Developer", "Readiness Score: 78/100"])
    suggested_actions: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = Field(0.9, ge=0.0, le=1.0, example=0.9)
    conversation_id: Optional[str] = Field(None, example="conv_user_123_1791481...")
    created_at: Optional[datetime] = None

