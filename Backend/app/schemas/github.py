from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class GitHubConnectRequest(BaseModel):
    github_username: str = Field(..., example="octocat", description="GitHub username to connect")


class GitHubProfileDetail(BaseModel):
    id: Optional[int] = None
    login: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    blog: Optional[str] = None
    public_repos: int = 0
    followers: int = 0
    following: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    html_url: Optional[str] = None


class GitHubStatisticsDetail(BaseModel):
    total_repositories: int = 0
    total_stars: int = 0
    total_forks: int = 0
    languages: Dict[str, int] = Field(default_factory=dict)
    language_distribution: List[Dict[str, Any]] = Field(default_factory=list)
    public_repositories: int = 0
    forked_repositories: int = 0
    non_fork_repositories: int = 0
    repos_with_readme: int = 0
    repos_with_description: int = 0
    primary_language: Optional[str] = None
    impact_score: int = 0
    repo_quality_score: int = 0
    total_recent_commits: int = 0
    commits_last_30_days: int = 0
    active_streak_days: int = 0
    longest_streak_days: int = 0
    last_active_date: Optional[str] = None
    impact_breakdown: Dict[str, Any] = Field(default_factory=dict)
    weekly_activity: List[Dict[str, Any]] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)
    data_scope: Dict[str, Any] = Field(default_factory=dict)


class GitHubSyncInfo(BaseModel):
    status: str = "not_synced"
    last_synced_at: Optional[datetime] = None
    last_successful_sync_at: Optional[datetime] = None
    error: Optional[str] = None


class GitHubConnectResponse(BaseModel):
    user_id: str
    github_username: str
    is_connected: bool = True
    profile: Optional[Dict[str, Any]] = None
    status: str = "connected"


class GitHubProfileResponse(BaseModel):
    id: str
    user_id: str
    github_username: str
    is_connected: bool = True
    profile: Optional[Dict[str, Any]] = None
    statistics: Optional[Dict[str, Any]] = None
    sync: Dict[str, Any] = Field(default_factory=dict)
    analysis_version: Optional[str] = "1.0"
    has_analysis: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class GitHubRepoItem(BaseModel):
    id: str
    repo_id: Optional[int] = None
    name: str
    full_name: str
    description: Optional[str] = None
    html_url: Optional[str] = None
    language: Optional[str] = None
    languages: Dict[str, int] = Field(default_factory=dict)
    stars: int = 0
    forks: int = 0
    topics: List[str] = Field(default_factory=list)
    has_readme: bool = False
    is_fork: bool = False
    size: int = 0
    ast_score: int = 0
    quality_score: int = 0
    quality_tier: str = "Active Project"
    tags: List[str] = Field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    pushed_at: Optional[str] = None


class GitHubRepoListResponse(BaseModel):
    items: List[GitHubRepoItem] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    limit: int = 50


class GitHubAnalysisResponse(BaseModel):
    user_id: str
    github_username: str
    analysis_version: str = "1.0"
    analyzed_at: Optional[datetime] = None
    analysis: Optional[Dict[str, Any]] = None
