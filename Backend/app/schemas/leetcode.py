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


class DailyPracticeTaskItem(BaseModel):
    task_id: str
    title: str
    difficulty: str
    topic: str
    status: str = "pending"
    resource_url: str
    estimated_minutes: int = 30


class DailyPracticePlanResponse(BaseModel):
    date: str
    target_count: int
    completed_count: int
    remaining_count: int
    tasks: List[DailyPracticeTaskItem] = Field(default_factory=list)


class ActivityTrendPoint(BaseModel):
    date: str
    day: str
    problems_solved: int = 0
    submissions: Optional[int] = 0
    status: str
    contest_rating: Optional[float] = None


class ActivityTrendResponse(BaseModel):
    days: int
    data_points: List[ActivityTrendPoint] = Field(default_factory=list)
    total_solved_in_period: int = 0
    total_submissions_in_period: Optional[int] = 0
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    has_contest_history: bool = False


class SuggestedProblemItem(BaseModel):
    title: str
    difficulty: str
    url: str


class FocusAreaTopic(BaseModel):
    topic: str
    problems_solved: int
    target: int
    mastery_percentage: int
    priority: str
    interview_weight: str
    recommended_action: str
    suggested_problems: List[SuggestedProblemItem] = Field(default_factory=list)


class ReadinessBreakdown(BaseModel):
    readiness_score: int
    target_tier: str = "Tier-1 Technical Screening"
    easy_pts: float
    medium_pts: float
    hard_pts: float
    coverage_pts: float
    contest_bonus: float
    strengths: List[str] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)
    explanation: str
    disclaimer: str = "Calibrated for algorithmic screening cutoffs. Does not guarantee placement outcomes."


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
    daily_plan: Optional[DailyPracticePlanResponse] = None
    focus_areas: Optional[List[FocusAreaTopic]] = None
    readiness_breakdown: Optional[ReadinessBreakdown] = None
    activity_history: Optional[ActivityTrendResponse] = None
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
