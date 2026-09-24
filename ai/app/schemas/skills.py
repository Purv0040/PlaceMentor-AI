"""
Pydantic schemas for the Student Profile Intelligence Engine.
Defines normalized skills, categories, conflicts, and the unified intelligence profile.
"""
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas.student import StudentProfile
from app.schemas.resume import ResumeAnalysis
from app.schemas.github import GitHubAnalysis
from app.schemas.leetcode import LeetCodeAnalysis


class SkillLevel(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"
    UNTESTED = "Untested"
    NOT_DETECTED = "Not Detected"


class NormalizedSkill(BaseModel):
    """
    A single unified skill representation verified across multiple sources.
    Guarantees strict evidence grounding and transparent confidence scoring.
    """
    skill: str = Field(..., description="Normalized canonical name of the skill (e.g., 'Python', 'React', 'Docker')")
    current_level: str = Field(
        ...,
        description="Assessed level: 'Beginner', 'Intermediate', 'Advanced', 'Expert', 'Untested'"
    )
    evidence: List[str] = Field(
        default_factory=list,
        description="Concrete, verifiable evidence strings from ingested sources"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0 based on source verification count and depth"
    )
    source: List[str] = Field(
        default_factory=list,
        description="List of sources confirming this skill: ['resume', 'github', 'leetcode', 'student_profile']"
    )


class ProfileConflict(BaseModel):
    """
    Represents a discrepancy detected between sources (e.g. self-reported vs codebase evidence).
    Never silently ignored; explicitly flagged with resolution rules.
    """
    id: str = Field(..., description="Unique slug or identifier for the conflict")
    category: str = Field(..., description="Category where the conflict was detected (e.g. 'programming', 'dsa')")
    skill_or_topic: str = Field(..., description="The specific skill, topic, or metric in conflict")
    conflict: str = Field(..., description="Clear explanation of the disagreement between sources")
    sources: Dict[str, Any] = Field(
        default_factory=dict,
        description="Map of source name -> claimed value or evidence"
    )
    resolution_rule: str = Field(
        ...,
        description="Rule applied to resolve or flag the discrepancy (e.g., 'Discounted self-claim; penalized confidence')"
    )
    severity: str = Field(
        default="medium",
        description="Severity: 'low', 'medium', 'high'"
    )


class CategorySkillProfile(BaseModel):
    """Normalized profile for a technical skill category."""
    category: str = Field(..., description="Canonical category name")
    overall_level: str = Field(..., description="'Beginner', 'Intermediate', 'Advanced', 'Untested', 'Not Detected'")
    skills: List[NormalizedSkill] = Field(default_factory=list, description="Skills belonging to this category")
    evidence: List[str] = Field(default_factory=list, description="Aggregate evidence for this category")
    summary: str = Field(..., description="Summary of student's standing in this category based on evidence")


class ProjectsProfileCategory(BaseModel):
    """Category 11: Projects profile normalized across resume and GitHub."""
    category: str = "Projects"
    overall_level: str = Field(..., description="'Beginner', 'Intermediate', 'Advanced', 'Untested'")
    total_projects_detected: int = 0
    resume_projects_count: int = 0
    github_repos_count: int = 0
    projects_with_metrics_count: int = 0
    complexity_breakdown: Dict[str, int] = Field(
        default_factory=dict,
        description="e.g. {'beginner': 2, 'intermediate': 3, 'advanced': 1}"
    )
    top_technologies: List[str] = Field(default_factory=list)
    highlights: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    summary: str = Field(..., description="Evidence-backed evaluation of project portfolio")


class ResumeProfileCategory(BaseModel):
    """Category 12: Resume profile summarizing ATS health, structure, and quality."""
    category: str = "Resume"
    overall_level: str = Field(..., description="'Strong', 'Moderate', 'Needs Work', 'Untested'")
    ats_score: Optional[int] = None
    overall_score: Optional[int] = None
    sections_present: List[str] = Field(default_factory=list)
    missing_sections: List[str] = Field(default_factory=list)
    weak_bullets_count: int = 0
    keyword_gaps: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    summary: str = Field(..., description="Evidence-based assessment of resume health")


class GitHubProfileCategory(BaseModel):
    """Category 13: GitHub profile summarizing repository depth, activity, and languages."""
    category: str = "GitHub"
    overall_level: str = Field(..., description="'Active', 'Moderate', 'Low Activity', 'Untested'")
    username: Optional[str] = None
    total_public_repos: int = 0
    non_fork_repos: int = 0
    total_stars: int = 0
    primary_language: Optional[str] = None
    languages_detected: List[str] = Field(default_factory=list)
    readme_coverage_pct: float = 0.0
    activity_level: str = "Untested"
    evidence: List[str] = Field(default_factory=list)
    summary: str = Field(..., description="Evidence-backed assessment of GitHub activity")


class CommunicationProfileCategory(BaseModel):
    """Category 14: Communication & documentation profile derived from resume and repository clarity."""
    category: str = "Communication"
    overall_level: str = Field(..., description="'Strong', 'Adequate', 'Needs Improvement', 'Untested'")
    documentation_score: int = Field(default=0, ge=0, le=100)
    bullet_clarity_score: int = Field(default=0, ge=0, le=100)
    readme_coverage_pct: float = 0.0
    generic_phrases_count: int = 0
    evidence: List[str] = Field(default_factory=list)
    summary: str = Field(..., description="Evidence-backed assessment of technical communication and documentation")


class ProfileCategories(BaseModel):
    """Container for all 14 normalized profile categories."""
    programming: CategorySkillProfile
    dsa: CategorySkillProfile
    backend: CategorySkillProfile
    frontend: CategorySkillProfile
    machine_learning: CategorySkillProfile
    data_science: CategorySkillProfile
    databases: CategorySkillProfile
    devops: CategorySkillProfile
    cloud: CategorySkillProfile
    cs_fundamentals: CategorySkillProfile
    projects: ProjectsProfileCategory
    resume: ResumeProfileCategory
    github: GitHubProfileCategory
    communication: CommunicationProfileCategory


class ProfileSourceStatus(BaseModel):
    """Status indicating which input data sources were provided and utilized."""
    student_profile: bool = False
    resume_analysis: bool = False
    github_analysis: bool = False
    leetcode_analysis: bool = False
    total_sources_provided: int = 0


class StudentIntelligenceProfile(BaseModel):
    """
    Unified, evidence-backed representation of the student's placement profile.
    Combines Resume, GitHub, LeetCode, and Student Profile into 14 normalized categories.
    """
    student_metadata: Optional[Dict[str, Any]] = None
    target_role: Optional[str] = None
    source_status: ProfileSourceStatus
    skills: List[NormalizedSkill] = Field(
        default_factory=list,
        description="Flat deduplicated list of all normalized skills across categories"
    )
    categories: ProfileCategories
    conflicts: List[ProfileConflict] = Field(
        default_factory=list,
        description="Flagged discrepancies between sources with explicit resolution rules"
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="Top evidence-backed strengths across all analyzed dimensions"
    )
    growth_areas: List[str] = Field(
        default_factory=list,
        description="Top evidence-backed gaps or growth opportunities"
    )
    overall_readiness_level: str = Field(
        ...,
        description="Overall placement readiness: 'Beginner', 'Developing', 'Placement Ready', 'Advanced'"
    )
    executive_summary: str = Field(
        ...,
        description="Evidence-grounded executive summary of student's complete profile"
    )


class ProfileBuildRequest(BaseModel):
    """Input payload for building a unified StudentIntelligenceProfile."""
    student_profile: Optional[StudentProfile] = None
    resume_analysis: Optional[ResumeAnalysis] = None
    github_analysis: Optional[GitHubAnalysis] = None
    leetcode_analysis: Optional[LeetCodeAnalysis] = None
