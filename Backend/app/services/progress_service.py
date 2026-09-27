import logging
from datetime import datetime, date, timedelta, timezone
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.repositories.progress_repository import ProgressRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.roadmap_repository import RoadmapRepository

logger = logging.getLogger(__name__)


class ProgressService:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.progress_repo = ProgressRepository(db)
        self.task_repo = TaskRepository(db)
        self.roadmap_repo = RoadmapRepository(db)

    async def get_progress(self, user_id: str) -> Dict[str, Any]:
        """Fetch current progress or recalculate if not initialized."""
        record = await self.progress_repo.get_by_user_id(user_id)
        if not record:
            return await self.recalculate_progress(user_id)
        return record

    async def recalculate_progress(self, user_id: str) -> Dict[str, Any]:
        """Calculate exact progress metrics from stored task records."""
        tasks = await self.task_repo.get_all_by_user(user_id, limit=2000)
        active_roadmap = await self.roadmap_repo.get_active_by_user_id(user_id)
        roadmap_id = active_roadmap.get("roadmap_id") or active_roadmap.get("_id") if active_roadmap else None

        total_tasks = len(tasks)
        completed_tasks = [t for t in tasks if t.get("status") == "completed"]
        pending_tasks = [t for t in tasks if t.get("status") in ("pending", "in_progress")]
        skipped_tasks = [t for t in tasks if t.get("status") == "skipped"]

        completed_count = len(completed_tasks)
        pending_count = len(pending_tasks)
        skipped_count = len(skipped_tasks)

        completion_pct = round((completed_count / total_tasks * 100.0), 1) if total_tasks > 0 else 0.0

        # Roadmap completion percentage
        roadmap_tasks = [t for t in tasks if t.get("roadmap_id") == roadmap_id] if roadmap_id else tasks
        roadmap_completed = [t for t in roadmap_tasks if t.get("status") == "completed"]
        roadmap_completion_pct = round((len(roadmap_completed) / len(roadmap_tasks) * 100.0), 1) if roadmap_tasks else 0.0

        # Skill progress calculation
        skill_totals: Dict[str, int] = {}
        skill_completed: Dict[str, int] = {}
        for t in tasks:
            skill = t.get("skill") or t.get("category") or "General"
            skill_totals[skill] = skill_totals.get(skill, 0) + 1
            if t.get("status") == "completed":
                skill_completed[skill] = skill_completed.get(skill, 0) + 1

        skill_progress: Dict[str, float] = {}
        for skill, total in skill_totals.items():
            done = skill_completed.get(skill, 0)
            skill_progress[skill] = round((done / total * 100.0), 1)

        # Weekly and daily completion breakdown
        daily_map: Dict[str, Dict[str, int]] = {}
        for t in tasks:
            d_str = t.get("date") or datetime.now(timezone.utc).strftime("%Y-%m-%d")
            if d_str not in daily_map:
                daily_map[d_str] = {"total": 0, "completed": 0}
            daily_map[d_str]["total"] += 1
            if t.get("status") == "completed":
                daily_map[d_str]["completed"] += 1

        daily_completion: List[Dict[str, Any]] = [
            {
                "date": d_str,
                "total": stats["total"],
                "completed": stats["completed"],
                "percentage": round((stats["completed"] / stats["total"] * 100.0), 1) if stats["total"] > 0 else 0.0
            }
            for d_str, stats in sorted(daily_map.items())
        ]

        # Streak calculation
        existing = await self.progress_repo.get_by_user_id(user_id) or {}
        curr_streak, max_streak, last_date = self._calculate_streak(daily_completion, existing)

        data = {
            "user_id": user_id,
            "roadmap_id": roadmap_id,
            "total_tasks": total_tasks,
            "completed_tasks": completed_count,
            "pending_tasks": pending_count,
            "skipped_tasks": skipped_count,
            "completion_percentage": completion_pct,
            "roadmap_completion_percentage": roadmap_completion_pct,
            "weekly_completion": [],
            "daily_completion": daily_completion[-14:],  # Last 14 days
            "skill_progress": skill_progress,
            "current_streak": curr_streak,
            "longest_streak": max_streak,
            "last_active_date": last_date,
            "completed_milestones": [],
        }

        # Sync roadmap progress
        if active_roadmap and roadmap_id:
            await self.roadmap_repo.update(roadmap_id, user_id, {"progress": roadmap_completion_pct})

        return await self.progress_repo.save_or_update(user_id, data)

    def _calculate_streak(
        self, daily_completion: List[Dict[str, Any]], existing: Dict[str, Any]
    ) -> tuple[int, int, Optional[str]]:
        """Calculate continuous activity streak across days."""
        active_dates = sorted(
            [item["date"] for item in daily_completion if item.get("completed", 0) > 0]
        )
        if not active_dates:
            return 0, existing.get("longest_streak", 0), existing.get("last_active_date")

        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        yesterday_str = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")

        last_active = active_dates[-1]
        date_objs = [datetime.strptime(d, "%Y-%m-%d").date() for d in active_dates]
        
        # Calculate max streak
        current = 1
        longest = 1
        for i in range(1, len(date_objs)):
            diff = (date_objs[i] - date_objs[i - 1]).days
            if diff == 1:
                current += 1
            elif diff > 1:
                current = 1
            if current > longest:
                longest = current

        # Current streak check
        current_streak = 0
        if last_active in (today_str, yesterday_str):
            rev_dates = sorted(list(set(date_objs)), reverse=True)
            streak_count = 1
            for i in range(len(rev_dates) - 1):
                if (rev_dates[i] - rev_dates[i + 1]).days == 1:
                    streak_count += 1
                else:
                    break
            current_streak = streak_count

        max_streak = max(longest, existing.get("longest_streak", 0))
        return current_streak, max_streak, last_active

    async def get_streak(self, user_id: str) -> Dict[str, Any]:
        progress = await self.get_progress(user_id)
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return {
            "current_streak": progress.get("current_streak", 0),
            "longest_streak": progress.get("longest_streak", 0),
            "last_active_date": progress.get("last_active_date"),
            "is_active_today": progress.get("last_active_date") == today_str
        }

    async def get_summary(self, user_id: str) -> Dict[str, Any]:
        p = await self.get_progress(user_id)
        skill_prog = p.get("skill_progress", {})
        top_skills = sorted(skill_prog.keys(), key=lambda k: skill_prog[k], reverse=True)[:5]
        return {
            "user_id": user_id,
            "total_tasks": p.get("total_tasks", 0),
            "completed_tasks": p.get("completed_tasks", 0),
            "completion_percentage": p.get("completion_percentage", 0.0),
            "current_streak": p.get("current_streak", 0),
            "longest_streak": p.get("longest_streak", 0),
            "roadmap_completion_percentage": p.get("roadmap_completion_percentage", 0.0),
            "top_skills_completed": top_skills,
        }
