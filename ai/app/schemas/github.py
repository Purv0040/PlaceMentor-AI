"""
Pydantic schemas for GitHub profile analysis.
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Raw GitHub data models (one-to-one with GitHub API responses)
# ---------------------------------------------------------------------------

class GitHubRepoRaw(BaseModel):
    """Represents raw data collected from a single GitHub repository."""
    name: str
    description: Optional[str] = None
    language: Optional[str] = None
    languages: Dict[str, int] = Field(
        default_factory=dict,
        description="Mapping of language name → bytes of code"
    )
    stars: int = Field(default=0, alias="stargazers_count")
    forks: int = Field(default=0, alias="forks_count")
    topics: List[str] = Field(default_factory=list)
    has_readme: bool = False
    is_fork: bool = Field(default=False, alias="fork")
    updated_at: Optional[str] = None
    pushed_at: Optional[str] = None
    size: int = Field(default=0, description="Repo size in KB")

    model_config = {"populate_by_name": True}


class GitHubProfileRaw(BaseModel):
    """Raw profile data collected from the GitHub API."""
    username: str
    name: Optional[str] = None
    bio: Optional[str] = None
    public_repos: int = 0
    followers: int = 0
    following: int = 0
    location: Optional[str] = None
    company: Optional[str] = None
    blog: Optional[str] = None
    repositories: List[GitHubRepoRaw] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Processed / derived models
# ---------------------------------------------------------------------------

class TechCategory(BaseModel):
    """A detected technical category and the evidence that supports it."""
    name: str = Field(..., description="e.g. 'Machine Learning', 'REST API', 'Docker'")
    detected: bool
    evidence: List[str] = Field(
        default_factory=list,
        description="List of repo names / topics / languages that indicate this category"
    )


class ComplexityAnalysis(BaseModel):
    """Transparent rule-based complexity estimate for a repository."""
    repo_name: str
    complexity_level: str = Field(
        ...,
        description="One of: 'beginner', 'intermediate', 'advanced'"
    )
    evidence: List[str] = Field(
        ...,
        description="Concrete reasons behind the complexity rating"
    )
    confidence: str = Field(
        ...,
        description="One of: 'high', 'medium', 'low'"
    )


class ActivitySummary(BaseModel):
    """High-level activity metrics derived from repository data."""
    total_public_repos: int
    non_fork_repos: int
    repos_with_readme: int
    most_recent_push: Optional[str] = None
    most_starred_repo: Optional[str] = None
    most_starred_count: int = 0
    total_stars: int = 0
    total_forks: int = 0


class LanguageDistribution(BaseModel):
    """Aggregated language usage across all repositories."""
    primary_language: Optional[str] = None
    all_languages: List[str] = Field(default_factory=list)
    language_repo_counts: Dict[str, int] = Field(
        default_factory=dict,
        description="How many repos use each language"
    )


# ---------------------------------------------------------------------------
# LLM output model (what we ask the LLM to produce)
# ---------------------------------------------------------------------------

class LLMGitHubInterpretation(BaseModel):
    """Structured interpretation produced by the LLM based on collected data."""
    strengths: List[str] = Field(
        ...,
        description=(
            "Specific strengths observed in the portfolio. "
            "Each point must cite evidence from the provided data."
        )
    )
    gaps: List[str] = Field(
        ...,
        description=(
            "Gaps or under-represented areas. "
            "Only cite gaps that are detectable from the available data."
        )
    )
    technical_patterns: List[str] = Field(
        ...,
        description="Observable patterns in the technology choices across repositories."
    )
    recommendations: List[str] = Field(
        ...,
        description=(
            "Concrete, actionable portfolio recommendations. "
            "Do NOT recommend adding skills unless the gap is supported by evidence."
        )
    )
    evidence_summary: str = Field(
        ...,
        description="A 2-3 sentence summary of the portfolio based strictly on available evidence."
    )


# ---------------------------------------------------------------------------
# Final output model returned to the caller
# ---------------------------------------------------------------------------

class GitHubAnalysis(BaseModel):
    """Complete GitHub intelligence analysis result."""
    profile: GitHubProfileRaw
    activity: ActivitySummary
    languages: LanguageDistribution
    technical_categories: List[TechCategory]
    complexity_analyses: List[ComplexityAnalysis]
    strengths: List[str]
    gaps: List[str]
    technical_patterns: List[str]
    recommendations: List[str]
    evidence_summary: str
