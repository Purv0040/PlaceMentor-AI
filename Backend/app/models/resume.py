from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ResumeStatus(str, Enum):
    UPLOADED = "uploaded"
    PARSING = "parsing"
    PARSED = "parsed"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class ResumeFileMetadata(BaseModel):
    filename: str
    content_type: str = "application/pdf"
    size: int
    storage_type: str = "gridfs"
    file_id: str


class ResumeModel(BaseModel):
    """Domain model representing a student resume document in MongoDB."""

    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    file: ResumeFileMetadata
    status: ResumeStatus = ResumeStatus.UPLOADED
    is_active: bool = False
    parsed_data: Dict[str, Any] = Field(default_factory=dict)
    analysis: Dict[str, Any] = Field(default_factory=dict)
    analysis_version: str = "1.0"
    error_message: Optional[str] = None
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    analyzed_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}
