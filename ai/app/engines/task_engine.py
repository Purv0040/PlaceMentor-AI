"""
Deterministic Daily Task Engine.
Calculates today's prioritized, evidence-backed preparation tasks based on a student's 90-day roadmap,
current day, completed tasks, missed tasks, and available daily time budget.
"""
from typing import Any, Dict, List, Optional, Set, Tuple

from app.role_requirements.roles import get_canonical_role_name
from app.schemas.skills import StudentIntelligenceProfile, ProfileBuildRequest
from app.schemas.skill_gap import SkillGapAnalysis
from app.schemas.roadmap import PersonalizedRoadmap, RoadmapTask, RoadmapGenerateRequest
from app.schemas.daily_task import TodayTaskItem, TodayTasksRequest, TodayTasksResponse
from app.services.llm_service import LLMService
from app.engines.roadmap_engine import PersonalizedRoadmapEngine
from app.engines.skill_gap_engine import SkillGapEngine


class DailyTaskEngine:
    """
    Deterministic Daily Task Engine.
    Filters completed tasks, ranks overdue & current day candidates using 5-level priority rules,
    and enforces strict daily time budget constraints.
    """

    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service or LLMService()
        self.roadmap_engine = PersonalizedRoadmapEngine(llm_service=self.llm_service)
        self.skill_gap_engine = SkillGapEngine(llm_service=self.llm_service)

    def get_today_tasks(self, request: TodayTasksRequest) -> TodayTasksResponse:
        """
        Main entry point to calculate today's prioritized tasks plan.
        """
        canonical_role = get_canonical_role_name(request.target_role or "Backend Developer")
        current_day = max(1, min(90, request.current_day))
        available_time = request.available_time
        completed_set: Set[str] = set(request.completed_tasks)
        missed_set: Set[str] = set(request.missed_tasks)

        # 1. Resolve or generate 90-day roadmap
        roadmap = self._resolve_roadmap(request, canonical_role, available_time)

        # 2. Resolve skill gaps
        high_gap_skills: Set[str] = set()
        if request.skill_gaps:
            if isinstance(request.skill_gaps, SkillGapAnalysis):
                high_gap_skills = {s.lower() for s in request.skill_gaps.high_priority}
            elif isinstance(request.skill_gaps, dict):
                high_gap_skills = {s.lower() for s in request.skill_gaps.get("high_priority", [])}

        # 3. Collect candidate tasks across overdue, current day, and upcoming
        candidates = self._collect_candidate_tasks(
            roadmap=roadmap,
            current_day=current_day,
            completed_set=completed_set,
            missed_set=missed_set,
            high_gap_skills=high_gap_skills,
            upcoming_priorities=request.upcoming_priorities,
        )

        # 4. Rank candidates deterministically using 5-level priority rules
        ranked_candidates = self._rank_candidates(candidates, high_gap_skills, current_day)

        # 5. Greedy time-budget selection (sum(estimated_minutes) <= available_time)
        selected_today_tasks, overdue_rescheduled_count = self._select_within_time_budget(
            ranked_candidates=ranked_candidates,
            available_time=available_time,
            current_day=current_day,
        )

        total_scheduled = sum(t.estimated_minutes for t in selected_today_tasks)

        # 6. Generate reasoning and summary
        reasoning = self._generate_reasoning(
            selected_tasks=selected_today_tasks,
            current_day=current_day,
            available_time=available_time,
            total_scheduled=total_scheduled,
            overdue_count=overdue_rescheduled_count,
            completed_count=len(completed_set),
        )

        summary = (
            f"Today's plan (Day {current_day}) schedules {len(selected_today_tasks)} task(s) totaling {total_scheduled} minutes "
            f"out of {available_time} available study minutes for {canonical_role}. "
            f"Includes {overdue_rescheduled_count} overdue task carryover(s)."
        )

        return TodayTasksResponse(
            target_role=canonical_role,
            current_day=current_day,
            available_time=available_time,
            total_scheduled_minutes=total_scheduled,
            tasks=selected_today_tasks,
            overdue_rescheduled_count=overdue_rescheduled_count,
            completed_count_so_far=len(completed_set),
            summary=summary,
            reasoning=reasoning,
        )

    # -----------------------------------------------------------------------
    # Helper functions
    # -----------------------------------------------------------------------

    def _resolve_roadmap(
        self, request: TodayTasksRequest, canonical_role: str, available_time: int
    ) -> PersonalizedRoadmap:
        if request.roadmap:
            if isinstance(request.roadmap, PersonalizedRoadmap):
                return request.roadmap
            elif isinstance(request.roadmap, dict) and request.roadmap:
                try:
                    return PersonalizedRoadmap.model_validate(request.roadmap)
                except Exception:
                    pass

        # Generate roadmap on the fly if missing
        return self.roadmap_engine.generate_roadmap(
            RoadmapGenerateRequest(
                target_role=canonical_role,
                available_minutes_per_day=available_time,
                profile_request=request.profile_request,
            )
        )

    def _collect_candidate_tasks(
        self,
        roadmap: PersonalizedRoadmap,
        current_day: int,
        completed_set: Set[str],
        missed_set: Set[str],
        high_gap_skills: Set[str],
        upcoming_priorities: List[str],
    ) -> List[Tuple[RoadmapTask, str, int]]:
        """
        Collects candidate tasks from roadmap.
        Returns list of (RoadmapTask, reason_template, day_origin).
        """
        candidates: List[Tuple[RoadmapTask, str, int]] = []

        all_tasks = roadmap.all_tasks if roadmap.all_tasks else []
        if not all_tasks and roadmap.phases:
            for phase in roadmap.phases:
                all_tasks.extend(phase.tasks)

        for task in all_tasks:
            # Filter out already completed tasks
            if task.id in completed_set:
                continue

            # Candidate Pool A: Overdue / Missed Tasks (from days < current_day)
            if task.day < current_day and task.id in missed_set:
                reason = f"Overdue High-priority task carried over from Day {task.day}" if task.priority == "High" else f"Overdue task carried over from Day {task.day}"
                candidates.append((task, reason, task.day))

            # Candidate Pool B: Today's Scheduled Tasks (day == current_day)
            elif task.day == current_day:
                reason = f"Scheduled core task for Day {current_day}"
                candidates.append((task, reason, task.day))

            # Candidate Pool C: Upcoming Tasks (days current_day+1 to current_day+3) if high priority gap
            elif current_day < task.day <= current_day + 3 and (task.skill.lower() in high_gap_skills or task.priority == "High"):
                reason = f"Upcoming priority task for Day {task.day} targeting gap '{task.skill}'"
                candidates.append((task, reason, task.day))

        return candidates

    def _rank_candidates(
        self,
        candidates: List[Tuple[RoadmapTask, str, int]],
        high_gap_skills: Set[str],
        current_day: int,
    ) -> List[Tuple[RoadmapTask, str, int, int]]:
        """
        Ranks candidate tasks using deterministic 5-level priority rules.
        Returns list of (RoadmapTask, reason, day_origin, rank_level).
        """
        ranked: List[Tuple[RoadmapTask, str, int, int]] = []

        for task, default_reason, origin_day in candidates:
            skill_lower = task.skill.lower()
            is_critical_gap = skill_lower in high_gap_skills or task.priority == "High"
            is_overdue = origin_day < current_day
            is_milestone = (origin_day % 10 == 0) or task.category in ["Interview", "System Design"]

            # Deterministic 5-Level Priority Ranking:
            # 1. Overdue Important Tasks & Critical Skill Gaps
            # 2. Critical Skill Gaps (Current Day)
            # 3. Prerequisites
            # 4. Upcoming Milestones
            # 5. Balanced Preparation Tasks

            if is_overdue and (is_critical_gap or task.priority in ["High", "Medium"]):
                rank = 1
                reason = f"Overdue High-priority task carried over from Day {origin_day}"
            elif is_critical_gap:
                rank = 2
                reason = default_reason if "gap" in default_reason.lower() else f"Prioritized critical skill gap: '{task.skill}'"
            elif task.category in ["Programming", "DSA"] and task.difficulty == "Beginner":
                rank = 3
                reason = f"Prerequisite foundation task for '{task.skill}'"
            elif is_milestone:
                rank = 4
                reason = f"Milestone placement prep for '{task.title}'"
            else:
                rank = 5
                reason = default_reason

            ranked.append((task, reason, origin_day, rank))

        # Sort by: 1) rank level ascending (1 is highest priority), 2) original priority ("High" < "Medium" < "Low"), 3) origin day
        prio_map = {"High": 1, "Medium": 2, "Low": 3}
        ranked.sort(key=lambda item: (item[3], prio_map.get(item[0].priority, 2), item[2]))

        return ranked

    def _select_within_time_budget(
        self,
        ranked_candidates: List[Tuple[RoadmapTask, str, int, int]],
        available_time: int,
        current_day: int,
    ) -> Tuple[List[TodayTaskItem], int]:
        """
        Greedy time-budget selection algorithm guaranteeing sum(estimated_minutes) <= available_time.
        """
        selected_today_tasks: List[TodayTaskItem] = []
        remaining_time = available_time
        overdue_count = 0
        seen_ids: Set[str] = set()

        for task, reason, origin_day, rank in ranked_candidates:
            if task.id in seen_ids:
                continue

            if task.estimated_minutes <= remaining_time:
                item = TodayTaskItem(
                    id=task.id,
                    title=task.title,
                    category=task.category,
                    estimated_minutes=task.estimated_minutes,
                    priority=task.priority,
                    reason=reason,
                    skill=task.skill,
                    source_roadmap_day=origin_day,
                    status=task.status,
                )
                selected_today_tasks.append(item)
                seen_ids.add(task.id)
                remaining_time -= task.estimated_minutes
                if origin_day < current_day:
                    overdue_count += 1
            elif remaining_time >= 15:
                # Scale down remaining mins if enough budget left for a partial session
                scaled_mins = remaining_time
                item = TodayTaskItem(
                    id=task.id,
                    title=task.title,
                    category=task.category,
                    estimated_minutes=scaled_mins,
                    priority=task.priority,
                    reason=f"{reason} (Scaled to fit remaining {scaled_mins} mins budget)",
                    skill=task.skill,
                    source_roadmap_day=origin_day,
                    status=task.status,
                )
                selected_today_tasks.append(item)
                seen_ids.add(task.id)
                remaining_time = 0
                if origin_day < current_day:
                    overdue_count += 1
                break

            if remaining_time == 0:
                break

        return selected_today_tasks, overdue_count

    def _generate_reasoning(
        self,
        selected_tasks: List[TodayTaskItem],
        current_day: int,
        available_time: int,
        total_scheduled: int,
        overdue_count: int,
        completed_count: int,
    ) -> List[str]:
        reasoning: List[str] = [
            f"Daily study time budget of {available_time} minutes strictly enforced ({total_scheduled} mins scheduled).",
        ]

        if overdue_count > 0:
            reasoning.append(f"Carried over {overdue_count} overdue task(s) from previous days without overloading daily budget.")

        if completed_count > 0:
            reasoning.append(f"Excluded {completed_count} previously completed task(s).")

        cats = sorted(list({t.category for t in selected_tasks}))
        if cats:
            reasoning.append(f"Maintained balanced preparation across categories: {', '.join(cats)}.")

        return reasoning
