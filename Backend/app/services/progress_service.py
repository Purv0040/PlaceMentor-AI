import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.progress_repository import ProgressRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.roadmap_repository import RoadmapRepository
from app.utils.dates import get_today_date_str, APP_TIMEZONE


logger = logging.getLogger(__name__)


class ProgressService:

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.progress_repo = ProgressRepository(db)
        self.task_repo = TaskRepository(db)
        self.roadmap_repo = RoadmapRepository(db)

    async def get_progress(
        self,
        user_id: str,
    ) -> Dict[str, Any]:
        return await self.recalculate_progress(user_id)

    async def recalculate_progress(
        self,
        user_id: str,
    ) -> Dict[str, Any]:

        tasks = await self.task_repo.get_all_by_user(
            user_id,
            limit=2000,
        )

        active_roadmap = (
            await self.roadmap_repo.get_active_by_user_id(user_id)
        )

        roadmap_id = None

        if active_roadmap:
            roadmap_id = (
                active_roadmap.get("roadmap_id")
                or active_roadmap.get("_id")
            )

            if roadmap_id is not None:
                roadmap_id = str(roadmap_id)

        total_tasks = len(tasks)

        completed_tasks = [
            task
            for task in tasks
            if task.get("status") == "completed"
        ]

        pending_tasks = [
            task
            for task in tasks
            if task.get("status") in (
                "pending",
                "in_progress",
            )
        ]

        skipped_tasks = [
            task
            for task in tasks
            if task.get("status") == "skipped"
        ]

        completed_count = len(completed_tasks)
        pending_count = len(pending_tasks)
        skipped_count = len(skipped_tasks)

        completion_percentage = (
            round(
                completed_count / total_tasks * 100.0,
                1,
            )
            if total_tasks
            else 0.0
        )

        # ---------------------------------------------
        # ROADMAP PROGRESS
        # ---------------------------------------------

        if roadmap_id:
            roadmap_tasks = [
                task
                for task in tasks
                if str(task.get("roadmap_id")) == str(roadmap_id)
            ]
        else:
            roadmap_tasks = []

        roadmap_completed = [
            task
            for task in roadmap_tasks
            if task.get("status") == "completed"
        ]

        roadmap_completion_percentage = (
            round(
                len(roadmap_completed)
                / len(roadmap_tasks)
                * 100.0,
                1,
            )
            if roadmap_tasks
            else 0.0
        )

        # ---------------------------------------------
        # SKILL PROGRESS
        # ---------------------------------------------

        skill_totals: Dict[str, int] = {}
        skill_completed: Dict[str, int] = {}

        for task in tasks:

            skill = (
                task.get("skill")
                or task.get("category")
                or "General"
            )

            skill_totals[skill] = (
                skill_totals.get(skill, 0) + 1
            )

            if task.get("status") == "completed":
                skill_completed[skill] = (
                    skill_completed.get(skill, 0) + 1
                )

        skill_progress: Dict[str, float] = {}

        for skill, total in skill_totals.items():

            completed = skill_completed.get(
                skill,
                0,
            )

            skill_progress[skill] = round(
                completed / total * 100.0,
                1,
            )

        # ---------------------------------------------
        # TOP COMPLETED SKILLS
        # ---------------------------------------------

        completed_skills: List[str] = []

        for task in completed_tasks:

            skill = (
                task.get("skill")
                or task.get("category")
            )

            if (
                skill
                and skill not in completed_skills
            ):
                completed_skills.append(skill)

        # ---------------------------------------------
        # DAILY COMPLETION
        # ---------------------------------------------

        daily_map: Dict[
            str,
            Dict[str, int],
        ] = {}

        today_default = get_today_date_str()

        for task in tasks:

            task_date = (
                task.get("date")
                or today_default
            )

            if task_date not in daily_map:
                daily_map[task_date] = {
                    "total": 0,
                    "completed": 0,
                }

            daily_map[task_date]["total"] += 1

            if task.get("status") == "completed":
                daily_map[task_date]["completed"] += 1

        daily_completion = []

        for task_date, values in sorted(
            daily_map.items()
        ):

            total = values["total"]
            completed = values["completed"]

            percentage = (
                round(
                    completed / total * 100.0,
                    1,
                )
                if total
                else 0.0
            )

            daily_completion.append(
                {
                    "date": task_date,
                    "total": total,
                    "completed": completed,
                    "percentage": percentage,
                }
            )

        # ---------------------------------------------
        # STREAK
        # ---------------------------------------------

        existing = (
            await self.progress_repo.get_by_user_id(
                user_id
            )
            or {}
        )

        current_streak, longest_streak, last_active_date = (
            self._calculate_streak(
                daily_completion,
                existing,
            )
        )

        data = {
            "user_id": user_id,
            "roadmap_id": roadmap_id,
            "total_tasks": total_tasks,
            "completed_tasks": completed_count,
            "pending_tasks": pending_count,
            "skipped_tasks": skipped_count,
            "completion_percentage": completion_percentage,
            "roadmap_completion_percentage": roadmap_completion_percentage,
            "weekly_completion": [],
            "daily_completion": daily_completion[-14:],
            "skill_progress": skill_progress,
            "top_skills_completed": completed_skills,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "last_active_date": last_active_date,
            "completed_milestones": [],
        }

        if active_roadmap and roadmap_id:
            await self.roadmap_repo.update(
                roadmap_id,
                user_id,
                {
                    "progress": roadmap_completion_percentage
                },
            )

        return await self.progress_repo.save_or_update(
            user_id,
            data,
        )

    def _calculate_streak(
        self,
        daily_completion: List[Dict[str, Any]],
        existing: Dict[str, Any],
    ) -> Tuple[int, int, Optional[str]]:

        active_dates = sorted(
            {
                item["date"]
                for item in daily_completion
                if item.get("completed", 0) > 0
            }
        )

        if not active_dates:
            return (
                0,
                existing.get(
                    "longest_streak",
                    0,
                ),
                existing.get(
                    "last_active_date"
                ),
            )

        today = datetime.now(APP_TIMEZONE).date()

        today_str = today.strftime("%Y-%m-%d")

        yesterday_str = (
            today - timedelta(days=1)
        ).strftime("%Y-%m-%d")

        last_active = active_dates[-1]

        date_objects = [
            datetime.strptime(
                value,
                "%Y-%m-%d",
            ).date()
            for value in active_dates
        ]

        # Longest streak
        longest = 1
        running = 1

        for index in range(
            1,
            len(date_objects),
        ):

            difference = (
                date_objects[index]
                - date_objects[index - 1]
            ).days

            if difference == 1:
                running += 1
            else:
                running = 1

            longest = max(
                longest,
                running,
            )

        # Current streak
        current_streak = 0

        if last_active in (
            today_str,
            yesterday_str,
        ):

            current_streak = 1

            for index in range(
                len(date_objects) - 1,
                0,
                -1,
            ):

                difference = (
                    date_objects[index]
                    - date_objects[index - 1]
                ).days

                if difference == 1:
                    current_streak += 1
                else:
                    break

        stored_longest = existing.get(
            "longest_streak",
            0,
        )

        longest_streak = max(
            longest,
            current_streak,
            stored_longest,
        )

        return (
            current_streak,
            longest_streak,
            last_active,
        )

    async def get_streak(
        self,
        user_id: str,
    ) -> Dict[str, Any]:

        progress = await self.get_progress(
            user_id
        )

        today = get_today_date_str()

        last_active = progress.get(
            "last_active_date"
        )

        return {
            "current_streak": progress.get(
                "current_streak",
                0,
            ),
            "longest_streak": progress.get(
                "longest_streak",
                0,
            ),
            "last_active_date": last_active,
            "is_active_today": (
                last_active == today
            ),
        }

    async def get_summary(
        self,
        user_id: str,
    ) -> Dict[str, Any]:

        progress = await self.get_progress(
            user_id
        )

        return {
            "user_id": user_id,
            "total_tasks": progress.get(
                "total_tasks",
                0,
            ),
            "completed_tasks": progress.get(
                "completed_tasks",
                0,
            ),
            "completion_percentage": progress.get(
                "completion_percentage",
                0.0,
            ),
            "current_streak": progress.get(
                "current_streak",
                0,
            ),
            "longest_streak": progress.get(
                "longest_streak",
                0,
            ),
            "roadmap_completion_percentage": progress.get(
                "roadmap_completion_percentage",
                0.0,
            ),
            "top_skills_completed": progress.get(
                "top_skills_completed",
                [],
            ),
        }