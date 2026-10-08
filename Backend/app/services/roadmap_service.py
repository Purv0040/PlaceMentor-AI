import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List

from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.roadmap_repository import RoadmapRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.readiness_repository import ReadinessRepository
from app.repositories.skill_gap_repository import SkillGapRepository

from app.services.task_service import TaskService
from app.services.progress_service import ProgressService

from app.integrations.ai_client import (
    AIClient,
    AIClientError,
)
from app.services.roadmap_curriculum import (
    resolve_role_domain,
    get_role_phase_goals,
    generate_90_day_curriculum,
)


logger = logging.getLogger(__name__)


class RoadmapService:

    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        ai_client: Optional[AIClient] = None,
    ) -> None:

        self.roadmap_repo = RoadmapRepository(db)

        self.profile_repo = ProfileRepository(db)

        self.readiness_repo = ReadinessRepository(db)

        self.skill_gap_repo = SkillGapRepository(db)

        self.task_service = TaskService(
            db,
            ai_client=ai_client,
        )

        self.progress_service = ProgressService(db)

        self.ai_client = ai_client or AIClient()

    # ============================================================
    # GET ACTIVE ROADMAP
    # ============================================================

    async def get_active_roadmap(
        self,
        user_id: str,
    ) -> Optional[Dict[str, Any]]:

        return await self.roadmap_repo.get_active_by_user_id(
            str(user_id)
        )

    # ============================================================
    # GET ROADMAP BY ID
    # ============================================================

    async def get_roadmap_by_id(
        self,
        roadmap_id: str,
        user_id: str,
    ) -> Optional[Dict[str, Any]]:

        doc = await self.roadmap_repo.get_by_id(
            roadmap_id
        )

        if not doc:
            return None

        # Always enforce user ownership
        if str(doc.get("user_id")) != str(user_id):
            return None

        return doc

    # ============================================================
    # NORMALIZE TARGET ROLE
    # ============================================================

    @staticmethod
    def _normalize_role(value: Any) -> str:
        if value is None:
            return ""

        return str(value).strip()

    # ============================================================
    # CHECK PLACEHOLDER VALUES
    # ============================================================

    @staticmethod
    def _is_placeholder_string(value: Any) -> bool:

        if not isinstance(value, str):
            return False

        normalized = value.strip().lower()

        return normalized in {
            "string",
            "<string>",
            "target_role",
            "{target_role}",
        }

    # ============================================================
    # REPLACE AI PLACEHOLDERS
    # ============================================================

    def _replace_role_placeholders(
        self,
        data: Any,
        target_role: str,
    ) -> Any:

        if isinstance(data, str):

            # Exact placeholder
            if self._is_placeholder_string(data):
                return target_role

            # Replace placeholder appearing inside text
            return data.replace(
                "{target_role}",
                target_role,
            ).replace(
                "<target_role>",
                target_role,
            )

        if isinstance(data, list):

            return [
                self._replace_role_placeholders(
                    item,
                    target_role,
                )
                for item in data
            ]

        if isinstance(data, dict):

            return {
                key: self._replace_role_placeholders(
                    value,
                    target_role,
                )
                for key, value in data.items()
            }

        return data

    # ============================================================
    # GENERATE ROADMAP
    # ============================================================

    async def generate_roadmap(
        self,
        user_id: str,
        target_role: Optional[str] = None,
        available_minutes_per_day: int = 120,
        force_regenerate: bool = False,
    ) -> Dict[str, Any]:

        """
        Generate a personalized 90-day preparation roadmap.

        Flow:

        Student Profile
              ↓
        Readiness
              ↓
        Skill Gap
              ↓
        AI Roadmap Service
              ↓
        MongoDB
              ↓
        Daily Tasks
              ↓
        Progress
        """

        user_id = str(user_id)

        # --------------------------------------------------------
        # 1. Validate available time
        # --------------------------------------------------------

        try:
            available_minutes_per_day = int(
                available_minutes_per_day
            )
        except (TypeError, ValueError):
            available_minutes_per_day = 120

        available_minutes_per_day = max(
            30,
            min(
                available_minutes_per_day,
                480,
            ),
        )

        requested_target_role = self._normalize_role(
            target_role
        )

        # --------------------------------------------------------
        # 2. Load existing active roadmap
        # --------------------------------------------------------

        active = await self.roadmap_repo.get_active_by_user_id(
            user_id
        )

        # --------------------------------------------------------
        # 3. Reuse active roadmap only when it matches request
        # --------------------------------------------------------

        if active and not force_regenerate:

            active_role = self._normalize_role(
                active.get("target_role")
            )

            active_minutes = active.get(
                "available_minutes_per_day"
            )

            try:
                active_minutes = int(active_minutes)
            except (TypeError, ValueError):
                active_minutes = 120

            role_matches = (
                not requested_target_role
                or active_role.casefold()
                == requested_target_role.casefold()
            )

            minutes_match = (
                active_minutes
                == available_minutes_per_day
            )

            # IMPORTANT:
            # If both role and available time match,
            # return existing roadmap.
            #
            # If either changes, generate a new roadmap.

            if role_matches and minutes_match:

                logger.info(
                    "Returning existing active roadmap "
                    "for user %s because requested "
                    "configuration matches.",
                    user_id,
                )

                return active

            logger.info(
                "Active roadmap configuration differs "
                "from requested configuration. "
                "Generating a new roadmap for user %s.",
                user_id,
            )

        # --------------------------------------------------------
        # 4. Gather student intelligence
        # --------------------------------------------------------

        profile_doc = (
            await self.profile_repo.get_by_user_id(
                user_id
            )
            or {}
        )

        readiness_doc = (
            await self.readiness_repo.get_latest_by_user(
                user_id
            )
            or {}
        )

        skill_gap_doc = (
            await self.skill_gap_repo.get_latest_by_user(
                user_id
            )
            or {}
        )

        # --------------------------------------------------------
        # 5. Resolve target role dynamically
        # --------------------------------------------------------

        resolved_target_role = (
            requested_target_role
            or self._normalize_role(
                profile_doc.get("target_role")
            )
            or self._normalize_role(
                profile_doc.get("career", {}).get(
                    "targetRole"
                )
                if isinstance(
                    profile_doc.get("career"),
                    dict,
                )
                else None
            )
            or self._normalize_role(
                skill_gap_doc.get("target_role")
            )
            or "Backend Developer"
        )

        # --------------------------------------------------------
        # 6. Build AI payload
        # --------------------------------------------------------

        raw_payload: Dict[str, Any] = {
            "target_role": resolved_target_role,
            "available_minutes_per_day": (
                available_minutes_per_day
            ),
            "profile": profile_doc,
            "skill_gaps": skill_gap_doc,
            "readiness": readiness_doc,
        }

        # IMPORTANT:
        # MongoDB documents may contain datetime,
        # ObjectId, Pydantic values, etc.
        #
        # Convert them before sending to AI.

        payload = jsonable_encoder(
            raw_payload
        )

        # --------------------------------------------------------
        # 7. Generate roadmap using AI
        # --------------------------------------------------------

        ai_data: Dict[str, Any] = {}

        try:

            ai_data = await self.ai_client.generate_roadmap(
                payload
            )

            if not isinstance(ai_data, dict):

                logger.warning(
                    "AI roadmap response was not a dictionary. "
                    "Using deterministic fallback."
                )

                ai_data = {}

        except AIClientError as exc:

            logger.warning(
                "AI Roadmap Service unavailable: %s. "
                "Using deterministic fallback.",
                exc,
            )

            ai_data = (
                self._generate_deterministic_fallback(
                    resolved_target_role,
                    available_minutes_per_day,
                    skill_gap_doc,
                    profile_doc,
                )
            )

        except Exception as exc:

            logger.exception(
                "Unexpected AI roadmap generation error: %s. "
                "Using deterministic fallback.",
                exc,
            )

            ai_data = (
                self._generate_deterministic_fallback(
                    resolved_target_role,
                    available_minutes_per_day,
                    skill_gap_doc,
                    profile_doc,
                )
            )

        # --------------------------------------------------------
        # 8. Normalize AI response
        # --------------------------------------------------------

        if not isinstance(ai_data, dict):
            ai_data = {}

        # Replace bad placeholder values such as:
        #
        # "string"
        #
        # with the actual requested role.

        ai_data = self._replace_role_placeholders(
            ai_data,
            resolved_target_role,
        )

        # Never trust AI for the canonical target role.
        ai_data["target_role"] = (
            resolved_target_role
        )

        # Never trust AI for available daily time.
        ai_data["available_minutes_per_day"] = (
            available_minutes_per_day
        )

        # --------------------------------------------------------
        # 9. Extract phases and tasks
        # --------------------------------------------------------

        phases = ai_data.get(
            "phases",
            [],
        )

        all_tasks = ai_data.get(
            "all_tasks",
            [],
        )

        if not isinstance(phases, list):
            phases = []

        if not isinstance(all_tasks, list):
            all_tasks = []

        # --------------------------------------------------------
        # 10. Validate AI tasks
        # --------------------------------------------------------

        cleaned_tasks: List[Dict[str, Any]] = []

        for index, task in enumerate(all_tasks):

            if not isinstance(task, dict):
                continue

            task = dict(task)

            # Dynamic target-role placeholder cleanup
            task = self._replace_role_placeholders(
                task,
                resolved_target_role,
            )

            # Ensure required fields
            task.setdefault(
                "id",
                f"task_d{task.get('day', index + 1)}_1",
            )

            try:
                day = int(
                    task.get(
                        "day",
                        index + 1,
                    )
                )
            except (TypeError, ValueError):
                day = index + 1

            day = max(
                1,
                min(
                    day,
                    90,
                ),
            )

            task["day"] = day

            task.setdefault(
                "category",
                "Core Engineering",
            )

            task.setdefault(
                "title",
                (
                    f"Day {day}: "
                    f"{resolved_target_role} Preparation"
                ),
            )

            task.setdefault(
                "description",
                (
                    f"Complete a focused "
                    f"preparation task for "
                    f"{resolved_target_role}."
                ),
            )

            try:
                estimated_minutes = int(
                    task.get(
                        "estimated_minutes",
                        min(
                            120,
                            available_minutes_per_day,
                        ),
                    )
                )
            except (TypeError, ValueError):
                estimated_minutes = min(
                    120,
                    available_minutes_per_day,
                )

            task["estimated_minutes"] = max(
                15,
                min(
                    estimated_minutes,
                    available_minutes_per_day,
                ),
            )

            task.setdefault(
                "difficulty",
                "Intermediate",
            )

            task.setdefault(
                "priority",
                "Medium",
            )

            task.setdefault(
                "skill",
                "Core Engineering",
            )

            task.setdefault(
                "status",
                "pending",
            )

            if day <= 30:
                phase_number = 1
            elif day <= 60:
                phase_number = 2
            else:
                phase_number = 3

            task["phase_number"] = phase_number

            cleaned_tasks.append(task)

        all_tasks = cleaned_tasks

        # --------------------------------------------------------
        # 11. Fallback if AI generated no usable tasks
        # --------------------------------------------------------

        if not all_tasks:

            fallback = (
                self._generate_deterministic_fallback(
                    resolved_target_role,
                    available_minutes_per_day,
                    skill_gap_doc,
                    profile_doc,
                )
            )

            phases = fallback.get(
                "phases",
                [],
            )

            all_tasks = fallback.get(
                "all_tasks",
                [],
            )

            ai_data["summary"] = fallback.get(
                "summary",
                (
                    f"90-Day placement preparation "
                    f"plan for {resolved_target_role}."
                ),
            )

            ai_data["total_estimated_hours"] = (
                fallback.get(
                    "total_estimated_hours",
                    0.0,
                )
            )

            ai_data["validation_report"] = (
                fallback.get(
                    "validation_report",
                    {},
                )
            )

        # --------------------------------------------------------
        # 12. Ensure phases exist
        # --------------------------------------------------------

        if not phases:

            phases = self._build_phases(
                all_tasks,
                resolved_target_role,
            )

        else:

            phases = self._replace_role_placeholders(
                phases,
                resolved_target_role,
            )

        # --------------------------------------------------------
        # 13. Supersede existing active roadmap
        # --------------------------------------------------------

        await self.roadmap_repo.supersede_active_roadmaps(
            user_id
        )

        # --------------------------------------------------------
        # 14. Build weekly goals
        # --------------------------------------------------------

        weekly_goals = self._build_weekly_goals(
            all_tasks,
            resolved_target_role,
        )

        # --------------------------------------------------------
        # 15. Build dates
        # --------------------------------------------------------

        start_dt = datetime.now(
            timezone.utc
        )

        end_dt = start_dt + timedelta(
            days=89
        )

        # --------------------------------------------------------
        # 16. Calculate total estimated hours
        # --------------------------------------------------------

        calculated_minutes = 0

        for task in all_tasks:

            try:
                calculated_minutes += int(
                    task.get(
                        "estimated_minutes",
                        0,
                    )
                )
            except (TypeError, ValueError):
                continue

        calculated_hours = round(
            calculated_minutes / 60.0,
            1,
        )

        try:

            total_estimated_hours = float(
                ai_data.get(
                    "total_estimated_hours",
                    calculated_hours,
                )
                or calculated_hours
            )

        except (TypeError, ValueError):

            total_estimated_hours = (
                calculated_hours
            )

        # --------------------------------------------------------
        # 17. Build roadmap MongoDB document
        # --------------------------------------------------------

        roadmap_record: Dict[str, Any] = {

            "user_id": user_id,

            # Canonical values controlled by backend
            "target_role": resolved_target_role,

            "title": (
                f"90-Day "
                f"{resolved_target_role} "
                f"Placement Roadmap"
            ),

            "description": (
                ai_data.get("summary")
                or
                (
                    f"Personalized 90-day plan "
                    f"for {resolved_target_role}"
                )
            ),

            "summary": (
                ai_data.get("summary")
                or
                (
                    f"Personalized 90-day plan "
                    f"for {resolved_target_role}"
                )
            ),

            "start_date": start_dt,

            "end_date": end_dt,

            "duration_days": 90,

            "available_minutes_per_day": (
                available_minutes_per_day
            ),

            "total_estimated_hours": (
                total_estimated_hours
            ),

            "phases": phases,

            "weekly_goals": weekly_goals,

            "all_tasks": all_tasks,

            "milestones": ai_data.get(
                "milestones",
                [],
            ),

            "status": "active",

            "progress": 0.0,

            "analysis_version": 1,

            "validation_report": (
                ai_data.get(
                    "validation_report",
                    {},
                )
            ),

            "created_at": start_dt,

            "updated_at": start_dt,
        }

        # --------------------------------------------------------
        # 18. Save roadmap
        # --------------------------------------------------------

        created_roadmap = (
            await self.roadmap_repo.create(
                roadmap_record
            )
        )

        roadmap_id = (
            created_roadmap.get("roadmap_id")
            or created_roadmap.get("_id")
            or created_roadmap.get("id")
        )

        if not roadmap_id:

            raise RuntimeError(
                "Roadmap was created but no roadmap ID "
                "was returned."
            )

        # --------------------------------------------------------
        # 19. Generate daily tasks
        # --------------------------------------------------------

        if all_tasks:

            await self.task_service.generate_tasks_for_roadmap(
                user_id=user_id,
                roadmap_id=str(roadmap_id),
                roadmap_tasks=all_tasks,
                start_date=start_dt,
            )

        # --------------------------------------------------------
        # 20. Recalculate progress
        # --------------------------------------------------------

        try:

            await self.progress_service.recalculate_progress(
                user_id
            )

        except Exception as exc:

            logger.warning(
                "Progress recalculation failed after "
                "roadmap creation: %s",
                exc,
            )

        # --------------------------------------------------------
        # 21. Return created roadmap
        # --------------------------------------------------------

        return created_roadmap

    # ============================================================
    # BUILD PHASES
    # ============================================================

    def _build_phases(
        self,
        all_tasks: List[Dict[str, Any]],
        target_role: str,
        high_gaps: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:

        domain = resolve_role_domain(target_role)
        p1_goal, p2_goal, p3_goal = get_role_phase_goals(
            target_role,
            domain,
            high_gaps,
        )

        phases = []

        ranges = [
            (
                1,
                "Phase 1: Foundation",
                1,
                30,
                p1_goal,
            ),
            (
                2,
                "Phase 2: Skill Development",
                31,
                60,
                p2_goal,
            ),
            (
                3,
                "Phase 3: Placement Preparation",
                61,
                90,
                p3_goal,
            ),
        ]

        for (
            phase_number,
            name,
            start_day,
            end_day,
            goal,
        ) in ranges:

            phase_tasks = [
                task
                for task in all_tasks
                if start_day
                <= int(task.get("day", 1))
                <= end_day
            ]

            phases.append(
                {
                    "phase_number": phase_number,
                    "name": name,
                    "day_range": (
                        f"Days {start_day}-{end_day}"
                    ),
                    "start_day": start_day,
                    "end_day": end_day,
                    "goal": goal,
                    "tasks": phase_tasks,
                }
            )

        return phases

    # ============================================================
    # BUILD WEEKLY GOALS
    # ============================================================

    def _build_weekly_goals(
        self,
        all_tasks: List[Dict[str, Any]],
        target_role: str,
    ) -> List[Dict[str, Any]]:

        weeks: List[Dict[str, Any]] = []

        for week_number in range(1, 14):

            start_day = (
                (week_number - 1) * 7
            ) + 1

            end_day = min(
                90,
                week_number * 7,
            )

            week_tasks = [
                task
                for task in all_tasks
                if start_day
                <= int(task.get("day", 1))
                <= end_day
            ]

            skills = list(
                dict.fromkeys(
                    task.get("skill")
                    for task in week_tasks
                    if task.get("skill")
                )
            )

            if not skills:

                skills = [
                    "Core Engineering",
                    "Domain Foundations",
                ]

            task_titles = [
                task.get(
                    "title",
                    "",
                )
                for task in week_tasks[:4]
            ]

            estimated_minutes = sum(
                int(
                    task.get(
                        "estimated_minutes",
                        0,
                    )
                )
                for task in week_tasks
                if str(
                    task.get(
                        "estimated_minutes",
                        "0",
                    )
                ).isdigit()
            )

            estimated_hours = (
                estimated_minutes / 60
            )

            weeks.append(
                {
                    "week_number": week_number,

                    "objective": (
                        f"Week {week_number}: "
                        f"Focus on "
                        f"{', '.join(skills[:2])} "
                        f"for {target_role}."
                    ),

                    "skills": skills,

                    "tasks": task_titles,

                    "expected_outcome": (
                        f"Complete practice modules "
                        f"and coding benchmarks "
                        f"for Week {week_number}."
                    ),

                    "estimated_effort": (
                        f"{estimated_hours:.1f} Hours"
                    ),

                    "completion_percentage": 0.0,
                }
            )

        return weeks

    # ============================================================
    # DETERMINISTIC FALLBACK
    # ============================================================

    def _generate_deterministic_fallback(
        self,
        target_role: str,
        daily_minutes: int,
        skill_gap_doc: Dict[str, Any],
        profile_doc: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        priority_gaps = []

        if skill_gap_doc:

            gaps = skill_gap_doc.get(
                "priority_gaps",
                [],
            )

            if isinstance(gaps, list):

                for gap in gaps:
                    if isinstance(gap, dict) and gap.get("skill"):
                        priority_gaps.append(gap.get("skill"))
                    elif isinstance(gap, str) and gap:
                        priority_gaps.append(gap)

        preferred_lang = None

        if profile_doc:

            skills = profile_doc.get("skills") or []

            if isinstance(skills, list):

                for s in skills:
                    if (
                        isinstance(s, str)
                        and s.lower()
                        in [
                            "python",
                            "javascript",
                            "typescript",
                            "java",
                            "golang",
                            "go",
                            "c++",
                        ]
                    ):
                        preferred_lang = s
                        break

        daily_minutes = max(
            30,
            min(
                int(daily_minutes),
                480,
            ),
        )

        all_tasks = generate_90_day_curriculum(
            target_role=target_role,
            daily_minutes=daily_minutes,
            high_gaps=priority_gaps,
            preferred_language=preferred_lang,
        )

        phase1_tasks = [
            task
            for task in all_tasks
            if 1 <= task["day"] <= 30
        ]

        phase2_tasks = [
            task
            for task in all_tasks
            if 31 <= task["day"] <= 60
        ]

        phase3_tasks = [
            task
            for task in all_tasks
            if 61 <= task["day"] <= 90
        ]

        domain = resolve_role_domain(target_role)

        p1_goal, p2_goal, p3_goal = get_role_phase_goals(
            target_role,
            domain,
            priority_gaps,
        )

        total_mins = sum(
            task.get("estimated_minutes", 0)
            for task in all_tasks
        )

        total_hours = round(
            total_mins / 60.0,
            1,
        )

        summary = (
            f"Personalized 90-day placement preparation plan for '{target_role}' "
            f"totaling {total_hours} study hours across 3 phases ({daily_minutes} mins/day)."
        )

        return {
            "target_role": target_role,

            "total_days": 90,

            "available_minutes_per_day": daily_minutes,

            "total_estimated_hours": total_hours,

            "phases": [
                {
                    "phase_number": 1,
                    "name": "Phase 1: Foundation",
                    "day_range": "Days 1-30",
                    "start_day": 1,
                    "end_day": 30,
                    "goal": p1_goal,
                    "tasks": phase1_tasks,
                },
                {
                    "phase_number": 2,
                    "name": "Phase 2: Skill Development",
                    "day_range": "Days 31-60",
                    "start_day": 31,
                    "end_day": 60,
                    "goal": p2_goal,
                    "tasks": phase2_tasks,
                },
                {
                    "phase_number": 3,
                    "name": "Phase 3: Placement Preparation",
                    "day_range": "Days 61-90",
                    "start_day": 61,
                    "end_day": 90,
                    "goal": p3_goal,
                    "tasks": phase3_tasks,
                },
            ],

            "all_tasks": all_tasks,

            "summary": summary,

            "validation_report": {
                "status": "valid_fallback",
                "source": "deterministic_fallback",
                "valid_90_days": True,
                "daily_time_constraint_passed": True,
            },
        }

    # ============================================================
    # GET SUMMARY
    # ============================================================

    async def get_summary(
        self,
        user_id: str,
    ) -> Dict[str, Any]:

        active = await self.get_active_roadmap(
            user_id
        )

        if not active:

            return {
                "roadmap_id": None,
                "target_role": "Not Set",
                "total_days": 90,
                "current_day": 1,
                "phases_count": 0,
                "progress_percentage": 0.0,
                "status": "none",
                "current_phase_name": None,
            }

        start_dt = (
            active.get("start_date")
            or datetime.now(timezone.utc)
        )

        if isinstance(start_dt, str):

            try:

                start_dt = datetime.fromisoformat(
                    start_dt.replace(
                        "Z",
                        "+00:00",
                    )
                )

            except Exception:

                start_dt = datetime.now(
                    timezone.utc
                )

        if start_dt.tzinfo is None:

            start_dt = start_dt.replace(
                tzinfo=timezone.utc
            )

        current_day = max(
            1,
            min(
                90,
                (
                    datetime.now(
                        timezone.utc
                    ).date()
                    - start_dt.date()
                ).days
                + 1,
            ),
        )

        phases = active.get(
            "phases",
            [],
        )

        if not isinstance(phases, list):
            phases = []

        current_phase_name = (
            phases[0].get("name")
            if phases
            and isinstance(phases[0], dict)
            else "Phase 1: Foundation"
        )

        for phase in phases:

            if not isinstance(
                phase,
                dict,
            ):
                continue

            try:
                phase_start = int(
                    phase.get(
                        "start_day",
                        1,
                    )
                )
            except (TypeError, ValueError):
                phase_start = 1

            try:
                phase_end = int(
                    phase.get(
                        "end_day",
                        30,
                    )
                )
            except (TypeError, ValueError):
                phase_end = 30

            if (
                phase_start
                <= current_day
                <= phase_end
            ):

                current_phase_name = phase.get(
                    "name",
                    current_phase_name,
                )

                break

        return {
            "roadmap_id": (
                active.get("roadmap_id")
                or active.get("_id")
                or active.get("id")
            ),

            "target_role": active.get(
                "target_role",
                "Backend Developer",
            ),

            "total_days": active.get(
                "duration_days",
                90,
            ),

            "current_day": current_day,

            "phases_count": len(
                phases
            ),

            "progress_percentage": float(
                active.get(
                    "progress",
                    0.0,
                )
                or 0.0
            ),

            "status": active.get(
                "status",
                "active",
            ),

            "current_phase_name": current_phase_name,
        }

    # ============================================================
    # UPDATE ROADMAP
    # ============================================================

    async def update_roadmap(
        self,
        roadmap_id: str,
        user_id: str,
        data: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:

        return await self.roadmap_repo.update(
            roadmap_id,
            user_id,
            data,
        )

    # ============================================================
    # DELETE ROADMAP
    # ============================================================

    async def delete_roadmap(
        self,
        roadmap_id: str,
        user_id: str,
    ) -> bool:

        return await self.roadmap_repo.delete(
            roadmap_id,
            user_id,
        )

    # ============================================================
    # GET ROADMAP WEEKS
    # ============================================================

    async def get_roadmap_weeks(
        self,
        roadmap_id: str,
        user_id: str,
    ) -> List[Dict[str, Any]]:

        roadmap = await self.get_roadmap_by_id(
            roadmap_id,
            user_id,
        )

        if not roadmap:
            return []

        return roadmap.get(
            "weekly_goals",
            [],
        )

    # ============================================================
    # GET ROADMAP PHASES
    # ============================================================

    async def get_roadmap_phases(
        self,
        roadmap_id: str,
        user_id: str,
    ) -> List[Dict[str, Any]]:

        roadmap = await self.get_roadmap_by_id(
            roadmap_id,
            user_id,
        )

        if not roadmap:
            return []

        return roadmap.get(
            "phases",
            [],
        )