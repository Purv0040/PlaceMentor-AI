import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.profile_repository import ProfileRepository
from app.repositories.user_repository import UserRepository
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
        self.user_repo = UserRepository(db)
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

    async def build_student_context(
        self,
        user_id: str,
        target_role_override: Optional[str] = None,
        student_name_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Fetch and assemble student placement context across all modules."""
        # Fetch profile and user
        profile = await self.profile_repo.get_by_user_id(user_id) or {}
        user_doc = await self.user_repo.get_by_id(user_id) or {}

        target_role = (
            target_role_override
            or profile.get("target_role")
            or user_doc.get("target_role")
            or user_doc.get("targetRole")
            or None
        )
        name = (
            student_name_override
            or profile.get("full_name")
            or profile.get("name")
            or user_doc.get("full_name")
            or user_doc.get("name")
            or "Student"
        )

        resume = await self.resume_repo.find_active_by_user(user_id) or {}
        github = await self.github_repo.find_by_user_id(user_id) or {}
        leetcode = await self.leetcode_repo.find_by_user_id(user_id) or {}
        projects = await self.project_repo.find_by_user_id(user_id) or []
        readiness = await self.readiness_repo.get_latest_by_user(user_id) or {}
        skill_gaps = await self.skill_gap_repo.get_latest_by_user(user_id) or {}
        
        # Resolve active or target-role roadmap
        roadmap = None
        if target_role:
            rms = await self.roadmap_repo.get_all_by_user_id(user_id)
            matching_rm = next((r for r in rms if r.get("status") == "active" and (r.get("target_role") or "").strip().lower() == target_role.strip().lower()), None)
            if not matching_rm:
                matching_rm = next((r for r in rms if (r.get("target_role") or "").strip().lower() == target_role.strip().lower()), None)
            if matching_rm:
                roadmap = matching_rm
        if not roadmap:
            roadmap = await self.roadmap_repo.get_active_by_user_id(user_id) or {}

        all_tasks = await self.task_repo.get_all_by_user(user_id) or []
        progress = await self.progress_repo.get_by_user_id(user_id) or {}
        interviews = await self.interview_repo.get_history_by_user_id(user_id, limit=5) or []
        communication = await self.comm_repo.get_history_by_user_id(user_id, limit=5) or []

        # Roadmap day & timeline calculation using APP_TIMEZONE
        from app.utils.dates import APP_TIMEZONE, get_today_date_str

        now_local = datetime.now(APP_TIMEZONE)
        today_date = now_local.date()
        today_str = get_today_date_str()
        yesterday_local = now_local - timedelta(days=1)
        yesterday_date = yesterday_local.date()
        yesterday_str = yesterday_local.strftime("%Y-%m-%d")

        total_days = roadmap.get("duration_days") or roadmap.get("total_days") or 90
        start_dt = roadmap.get("start_date") or now_local
        if isinstance(start_dt, str):
            try:
                start_dt = datetime.fromisoformat(start_dt.replace("Z", "+00:00"))
            except Exception:
                start_dt = now_local
        if isinstance(start_dt, datetime):
            start_date = start_dt.astimezone(APP_TIMEZONE).date() if start_dt.tzinfo else start_dt.date()
        else:
            start_date = start_dt

        current_day = max(1, min(total_days, (today_date - start_date).days + 1))
        remaining_days = max(0, total_days - current_day)

        # Merge roadmap tasks and daily_tasks from DB for complete 90-day coverage
        roadmap_tasks = roadmap.get("all_tasks") or []
        if not roadmap_tasks and roadmap.get("phases"):
            for p in roadmap["phases"]:
                roadmap_tasks.extend(p.get("tasks", []))

        active_roadmap_id = str(roadmap.get("roadmap_id") or roadmap.get("_id") or "")
        if active_roadmap_id:
            active_db_tasks = [
                t for t in all_tasks
                if str(t.get("roadmap_id")) == active_roadmap_id and not t.get("is_leetcode")
            ]
        else:
            active_db_tasks = [t for t in all_tasks if not t.get("is_leetcode")]

        db_tasks_by_id = {}
        db_tasks_by_title = {}
        for t in active_db_tasks:
            tid = str(t.get("task_id") or t.get("id") or "")
            title = t.get("title")
            is_completed = t.get("status") in ("completed", "done")
            if tid:
                if tid not in db_tasks_by_id or (is_completed and db_tasks_by_id[tid].get("status") not in ("completed", "done")):
                    db_tasks_by_id[tid] = t
            if title:
                if title not in db_tasks_by_title or (is_completed and db_tasks_by_title[title].get("status") not in ("completed", "done")):
                    db_tasks_by_title[title] = t

        unified_tasks = []
        seen_task_keys = set()

        if roadmap_tasks:
            for idx, rt in enumerate(roadmap_tasks):
                task_id = str(rt.get("id") or rt.get("task_id") or "")
                title = rt.get("title", f"Task {idx+1}")
                day = rt.get("day") or rt.get("day_number") or 1
                try:
                    day = int(day)
                except (ValueError, TypeError):
                    day = 1

                task_key = (day, title.strip().lower())
                if task_key in seen_task_keys:
                    continue
                seen_task_keys.add(task_key)

                matching_db = db_tasks_by_id.get(task_id) or db_tasks_by_title.get(title)
                if matching_db:
                    status_val = matching_db.get("status", "pending")
                    completed_at = matching_db.get("completed_at")
                    date_val = matching_db.get("date")
                    est_min = matching_db.get("estimated_minutes") or rt.get("estimated_minutes", 60)
                else:
                    status_val = rt.get("status", "pending")
                    completed_at = rt.get("completed_at")
                    date_val = rt.get("date")
                    est_min = rt.get("estimated_minutes", 60)

                unified_tasks.append({
                    "task_id": task_id or (matching_db.get("task_id") if matching_db else f"task_d{day}_{idx+1}"),
                    "title": title,
                    "category": rt.get("category") or (matching_db.get("category") if matching_db else "General"),
                    "priority": rt.get("priority") or "MEDIUM",
                    "difficulty": rt.get("difficulty") or "Intermediate",
                    "estimated_minutes": est_min,
                    "day": day,
                    "day_number": day,
                    "status": status_val,
                    "completed_at": completed_at,
                    "date": date_val,
                })
        else:
            unified_tasks = active_db_tasks

        # Group tasks by day
        tasks_by_day: Dict[int, List[Dict[str, Any]]] = {}
        for t in unified_tasks:
            d = t.get("day_number") or t.get("day")
            if d is None:
                continue
            try:
                d = int(d)
            except (ValueError, TypeError):
                continue
            if d not in tasks_by_day:
                tasks_by_day[d] = []
            tasks_by_day[d].append(t)

        # 1. Today's tasks (strictly matching current day from the active roadmap)
        today_tasks_list = [
            t for t in unified_tasks
            if t.get("day_number") == current_day or t.get("day") == current_day
        ]
        if not today_tasks_list:
            today_tasks_list = [
                t for t in unified_tasks
                if t.get("date") == today_str
            ]
        today_incomplete = [t for t in today_tasks_list if t.get("status") not in ("completed", "done")]
        today_completed = [t for t in today_tasks_list if t.get("status") in ("completed", "done")]

        # 2. Yesterday's completed tasks
        yesterday_completed_list = []
        for t in unified_tasks:
            if t.get("status") in ("completed", "done"):
                comp_at = t.get("completed_at")
                matched_yesterday = False
                if comp_at:
                    if isinstance(comp_at, str):
                        try:
                            comp_at = datetime.fromisoformat(comp_at.replace("Z", "+00:00"))
                        except Exception:
                            comp_at = None
                    if isinstance(comp_at, datetime):
                        comp_date = comp_at.astimezone(APP_TIMEZONE).date() if comp_at.tzinfo else comp_at.date()
                        if comp_date == yesterday_date:
                            matched_yesterday = True
                if not matched_yesterday and t.get("date") == yesterday_str:
                    matched_yesterday = True

                if matched_yesterday:
                    yesterday_completed_list.append(t)

        # 3. All pending vs completed across the roadmap
        all_pending_list = [t for t in unified_tasks if t.get("status") not in ("completed", "done")]
        all_completed_list = [t for t in unified_tasks if t.get("status") in ("completed", "done")]

        # 4. Overdue tasks: incomplete tasks where day < current_day or date < today_str
        overdue_list = []
        for t in all_pending_list:
            t_day = t.get("day") or t.get("day_number")
            t_date = t.get("date") or t.get("due_date")
            is_overdue = False
            if t_date and str(t_date) < today_str:
                is_overdue = True
            elif t_day is not None:
                try:
                    if int(t_day) < current_day:
                        is_overdue = True
                except (ValueError, TypeError):
                    pass
            if is_overdue:
                overdue_list.append(t)

        # 5. Next recommended incomplete task
        next_incomplete_task = None
        if today_incomplete:
            next_incomplete_task = today_incomplete[0]
        else:
            upcoming_incomplete = []
            for t in all_pending_list:
                t_day = t.get("day") or t.get("day_number")
                try:
                    if int(t_day) >= current_day:
                        upcoming_incomplete.append(t)
                except (ValueError, TypeError):
                    upcoming_incomplete.append(t)
            if upcoming_incomplete:
                next_incomplete_task = upcoming_incomplete[0]
            elif all_pending_list:
                next_incomplete_task = all_pending_list[0]

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
            "student_name": name,
            "profile": {
                "name": name,
                "email": user_doc.get("email"),
                "target_role": target_role,
                "target_company_tier": profile.get("target_company_tier"),
                "skills": profile.get("skills") or [],
                "experience_level": profile.get("experience_level"),
                "college": profile.get("college"),
                "graduation_year": profile.get("graduation_year"),
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
                "current_day": current_day,
                "total_days": total_days,
                "remaining_days": remaining_days,
                "start_date": str(start_date),
                "current_phase": roadmap.get("current_phase"),
                "completion_percentage": roadmap.get("completion_percentage"),
                "status": roadmap.get("status"),
                "total_tasks_count": len(unified_tasks),
                "completed_tasks_count": len(all_completed_list),
                "pending_tasks_count": len(all_pending_list),
            },
            "next_recommended_task": {
                "task_id": next_incomplete_task.get("task_id"),
                "title": next_incomplete_task.get("title"),
                "category": next_incomplete_task.get("category"),
                "day": next_incomplete_task.get("day") or next_incomplete_task.get("day_number"),
                "priority": next_incomplete_task.get("priority", "MEDIUM"),
                "difficulty": next_incomplete_task.get("difficulty", "Intermediate"),
                "estimated_minutes": next_incomplete_task.get("estimated_minutes", 60),
                "status": next_incomplete_task.get("status", "pending"),
            } if next_incomplete_task else None,
            "overdue_tasks": {
                "total_overdue": len(overdue_list),
                "tasks": [
                    {
                        "task_id": t.get("task_id"),
                        "title": t.get("title"),
                        "category": t.get("category"),
                        "day": t.get("day") or t.get("day_number"),
                        "priority": t.get("priority", "MEDIUM"),
                        "estimated_minutes": t.get("estimated_minutes", 60),
                        "status": t.get("status", "pending"),
                    }
                    for t in overdue_list[:15]
                ],
            },
            "today_tasks": {
                "current_day": current_day,
                "total": len(today_tasks_list),
                "completed_count": len(today_completed),
                "pending_count": len(today_incomplete),
                "pending_tasks": [
                    {
                        "task_id": t.get("task_id"),
                        "title": t.get("title"),
                        "category": t.get("category"),
                        "priority": t.get("priority"),
                        "day": t.get("day") or t.get("day_number") or current_day,
                        "status": t.get("status", "pending"),
                        "estimated_minutes": t.get("estimated_minutes", 60),
                    }
                    for t in today_incomplete
                ],
                "completed_tasks": [
                    {
                        "task_id": t.get("task_id"),
                        "title": t.get("title"),
                        "category": t.get("category"),
                        "day": t.get("day") or t.get("day_number") or current_day,
                        "status": "completed",
                    }
                    for t in today_completed
                ],
            },
            "yesterday_completed_tasks": {
                "date": yesterday_str,
                "count": len(yesterday_completed_list),
                "tasks": [
                    {
                        "task_id": t.get("task_id"),
                        "title": t.get("title"),
                        "category": t.get("category"),
                        "day": t.get("day") or t.get("day_number"),
                        "completed_at": str(t.get("completed_at")) if t.get("completed_at") else None,
                    }
                    for t in yesterday_completed_list
                ],
            },
            "all_pending_tasks": {
                "total_pending": len(all_pending_list),
                "tasks": [
                    {
                        "task_id": t.get("task_id"),
                        "title": t.get("title"),
                        "category": t.get("category"),
                        "day": t.get("day") or t.get("day_number"),
                        "priority": t.get("priority"),
                        "estimated_minutes": t.get("estimated_minutes", 60),
                        "status": t.get("status", "pending"),
                    }
                    for t in all_pending_list[:15]
                ],
            },
            "tasks_by_day": {
                str(d): [
                    {
                        "task_id": t.get("task_id"),
                        "title": t.get("title"),
                        "category": t.get("category"),
                        "difficulty": t.get("difficulty", "Intermediate"),
                        "priority": t.get("priority", "MEDIUM"),
                        "estimated_minutes": t.get("estimated_minutes", 60),
                        "status": t.get("status", "pending"),
                    }
                    for t in day_tasks
                ]
                for d, day_tasks in tasks_by_day.items()
            },
            "progress": {
                "overall_progress_percent": progress.get("overall_progress_percent"),
                "streak_days": progress.get("streak_days"),
                "completed_tasks": len(all_completed_list),
                "pending_tasks": len(all_pending_list),
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
