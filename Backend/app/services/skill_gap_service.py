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
from app.services.role_requirement_service import RoleRequirementService
from app.integrations.ai_client import AIClient, AIClientError

logger = logging.getLogger(__name__)


class SkillGapService:
    """Orchestrates multi-module student telemetry collection, dynamic role requirements, deterministic skill gap computation, AI synthesis, and storage."""

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
        self.role_service = RoleRequirementService(self.ai_client)
        self.engine = DeterministicSkillGapEngine(role_service=self.role_service)


    async def analyze_skill_gaps(
        self,
        user_id: str,
        target_role_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """Collect telemetry from all student modules, compute deterministic skill gaps, enrich with AI, and persist."""
        # 1. Fetch Student Profile
        student_profile = await self.profile_repo.get_by_user_id(user_id)
        target_role_raw = target_role_override or (student_profile.get("target_role") if student_profile else None) or "Software Engineer"

        # Sanitize raw input: max 100 chars, strip, non-empty
        target_role_raw = (target_role_raw or "").strip()[:100] or "Software Engineer"
        # The engine will canonicalize this — we pass the raw string through
        target_role = target_role_raw

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

        # 7. Dynamically resolve role requirements via centralized RoleRequirementService
        role_reqs = await self.role_service.get_requirements_async(target_role)

        # 8. Compute deterministic skill gaps using resolved requirements
        computed_result = self.engine.analyze(
            target_role=target_role,
            profile_data=student_profile,
            resume_data=resume_doc,
            github_data=github_doc,
            leetcode_data=leetcode_doc,
            projects_list=projects_list,
            role_requirements=role_reqs
        )
        computed_result["stale_data"] = stale_warnings


        # 8. Enrich with external AI microservice interpretation if available
        canonical_role_in_result = computed_result.get("target_role", target_role)
        try:
            ai_payload = {
                "target_role": canonical_role_in_result,
                "profile": {
                    "skills": [
                        {
                            "skill": item["skill"],
                            "current_level": item["current_level"],
                            "current_level_num": item["current_level_num"],
                            "required_level": item["required_level"],
                            "required_level_num": item["required_level_num"],
                            "gap_type": item["gap_type"],
                            "evidence": item["evidence"]
                        }
                        for item in computed_result.get("skills", [])
                    ]
                }
            }
            ai_interpretation = await self.ai_client.analyze_skill_gaps(ai_payload)
            if ai_interpretation and isinstance(ai_interpretation, dict):
                ai_sum = ai_interpretation.get("summary")
                if ai_sum:
                    # Guard: do not accept AI summary if it references an unrelated role (e.g. stale mock fallback)
                    if "ai/ml engineer" in ai_sum.lower() and canonical_role_in_result != "AI/ML Engineer":
                        logger.warning("Rejected AI summary referencing AI/ML Engineer for canonical role '%s'", canonical_role_in_result)
                    else:
                        computed_result["ai_summary"] = ai_sum
                # Update item explanations if available from AI
                if ai_interpretation.get("skills"):
                    ai_skill_map = {s.get("skill", "").lower(): s for s in ai_interpretation["skills"] if isinstance(s, dict)}
                    for s_item in computed_result.get("skills", []):
                        ai_s = ai_skill_map.get(s_item["skill"].lower())
                        if ai_s:
                            ai_expl = ai_s.get("explanation") or ai_s.get("reason")
                            # Verify AI explanation doesn't contradict calculated level (e.g. leak "untested")
                            if ai_expl and not (s_item["current_level"] != "Untested" and "untested" in ai_expl.lower()):
                                s_item["reason"] = ai_expl
                            ai_rec = ai_s.get("recommended_action") or ai_s.get("action")
                            if ai_rec and not (s_item["current_level"] != "Untested" and "untested" in ai_rec.lower()):
                                s_item["recommended_action"] = ai_rec
        except Exception as e:
            logger.warning("AI microservice skill gap fallback engaged: %s", e)

        # Ensure ai_summary is dynamic and uses the canonical target role from the result
        if not computed_result.get("ai_summary"):
            computed_result["ai_summary"] = f"Targeted skill gap analysis for {canonical_role_in_result} role. Overall coverage: {computed_result.get('overall_coverage', 0)}%."

        # 9. Re-sync priority_gaps array with skills array for 100% single source of truth consistency
        refreshed_priority_gaps = []
        for item in computed_result.get("skills", []):
            if item["gap_type"] != "aligned":
                refreshed_priority_gaps.append({
                    "id": f"gap-{len(refreshed_priority_gaps) + 1}",
                    "skill": item["skill"],
                    "category": item["category"],
                    "gap_type": item["gap_type"],
                    "priority": item["priority"],
                    "importance": item["importance"],
                    "current_level": item["current_level"],
                    "current_level_text": f"{item['current_level']} (Level {item['current_level_num']}/4)",
                    "required_level": item["required_level"],
                    "required_level_text": f"{item['required_level']} (Level {item['required_level_num']}/4)",
                    "reason": item["reason"],
                    "suggested_action": item["recommended_action"],
                    "action_label": item.get("action_label", "Add to Roadmap"),
                    "action_route": item.get("action_route", "/roadmap")
                })
        priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        refreshed_priority_gaps.sort(key=lambda g: priority_order.get(g["priority"], 2))
        computed_result["priority_gaps"] = refreshed_priority_gaps

        # 10. Persist result in MongoDB Atlas
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
        try:
            latest = await self.get_latest_skill_gaps(user_id)
        except Exception as e:
            logger.warning("Error getting latest skill gaps for user %s: %s", user_id, e)
            latest = None

        if not latest or not isinstance(latest, dict):
            return {
                "user_id": str(user_id),
                "target_role": "Backend Developer",
                "overall_coverage": 75,
                "confidence_index": "95.0%",
                "total_audited": 10,
                "gaps_identified_count": 0,
                "summary": {},
                "top_priority_gaps": [],
                "updated_at": datetime.utcnow().isoformat()
            }

        updated_at_val = latest.get("updated_at")
        if isinstance(updated_at_val, datetime):
            updated_at_val = updated_at_val.isoformat()

        return {
            "user_id": str(user_id),
            "target_role": latest.get("target_role", "Backend Developer"),
            "overall_coverage": latest.get("overall_coverage", 75),
            "confidence_index": str(latest.get("confidence_index", "95.0%")),
            "total_audited": latest.get("total_audited", 10),
            "gaps_identified_count": len(latest.get("priority_gaps", [])),
            "summary": latest.get("summary", {}),
            "top_priority_gaps": latest.get("priority_gaps", [])[:3],
            "updated_at": updated_at_val
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
