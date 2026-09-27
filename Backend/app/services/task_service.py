import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.repositories.task_repository import TaskRepository
from app.repositories.roadmap_repository import RoadmapRepository
from app.services.progress_service import ProgressService
from app.integrations.ai_client import AIClient, AIClientError

logger = logging.getLogger(__name__)


class TaskService:
    def __init__(self, db: AsyncIOMotorDatabase, ai_client: Optional[AIClient] = None) -> None:
        self.task_repo = TaskRepository(db)
        self.roadmap_repo = RoadmapRepository(db)
        self.progress_service = ProgressService(db)
        self.ai_client = ai_client or AIClient()

    async def get_today_tasks(self, user_id: str) -> Dict[str, Any]:
        """Fetch today's tasks or generate initial tasks from active roadmap."""
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        existing_today = await self.task_repo.get_by_user_and_date(user_id, today_str)

        active_roadmap = await self.roadmap_repo.get_active_by_user_id(user_id)
        
        if not existing_today and active_roadmap:
            start_dt = active_roadmap.get("start_date") or datetime.now(timezone.utc)
            if isinstance(start_dt, str):
                try:
                    start_dt = datetime.fromisoformat(start_dt.replace("Z", "+00:00"))
                except Exception:
                    start_dt = datetime.now(timezone.utc)
            
            day_number = max(1, min(90, (datetime.now(timezone.utc).date() - start_dt.date()).days + 1))
            
            # Find tasks in roadmap for this day_number
            all_tasks = active_roadmap.get("all_tasks") or []
            roadmap_id = active_roadmap.get("roadmap_id") or active_roadmap.get("_id")
            
            day_tasks = [t for t in all_tasks if t.get("day") == day_number]
            if not day_tasks and all_tasks:
                # Fallback: take first 2-3 pending tasks from all_tasks
                day_tasks = all_tasks[:3]

            if day_tasks:
                new_db_tasks = []
                for idx, t in enumerate(day_tasks):
                    new_db_tasks.append({
                        "task_id": t.get("id") or f"task_{user_id}_{today_str}_{idx+1}",
                        "user_id": user_id,
                        "roadmap_id": roadmap_id,
                        "date": today_str,
                        "day_number": day_number,
                        "title": t.get("title", "Daily Practice"),
                        "description": t.get("description", "Daily task from placement roadmap"),
                        "category": t.get("category", "General"),
                        "skill": t.get("skill", "Core"),
                        "priority": t.get("priority", "HIGH").upper(),
                        "estimated_minutes": t.get("estimated_minutes", 60),
                        "difficulty": t.get("difficulty", "Intermediate"),
                        "status": "pending",
                        "completion_percentage": 0.0,
                    })
                existing_today = await self.task_repo.create_many(new_db_tasks)

        completed_tasks = [t for t in existing_today if t.get("status") == "completed"]
        pending_tasks = [t for t in existing_today if t.get("status") in ("pending", "in_progress")]
        total_est = sum(t.get("estimated_minutes", 60) for t in existing_today)

        return {
            "date": today_str,
            "day_number": existing_today[0].get("day_number", 1) if existing_today else 1,
            "total_tasks": len(existing_today),
            "completed_tasks": len(completed_tasks),
            "pending_tasks": len(pending_tasks),
            "estimated_total_minutes": total_est,
            "tasks": existing_today,
        }

    async def get_all_tasks(
        self,
        user_id: str,
        status: Optional[str] = None,
        category: Optional[str] = None,
        date_str: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if date_str:
            return await self.task_repo.get_by_user_and_date(user_id, date_str)
        return await self.task_repo.get_all_by_user(user_id, status=status, category=category)

    async def get_task_by_id(self, task_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.task_repo.get_by_id(task_id, user_id)

    async def create_task(self, user_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        task_data["user_id"] = user_id
        if "date" not in task_data or not task_data["date"]:
            task_data["date"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if "task_id" not in task_data or not task_data["task_id"]:
            task_data["task_id"] = f"task_{user_id}_{int(datetime.now(timezone.utc).timestamp())}"
        task_data.setdefault("status", "pending")
        task_data.setdefault("completion_percentage", 0.0)
        
        created = await self.task_repo.create(task_data)
        await self.progress_service.recalculate_progress(user_id)
        return created

    async def update_task(self, task_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        updated = await self.task_repo.update(task_id, user_id, update_data)
        if updated:
            await self.progress_service.recalculate_progress(user_id)
        return updated

    async def update_task_status(
        self,
        task_id: str,
        user_id: str,
        status: str,
        actual_minutes: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        updated = await self.task_repo.update_status(
            task_id=task_id,
            user_id=user_id,
            status=status,
            actual_minutes=actual_minutes,
            notes=notes,
        )
        if updated:
            await self.progress_service.recalculate_progress(user_id)
        return updated

    async def complete_task(
        self, task_id: str, user_id: str, actual_minutes: Optional[int] = None, notes: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        return await self.update_task_status(
            task_id=task_id, user_id=user_id, status="completed", actual_minutes=actual_minutes, notes=notes
        )

    async def skip_task(
        self, task_id: str, user_id: str, reason: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        notes_str = f"Skipped: {reason}" if reason else "Skipped"
        return await self.update_task_status(
            task_id=task_id, user_id=user_id, status="skipped", notes=notes_str
        )

    async def generate_tasks_for_roadmap(
        self, user_id: str, roadmap_id: str, roadmap_tasks: List[Dict[str, Any]], start_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        if not roadmap_tasks:
            return []
        
        base_date = (start_date or datetime.now(timezone.utc)).date()
        db_tasks = []
        for t in roadmap_tasks:
            day_num = t.get("day", 1)
            task_date = (base_date + timedelta(days=day_num - 1)).strftime("%Y-%m-%d")
            db_tasks.append({
                "task_id": t.get("id") or f"task_{roadmap_id}_d{day_num}_{int(datetime.now(timezone.utc).timestamp())}",
                "user_id": user_id,
                "roadmap_id": roadmap_id,
                "date": task_date,
                "day_number": day_num,
                "title": t.get("title", "Daily Task"),
                "description": t.get("description", ""),
                "category": t.get("category", "General"),
                "skill": t.get("skill", "Core"),
                "priority": str(t.get("priority", "HIGH")).upper(),
                "estimated_minutes": t.get("estimated_minutes", 60),
                "difficulty": t.get("difficulty", "Intermediate"),
                "status": t.get("status", "pending"),
                "completion_percentage": 100.0 if t.get("status") == "completed" else 0.0,
            })
        
        created_list = await self.task_repo.create_many(db_tasks)
        await self.progress_service.recalculate_progress(user_id)
        return created_list
