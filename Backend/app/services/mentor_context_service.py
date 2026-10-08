import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.profile_repository import ProfileRepository
from app.repositories.resume_repository import ResumeRepository
from app.repositories.github_repository import GitHubRepository
from app.repositories.leetcode_repository import LeetCodeRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.readiness_repository import ReadinessRepository
from app.repositories.skill_gap_repository import SkillGapRepository
from app.repositories.roadmap_repository import RoadmapRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.progress_repository import ProgressRepository
from app.repositories.interview_repository import InterviewRepository
from app.repositories.communication_repository import CommunicationRepository

logger = logging.getLogger(__name__)


class MentorContextService:
    """Collects and normalizes multi-module student telemetry for context-aware AI mentor guidance."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.profile_repo = ProfileRepository(db)
        self.resume_repo = ResumeRepository(db)
        self.github_repo = GitHubRepository(db)
        self.leetcode_repo = LeetCodeRepository(db)
        self.project_repo = ProjectRepository(db)
        self.readiness_repo = ReadinessRepository(db)
        self.skill_gap_repo = SkillGapRepository(db)
        self.roadmap_repo = RoadmapRepository(db)
        self.task_repo = TaskRepository(db)
        self.progress_repo = ProgressRepository(db)
        self.interview_repo = InterviewRepository(db)
        self.comm_repo = CommunicationRepository(db)

    async def build_student_context(self, user_id: str) -> Dict[str, Any]:
        """Fetch and assemble student placement context across all modules."""
        # Fetch profile
        profile = await self.profile_repo.get_by_user_id(user_id) or {}
        target_role = profile.get("target_role")

        resume = await self.resume_repo.find_active_by_user(user_id) or {}
        github = await self.github_repo.find_by_user_id(user_id) or {}
        leetcode = await self.leetcode_repo.find_by_user_id(user_id) or {}
        projects = await self.project_repo.find_by_user_id(user_id) or []
        readiness = await self.readiness_repo.get_latest_by_user(user_id) or {}
        skill_gaps = await self.skill_gap_repo.get_latest_by_user(user_id) or {}
        roadmap = await self.roadmap_repo.get_active_by_user_id(user_id) or {}
        all_tasks = await self.task_repo.get_all_by_user(user_id) or []
        progress = await self.progress_repo.get_by_user_id(user_id) or {}
        interviews = await self.interview_repo.get_history_by_user_id(user_id, limit=5) or []
        communication = await self.comm_repo.get_history_by_user_id(user_id, limit=5) or []

        # Summarize today's and pending tasks
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        today_tasks = [t for t in all_tasks if t.get("date") == today_str or t.get("status") == "pending"]

        # LeetCode extraction
        leetcode_analysis = leetcode.get("analysis") or leetcode.get("metrics") or {}
        leetcode_weak_topics = (
            leetcode.get("weak_topics")
            or leetcode_analysis.get("weak_topics")
            or leetcode_analysis.get("weak_areas")
            or []
        )

        # GitHub extraction
        github_analysis = github.get("analysis") or github.get("metrics") or {}

        # Skill gap extraction
        gap_items = (
            skill_gaps.get("top_gaps")
            or skill_gaps.get("missing_skills")
            or skill_gaps.get("gaps")
            or []
        )

        return {
            "target_role": target_role,
            "profile": {
                "name": profile.get("full_name") or "Student",
                "target_role": target_role,
                "target_company_tier": profile.get("target_company_tier"),
                "skills": profile.get("skills") or [],
                "experience_level": profile.get("experience_level"),
            },
            "resume_analysis": resume.get("analysis") or resume.get("metrics") or {},
            "github_analysis": github_analysis,
            "leetcode_analysis": leetcode_analysis,
            "leetcode_weak_topics": leetcode_weak_topics,
            "projects": [
                {
                    "title": p.get("title") or p.get("name"),
                    "tech_stack": p.get("tech_stack") or [],
                    "score": p.get("score") or p.get("architecture_score"),
                }
                for p in projects[:5]
                if p.get("title") or p.get("name")
            ],
            "readiness": {
                "overall_score": readiness.get("overall_score") or readiness.get("readiness_score"),
                "readiness_label": readiness.get("readiness_label"),
                "confidence": readiness.get("overall_confidence"),
                "breakdown": readiness.get("breakdown") or readiness.get("category_scores") or {},
            },
            "skill_gaps": {
                "top_gaps": gap_items,
                "critical_gaps_count": skill_gaps.get("critical_gaps_count", len(gap_items)),
            },
            "roadmap": {
                "roadmap_id": roadmap.get("roadmap_id") or (str(roadmap.get("_id")) if roadmap.get("_id") else None),
                "current_day": roadmap.get("current_day"),
                "total_days": roadmap.get("total_days"),
                "current_phase": roadmap.get("current_phase"),
                "completion_percentage": roadmap.get("completion_percentage"),
                "status": roadmap.get("status"),
            },
            "today_tasks": {
                "total": len(today_tasks),
                "pending_tasks": [
                    {
                        "task_id": t.get("task_id"),
                        "title": t.get("title"),
                        "category": t.get("category"),
                        "priority": t.get("priority"),
                        "day": t.get("day"),
                        "status": t.get("status"),
                    }
                    for t in today_tasks[:5]
                ],
            },
            "progress": {
                "overall_progress_percent": progress.get("overall_progress_percent"),
                "streak_days": progress.get("streak_days"),
                "completed_tasks": progress.get("completed_tasks"),
                "pending_tasks": progress.get("pending_tasks"),
            },
            "interview_results": [
                {
                    "type": i.get("interview_type"),
                    "score": i.get("overall_score"),
                    "date": str(i.get("completed_at")),
                }
                for i in interviews[:3]
                if i.get("interview_type") or i.get("overall_score") is not None
            ],
            "communication_results": [
                {
                    "overall_score": c.get("overall_score"),
                    "clarity": c.get("clarity"),
                    "wpm": c.get("speaking_pace_wpm"),
                }
                for c in communication[:3]
                if c.get("overall_score") is not None
            ],
        }
