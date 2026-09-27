import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class AchievementEngine:
    """Pure deterministic achievement evaluation engine checking student telemetry against badge requirements."""

    def evaluate_user_achievements(
        self,
        definitions: List[Dict[str, Any]],
        unlocked_codes: List[str],
        context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Evaluate each achievement definition against current student context telemetry."""
        evaluated_achievements = []

        profile = context.get("profile") or {}
        resume = context.get("resume") or {}
        github = context.get("github") or {}
        leetcode = context.get("leetcode") or {}
        projects = context.get("projects") or []
        roadmap = context.get("roadmap") or {}
        tasks = context.get("tasks") or []
        progress = context.get("progress") or {}
        interviews = context.get("interviews") or []
        communication = context.get("communication") or []
        readiness = context.get("readiness") or {}

        completed_tasks_count = len([t for t in tasks if t.get("status") in ["completed", "done"] or t.get("completed") is True])
        current_streak = progress.get("streak_days") or progress.get("current_streak") or 0
        ats_score = resume.get("ats_score") or resume.get("score") or (resume.get("metrics") or {}).get("atsScore") or 0
        total_solved = leetcode.get("total_solved") or leetcode.get("solved_count") or (leetcode.get("metrics") or {}).get("totalSolved") or 0
        total_commits = github.get("total_commits") or github.get("commits") or (github.get("metrics") or {}).get("totalCommits") or 0
        overall_readiness = readiness.get("overall_score") or readiness.get("readiness_score") or progress.get("overall_progress_percent") or 0
        current_day = roadmap.get("current_day") or 0
        project_count = len(projects)
        interview_count = len(interviews)
        best_interview_score = max([i.get("overall_score") or i.get("score") or 0 for i in interviews], default=0)
        comm_count = len(communication)
        best_comm_clarity = max([c.get("overall_score") or c.get("clarity") or 0 for c in communication], default=0)

        for defn in definitions:
            code = defn.get("code")
            req_count = defn.get("required_count", 1)
            already_unlocked = code in unlocked_codes
            current_count = 0

            if code == "FIRST_STEP":
                current_count = 1 if profile.get("is_onboarded") or profile else 0
            elif code == "FIRST_RESUME":
                current_count = ats_score if ats_score > 0 else (1 if resume else 0)
            elif code == "GITHUB_CONNECTED":
                current_count = 1 if github.get("connected") or github.get("github_username") or github else 0
            elif code == "LEETCODE_CONNECTED":
                current_count = total_solved if total_solved > 0 else (1 if leetcode.get("username") or leetcode else 0)
            elif code == "FIRST_PROJECT":
                current_count = project_count
            elif code == "PROJECT_BUILDER":
                current_count = project_count
            elif code == "ROADMAP_STARTED":
                current_count = 1 if roadmap else 0
            elif code == "TASK_STARTER":
                current_count = completed_tasks_count
            elif code == "TASK_10":
                current_count = completed_tasks_count
            elif code == "WEEK_WARRIOR":
                current_count = current_streak
            elif code == "FIRST_INTERVIEW":
                current_count = interview_count
            elif code == "COMMUNICATION_START":
                current_count = comm_count
            elif code == "READINESS_TIER_1":
                current_count = overall_readiness

            # Determine unlocked state
            is_unlocked = already_unlocked or (current_count >= req_count and current_count > 0)
            pct = min(100.0, round((current_count / max(1, req_count)) * 100, 1)) if req_count > 0 else (100.0 if is_unlocked else 0.0)

            item = {
                "id": defn.get("id") or f"ach-{code}",
                "code": code,
                "title": defn.get("title"),
                "description": defn.get("description"),
                "category": defn.get("category"),
                "icon": defn.get("icon"),
                "color": defn.get("color"),
                "xp": defn.get("points", 100),
                "requiredCount": req_count,
                "currentCount": current_count if not is_unlocked else req_count,
                "unlocked": is_unlocked,
                "unlockedAt": "Unlocked" if is_unlocked else None,
                "route": defn.get("route"),
                "actionLabel": defn.get("action_label"),
                "progressPercentage": 100.0 if is_unlocked else pct,
                "is_newly_unlocked": is_unlocked and not already_unlocked,
            }
            evaluated_achievements.append(item)

        return evaluated_achievements
