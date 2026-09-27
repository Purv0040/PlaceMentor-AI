from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class LeetCodeConnectRequest(BaseModel):
    username: str = Field(..., example="digisha_prep", description="LeetCode profile username to connect")


class LeetCodeConnectResponse(BaseModel):
    user_id: str
    leetcode_username: str
    is_connected: bool = True
    profile: Optional[Dict[str, Any]] = None
    status: str = "connected"


class LeetCodeProfileResponse(BaseModel):
    id: str
    user_id: str
    leetcode_username: str
    is_connected: bool = True
    profile: Optional[Dict[str, Any]] = None
    statistics: Optional[Dict[str, Any]] = None
    contest: Optional[Dict[str, Any]] = None
    topic_statistics: List[Dict[str, Any]] = Field(default_factory=list)
    recent_activity: List[Dict[str, Any]] = Field(default_factory=list)
    sync: Dict[str, Any] = Field(default_factory=dict)
    analysis_version: Optional[str] = "1.0"
    has_analysis: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class LeetCodeStatisticsResponse(BaseModel):
    user_id: str
    leetcode_username: str
    statistics: Optional[Dict[str, Any]] = None
    contest: Optional[Dict[str, Any]] = None
    topic_statistics: List[Dict[str, Any]] = Field(default_factory=list)


class LeetCodeActivityResponse(BaseModel):
    user_id: str
    leetcode_username: str
    recent_activity: List[Dict[str, Any]] = Field(default_factory=list)


class LeetCodeAnalysisResponse(BaseModel):
    user_id: str
    leetcode_username: str
    analysis_version: str = "1.0"
    analyzed_at: Optional[datetime] = None
    analysis: Optional[Dict[str, Any]] = None
