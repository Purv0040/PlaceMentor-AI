"""
Pydantic schemas for the End-to-End AI Placement Copilot Pipeline.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas.student import StudentProfile
from app.schemas.resume import ResumeAnalysis
from app.schemas.github import GitHubAnalysis
from app.schemas.leetcode import LeetCodeAnalysis
from app.schemas.skills import StudentIntelligenceProfile
from app.schemas.skill_gap import SkillGapAnalysis
from app.schemas.readiness import PlacementReadinessAnalysis
from app.schemas.roadmap import PersonalizedRoadmap
from app.schemas.daily_task import TodayTasksResponse
from app.schemas.adaptive import AdaptiveRoadmapResponse
from app.schemas.mentor import MentorChatResponse


class PipelineRunRequest(BaseModel):
    """Input payload to trigger the full end-to-end AI pipeline."""
    target_role: str = Field(default="AI/ML Engineer", description="Target role name")
    available_time: int = Field(default=120, description="Available daily study time in minutes")
    resume_text: Optional[str] = Field(None, description="Custom resume text, or uses synthetic demo resume")
    github_username: Optional[str] = Field(None, description="Custom GitHub username, or uses synthetic demo user")
    leetcode_username: Optional[str] = Field(None, description="Custom LeetCode username, or uses synthetic demo user")
    student_profile: Optional[StudentProfile] = Field(None, description="Custom student self-reported profile")


class PipelineRunResponse(BaseModel):
    """Output payload containing results from all 11 steps of the end-to-end pipeline."""
    target_role: str
    available_time: int
    step_1_resume_analysis: ResumeAnalysis
    step_2_github_analysis: GitHubAnalysis
    step_3_leetcode_analysis: LeetCodeAnalysis
    step_4_unified_profile: StudentIntelligenceProfile
    step_5_skill_gaps: SkillGapAnalysis
    step_6_readiness: PlacementReadinessAnalysis
    step_7_roadmap: PersonalizedRoadmap
    step_8_today_tasks: TodayTasksResponse
    step_9_simulated_completed_tasks: List[str]
    step_10_adapted_roadmap: AdaptiveRoadmapResponse
    step_11_mentor_response: MentorChatResponse
