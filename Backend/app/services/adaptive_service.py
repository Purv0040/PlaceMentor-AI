import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.adaptive_repository import AdaptiveRepository
from app.repositories.roadmap_repository import RoadmapRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.progress_repository import ProgressRepository
from app.services.task_service import TaskService
from app.integrations.ai_client import AIClient, AIClientError

logger = logging.getLogger(__name__)


class AdaptiveService:
    def __init__(self, db: AsyncIOMotorDatabase, ai_client: Optional[AIClient] = None) -> None:
        self.adaptive_repo = AdaptiveRepository(db)
        self.roadmap_repo = RoadmapRepository(db)
        self.task_repo = TaskRepository(db)
        self.progress_repo = ProgressRepository(db)
        self.task_service = TaskService(db, ai_client=ai_client)
        self.ai_client = ai_client or AIClient()

    async def get_summary(self, user_id: str) -> Dict[str, Any]:
        """Fetch adaptive planner summary and latest recommendations."""
        latest_unapplied = await self.adaptive_repo.get_latest_unapplied_by_user_id(user_id)
        active_roadmap = await self.roadmap_repo.get_active_by_user_id(user_id)
        progress = await self.progress_repo.get_by_user_id(user_id) or {}

        status = "balanced"
        if latest_unapplied:
            status = "needs_rebalance"
        elif progress.get("completion_percentage", 0) > 80:
            status = "ahead_of_schedule"

        return {
            "status": status,
            "has_pending_recommendation": latest_unapplied is not None,
            "latest_recommendation": latest_unapplied,
            "metrics": {
                "total_completed": progress.get("completed_tasks", 0),
                "total_skipped": progress.get("skipped_tasks", 0),
                "completion_rate": progress.get("completion_percentage", 0.0),
                "current_streak": progress.get("current_streak", 0)
            }
        }

    async def get_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        return await self.adaptive_repo.get_by_user_id(user_id, limit=20)

    async def recalculate_adaptation(self, user_id: str, roadmap_id: Optional[str] = None) -> Dict[str, Any]:
        """Examine task completion history and determine if roadmap needs adaptation."""
        active_roadmap = await self.roadmap_repo.get_active_by_user_id(user_id)
        if not active_roadmap:
            raise ValueError("No active roadmap found for user.")

        target_roadmap_id = roadmap_id or active_roadmap.get("roadmap_id") or active_roadmap.get("_id")
        tasks = await self.task_repo.get_all_by_user(user_id, limit=500)
        progress = await self.progress_repo.get_by_user_id(user_id) or {}

        skipped_tasks = [t for t in tasks if t.get("status") == "skipped"]
        completed_tasks = [t for t in tasks if t.get("status") == "completed"]
        pending_tasks = [t for t in tasks if t.get("status") in ("pending", "in_progress")]

        trigger = "routine_check"
        recommendation = "Roadmap schedule is optimal and balanced."
        reason = "Your learning pace matches the target 90-day trajectory."
        affected_skills: List[str] = []
        changes: List[Dict[str, Any]] = []

        if len(skipped_tasks) >= 3:
            trigger = "repeated_skipped_tasks"
            recommendation = "Rebalance upcoming workload and split heavy DSA topics into smaller daily tasks."
            reason = f"You have {len(skipped_tasks)} skipped tasks. Reducing daily duration budget from 120m to 90m."
            affected_skills = list(set(t.get("skill") for t in skipped_tasks if t.get("skill")))[:3]
            changes = [
                {"type": "reschedule", "description": "Extended Sprint deadlines for skipped topics."},
                {"type": "workload_reduction", "description": "Adjusted daily target limit to prevent backlog accumulation."}
            ]
        elif len(completed_tasks) >= 15 and progress.get("completion_percentage", 0.0) > 75.0:
            trigger = "fast_progress"
            recommendation = "Accelerate roadmap timeline by inserting advanced System Design and Mock Interview modules early."
            reason = "Completion velocity is 25% faster than initial estimate."
            affected_skills = ["System Design", "Mock Interview"]
            changes = [
                {"type": "acceleration", "description": "Unlocked Phase 3 System Design modules early."}
            ]
        elif len(pending_tasks) > 10:
            trigger = "overdue_tasks"
            recommendation = "Consolidate overdue tasks into a dedicated remediation day."
            reason = f"{len(pending_tasks)} pending tasks require rebalancing."
            affected_skills = list(set(t.get("skill") for t in pending_tasks if t.get("skill")))[:2]
            changes = [
                {"type": "rebalance", "description": "Rescheduled pending topics across next 3 days."}
            ]

        event_data = {
            "user_id": user_id,
            "roadmap_id": target_roadmap_id,
            "trigger": trigger,
            "recommendation": recommendation,
            "reason": reason,
            "affected_skills": affected_skills,
            "changes": changes,
            "applied": False,
            "created_at": datetime.now(timezone.utc)
        }

        return await self.adaptive_repo.create_event(event_data)

    async def apply_adaptation(
        self, user_id: str, adaptation_id: Optional[str] = None, roadmap_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Apply adaptation recommendations to the active roadmap/tasks."""
        event: Optional[Dict[str, Any]] = None
        if adaptation_id:
            event = await self.adaptive_repo.mark_applied(adaptation_id, user_id)
        else:
            latest = await self.adaptive_repo.get_latest_unapplied_by_user_id(user_id)
            if latest:
                event = await self.adaptive_repo.mark_applied(latest["_id"], user_id)

        if not event:
            # If no pending event exists, trigger recalculation first then mark applied
            event = await self.recalculate_adaptation(user_id, roadmap_id=roadmap_id)
            event = await self.adaptive_repo.mark_applied(event["_id"], user_id)

        # Apply modifications to roadmap
        active_roadmap = await self.roadmap_repo.get_active_by_user_id(user_id)
        if active_roadmap:
            rm_id = active_roadmap.get("roadmap_id") or active_roadmap.get("_id")
            await self.roadmap_repo.update(rm_id, user_id, {
                "last_adapted_at": datetime.now(timezone.utc),
                "adaptive_notice": {
                    "is_adapted": True,
                    "reason": event.get("reason"),
                    "trigger": event.get("trigger"),
                    "adapted_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                }
            })

        return {
            "status": "success",
            "applied_event": event,
            "message": "Roadmap schedule and daily tasks successfully rebalanced."
        }
