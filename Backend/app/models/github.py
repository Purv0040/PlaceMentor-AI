from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class GitHubSyncStatus(BaseModel):
    status: str = Field(default="not_synced", description="One of: not_connected, not_synced, syncing, synced, failed")
    last_synced_at: Optional[datetime] = None
    last_successful_sync_at: Optional[datetime] = None
    error: Optional[str] = None


class GitHubStatistics(BaseModel):
    total_repositories: int = 0
    total_stars: int = 0
    total_forks: int = 0
    languages: Dict[str, int] = Field(default_factory=dict)
    public_repositories: int = 0
    forked_repositories: int = 0
    non_fork_repositories: int = 0
    repos_with_readme: int = 0
    primary_language: Optional[str] = None


class GitHubProfileInfo(BaseModel):
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


class GitHubProfileModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    github_username: str
    profile: Optional[Dict[str, Any]] = None
    statistics: Optional[Dict[str, Any]] = None
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


class GitHubRepoModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    github_profile_id: Optional[str] = None
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
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    pushed_at: Optional[str] = None

    class Config:
        populate_by_name = True
