from datetime import datetime, timezone
import logging
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.achievement_repository import AchievementRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.resume_repository import ResumeRepository
from app.repositories.github_repository import GitHubRepository
from app.repositories.leetcode_repository import LeetCodeRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.readiness_repository import ReadinessRepository
from app.repositories.roadmap_repository import RoadmapRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.progress_repository import ProgressRepository
from app.repositories.interview_repository import InterviewRepository
from app.repositories.communication_repository import CommunicationRepository

from app.engines.achievement_engine import AchievementEngine
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class AchievementService:
    """Service orchestrating achievement evaluation, unlocks, notifications, and user stats."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self.achievement_repo = AchievementRepository(db)
        self.notification_service = NotificationService(db)
        self.engine = AchievementEngine()

        # Telemetry repos
        self.profile_repo = ProfileRepository(db)
        self.resume_repo = ResumeRepository(db)
        self.github_repo = GitHubRepository(db)
        self.leetcode_repo = LeetCodeRepository(db)
        self.project_repo = ProjectRepository(db)
        self.readiness_repo = ReadinessRepository(db)
        self.roadmap_repo = RoadmapRepository(db)
        self.task_repo = TaskRepository(db)
        self.progress_repo = ProgressRepository(db)
        self.interview_repo = InterviewRepository(db)
        self.comm_repo = CommunicationRepository(db)

    async def _build_telemetry_context(self, user_id: str) -> Dict[str, Any]:
        """Fetch student telemetry across modules."""
        profile = await self.profile_repo.get_by_user_id(user_id) or {}
        resume = await self.resume_repo.find_active_by_user(user_id) or {}
        github = await self.github_repo.find_by_user_id(user_id) or {}
        leetcode = await self.leetcode_repo.find_by_user_id(user_id) or {}
        projects = await self.project_repo.find_by_user_id(user_id) or []
        readiness = await self.readiness_repo.get_latest_by_user(user_id) or {}
        roadmap = await self.roadmap_repo.get_active_by_user_id(user_id) or {}
        tasks = await self.task_repo.get_all_by_user(user_id) or []
        progress = await self.progress_repo.get_by_user_id(user_id) or {}
        interviews = await self.interview_repo.get_history_by_user_id(user_id, limit=50) or []
        communication = await self.comm_repo.get_history_by_user_id(user_id, limit=50) or []

        return {
            "profile": profile,
            "resume": resume,
            "github": github,
            "leetcode": leetcode,
            "projects": projects,
            "readiness": readiness,
            "roadmap": roadmap,
            "tasks": tasks,
            "progress": progress,
            "interviews": interviews,
            "communication": communication,
        }

    async def evaluate_and_unlock(self, user_id: str) -> List[Dict[str, Any]]:
        """Evaluate achievements for user, save newly unlocked ones to DB, and emit notifications."""
        definitions = await self.achievement_repo.get_all_definitions()
        unlocked_docs = await self.achievement_repo.get_user_achievements(user_id)
        unlocked_codes = [u.get("code") for u in unlocked_docs if u.get("code")]

        context = await self._build_telemetry_context(user_id)
        evaluated = self.engine.evaluate_user_achievements(definitions, unlocked_codes, context)

        newly_unlocked = []
        for item in evaluated:
            if item.get("is_newly_unlocked"):
                save_data = {
                    "achievement_id": str(item.get("id")),
                    "code": item.get("code"),
                    "points": item.get("xp", 100),
                    "current_count": item.get("currentCount"),
                    "required_count": item.get("requiredCount"),
                    "progress_percentage": item.get("progressPercentage", 100.0),
                    "metadata": {
                        "title": item.get("title"),
                        "category": item.get("category"),
                    },
                }
                saved = await self.achievement_repo.unlock_achievement(user_id, save_data)
                if saved:
                    newly_unlocked.append(item)
                    # Trigger notification for unlocked achievement
                    await self.notification_service.create_notification(
                        user_id=user_id,
                        notif_type="achievement",
                        title=f"Achievement Unlocked: {item.get('title')}",
                        message=f"Congratulations! You earned the {item.get('title')} badge (+{item.get('xp', 100)} XP).",
                        priority="normal",
                        action_type="achievement",
                        action_id=item.get("code"),
                        action_route=item.get("route") or "/achievements",
                    )

        return newly_unlocked

    async def get_user_achievements_with_progress(self, user_id: str) -> Dict[str, Any]:
        """Fetch all achievements formatted with user progress and calculated summary stats."""
        # 1. Trigger evaluation first
        await self.evaluate_and_unlock(user_id)

        # 2. Fetch definitions & user unlocks
        definitions = await self.achievement_repo.get_all_definitions()
        unlocked_docs = await self.achievement_repo.get_user_achievements(user_id)
        unlocked_codes = [u.get("code") for u in unlocked_docs if u.get("code")]

        context = await self._build_telemetry_context(user_id)
        evaluated = self.engine.evaluate_user_achievements(definitions, unlocked_codes, context)

        # 3. Calculate summary stats including daily bonus XP
        daily_xp = await self.achievement_repo.get_total_daily_xp(user_id)
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        is_daily_claimed = await self.achievement_repo.has_claimed_daily(user_id, today_str)

        unlocked_count = len([a for a in evaluated if a.get("unlocked")])
        total_count = len(evaluated)
        earned_xp = sum([a.get("xp", 100) for a in evaluated if a.get("unlocked")]) + daily_xp
        total_xp = 3000
        level = max(1, (earned_xp // 300) + 1)
        level_title = "Placement Ready SDE" if level >= 6 else ("Active Competitor" if level >= 5 else "Initiate")
        xp_in_level = earned_xp % 300
        xp_remaining = 300 - xp_in_level

        stats = {
            "unlockedCount": unlocked_count,
            "totalCount": total_count,
            "earnedXp": earned_xp,
            "totalXp": total_xp,
            "level": level,
            "levelTitle": level_title,
            "xpInCurrentLevel": xp_in_level,
            "xpRemaining": xp_remaining,
            "completionPercentage": round((unlocked_count / max(1, total_count)) * 100),
            "isDailyClaimed": is_daily_claimed,
        }

        return {
            "achievements": evaluated,
            "stats": stats,
        }

    async def claim_daily_xp(self, user_id: str, points: int = 50) -> Dict[str, Any]:
        """Claim daily bonus XP for user."""
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        already_claimed = await self.achievement_repo.has_claimed_daily(user_id, today_str)
        if already_claimed:
            return {"success": False, "message": "Daily bonus already claimed for today.", "points": 0}

        await self.achievement_repo.record_daily_claim(user_id, today_str, points)
        return {"success": True, "message": f"+{points} Daily XP successfully claimed!", "points": points}

    async def get_unlocked_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """Fetch only unlocked achievements for user."""
        res = await self.get_user_achievements_with_progress(user_id)
        return [a for a in res.get("achievements", []) if a.get("unlocked")]

    async def get_achievement_by_id(self, achievement_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch single achievement details for user."""
        res = await self.get_user_achievements_with_progress(user_id)
        for a in res.get("achievements", []):
            if str(a.get("id")) == str(achievement_id) or a.get("code") == str(achievement_id):
                return a
        return None
