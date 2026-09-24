"""
Adaptive Roadmap Engine.
Dynamically adjusts a student's 90-day placement preparation plan based on actual progress,
completion rates, performance trends, and transparent behavior state detection:
ON_TRACK, BEHIND, AHEAD, STRUGGLING, IMPROVING.

Maintains non-destructive lineage:
- Completed work is NEVER deleted or overwritten.
- Tracks `original_plan`, `current_plan`, and `adjustments[]`.
- Every adjustment includes id, timestamp, action_type, reason, old_task, new_task, impact_description.
"""
import copy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from app.role_requirements.roles import get_canonical_role_name
from app.schemas.adaptive import (
    AdaptiveRoadmapRequest,
    AdaptiveRoadmapResponse,
    AdaptiveThresholds,
    RoadmapAdjustment,
    StudentPerformancePayload,
    StudentProgressPayload,
)
from app.schemas.roadmap import (
    PersonalizedRoadmap,
    RoadmapGenerateRequest,
    RoadmapPhase,
    RoadmapTask,
)
from app.engines.roadmap_engine import PersonalizedRoadmapEngine
from app.services.llm_service import LLMService


class AdaptiveRoadmapEngine:
    """
    Adaptive Roadmap Engine.
    Executes transparent behavior state detection, strategy selection, non-destructive task adaptation,
    audit lineage recording, and Python daily time-budget post-validation.
    """

    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service or LLMService()
        self.roadmap_engine = PersonalizedRoadmapEngine(llm_service=self.llm_service)

    def adapt_roadmap(self, request: AdaptiveRoadmapRequest) -> AdaptiveRoadmapResponse:
        """
        Main entry point for POST /api/ai/roadmap/adapt.
        """
        # 1. Resolve thresholds (use provided or defaults)
        thresholds = request.thresholds or AdaptiveThresholds()

        # 2. Resolve target role
        target_role = get_canonical_role_name(request.target_role or "Backend Developer")

        # 3. Resolve or parse starting roadmap
        starting_roadmap = self._resolve_starting_roadmap(request, target_role)

        # 4. Preserve original plan for non-destructive audit lineage
        original_plan = copy.deepcopy(starting_roadmap)

        # 5. Detect student behavior state using transparent rules
        detected_state, state_desc = self._detect_student_state(
            progress=request.progress,
            performance=request.performance or StudentPerformancePayload(),
            thresholds=thresholds,
        )

        # 6. Prepare working copy of roadmap (current_plan)
        current_plan = copy.deepcopy(starting_roadmap)
        adjustments: List[RoadmapAdjustment] = []
        adj_counter = 1000

        # 7. Apply completed task statuses FIRST (non-destructive rule!)
        completed_ids = set(request.progress.completed_tasks or [])
        missed_ids = set(request.progress.missed_tasks or [])

        for task in current_plan.all_tasks:
            if task.id in completed_ids:
                task.status = "completed"

        # 8. Execute state-specific adaptation strategies
        if detected_state == "STRUGGLING":
            adj_counter = self._adapt_struggling(
                current_plan=current_plan,
                progress=request.progress,
                performance=request.performance or StudentPerformancePayload(),
                adjustments=adjustments,
                adj_counter=adj_counter,
            )
        elif detected_state == "BEHIND":
            adj_counter = self._adapt_behind(
                current_plan=current_plan,
                progress=request.progress,
                performance=request.performance or StudentPerformancePayload(),
                adjustments=adjustments,
                adj_counter=adj_counter,
                missed_ids=missed_ids,
            )
        elif detected_state == "AHEAD":
            adj_counter = self._adapt_ahead(
                current_plan=current_plan,
                progress=request.progress,
                performance=request.performance or StudentPerformancePayload(),
                adjustments=adjustments,
                adj_counter=adj_counter,
            )
        elif detected_state == "IMPROVING":
            adj_counter = self._adapt_improving(
                current_plan=current_plan,
                progress=request.progress,
                performance=request.performance or StudentPerformancePayload(),
                adjustments=adjustments,
                adj_counter=adj_counter,
            )
        else:
            # ON_TRACK
            adj_counter = self._adapt_on_track(
                current_plan=current_plan,
                progress=request.progress,
                performance=request.performance or StudentPerformancePayload(),
                adjustments=adjustments,
                adj_counter=adj_counter,
                missed_ids=missed_ids,
            )

        # 9. Ensure missed tasks are rescheduled if not completed
        adj_counter = self._reconcile_missed_tasks(
            current_plan=current_plan,
            progress=request.progress,
            missed_ids=missed_ids,
            completed_ids=completed_ids,
            adjustments=adjustments,
            adj_counter=adj_counter,
        )

        # 10. Re-validate daily time budgets & rebuild phase structures
        self._revalidate_and_rebuild_phases(current_plan, request.performance)

        # 11. Build executive adaptation summary
        summary = self._build_adaptation_summary(
            detected_state=detected_state,
            adjustments=adjustments,
            progress=request.progress,
        )

        return AdaptiveRoadmapResponse(
            target_role=target_role,
            detected_state=detected_state,
            state_description=state_desc,
            adaptation_summary=summary,
            original_plan=original_plan,
            current_plan=current_plan,
            adjustments=adjustments,
            thresholds_used=thresholds,
        )

    def _resolve_starting_roadmap(
        self, request: AdaptiveRoadmapRequest, target_role: str
    ) -> PersonalizedRoadmap:
        """Helper to resolve or generate the base PersonalizedRoadmap object."""
        if request.roadmap:
            if isinstance(request.roadmap, PersonalizedRoadmap):
                return request.roadmap
            if isinstance(request.roadmap, dict):
                return PersonalizedRoadmap.model_validate(request.roadmap)

        # Generate default baseline roadmap
        avail_min = (
            request.performance.available_time
            if request.performance and request.performance.available_time
            else 120
        )
        gen_req = RoadmapGenerateRequest(
            target_role=target_role,
            available_minutes_per_day=avail_min,
            profile_request=request.profile_request,
        )
        return self.roadmap_engine.generate_roadmap(gen_req)

    def _detect_student_state(
        self,
        progress: StudentProgressPayload,
        performance: StudentPerformancePayload,
        thresholds: AdaptiveThresholds,
    ) -> Tuple[str, str]:
        """Detect student behavior state using transparent rules."""
        rate = progress.completion_rate
        dsa_acc = None
        if performance.dsa_performance and "accuracy" in performance.dsa_performance:
            dsa_acc = float(performance.dsa_performance["accuracy"])

        # 1. Check trend for IMPROVING state
        if (
            progress.recent_completion_rate is not None
            and progress.previous_completion_rate is not None
        ):
            delta = progress.recent_completion_rate - progress.previous_completion_rate
            if delta >= thresholds.improving_delta_pct and rate >= thresholds.behind_completion_pct:
                return (
                    "IMPROVING",
                    f"Student progress is IMPROVING (+{delta:.1f}% recent gain in task completion rate).",
                )

        # 2. Check STRUGGLING triggers
        if rate < thresholds.struggling_completion_pct or (
            dsa_acc is not None and dsa_acc < thresholds.struggling_dsa_accuracy_pct
        ):
            reasons = []
            if rate < thresholds.struggling_completion_pct:
                reasons.append(
                    f"completion rate ({rate:.1f}%) is below {thresholds.struggling_completion_pct}% threshold"
                )
            if dsa_acc is not None and dsa_acc < thresholds.struggling_dsa_accuracy_pct:
                reasons.append(
                    f"DSA accuracy ({dsa_acc:.1f}%) is below {thresholds.struggling_dsa_accuracy_pct}% threshold"
                )
            desc = f"Student is STRUGGLING: {', '.join(reasons)}."
            return ("STRUGGLING", desc)

        # 3. Check BEHIND
        if thresholds.behind_completion_pct <= rate < thresholds.on_track_completion_pct:
            return (
                "BEHIND",
                f"Student is BEHIND: completion rate ({rate:.1f}%) is between {thresholds.behind_completion_pct}% and {thresholds.on_track_completion_pct}%.",
            )

        # 4. Check AHEAD
        if rate >= thresholds.ahead_completion_pct:
            return (
                "AHEAD",
                f"Student is AHEAD: completion rate ({rate:.1f}%) meets or exceeds the {thresholds.ahead_completion_pct}% threshold.",
            )

        # 5. Default ON_TRACK (80% <= rate < 90%)
        return (
            "ON_TRACK",
            f"Student is ON_TRACK: completion rate ({rate:.1f}%) meets target expectations ({thresholds.on_track_completion_pct}%).",
        )

    def _adapt_struggling(
        self,
        current_plan: PersonalizedRoadmap,
        progress: StudentProgressPayload,
        performance: StudentPerformancePayload,
        adjustments: List[RoadmapAdjustment],
        adj_counter: int,
    ) -> int:
        """Strategy for STRUGGLING students: reduce difficulty, inject prerequisites, reduce workload."""
        current_day = progress.current_day
        weak_topics = []
        if performance.dsa_performance and "weak_topics" in performance.dsa_performance:
            weak_topics = performance.dsa_performance.get("weak_topics", [])
        if performance.skill_gaps:
            weak_topics.extend(performance.skill_gaps)

        # Step A: Reduce task difficulty for upcoming pending tasks
        for task in current_plan.all_tasks:
            if task.day >= current_day and task.status != "completed":
                old_task_dict = task.model_dump()
                if task.difficulty == "Advanced":
                    task.difficulty = "Intermediate"
                    adj_counter += 1
                    adjustments.append(
                        RoadmapAdjustment(
                            id=f"adj_{adj_counter}",
                            action_type="difficulty_reduced",
                            reason=f"Student completion rate ({progress.completion_rate}%) is struggling; reduced task '{task.title}' difficulty from Advanced to Intermediate.",
                            old_task=old_task_dict,
                            new_task=task.model_dump(),
                            impact_description="Lowered cognitive difficulty to rebuild problem-solving confidence.",
                        )
                    )
                elif task.difficulty == "Intermediate":
                    task.difficulty = "Beginner"
                    adj_counter += 1
                    adjustments.append(
                        RoadmapAdjustment(
                            id=f"adj_{adj_counter}",
                            action_type="difficulty_reduced",
                            reason=f"Student completion rate ({progress.completion_rate}%) is struggling; reduced task '{task.title}' difficulty from Intermediate to Beginner.",
                            old_task=old_task_dict,
                            new_task=task.model_dump(),
                            impact_description="Lowered difficulty to foundational level to ensure task completion.",
                        )
                    )

        # Step B: Prerequisite Injection for weak topics
        if weak_topics:
            target_topic = weak_topics[0]
            inject_day = current_day
            prereq_task = RoadmapTask(
                id=f"task_prereq_d{inject_day}_1",
                day=inject_day,
                category="DSA" if "Array" in target_topic or "Tree" in target_topic or "DP" in target_topic else "CS Fundamentals",
                title=f"Prerequisite Review: {target_topic} Core Fundamentals",
                description=f"Step-by-step foundation review and guided practice on {target_topic} before attempting complex problems.",
                estimated_minutes=30,
                difficulty="Beginner",
                priority="High",
                skill=target_topic,
                status="pending",
            )
            current_plan.all_tasks.append(prereq_task)
            adj_counter += 1
            adjustments.append(
                RoadmapAdjustment(
                    id=f"adj_{adj_counter}",
                    action_type="prerequisite_injected",
                    reason=f"Injected prerequisite review task for weak topic '{target_topic}' to support struggling student on day {inject_day}.",
                    old_task=None,
                    new_task=prereq_task.model_dump(),
                    impact_description=f"Added foundational {target_topic} learning module to bridge identified skill gap.",
                )
            )

        return adj_counter

    def _adapt_behind(
        self,
        current_plan: PersonalizedRoadmap,
        progress: StudentProgressPayload,
        performance: StudentPerformancePayload,
        adjustments: List[RoadmapAdjustment],
        adj_counter: int,
        missed_ids: Set[str],
    ) -> int:
        """Strategy for BEHIND students: reschedule low-priority tasks, preserve high-priority tasks."""
        current_day = progress.current_day

        for task in current_plan.all_tasks:
            if task.day >= current_day and task.status != "completed":
                # If low or medium priority, stretch or move later
                if task.priority in ["Low", "Medium"] and (task.id in missed_ids or task.day == current_day):
                    old_task_dict = task.model_dump()
                    new_day = min(90, task.day + 3)
                    task.day = new_day
                    adj_counter += 1
                    adjustments.append(
                        RoadmapAdjustment(
                            id=f"adj_{adj_counter}",
                            action_type="task_rescheduled",
                            reason=f"Rescheduled {task.priority}-priority task '{task.title}' to Day {new_day} to lighten current workload for behind student ({progress.completion_rate}% completion).",
                            old_task=old_task_dict,
                            new_task=task.model_dump(),
                            impact_description="Deferred lower-priority topic to create room for critical high-priority gaps.",
                        )
                    )

        return adj_counter

    def _adapt_ahead(
        self,
        current_plan: PersonalizedRoadmap,
        progress: StudentProgressPayload,
        performance: StudentPerformancePayload,
        adjustments: List[RoadmapAdjustment],
        adj_counter: int,
    ) -> int:
        """Strategy for AHEAD students: accelerate future milestone tasks, introduce challenge difficulty."""
        current_day = progress.current_day

        # Step A: Upgrade difficulty on select upcoming pending tasks
        upgraded_count = 0
        for task in current_plan.all_tasks:
            if task.day >= current_day and task.status != "completed" and upgraded_count < 3:
                old_task_dict = task.model_dump()
                if task.difficulty == "Beginner":
                    task.difficulty = "Intermediate"
                    upgraded_count += 1
                    adj_counter += 1
                    adjustments.append(
                        RoadmapAdjustment(
                            id=f"adj_{adj_counter}",
                            action_type="difficulty_increased",
                            reason=f"Student is AHEAD ({progress.completion_rate}% completion rate); upgraded task '{task.title}' to Intermediate difficulty.",
                            old_task=old_task_dict,
                            new_task=task.model_dump(),
                            impact_description="Elevated task difficulty to accelerate student placement readiness.",
                        )
                    )
                elif task.difficulty == "Intermediate":
                    task.difficulty = "Advanced"
                    upgraded_count += 1
                    adj_counter += 1
                    adjustments.append(
                        RoadmapAdjustment(
                            id=f"adj_{adj_counter}",
                            action_type="difficulty_increased",
                            reason=f"Student is AHEAD ({progress.completion_rate}% completion rate); upgraded task '{task.title}' to Advanced difficulty.",
                            old_task=old_task_dict,
                            new_task=task.model_dump(),
                            impact_description="Introduced advanced challenge difficulty for top-performing student.",
                        )
                    )

        # Step B: Accelerate future milestone task from later day to current phase
        future_tasks = [
            t for t in current_plan.all_tasks
            if t.day > current_day + 10 and t.status != "completed" and t.priority == "High"
        ]
        if future_tasks:
            accel_task = future_tasks[0]
            old_dict = accel_task.model_dump()
            target_day = current_day + 1
            accel_task.day = target_day
            adj_counter += 1
            adjustments.append(
                RoadmapAdjustment(
                    id=f"adj_{adj_counter}",
                    action_type="task_accelerated",
                    reason=f"Accelerated high-priority milestone task '{accel_task.title}' from Day {old_dict['day']} to Day {target_day} due to ahead progress.",
                    old_task=old_dict,
                    new_task=accel_task.model_dump(),
                    impact_description="Pulled forward key placement milestone to maximize prep velocity.",
                )
            )

        return adj_counter

    def _adapt_improving(
        self,
        current_plan: PersonalizedRoadmap,
        progress: StudentProgressPayload,
        performance: StudentPerformancePayload,
        adjustments: List[RoadmapAdjustment],
        adj_counter: int,
    ) -> int:
        """Strategy for IMPROVING students: transition foundational tasks to intermediate/advanced momentum tasks."""
        current_day = progress.current_day
        upgraded_count = 0

        for task in current_plan.all_tasks:
            if task.day >= current_day and task.status != "completed" and upgraded_count < 2:
                if task.difficulty == "Beginner":
                    old_dict = task.model_dump()
                    task.difficulty = "Intermediate"
                    upgraded_count += 1
                    adj_counter += 1
                    adjustments.append(
                        RoadmapAdjustment(
                            id=f"adj_{adj_counter}",
                            action_type="difficulty_increased",
                            reason=f"Student showing strong IMPROVING momentum (+{progress.recent_completion_rate - progress.previous_completion_rate:.1f}% gain); upgraded task '{task.title}' from Beginner to Intermediate.",
                            old_task=old_dict,
                            new_task=task.model_dump(),
                            impact_description="Capitalized on recent momentum by transitioning task to intermediate complexity.",
                        )
                    )

        return adj_counter

    def _adapt_on_track(
        self,
        current_plan: PersonalizedRoadmap,
        progress: StudentProgressPayload,
        performance: StudentPerformancePayload,
        adjustments: List[RoadmapAdjustment],
        adj_counter: int,
        missed_ids: Set[str],
    ) -> int:
        """Strategy for ON_TRACK students: preserve baseline plan, handle minor schedule maintenance."""
        # Baseline plan is solid. Missed task reconciliation handles minor drifts.
        return adj_counter

    def _reconcile_missed_tasks(
        self,
        current_plan: PersonalizedRoadmap,
        progress: StudentProgressPayload,
        missed_ids: Set[str],
        completed_ids: Set[str],
        adjustments: List[RoadmapAdjustment],
        adj_counter: int,
    ) -> int:
        """Ensure all missed/skipped pending tasks are rescheduled to current or next day."""
        current_day = progress.current_day

        for task in current_plan.all_tasks:
            if task.id in missed_ids and task.id not in completed_ids:
                if task.day < current_day:
                    old_dict = task.model_dump()
                    task.day = current_day
                    adj_counter += 1
                    adjustments.append(
                        RoadmapAdjustment(
                            id=f"adj_{adj_counter}",
                            action_type="task_rescheduled",
                            reason=f"Rescheduled missed task '{task.title}' (Day {old_dict['day']}) to current Day {current_day} to prevent learning gaps.",
                            old_task=old_dict,
                            new_task=task.model_dump(),
                            impact_description="Carried over missed learning task into active day schedule.",
                        )
                    )

        return adj_counter

    def _revalidate_and_rebuild_phases(
        self,
        roadmap: PersonalizedRoadmap,
        performance: Optional[StudentPerformancePayload],
    ) -> None:
        """
        Re-sort tasks, validate daily minute limits, and rebuild phase groupings.
        """
        avail_minutes = performance.available_time if performance and performance.available_time else 120

        # Sort tasks by day and priority
        roadmap.all_tasks.sort(key=lambda t: (t.day, 0 if t.priority == "High" else (1 if t.priority == "Medium" else 2)))

        # Enforce daily time limit per day
        tasks_by_day: Dict[int, List[RoadmapTask]] = {}
        for t in roadmap.all_tasks:
            tasks_by_day.setdefault(t.day, []).append(t)

        for day_num in range(1, 91):
            day_tasks = tasks_by_day.get(day_num, [])
            day_total = sum(t.estimated_minutes for t in day_tasks)

            if day_total > avail_minutes:
                # Shift excessive non-completed tasks to next day
                excess = day_total - avail_minutes
                # Push lowest priority non-completed tasks forward
                pending_tasks = [t for t in day_tasks if t.status != "completed"]
                pending_tasks.sort(key=lambda t: 0 if t.priority == "Low" else (1 if t.priority == "Medium" else 2))

                shifted_minutes = 0
                for t in pending_tasks:
                    if shifted_minutes < excess and day_num < 90:
                        t.day = day_num + 1
                        shifted_minutes += t.estimated_minutes

        # Re-sort flat task list
        roadmap.all_tasks.sort(key=lambda t: (t.day, 0 if t.priority == "High" else (1 if t.priority == "Medium" else 2)))

        # Rebuild 3 phases
        p1_tasks = [t for t in roadmap.all_tasks if 1 <= t.day <= 30]
        p2_tasks = [t for t in roadmap.all_tasks if 31 <= t.day <= 60]
        p3_tasks = [t for t in roadmap.all_tasks if 61 <= t.day <= 90]

        roadmap.phases = [
            RoadmapPhase(
                phase_number=1,
                name="Phase 1: Foundation",
                day_range="Days 1-30",
                start_day=1,
                end_day=30,
                goal=f"Master foundational skills and core concepts for {roadmap.target_role}.",
                tasks=p1_tasks,
            ),
            RoadmapPhase(
                phase_number=2,
                name="Phase 2: Skill Development",
                day_range="Days 31-60",
                start_day=31,
                end_day=60,
                goal=f"Develop core technical proficiency and domain projects for {roadmap.target_role}.",
                tasks=p2_tasks,
            ),
            RoadmapPhase(
                phase_number=3,
                name="Phase 3: Placement Preparation",
                day_range="Days 61-90",
                start_day=61,
                end_day=90,
                goal=f"Advanced interview prep, mock assessments, and placement readiness execution for {roadmap.target_role}.",
                tasks=p3_tasks,
            ),
        ]

        # Update total hours
        roadmap.total_estimated_hours = round(
            sum(t.estimated_minutes for t in roadmap.all_tasks) / 60.0, 1
        )
        roadmap.validation_report = {
            "status": "VALIDATED",
            "total_tasks": len(roadmap.all_tasks),
            "completed_tasks_count": sum(1 for t in roadmap.all_tasks if t.status == "completed"),
            "daily_time_budget_minutes": avail_minutes,
            "max_daily_minutes_found": max(
                (sum(t.estimated_minutes for t in tasks_by_day.get(d, [])) for d in range(1, 91)),
                default=0,
            ),
        }

    def _build_adaptation_summary(
        self,
        detected_state: str,
        adjustments: List[RoadmapAdjustment],
        progress: StudentProgressPayload,
    ) -> str:
        """Synthesize an executive summary of adaptations made."""
        adj_count = len(adjustments)
        if adj_count == 0:
            return f"Student is {detected_state} with a completion rate of {progress.completion_rate:.1f}%. Baseline roadmap requires no adjustments."

        action_counts: Dict[str, int] = {}
        for a in adjustments:
            action_counts[a.action_type] = action_counts.get(a.action_type, 0) + 1

        actions_str = ", ".join([f"{k.replace('_', ' ')} ({v})" for k, v in action_counts.items()])
        return (
            f"Detected student state: {detected_state} (completion rate: {progress.completion_rate:.1f}%). "
            f"Executed {adj_count} explainable roadmap adjustments: {actions_str} while preserving all completed work."
        )
