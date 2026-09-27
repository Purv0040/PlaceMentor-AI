import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.skill_gap_repository import SkillGapRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.resume_repository import ResumeRepository
from app.repositories.github_repository import GitHubRepository
from app.repositories.leetcode_repository import LeetCodeRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.readiness_repository import ReadinessRepository
from app.engines.skill_gap_engine import DeterministicSkillGapEngine
from app.integrations.ai_client import AIClient, AIClientError

logger = logging.getLogger(__name__)


class SkillGapService:
    """Orchestrates multi-module student telemetry collection, deterministic skill gap computation, AI synthesis, and storage."""

    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        ai_client: Optional[AIClient] = None
    ) -> None:
        self.db = db
        self.repo = SkillGapRepository(db)
        self.profile_repo = ProfileRepository(db)
        self.resume_repo = ResumeRepository(db)
        self.github_repo = GitHubRepository(db)
        self.leetcode_repo = LeetCodeRepository(db)
        self.project_repo = ProjectRepository(db)
        self.readiness_repo = ReadinessRepository(db)
        self.ai_client = ai_client or AIClient()
        self.engine = DeterministicSkillGapEngine()

    async def analyze_skill_gaps(
        self,
        user_id: str,
        target_role_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """Collect telemetry from all student modules, compute deterministic skill gaps, enrich with AI, and persist."""
        # 1. Fetch Student Profile
        student_profile = await self.profile_repo.get_by_user_id(user_id)
        target_role = target_role_override or (student_profile.get("target_role") if student_profile else None) or "Backend Developer"

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

        # 6. Check for stale data
        stale_warnings: List[Dict[str, Any]] = []
        now = datetime.utcnow()

        if leetcode_doc and leetcode_doc.get("updated_at"):
            last_up = leetcode_doc["updated_at"]
            if isinstance(last_up, datetime) and (now - last_up).days > 7:
                stale_warnings.append({
                    "source": "leetcode",
                    "last_updated": last_up.isoformat(),
                    "message": "LeetCode telemetry is over 7 days old."
                })

        if github_doc and github_doc.get("updated_at"):
            last_up = github_doc["updated_at"]
            if isinstance(last_up, datetime) and (now - last_up).days > 14:
                stale_warnings.append({
                    "source": "github",
                    "last_updated": last_up.isoformat(),
                    "message": "GitHub repository data is over 14 days old."
                })

        # 7. Compute deterministic skill gaps
        computed_result = self.engine.analyze(
            target_role=target_role,
            profile_data=student_profile,
            resume_data=resume_doc,
            github_data=github_doc,
            leetcode_data=leetcode_doc,
            projects_list=projects_list
        )
        computed_result["stale_data"] = stale_warnings

        # 8. Enrich with external AI microservice interpretation if available
        try:
            ai_payload = {
                "target_role": target_role,
                "profile": {
                    "skills": [
                        {"skill": item["skill"], "current_level": item["current_level"], "evidence": item["evidence"]}
                        for item in computed_result.get("skills", [])
                    ]
                }
            }
            ai_interpretation = await self.ai_client.analyze_skill_gaps(ai_payload)
            if ai_interpretation and isinstance(ai_interpretation, dict):
                if ai_interpretation.get("summary"):
                    computed_result["ai_summary"] = ai_interpretation["summary"]
                # Update item explanations if available from AI
                if ai_interpretation.get("skills"):
                    ai_skill_map = {s.get("skill", "").lower(): s for s in ai_interpretation["skills"] if isinstance(s, dict)}
                    for s_item in computed_result.get("skills", []):
                        ai_s = ai_skill_map.get(s_item["skill"].lower())
                        if ai_s:
                            if ai_s.get("explanation"):
                                s_item["reason"] = ai_s["explanation"]
                            if ai_s.get("recommended_action"):
                                s_item["recommended_action"] = ai_s["recommended_action"]
        except Exception as e:
            logger.warning("AI microservice skill gap fallback engaged: %s", e)

        # 9. Persist result in MongoDB Atlas
        created = await self.repo.create_analysis(user_id, computed_result)
        logger.info("Saved Skill Gap Analysis for user %s (coverage %s%%)", user_id, created.get("overall_coverage"))
        return created

    async def get_latest_skill_gaps(self, user_id: str) -> Dict[str, Any]:
        """Fetch latest skill gap analysis or trigger recalculation if none exists."""
        latest = await self.repo.get_latest_by_user(user_id)
        if not latest:
            return await self.analyze_skill_gaps(user_id)
        return latest

    async def get_skill_gap_summary(self, user_id: str) -> Dict[str, Any]:
        """Fetch lightweight summary suitable for application dashboard."""
        latest = await self.get_latest_skill_gaps(user_id)
        return {
            "user_id": user_id,
            "target_role": latest.get("target_role"),
            "overall_coverage": latest.get("overall_coverage"),
            "confidence_index": latest.get("confidence_index"),
            "total_audited": latest.get("total_audited"),
            "gaps_identified_count": len(latest.get("priority_gaps", [])),
            "summary": latest.get("summary", {}),
            "top_priority_gaps": latest.get("priority_gaps", [])[:3],
            "updated_at": latest.get("updated_at")
        }

    async def get_skill_gap_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve historical calculation snapshots."""
        return await self.repo.get_history_by_user(user_id, limit=limit)

    async def get_analysis_by_id(self, analysis_id: str, user_id: str) -> Dict[str, Any]:
        """Retrieve specific skill gap analysis with ownership verification."""
        analysis = await self.repo.get_by_id(analysis_id, user_id=user_id)
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Skill gap analysis not found or access denied."
            )
        return analysis
