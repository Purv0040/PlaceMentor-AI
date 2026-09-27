import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.roadmap_repository import RoadmapRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.readiness_repository import ReadinessRepository
from app.repositories.skill_gap_repository import SkillGapRepository
from app.services.task_service import TaskService
from app.services.progress_service import ProgressService
from app.integrations.ai_client import AIClient, AIClientError

logger = logging.getLogger(__name__)


class RoadmapService:
    def __init__(self, db: AsyncIOMotorDatabase, ai_client: Optional[AIClient] = None) -> None:
        self.roadmap_repo = RoadmapRepository(db)
        self.profile_repo = ProfileRepository(db)
        self.readiness_repo = ReadinessRepository(db)
        self.skill_gap_repo = SkillGapRepository(db)
        self.task_service = TaskService(db, ai_client=ai_client)
        self.progress_service = ProgressService(db)
        self.ai_client = ai_client or AIClient()

    async def get_active_roadmap(self, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.roadmap_repo.get_active_by_user_id(user_id)

    async def get_roadmap_by_id(self, roadmap_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.roadmap_repo.get_by_id(roadmap_id)
        if doc and doc.get("user_id") == user_id:
            return doc
        return None

    async def generate_roadmap(
        self,
        user_id: str,
        target_role: Optional[str] = None,
        available_minutes_per_day: int = 120,
        force_regenerate: bool = False,
    ) -> Dict[str, Any]:
        """Generate a personalized 90-day preparation roadmap."""
        # 1. Check if active roadmap exists and force_regenerate is False
        if not force_regenerate:
            active = await self.roadmap_repo.get_active_by_user_id(user_id)
            if active:
                logger.info("Active roadmap found for user %s, returning existing roadmap.", user_id)
                return active

        # 2. Gather Student Profile, Readiness, Skill Gap intelligence
        profile_doc = await self.profile_repo.get_by_user_id(user_id) or {}
        readiness_doc = await self.readiness_repo.get_latest_by_user(user_id) or {}
        skill_gap_doc = await self.skill_gap_repo.get_latest_by_user(user_id) or {}


        resolved_target_role = (
            target_role
            or profile_doc.get("target_role")
            or skill_gap_doc.get("target_role")
            or "Backend Developer"
        )

        payload = {
            "target_role": resolved_target_role,
            "available_minutes_per_day": available_minutes_per_day,
            "profile": profile_doc,
            "skill_gaps": skill_gap_doc,
            "readiness": readiness_doc,
        }

        # 3. Call AI microservice to generate roadmap
        ai_data: Dict[str, Any] = {}
        try:
            ai_data = await self.ai_client.generate_roadmap(payload)
        except AIClientError as e:
            logger.warning("AI Roadmap Service unavailable: %s. Using deterministic fallback.", e)
            ai_data = self._generate_deterministic_fallback(resolved_target_role, available_minutes_per_day, skill_gap_doc)

        # 4. Supersede active roadmaps if regenerating
        await self.roadmap_repo.supersede_active_roadmaps(user_id)

        # 5. Format weekly goals and phases
        phases = ai_data.get("phases", [])
        all_tasks = ai_data.get("all_tasks", [])
        
        # Build weekly goals (13 weeks for 90 days)
        weekly_goals = self._build_weekly_goals(all_tasks, resolved_target_role)

        start_dt = datetime.now(timezone.utc)
        end_dt = start_dt + timedelta(days=90)

        roadmap_record = {
            "user_id": user_id,
            "target_role": resolved_target_role,
            "title": f"90-Day {resolved_target_role} Placement Roadmap",
            "description": ai_data.get("summary") or f"Personalized 90-day plan for {resolved_target_role}",
            "summary": ai_data.get("summary") or f"Personalized 90-day plan for {resolved_target_role}",
            "start_date": start_dt,
            "end_date": end_dt,
            "duration_days": 90,
            "available_minutes_per_day": available_minutes_per_day,
            "total_estimated_hours": ai_data.get("total_estimated_hours", 180.0),
            "phases": phases,
            "weekly_goals": weekly_goals,
            "all_tasks": all_tasks,
            "status": "active",
            "progress": 0.0,
            "analysis_version": 1,
            "validation_report": ai_data.get("validation_report", {}),
            "created_at": start_dt,
            "updated_at": start_dt,
        }

        # 6. Save in MongoDB
        created_roadmap = await self.roadmap_repo.create(roadmap_record)
        roadmap_id = created_roadmap.get("roadmap_id") or created_roadmap.get("_id")

        # 7. Generate and store initial daily tasks in DB
        if all_tasks:
            await self.task_service.generate_tasks_for_roadmap(
                user_id=user_id,
                roadmap_id=roadmap_id,
                roadmap_tasks=all_tasks,
                start_date=start_dt,
            )

        # 8. Recalculate progress
        await self.progress_service.recalculate_progress(user_id)

        return created_roadmap

    def _build_weekly_goals(self, all_tasks: List[Dict[str, Any]], target_role: str) -> List[Dict[str, Any]]:
        weeks = []
        for w in range(1, 14):
            start_day = (w - 1) * 7 + 1
            end_day = min(90, w * 7)
            w_tasks = [t for t in all_tasks if start_day <= t.get("day", 1) <= end_day]
            
            skills = list(set(t.get("skill") for t in w_tasks if t.get("skill")))
            if not skills:
                skills = ["Core Engineering", "DSA"]

            task_titles = [t.get("title", "") for t in w_tasks[:4]]
            
            weeks.append({
                "week_number": w,
                "objective": f"Week {w}: Focus on {', '.join(skills[:2])} for {target_role}.",
                "skills": skills,
                "tasks": task_titles,
                "expected_outcome": f"Complete practice modules and coding benchmarks for Week {w}.",
                "estimated_effort": f"{len(w_tasks) * 1.5:.1f} Hours",
                "completion_percentage": 0.0
            })
        return weeks

    def _generate_deterministic_fallback(
        self, target_role: str, daily_minutes: int, skill_gap_doc: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Safe deterministic fallback roadmap when AI service is unavailable."""
        high_gaps = [g.get("skill") for g in skill_gap_doc.get("priority_gaps", [])] if skill_gap_doc else []
        gap_1 = high_gaps[0] if high_gaps else "DSA Arrays & Hashing"
        gap_2 = high_gaps[1] if len(high_gaps) > 1 else "System Design Fundamentals"
        gap_3 = high_gaps[2] if len(high_gaps) > 2 else "Docker & Containerization"

        all_tasks = []
        for day in range(1, 91):
            if day <= 30:
                phase_num = 1
                cat = "DSA" if day % 2 == 1 else "Backend"
                skill = gap_1 if day % 2 == 1 else "Python / Node.js"
                title = f"Day {day}: Foundation in {skill}"
                desc = f"Solve 2-3 foundational problems and review core concepts in {skill} for {target_role}."
            elif day <= 60:
                phase_num = 2
                cat = "Backend" if day % 2 == 1 else "Projects"
                skill = gap_2 if day % 2 == 1 else "SQL & Database Design"
                title = f"Day {day}: Core Skill Development in {skill}"
                desc = f"Build and test modular code patterns focusing on {skill}."
            else:
                phase_num = 3
                cat = "System Design" if day % 2 == 1 else "Interview"
                skill = gap_3 if day % 2 == 1 else "Mock Behavioral Interview"
                title = f"Day {day}: Placement Preparation & {skill}"
                desc = f"Conduct timed practice and review STAR interview responses for {target_role}."

            all_tasks.append({
                "id": f"task_d{day}_1",
                "day": day,
                "category": cat,
                "title": title,
                "description": desc,
                "estimated_minutes": min(120, daily_minutes),
                "difficulty": "Beginner" if day <= 30 else "Intermediate" if day <= 60 else "Advanced",
                "priority": "High" if day % 3 == 0 else "Medium",
                "skill": skill,
                "status": "pending",
            })

        phase1_tasks = [t for t in all_tasks if 1 <= t["day"] <= 30]
        phase2_tasks = [t for t in all_tasks if 31 <= t["day"] <= 60]
        phase3_tasks = [t for t in all_tasks if 61 <= t["day"] <= 90]

        return {
            "target_role": target_role,
            "total_days": 90,
            "available_minutes_per_day": daily_minutes,
            "total_estimated_hours": round(sum(t["estimated_minutes"] for t in all_tasks) / 60.0, 1),
            "phases": [
                {
                    "phase_number": 1,
                    "name": "Phase 1: Foundation",
                    "day_range": "Days 1-30",
                    "start_day": 1,
                    "end_day": 30,
                    "goal": f"Establish core programming and DSA foundations targeting {target_role}.",
                    "tasks": phase1_tasks
                },
                {
                    "phase_number": 2,
                    "name": "Phase 2: Skill Development",
                    "day_range": "Days 31-60",
                    "start_day": 31,
                    "end_day": 60,
                    "goal": f"Develop advanced frameworks and build metric-backed portfolio projects for {target_role}.",
                    "tasks": phase2_tasks
                },
                {
                    "phase_number": 3,
                    "name": "Phase 3: Placement Preparation",
                    "day_range": "Days 61-90",
                    "start_day": 61,
                    "end_day": 90,
                    "goal": f"Master System Design, timed coding benchmarks, and mock interview practice.",
                    "tasks": phase3_tasks
                }
            ],
            "all_tasks": all_tasks,
            "summary": f"90-Day placement preparation plan for {target_role} addressing key skill gaps ({gap_1}, {gap_2}).",
            "validation_report": {"status": "valid_fallback"}
        }

    async def get_summary(self, user_id: str) -> Dict[str, Any]:
        active = await self.get_active_roadmap(user_id)
        if not active:
            return {
                "roadmap_id": None,
                "target_role": "Not Set",
                "total_days": 90,
                "current_day": 1,
                "phases_count": 0,
                "progress_percentage": 0.0,
                "status": "none",
                "current_phase_name": None
            }

        start_dt = active.get("start_date") or datetime.now(timezone.utc)
        if isinstance(start_dt, str):
            try:
                start_dt = datetime.fromisoformat(start_dt.replace("Z", "+00:00"))
            except Exception:
                start_dt = datetime.now(timezone.utc)

        current_day = max(1, min(90, (datetime.now(timezone.utc).date() - start_dt.date()).days + 1))
        
        phases = active.get("phases", [])
        curr_phase_name = phases[0].get("name") if phases else "Phase 1: Foundation"
        for p in phases:
            if p.get("start_day", 1) <= current_day <= p.get("end_day", 30):
                curr_phase_name = p.get("name")
                break

        return {
            "roadmap_id": active.get("roadmap_id") or active.get("_id"),
            "target_role": active.get("target_role", "Backend Developer"),
            "total_days": active.get("duration_days", 90),
            "current_day": current_day,
            "phases_count": len(phases),
            "progress_percentage": active.get("progress", 0.0),
            "status": active.get("status", "active"),
            "current_phase_name": curr_phase_name
        }

    async def update_roadmap(self, roadmap_id: str, user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.roadmap_repo.update(roadmap_id, user_id, data)

    async def delete_roadmap(self, roadmap_id: str, user_id: str) -> bool:
        return await self.roadmap_repo.delete(roadmap_id, user_id)

    async def get_roadmap_weeks(self, roadmap_id: str, user_id: str) -> List[Dict[str, Any]]:
        roadmap = await self.get_roadmap_by_id(roadmap_id, user_id)
        if not roadmap:
            return []
        return roadmap.get("weekly_goals", [])

    async def get_roadmap_phases(self, roadmap_id: str, user_id: str) -> List[Dict[str, Any]]:
        roadmap = await self.get_roadmap_by_id(roadmap_id, user_id)
        if not roadmap:
            return []
        return roadmap.get("phases", [])
