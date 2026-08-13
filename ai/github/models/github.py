"""Pydantic v2 data models for GitHub Analyzer."""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class GitHubAnalyzeRequest(BaseModel):
    """API Request model for GitHub profile analysis."""
    username: str = Field(..., min_length=1, description="GitHub username to analyze.")


class GitHubProfile(BaseModel):
    """GitHub profile information model."""
    username: str
    name: Optional[str] = None
    bio: Optional[str] = None
    followers: int = 0
    following: int = 0
    public_repos: int = 0
    public_gists: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    avatar_url: Optional[str] = None
    html_url: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    blog: Optional[str] = None
    email: Optional[str] = None


class RepositorySummary(BaseModel):
    """Detailed summary model for a GitHub repository."""
    name: str
    full_name: str
    description: Optional[str] = None
    is_fork: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    pushed_at: Optional[str] = None
    size: int = 0
    stargazers_count: int = 0
    watchers_count: int = 0
    forks_count: int = 0
    language: Optional[str] = None
    topics: List[str] = Field(default_factory=list)
    license: Optional[str] = None
    has_readme: bool = False
    default_branch: str = "main"
    open_issues_count: int = 0


class READMECheckDetails(BaseModel):
    """Rule-based README breakdown analysis model."""
    has_readme: bool = False
    has_description: bool = False
    has_installation: bool = False
    has_usage: bool = False
    has_features: bool = False
    has_technologies: bool = False
    has_screenshots: bool = False
    has_api_docs: bool = False
    has_license: bool = False
    score: float = Field(default=0.0, ge=0.0, le=20.0)


class GitHubStatistics(BaseModel):
    """Aggregated GitHub statistics."""
    total_repos: int = 0
    non_fork_repos: int = 0
    fork_repos: int = 0
    total_stars: int = 0
    total_forks: int = 0
    unique_topics_count: int = 0
    top_languages: List[str] = Field(default_factory=list)


class GitHubScoreBreakdown(BaseModel):
    """Detailed breakdown of GitHub score out of 100."""
    total_score: float = Field(..., ge=0.0, le=100.0, description="Total score out of 100.")
    repository_quality: float = Field(..., ge=0.0, le=30.0, description="Repository Quality score (Max 30).")
    activity: float = Field(..., ge=0.0, le=25.0, description="Activity score (Max 25).")
    documentation: float = Field(..., ge=0.0, le=20.0, description="Documentation score (Max 20).")
    technology_diversity: float = Field(..., ge=0.0, le=15.0, description="Technology Diversity score (Max 15).")
    profile_completeness: float = Field(..., ge=0.0, le=10.0, description="Profile Completeness score (Max 10).")


class GitHubSuggestion(BaseModel):
    """Actionable improvement suggestion model."""
    priority: str = Field(..., description="Priority level: HIGH, MEDIUM, LOW.")
    category: str = Field(..., description="Category: PROFILE, REPOSITORY, DOCUMENTATION, ACTIVITY, TOPICS.")
    message: str = Field(..., description="Actionable recommendation message.")
    impact: str = Field(..., description="Explanation of impact on candidate placement profile.")


class GitHubAnalyzeResponse(BaseModel):
    """Structured response payload for GitHub profile analysis."""
    success: bool = True
    username: str
    profile: GitHubProfile
    repositories: List[RepositorySummary]
    languages: Dict[str, int] = Field(default_factory=dict, description="Language byte/repo distribution.")
    statistics: GitHubStatistics
    score: GitHubScoreBreakdown
    suggestions: List[GitHubSuggestion]
