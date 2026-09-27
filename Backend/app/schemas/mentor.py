from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class MentorConversationCreateSchema(BaseModel):
    title: Optional[str] = Field(default=None, description="Optional conversation title")


class MentorConversationResponseSchema(BaseModel):
    id: str
    conversation_id: str
    user_id: str
    title: str
    status: str
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None


class MentorMessageCreateSchema(BaseModel):
    message: str = Field(..., min_length=1, description="Student query text")


class MentorMessageResponseSchema(BaseModel):
    id: str
    message_id: str
    conversation_id: str
    user_id: str
    role: str
    content: str
    intent: Optional[str] = "general_placement"
    context_sources: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    suggested_actions: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = 0.9
    created_at: datetime


class MentorConversationDetailResponseSchema(MentorConversationResponseSchema):
    messages: List[MentorMessageResponseSchema] = Field(default_factory=list)


class MentorAskSchema(BaseModel):
    message: str = Field(..., min_length=1, description="Quick mentor query")
    conversation_id: Optional[str] = Field(default=None, description="Optional existing conversation ID")


class MentorResponseSchema(BaseModel):
    answer: str
    intent: str = "general_placement"
    context_sources: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    suggested_actions: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = 0.9
    conversation_id: Optional[str] = None
    created_at: Optional[datetime] = None
