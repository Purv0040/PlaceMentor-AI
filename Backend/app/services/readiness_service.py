import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.readiness_repository import ReadinessRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.resume_repository import ResumeRepository
from app.repositories.github_repository import GitHubRepository
from app.repositories.leetcode_repository import LeetCodeRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.communication_repository import CommunicationRepository
from app.repositories.interview_repository import InterviewRepository
from app.engines.readiness_engine import DeterministicReadinessEngine
from app.integrations.ai_client import AIClient, AIClientError

logger = logging.getLogger(__name__)


class ReadinessService:
    """Orchestrates multi-module student telemetry collection, deterministic scoring, and AI analysis."""

    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        ai_client: Optional[AIClient] = None
    ) -> None:
        self.db = db
        self.repo = ReadinessRepository(db)
        self.profile_repo = ProfileRepository(db)
        self.resume_repo = ResumeRepository(db)
        self.github_repo = GitHubRepository(db)
        self.leetcode_repo = LeetCodeRepository(db)
        self.project_repo = ProjectRepository(db)
        self.comm_repo = CommunicationRepository(db)
        self.interview_repo = InterviewRepository(db)
        self.ai_client = ai_client or AIClient()
        self.engine = DeterministicReadinessEngine()

    async def analyze_readiness(
        self,
        user_id: str,
        target_role_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """Collect telemetry from all modules, compute deterministic readiness, enrich with AI, and persist."""
        # 1. Fetch Student Profile & Determine Target Role
        student_profile = await self.profile_repo.get_by_user_id(user_id)

        target_role = target_role_override
        if not target_role and student_profile:
            career = student_profile.get("career", {})
            if isinstance(career, dict):
                target_role = career.get("targetRole") or career.get("target_role")
            if not target_role:
                target_role = student_profile.get("target_role")

        # 2. Fetch Resume Intelligence
        resume_doc = await self.resume_repo.find_active_by_user(user_id)
        if not resume_doc:
            resumes = await self.resume_repo.find_all_by_user(user_id)
            resume_doc = resumes[0] if resumes else None

        # 3. Fetch GitHub Intelligence
        github_doc = await self.github_repo.find_by_user_id(user_id)

        # 4. Fetch LeetCode Intelligence
        leetcode_doc = await self.leetcode_repo.find_by_user_id(user_id)

        # 5. Fetch Projects
        projects_list = await self.project_repo.find_by_user_id(user_id)

        # 6. Fetch Communication & Mock Interview Telemetry
        comm_history = await self.comm_repo.get_history_by_user_id(user_id, limit=1)
        comm_doc = comm_history[0] if comm_history else None

        interview_history = await self.interview_repo.get_history_by_user_id(user_id, limit=1)
        interview_doc = interview_history[0] if interview_history else None

        # 7. Check for stale telemetry data
        stale_warnings: List[Dict[str, Any]] = []
        now = datetime.utcnow()

        if leetcode_doc and leetcode_doc.get("updated_at"):
            last_up = leetcode_doc["updated_at"]
            if isinstance(last_up, datetime) and (now - last_up).days > 7:
                stale_warnings.append({
                    "source": "leetcode",
                    "last_updated": last_up.isoformat(),
                    "message": "LeetCode telemetry has not been synchronized in over 7 days."
                })

        if github_doc and github_doc.get("updated_at"):
            last_up = github_doc["updated_at"]
            if isinstance(last_up, datetime) and (now - last_up).days > 14:
                stale_warnings.append({
                    "source": "github",
                    "last_updated": last_up.isoformat(),
                    "message": "GitHub repository data has not been synchronized in over 14 days."
                })

        if resume_doc and resume_doc.get("updated_at"):
            last_up = resume_doc["updated_at"]
            if isinstance(last_up, datetime) and (now - last_up).days > 30:
                stale_warnings.append({
                    "source": "resume",
                    "last_updated": last_up.isoformat(),
                    "message": "Resume analysis is older than 30 days. Re-upload your resume to refresh ATS audit."
                })

        # 8. Compute deterministic scoring across 7 categories
        computed_result = self.engine.compute(
            target_role=target_role,
            profile_data=student_profile,
            resume_data=resume_doc,
            github_data=github_doc,
            leetcode_data=leetcode_doc,
            projects_list=projects_list,
            communication_data=comm_doc,
            interview_data=interview_doc
        )
        computed_result["stale_data"] = stale_warnings

        # 9. Enrich with external AI microservice interpretation if available
        try:
            if target_role:
                ai_payload = {
                    "target_role": target_role,
                    "student_profile": student_profile,
                    "resume_analysis": resume_doc.get("analysis") if resume_doc else None,
                    "github_analysis": github_doc.get("analysis") if github_doc else None,
                    "leetcode_analysis": leetcode_doc.get("analysis") if leetcode_doc else None,
                }
                ai_interpretation = await self.ai_client.calculate_readiness(ai_payload)
                if ai_interpretation and isinstance(ai_interpretation, dict):
                    if ai_interpretation.get("strengths"):
                        for s in ai_interpretation["strengths"]:
                            if s not in computed_result["strengths"]:
                                computed_result["strengths"].append(s)
                        computed_result["strengths"] = computed_result["strengths"][:4]
                    if ai_interpretation.get("key_gaps"):
                        for g in ai_interpretation["key_gaps"]:
                            if g not in computed_result["key_gaps"]:
                                computed_result["key_gaps"].append(g)
                        computed_result["key_gaps"] = computed_result["key_gaps"][:4]
        except Exception as e:
            logger.warning("AI microservice readiness calculation fallback engaged: %s", e)

        # 10. Persist result in MongoDB Atlas
        created = await self.repo.create_analysis(user_id, computed_result)
        logger.info("Successfully saved Placement Readiness Analysis for user %s (score %s)", user_id, created.get("overall_score"))
        return created

    async def get_latest_readiness(self, user_id: str) -> Dict[str, Any]:
        """Fetch latest readiness analysis or trigger recalculation if none exists."""
        latest = await self.repo.get_latest_by_user(user_id)
        if not latest:
            return await self.analyze_readiness(user_id)
        return latest

    async def get_readiness_summary(self, user_id: str) -> Dict[str, Any]:
        """Fetch lightweight summary suitable for main application dashboard."""
        latest = await self.get_latest_readiness(user_id)
        return {
            "user_id": user_id,
            "overall_score": latest.get("overall_score"),
            "readiness_label": latest.get("readiness_label"),
            "overall_confidence": latest.get("overall_confidence"),
            "target_role": latest.get("target_role"),
            "scored_categories_count": latest.get("scored_categories_count"),
            "categories": {
                name: {"score": cat.get("score"), "status": cat.get("status")}
                for name, cat in latest.get("categories", {}).items()
            },
            "updated_at": latest.get("updated_at")
        }

    async def get_readiness_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve historical calculation snapshots."""
        return await self.repo.get_history_by_user(user_id, limit=limit)

    async def get_analysis_by_id(self, analysis_id: str, user_id: str) -> Dict[str, Any]:
        """Retrieve specific readiness analysis with ownership verification."""
        analysis = await self.repo.get_by_id(analysis_id, user_id=user_id)
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Readiness analysis not found or access denied."
            )
        return analysis
