from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field

from app.models.resume import (
    ResumeStatus,
    ResumeFileMetadata,
)


class ResumeUploadResponse(BaseModel):
    id: str
    user_id: str
    filename: str
    size: int
    page_count: Optional[int] = 1
    content_type: str
    status: ResumeStatus
    is_active: bool
    uploaded_at: datetime


class ResumeMetadataResponse(BaseModel):
    id: str
    user_id: str
    filename: str
    size: int
    page_count: Optional[int] = 1
    content_type: str
    status: ResumeStatus
    is_active: bool
    analysis_version: str
    uploaded_at: datetime
    analyzed_at: Optional[datetime] = None
    has_analysis: bool = False


class ResumeListResponse(BaseModel):
    items: List[ResumeMetadataResponse]
    total: int


class ResumeDetailResponse(BaseModel):
    id: str
    user_id: str
    file: ResumeFileMetadata
    status: ResumeStatus
    is_active: bool

    parsed_data: Dict[str, Any] = Field(
        default_factory=dict
    )

    analysis: Dict[str, Any] = Field(
        default_factory=dict
    )

    analysis_version: str = "1.0"

    error_message: Optional[str] = None

    uploaded_at: datetime

    analyzed_at: Optional[datetime] = None

    updated_at: datetime


class ResumeAnalysisResponse(BaseModel):
    resume_id: str
    user_id: str
    status: ResumeStatus
    analysis_version: str = "1.0"
    analyzed_at: Optional[datetime] = None
    analysis: Dict[str, Any]


class ResumeActivateRequest(BaseModel):
    resume_id: Optional[str] = None


class BulletOptimizeRequest(BaseModel):
    bullet: str
    target_role: Optional[str] = "Backend SDE-1 (Tier 1)"
    context: Optional[str] = None


class BulletOptimizeResponse(BaseModel):
    original: str
    improved: str
    rationale: str
    score: int = 96
    action_verbs: List[str] = Field(default_factory=list)