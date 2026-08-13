"""Pydantic v2 data models for LeetCode Analyzer."""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class LeetCodeAnalyzeRequest(BaseModel):
    """API Request model for LeetCode profile analysis."""
    username: str = Field(..., min_length=1, description="LeetCode username to analyze.")


class ProblemStatistics(BaseModel):
    """Problem solving metric breakdown."""
    total_solved: int = Field(default=0, ge=0, description="Total problems solved.")
    easy_solved: int = Field(default=0, ge=0, description="Easy difficulty problems solved.")
    medium_solved: int = Field(default=0, ge=0, description="Medium difficulty problems solved.")
    hard_solved: int = Field(default=0, ge=0, description="Hard difficulty problems solved.")
    easy_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Easy problem ratio.")
    medium_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Medium problem ratio.")
    hard_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Hard problem ratio.")


class WeakTopicItem(BaseModel):
    """Details of an identified weak topic requiring focused practice."""
    topic: str = Field(..., description="DSA Topic name (e.g., Dynamic Programming).")
    score: float = Field(..., description="Topic score or problem count.")
    priority: str = Field(..., description="Improvement priority: HIGH, MEDIUM, LOW.")


class ConsistencyData(BaseModel):
    """Submission activity and consistency metrics."""
    active_days: int = Field(default=0, ge=0, description="Total active submission days.")
    weekly_activity: int = Field(default=0, ge=0, description="Active days in last 7 days.")
    monthly_activity: int = Field(default=0, ge=0, description="Active days in last 30 days.")
    recent_activity_score: float = Field(default=0.0, ge=0.0, le=10.0, description="Recent activity score.")
    consistency_score: float = Field(default=0.0, ge=0.0, le=15.0, description="Consistency score out of 15.")
    is_available: bool = Field(default=True, description="Whether activity calendar data was available.")


class ContestData(BaseModel):
    """Contest performance metrics."""
    rating: Optional[float] = Field(default=None, description="Contest rating if available.")
    global_ranking: Optional[int] = Field(default=None, description="Global contest ranking if available.")
    total_participants: Optional[int] = Field(default=None, description="Total participants if available.")
    top_percentage: Optional[float] = Field(default=None, description="Top percentage percentile.")
    attended_contests: int = Field(default=0, ge=0, description="Total contests attended.")
    is_available: bool = Field(default=False, description="Whether contest data is available.")


class DSAScoreBreakdown(BaseModel):
    """Transparent breakdown of 100-point DSA Score."""
    total_score: float = Field(..., ge=0.0, le=100.0, description="Total score out of 100.")
    problems_solved_score: float = Field(..., ge=0.0, le=25.0, description="Problems Solved score (Max 25).")
    difficulty_distribution_score: float = Field(..., ge=0.0, le=20.0, description="Difficulty Distribution score (Max 20).")
    topic_coverage_score: float = Field(..., ge=0.0, le=30.0, description="Topic Coverage score (Max 30).")
    consistency_score: float = Field(..., ge=0.0, le=15.0, description="Consistency score (Max 15).")
    contest_performance_score: float = Field(..., ge=0.0, le=10.0, description="Contest Performance score (Max 10).")
    contest_available: bool = Field(default=True, description="Whether contest data was included in evaluation.")


class LeetCodeSuggestion(BaseModel):
    """Actionable improvement recommendation for DSA practice."""
    priority: str = Field(..., description="Priority: HIGH, MEDIUM, LOW.")
    category: str = Field(..., description="Category: TOPIC, DIFFICULTY, CONSISTENCY, CONTEST.")
    message: str = Field(..., description="Actionable recommendation message.")
    impact: str = Field(..., description="Impact on placement DSA readiness.")


class LeetCodeAnalyzeResponse(BaseModel):
    """Structured response payload for LeetCode analysis."""
    success: bool = True
    username: str
    problem_statistics: ProblemStatistics
    topic_statistics: Dict[str, int] = Field(default_factory=dict, description="Solved count per topic.")
    weak_topics: List[WeakTopicItem] = Field(default_factory=list, description="Identified weak DSA topics.")
    consistency: ConsistencyData
    contest_data: ContestData
    dsa_score: DSAScoreBreakdown
    suggestions: List[LeetCodeSuggestion] = Field(default_factory=list, description="Actionable DSA recommendations.")
