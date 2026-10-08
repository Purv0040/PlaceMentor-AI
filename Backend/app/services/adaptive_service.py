import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.adaptive_repository import AdaptiveRepository
from app.repositories.roadmap_repository import RoadmapRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.progress_repository import ProgressRepository
from app.services.task_service import TaskService
from app.integrations.ai_client import AIClient, AIClientError
from app.utils.dates import get_today_date_str, APP_TIMEZONE

logger = logging.getLogger(__name__)


class AdaptiveService:
    def __init__(self, db: AsyncIOMotorDatabase, ai_client: Optional[AIClient] = None) -> None:
        self.adaptive_repo = AdaptiveRepository(db)
        self.roadmap_repo = RoadmapRepository(db)
        self.task_repo = TaskRepository(db)
        self.progress_repo = ProgressRepository(db)
        self.task_service = TaskService(db, ai_client=ai_client)
        self.ai_client = ai_client or AIClient()

    async def _resolve_roadmap(self, user_id: str, roadmap_id: Optional[str] = None) -> Dict[str, Any]:
        """Validate and resolve active or requested roadmap for the authenticated user."""
        if roadmap_id:
            roadmap = await self.roadmap_repo.get_by_id(roadmap_id)
            if not roadmap:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found.")
            if str(roadmap.get("user_id")) != str(user_id):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this roadmap.")
            return roadmap

        active_roadmap = await self.roadmap_repo.get_active_by_user_id(user_id)
        if not active_roadmap:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active roadmap found for user.")
        return active_roadmap

    async def get_summary(self, user_id: str, roadmap_id: Optional[str] = None) -> Dict[str, Any]:
        """Fetch adaptive planner summary and current recommendation status dynamically."""
        try:
            target_roadmap = await self._resolve_roadmap(user_id, roadmap_id=roadmap_id)
        except HTTPException:
            target_roadmap = None

        if not target_roadmap:
            return {
                "status": "balanced",
                "has_pending_recommendation": False,
                "latest_recommendation": None,
                "metrics": {
                    "roadmap_id": None,
                    "total_tasks": 0,
                    "total_completed": 0,
                    "total_pending": 0,
                    "total_skipped": 0,
                    "total_overdue": 0,
                    "completion_rate": 0.0,
                    "current_streak": 0,
                },
            }

        target_roadmap_id = str(target_roadmap.get("roadmap_id") or target_roadmap.get("_id"))
        latest_rec = await self.adaptive_repo.get_latest_by_user_id(
            user_id, roadmap_id=target_roadmap_id
        )

        query: Dict[str, Any] = {"user_id": str(user_id)}
        if ObjectId.is_valid(target_roadmap_id):
            query["$or"] = [
                {"roadmap_id": str(target_roadmap_id)},
                {"roadmap_id": ObjectId(target_roadmap_id)},
            ]
        else:
            query["roadmap_id"] = str(target_roadmap_id)

        raw_tasks = await self.task_repo.collection.find(query).sort("date", 1).to_list(length=5000)
        tasks = self.task_repo._serialize_documents(raw_tasks)

        progress = await self.progress_repo.get_by_user_id(user_id) or {}
        today_date = datetime.now(APP_TIMEZONE).date()

        completed_tasks = [t for t in tasks if t.get("status") == "completed"]
        skipped_tasks = [t for t in tasks if t.get("status") == "skipped"]
        pending_tasks = [t for t in tasks if t.get("status") in ("pending", "in_progress")]

        overdue_tasks = []
        for t in pending_tasks:
            d_str = t.get("date")
            if d_str and isinstance(d_str, str):
                try:
                    t_date = datetime.strptime(d_str[:10], "%Y-%m-%d").date()
                    if t_date < today_date:
                        overdue_tasks.append(t)
                except Exception:
                    pass

        total_tasks = len(tasks)
        completion_rate = round(len(completed_tasks) / total_tasks * 100.0, 1) if total_tasks else 0.0

        # Actionable recommendation determination
        is_actionable = False
        if latest_rec and not latest_rec.get("applied", False):
            trigger = latest_rec.get("trigger")
            has_changes = bool(latest_rec.get("changes"))
            has_affected_skills = bool(latest_rec.get("affected_skills"))
            # If historical record claims overdue tasks but actual overdue count is 0, it is superseded
            if trigger == "overdue_tasks" and len(overdue_tasks) == 0:
                latest_rec["lifecycle_status"] = "superseded"
                latest_rec["is_actionable"] = False
            elif latest_rec.get("lifecycle_status") == "superseded":
                latest_rec["is_actionable"] = False
            elif trigger in ("overdue_tasks", "repeated_skipped_tasks") or has_changes or has_affected_skills:
                is_actionable = True
                latest_rec["is_actionable"] = True
                latest_rec["lifecycle_status"] = "pending"
            else:
                latest_rec["is_actionable"] = False
                latest_rec["lifecycle_status"] = "informational"

        has_overdue_tasks = len(overdue_tasks) > 0
        has_high_skipped = len(skipped_tasks) >= 3

        if has_overdue_tasks or has_high_skipped or is_actionable:
            status_value = "needs_rebalance"
            has_pending_rec = is_actionable or has_overdue_tasks or has_high_skipped
        elif latest_rec and latest_rec.get("trigger") == "fast_progress" and not latest_rec.get("applied", False) and latest_rec.get("lifecycle_status") != "superseded":
            status_value = "ahead_of_schedule"
            has_pending_rec = True
        elif completion_rate >= 80.0 and total_tasks > 10:
            status_value = "ahead_of_schedule"
            has_pending_rec = False
        else:
            status_value = "balanced"
            has_pending_rec = False

        return {
            "status": status_value,
            "has_pending_recommendation": has_pending_rec,
            "latest_recommendation": latest_rec,
            "metrics": {
                "roadmap_id": target_roadmap_id,
                "total_tasks": total_tasks,
                "total_completed": len(completed_tasks),
                "total_pending": len(pending_tasks),
                "total_skipped": len(skipped_tasks),
                "total_overdue": len(overdue_tasks),
                "completion_rate": completion_rate,
                "current_streak": progress.get("current_streak", 0),
            },
        }

    async def get_recommendations(
        self, user_id: str, roadmap_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fetch recommendations strictly scoped to the authenticated user with explicit lifecycle status."""
        recs = await self.adaptive_repo.get_by_user_id(user_id, roadmap_id=roadmap_id, limit=50)
        if not recs:
            return []

        # Scoped tasks check for validating older records
        target_roadmap_id = roadmap_id or recs[0].get("roadmap_id")
        query: Dict[str, Any] = {"user_id": str(user_id)}
        if target_roadmap_id:
            if ObjectId.is_valid(target_roadmap_id):
                query["$or"] = [{"roadmap_id": str(target_roadmap_id)}, {"roadmap_id": ObjectId(target_roadmap_id)}]
            else:
                query["roadmap_id"] = str(target_roadmap_id)

        raw_tasks = await self.task_repo.collection.find(query).to_list(length=5000)
        tasks = self.task_repo._serialize_documents(raw_tasks)
        today_date = datetime.now(APP_TIMEZONE).date()

        overdue_count = 0
        for t in tasks:
            if t.get("status") in ("pending", "in_progress"):
                d_str = t.get("date")
                if d_str and isinstance(d_str, str):
                    try:
                        if datetime.strptime(d_str[:10], "%Y-%m-%d").date() < today_date:
                            overdue_count += 1
                    except Exception:
                        pass

        # Dynamic lifecycle tagging for each recommendation
        for i, rec in enumerate(recs):
            if rec.get("applied") is True:
                rec["lifecycle_status"] = "applied"
                rec["is_actionable"] = False
            elif i > 0:
                # Any unapplied recommendation older than the latest is superseded
                rec["lifecycle_status"] = "superseded"
                rec["is_actionable"] = False
            else:
                # Latest unapplied recommendation
                trigger = rec.get("trigger")
                has_changes = bool(rec.get("changes"))
                # If it claimed overdue tasks but currently overdue count is 0, mark superseded
                if trigger == "overdue_tasks" and overdue_count == 0:
                    rec["lifecycle_status"] = "superseded"
                    rec["is_actionable"] = False
                elif rec.get("lifecycle_status") == "superseded":
                    rec["is_actionable"] = False
                elif trigger in ("overdue_tasks", "repeated_skipped_tasks") or has_changes:
                    rec["lifecycle_status"] = "pending"
                    rec["is_actionable"] = True
                else:
                    rec["lifecycle_status"] = "informational"
                    rec["is_actionable"] = False

        return recs

    async def recalculate_adaptation(
        self, user_id: str, roadmap_id: Optional[str] = None, force: bool = False
    ) -> Dict[str, Any]:
        """Examine task completion history dynamically and determine if roadmap needs adaptation."""
        target_roadmap = await self._resolve_roadmap(user_id, roadmap_id=roadmap_id)
        target_roadmap_id = str(target_roadmap.get("roadmap_id") or target_roadmap.get("_id"))

        query: Dict[str, Any] = {"user_id": str(user_id)}
        if ObjectId.is_valid(target_roadmap_id):
            query["$or"] = [
                {"roadmap_id": str(target_roadmap_id)},
                {"roadmap_id": ObjectId(target_roadmap_id)},
            ]
        else:
            query["roadmap_id"] = str(target_roadmap_id)

        raw_tasks = await self.task_repo.collection.find(query).sort("date", 1).to_list(length=5000)
        tasks = self.task_repo._serialize_documents(raw_tasks)

        progress = await self.progress_repo.get_by_user_id(user_id) or {}
        today_date = datetime.now(APP_TIMEZONE).date()

        completed_tasks = [t for t in tasks if t.get("status") == "completed"]
        skipped_tasks = [t for t in tasks if t.get("status") == "skipped"]
        pending_tasks = [t for t in tasks if t.get("status") in ("pending", "in_progress")]

        # Overdue tasks: pending/in_progress tasks with scheduled date strictly before today
        overdue_tasks = []
        for t in pending_tasks:
            d_str = t.get("date")
            if d_str and isinstance(d_str, str):
                try:
                    t_date = datetime.strptime(d_str[:10], "%Y-%m-%d").date()
                    if t_date < today_date:
                        overdue_tasks.append(t)
                except Exception:
                    pass

        # Planned tasks through today
        planned_tasks_through_today = []
        for t in tasks:
            d_str = t.get("date")
            if d_str and isinstance(d_str, str):
                try:
                    t_date = datetime.strptime(d_str[:10], "%Y-%m-%d").date()
                    if t_date <= today_date:
                        planned_tasks_through_today.append(t)
                except Exception:
                    pass

        total_tasks = len(tasks)
        completion_rate = round(len(completed_tasks) / total_tasks * 100.0, 1) if total_tasks else 0.0

        # Decision engine
        if len(overdue_tasks) > 0:
            trigger = "overdue_tasks"
            recommendation = f"Consolidate {len(overdue_tasks)} overdue tasks into a dedicated remediation day."
            reason = f"{len(overdue_tasks)} overdue tasks require rebalancing."
            affected_skills = list(dict.fromkeys(
                t.get("skill") or t.get("category")
                for t in overdue_tasks
                if (t.get("skill") or t.get("category"))
            ))[:3]
            changes = [
                {"type": "rebalance", "description": f"Rescheduled {len(overdue_tasks)} overdue topics into upcoming catch-up window."}
            ]
        elif len(skipped_tasks) >= 3:
            trigger = "repeated_skipped_tasks"
            recommendation = "Rebalance upcoming workload and split heavy topics into smaller daily tasks."
            reason = f"You have {len(skipped_tasks)} skipped tasks. Reducing daily duration budget to prevent backlog accumulation."
            affected_skills = list(dict.fromkeys(
                t.get("skill") or t.get("category")
                for t in skipped_tasks
                if (t.get("skill") or t.get("category"))
            ))[:3]
            changes = [
                {"type": "reschedule", "description": "Extended deadlines for skipped topics."},
                {"type": "workload_reduction", "description": "Adjusted daily target limit to prevent backlog accumulation."}
            ]
        elif len(completed_tasks) >= 5 and (len(completed_tasks) > len(planned_tasks_through_today) * 1.2 or (completion_rate >= 75.0 and total_tasks > 10)):
            trigger = "fast_progress"
            recommendation = "Accelerate roadmap timeline by inserting advanced System Design and Mock Interview modules early."
            reason = f"Completion velocity ({len(completed_tasks)} completed) is ahead of planned trajectory."
            affected_skills = ["System Design", "Mock Interview"]
            changes = [
                {"type": "acceleration", "description": "Unlocked Phase 3 advanced modules early."}
            ]
        else:
            trigger = "routine_check"
            recommendation = "Roadmap schedule is optimal and balanced."
            reason = f"Your learning pace matches the target roadmap trajectory."
            affected_skills = []
            changes = []

        is_actionable = (trigger in ("overdue_tasks", "repeated_skipped_tasks") or len(changes) > 0)
        lifecycle_status = "pending" if is_actionable else "informational"

        # Idempotency check when force is False
        if not force:
            latest_unapplied = await self.adaptive_repo.get_latest_unapplied_by_user_id(
                user_id, roadmap_id=target_roadmap_id
            )
            if latest_unapplied and latest_unapplied.get("trigger") == trigger:
                latest_unapplied["is_actionable"] = is_actionable
                latest_unapplied["lifecycle_status"] = lifecycle_status
                return latest_unapplied

        # Mark all previous unapplied recommendations as superseded
        await self.adaptive_repo.mark_superseded_unapplied(user_id, target_roadmap_id)

        event_data = {
            "user_id": str(user_id),
            "roadmap_id": str(target_roadmap_id),
            "trigger": trigger,
            "recommendation": recommendation,
            "reason": reason,
            "affected_skills": affected_skills,
            "changes": changes,
            "applied": False,
            "lifecycle_status": lifecycle_status,
            "is_actionable": is_actionable,
            "created_at": datetime.now(timezone.utc),
        }

        return await self.adaptive_repo.create_event(event_data)

    async def apply_adaptation(
        self,
        user_id: str,
        adaptation_id: Optional[str] = None,
        roadmap_id: Optional[str] = None,
        accept_changes: bool = True,
    ) -> Dict[str, Any]:
        """Safely apply adaptation recommendations to the active roadmap/tasks with strict lifecycle validation."""
        event: Optional[Dict[str, Any]] = None

        if adaptation_id:
            event = await self.adaptive_repo.get_by_id(adaptation_id, user_id)
            if not event:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Adaptation event not found.")
            if str(event.get("user_id")) != str(user_id):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to apply this adaptation.")
        else:
            event = await self.adaptive_repo.get_latest_unapplied_by_user_id(
                user_id, roadmap_id=roadmap_id
            )
            if not event:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No actionable pending adaptation recommendation found to apply.",
                )

        target_roadmap_id = str(event.get("roadmap_id"))
        if roadmap_id and target_roadmap_id != str(roadmap_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Adaptation recommendation does not belong to the specified roadmap.",
            )

        roadmap = await self.roadmap_repo.get_by_id(target_roadmap_id)
        if not roadmap:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target roadmap not found.")
        if str(roadmap.get("user_id")) != str(user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this roadmap.")

        # --- Strict Lifecycle Validation BEFORE Any Mutation ---

        # 1. Genuinely already applied -> return idempotent already_applied
        if event.get("lifecycle_status") == "applied" or (event.get("applied") is True and event.get("applied_at") is not None):
            return {
                "status": "already_applied",
                "applied_event": event,
                "message": "Adaptation recommendation was already applied.",
            }

        # 2. Superseded -> 409 Conflict
        if event.get("lifecycle_status") == "superseded":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Adaptation recommendation is superseded and cannot be applied.",
            )

        # 3. Informational / Non-actionable -> 409 Conflict
        if (
            event.get("lifecycle_status") == "informational"
            or not event.get("is_actionable")
            or not event.get("changes")
            or event.get("trigger") in ("routine_check", "on_track")
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Informational recommendation does not contain an actionable adaptation.",
            )

        # 4. Must be pending, actionable, and not applied
        if event.get("lifecycle_status") != "pending" or not event.get("is_actionable") or event.get("applied") is True:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Adaptation recommendation is not in a valid pending state to be applied.",
            )

        # --- Mutation only occurs after ALL validation passes ---

        if not accept_changes:
            # User dismissed the adaptation without altering task dates
            event["is_actionable"] = False
            event["lifecycle_status"] = "superseded"
            doc_id = event.get("_id") or event.get("id")
            if doc_id:
                query_filter = {"_id": ObjectId(doc_id)} if ObjectId.is_valid(doc_id) else {"_id": str(doc_id)}
                await self.adaptive_repo.collection.update_one(
                    query_filter,
                    {"$set": {"is_actionable": False, "lifecycle_status": "superseded"}},
                )
            return {
                "status": "dismissed",
                "applied_event": event,
                "message": "Adaptation changes were dismissed without altering the schedule.",
            }

        today_str = get_today_date_str()

        # If overdue tasks triggered the adaptation, safely move them to today
        if event.get("trigger") == "overdue_tasks":
            query: Dict[str, Any] = {
                "user_id": str(user_id),
                "status": {"$in": ["pending", "in_progress"]},
                "date": {"$lt": today_str},
            }
            if ObjectId.is_valid(target_roadmap_id):
                query["$or"] = [
                    {"roadmap_id": str(target_roadmap_id)},
                    {"roadmap_id": ObjectId(target_roadmap_id)},
                ]
            else:
                query["roadmap_id"] = str(target_roadmap_id)

            await self.task_repo.collection.update_many(
                query,
                {"$set": {"date": today_str, "updated_at": datetime.now(timezone.utc)}},
            )

        # Update roadmap notice and adaptation timestamp
        now_utc = datetime.now(timezone.utc)
        if roadmap:
            await self.roadmap_repo.update(
                target_roadmap_id,
                user_id,
                {
                    "last_adapted_at": now_utc,
                    "adaptive_notice": {
                        "is_adapted": True,
                        "reason": event.get("reason"),
                        "trigger": event.get("trigger"),
                        "adapted_at": now_utc.strftime("%Y-%m-%d %H:%M:%S"),
                    },
                },
            )

        applied_event = await self.adaptive_repo.mark_applied(event["id"], user_id)
        # Mark any other unapplied events for this roadmap as superseded
        await self.adaptive_repo.mark_superseded_unapplied(user_id, target_roadmap_id, exclude_event_id=event["id"])

        return {
            "status": "success",
            "applied_event": applied_event,
            "message": "Roadmap schedule and daily tasks successfully rebalanced.",
        }


