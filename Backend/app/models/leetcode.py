from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class LeetCodeProfileInfo(BaseModel):
    username: str
    real_name: Optional[str] = None
    about: Optional[str] = None
    ranking: Optional[int] = None
    reputation: Optional[int] = None
    avatar_url: Optional[str] = None


class LeetCodeProblemStatistics(BaseModel):
    total_solved: int = 0
    easy_solved: int = 0
    medium_solved: int = 0
    hard_solved: int = 0
    total_questions: int = 0
    easy_total: int = 0
    medium_total: int = 0
    hard_total: int = 0
    acceptance_rate: Optional[float] = None


class LeetCodeContestInfo(BaseModel):
    rating: Optional[float] = None
    global_ranking: Optional[int] = None
    attended_contests: Optional[int] = None
    top_percentage: Optional[float] = None


class LeetCodeProfileModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    leetcode_username: str
    profile: Optional[Dict[str, Any]] = None
    statistics: Optional[Dict[str, Any]] = None
    contest: Optional[Dict[str, Any]] = None
    topic_statistics: List[Dict[str, Any]] = Field(default_factory=list)
    recent_activity: List[Dict[str, Any]] = Field(default_factory=list)
    analysis: Optional[Dict[str, Any]] = None
    sync: Dict[str, Any] = Field(default_factory=lambda: {
        "status": "not_synced",
        "last_synced_at": None,
        "last_successful_sync_at": None,
        "error": None
    })
    analysis_version: Optional[str] = "1.0"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
