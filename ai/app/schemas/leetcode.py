"""
Pydantic schemas for LeetCode profile analysis.
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Raw data models (provider-agnostic)
# ---------------------------------------------------------------------------

class LeetCodeProfileRaw(BaseModel):
    """Basic public profile data for a LeetCode user."""
    username: str
    real_name: Optional[str] = None
    about: Optional[str] = None
    ranking: Optional[int] = None
    reputation: Optional[int] = None
    avatar_url: Optional[str] = None


class ProblemStatistics(BaseModel):
    """Counts of solved problems by difficulty."""
    total_solved: int = Field(default=0, ge=0)
    easy_solved: int = Field(default=0, ge=0)
    medium_solved: int = Field(default=0, ge=0)
    hard_solved: int = Field(default=0, ge=0)
    total_questions: int = Field(default=0, ge=0, description="Total available problems on LeetCode")
    easy_total: int = Field(default=0, ge=0)
    medium_total: int = Field(default=0, ge=0)
    hard_total: int = Field(default=0, ge=0)
    acceptance_rate: Optional[float] = Field(
        default=None,
        description="Overall submission acceptance rate (0–100), if available"
    )


class DifficultyDistribution(BaseModel):
    """Percentage of solved problems at each difficulty level."""
    easy_pct: float = Field(default=0.0, description="% of solved problems that are Easy")
    medium_pct: float = Field(default=0.0, description="% of solved problems that are Medium")
    hard_pct: float = Field(default=0.0, description="% of solved problems that are Hard")


class RecentSubmission(BaseModel):
    """A single recent submission entry."""
    title: str
    difficulty: Optional[str] = None
    timestamp: Optional[str] = None
    status: Optional[str] = None


class ContestInfo(BaseModel):
    """Contest rating information if available."""
    rating: Optional[float] = None
    global_ranking: Optional[int] = None
    attended_contests: Optional[int] = None
    top_percentage: Optional[float] = None


# ---------------------------------------------------------------------------
# Topic analysis models
# ---------------------------------------------------------------------------

class TopicAnalysis(BaseModel):
    """
    Transparent per-topic performance assessment.

    Performance is derived only from measurable signals:
    - How many tagged problems were solved
    - What difficulty those problems were
    - Whether the topic was recently active

    No black-box percentage claims are made.
    """
    topic: str
    solved_count: int = Field(default=0, description="Number of problems solved with this topic tag")
    difficulty_breakdown: Dict[str, int] = Field(
        default_factory=dict,
        description="e.g. {'Easy': 5, 'Medium': 3, 'Hard': 1}"
    )
    performance_level: str = Field(
        ...,
        description="One of: 'strong', 'developing', 'beginner', 'untested'"
    )
    evidence: List[str] = Field(
        ...,
        description="Concrete facts driving the performance_level rating"
    )
    confidence: str = Field(
        ...,
        description="One of: 'high', 'medium', 'low'"
    )


# ---------------------------------------------------------------------------
# Data source status
# ---------------------------------------------------------------------------

class DataSourceStatus(BaseModel):
    """
    Describes which data was successfully retrieved and from where.
    Ensures the caller always knows what is real vs. unavailable.
    """
    provider: str = Field(..., description="Name of the data provider used")
    profile_available: bool = False
    problems_available: bool = False
    topics_available: bool = False
    contest_available: bool = False
    recent_activity_available: bool = False
    notes: List[str] = Field(
        default_factory=list,
        description="Human-readable notes about data availability or limitations"
    )


# ---------------------------------------------------------------------------
# Final output schema
# ---------------------------------------------------------------------------

class LeetCodeAnalysis(BaseModel):
    """Complete LeetCode intelligence analysis result."""
    profile: LeetCodeProfileRaw
    problem_statistics: ProblemStatistics
    difficulty_distribution: DifficultyDistribution
    topic_analysis: List[TopicAnalysis]
    strong_topics: List[str] = Field(
        default_factory=list,
        description="Topics where performance_level == 'strong'"
    )
    weak_topics: List[str] = Field(
        default_factory=list,
        description="Topics where performance_level is 'beginner' or 'untested'"
    )
    contest: Optional[ContestInfo] = None
    recent_activity: List[RecentSubmission] = Field(default_factory=list)
    recommendations: List[str] = Field(
        default_factory=list,
        description="Evidence-based recommendations for improvement"
    )
    data_source_status: DataSourceStatus
