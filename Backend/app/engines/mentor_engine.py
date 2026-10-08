import logging
import re
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class AIMentorEngine:
    """Local fallback mentor engine when standalone AI service is unavailable."""

    def __init__(self, llm_service: Optional[Any] = None) -> None:
        self.llm_service = llm_service
        self.rules = {
            "resume": ["resume", "cv", "ats", "formatting", "experience", "bullet"],
            "github": ["github", "git", "commit", "repo", "repository", "open source"],
            "leetcode": ["leetcode", "dsa", "algorithm", "problem", "solve", "tree", "graph", "dp", "dynamic programming"],
            "projects": ["project", "architecture", "microservice", "portfolio", "build", "system design project"],
            "readiness": ["readiness", "score", "ready", "assessment", "tier", "placement readiness"],
            "skill_gap": ["skill", "gap", "missing", "weakness", "weak topic", "learn", "study"],
            "daily_plan": ["today", "now", "task", "schedule", "work on", "do today"],
            "roadmap": ["roadmap", "phase", "week", "month", "plan", "milestone"],
            "interview": ["interview", "mock", "technical interview", "behavioral", "hr"],
            "communication": ["communication", "clarity", "speech", "english", "filler", "wpm", "speaking"],
            "progress": ["progress", "streak", "improving", "level", "completion"],
            "career": ["career", "company", "tier", "salary", "role", "job", "offer"],
        }

    def detect_intent(self, message: str) -> str:
        msg_lower = message.lower()
        for intent, kws in self.rules.items():
            if any(re.search(rf"\b{kw}\b", msg_lower) for kw in kws):
                return intent
        return "general_placement"

    def chat(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        message = request_payload.get("message", "")
        context = request_payload.get("student_context") or {}
        intent = self.detect_intent(message)

        profile = context.get("profile") or {}
        target_role = context.get("target_role") or profile.get("target_role")
        name = profile.get("name") or "Student"
        skills = profile.get("skills") or []
        
        readiness = context.get("readiness") or {}
        score = readiness.get("overall_score")
        readiness_label = readiness.get("readiness_label")

        skill_gaps_obj = context.get("skill_gaps") or {}
        gaps = skill_gaps_obj.get("top_gaps") or []

        leetcode_analysis = context.get("leetcode_analysis") or {}
        leetcode_weak = context.get("leetcode_weak_topics") or []

        github_analysis = context.get("github_analysis") or {}

        today_tasks_obj = context.get("today_tasks") or {}
        tasks = today_tasks_obj.get("pending_tasks") or []

        roadmap = context.get("roadmap") or {}
        progress = context.get("progress") or {}

        # Build dynamic context sources and evidence based on what is genuinely available
        sources: List[str] = []
        evidence: List[str] = []

        if target_role or skills:
            sources.append("profile")
            if target_role:
                evidence.append(f"Target Role: {target_role}")
            if skills:
                evidence.append(f"Key Skills: {', '.join(skills[:3])}")

        if score is not None:
            sources.append("readiness")
            evidence.append(f"Readiness Score: {score}/100" + (f" ({readiness_label})" if readiness_label else ""))

        if gaps:
            sources.append("skill_gaps")
            evidence.append(f"Top Skill Gaps: {', '.join(str(g) for g in gaps[:2])}")

        if leetcode_weak or leetcode_analysis:
            sources.append("leetcode")
            if leetcode_weak:
                evidence.append(f"LeetCode Weak Topic: {', '.join(str(w) for w in leetcode_weak[:2])}")

        if github_analysis:
            sources.append("github")
            if github_analysis.get("repo_count") is not None:
                evidence.append(f"GitHub Repositories: {github_analysis.get('repo_count')}")

        if tasks:
            sources.append("today_tasks")
            evidence.append(f"Pending Tasks: {len(tasks)} items (Top: {tasks[0].get('title')})")

        if roadmap.get("current_day") is not None or roadmap.get("total_days") is not None or roadmap.get("current_phase"):
            sources.append("roadmap")
            if roadmap.get("current_phase"):
                evidence.append(f"Roadmap Phase: {roadmap.get('current_phase')}")

        if progress.get("overall_progress_percent") is not None or progress.get("streak_days") is not None:
            sources.append("progress")
            if progress.get("streak_days") is not None:
                evidence.append(f"Active Streak: {progress.get('streak_days')} days")

        # Determine confidence deterministically based on available evidence and intent match
        # Base confidence is 0.75; increases with available telemetry coverage
        confidence_val = 0.72
        if "profile" in sources:
            confidence_val += 0.05
        if "readiness" in sources:
            confidence_val += 0.05
        if "skill_gaps" in sources or "leetcode" in sources:
            confidence_val += 0.05
        if "today_tasks" in sources or "roadmap" in sources:
            confidence_val += 0.05
        confidence = round(min(0.95, max(0.70, confidence_val)), 2)

        role_display = target_role if target_role else "your target role"

        # Generate contextual answers and actions
        if intent == "daily_plan":
            if tasks:
                first_task = tasks[0].get("title", "Practice placement problems")
                answer = (
                    f"Hello **{name}**! Today is focused on advancing your **{role_display}** preparation.\n\n"
                    f"Your top priority task today is: **{first_task}**."
                )
                if gaps:
                    answer += f"\n\nCompleting this directly helps address your skill gap in **{gaps[0]}**."
            else:
                answer = (
                    f"Hello **{name}**! You currently have no pending tasks scheduled for today for **{role_display}**.\n\n"
                    f"You can review your roadmap or practice key technical skills."
                )
            actions = [
                {"label": "View Today's Tasks", "route": "/tasks"},
                {"label": "Open Roadmap", "route": "/roadmap"},
            ]

        elif intent == "readiness":
            if score is not None:
                answer = (
                    f"Your overall Placement Readiness score is currently **{score}/100** for **{role_display}**.\n\n"
                )
                if gaps:
                    answer += f"To boost your readiness further, focus on closing your top gaps: **{', '.join(str(g) for g in gaps[:2])}**."
                else:
                    answer += "Keep practicing regularly with tasks and mock interviews to maintain top readiness."
            else:
                answer = (
                    f"Your Placement Readiness score for **{role_display}** is being calculated as you complete tasks and assessments.\n\n"
                    f"Complete today's roadmap tasks to establish your initial score benchmark."
                )
            actions = [
                {"label": "Analyze Placement Readiness", "route": "/readiness"},
                {"label": "Review Skill Gaps", "route": "/skill-gaps"},
            ]

        elif intent == "skill_gap":
            if gaps:
                gap_list_str = "\n".join([f"{idx+1}. **{gap}**" for idx, gap in enumerate(gaps[:3])])
                answer = (
                    f"Based on your profile analysis for **{role_display}**, your primary skill gaps are:\n"
                    f"{gap_list_str}\n\n"
                    f"We recommend allocating your next study session to address these topics."
                )
            else:
                answer = (
                    f"No critical skill gaps are currently recorded for **{role_display}**.\n\n"
                    f"Continue following your active roadmap and solving challenging problems."
                )
            actions = [
                {"label": "View Skill Gap Report", "route": "/skill-gaps"},
                {"label": "Adapt Roadmap", "route": "/roadmap"},
            ]

        elif intent in ["leetcode", "dsa"]:
            if leetcode_weak:
                weak_topic = leetcode_weak[0]
                answer = (
                    f"For your **{role_display}** DSA preparation, your analysis highlights **{weak_topic}** as an area for improvement.\n\n"
                    f"Focus on practicing 2-3 medium difficulty problems specifically in **{weak_topic}** today."
                )
                actions = [
                    {"label": f"Practice {weak_topic} on LeetCode", "route": "/leetcode"},
                    {"label": "View Today's Tasks", "route": "/tasks"},
                ]
            else:
                answer = (
                    f"For your **{role_display}** DSA preparation, maintain a balanced rhythm across data structures and algorithms.\n\n"
                    f"Focus on time and space complexity analysis during problem solving."
                )
                actions = [
                    {"label": "Open LeetCode Analysis", "route": "/leetcode"},
                    {"label": "View Today's Tasks", "route": "/tasks"},
                ]

        elif intent == "github":
            answer = (
                f"For **{role_display}**, ensure your GitHub demonstrates clean commit history, "
                f"descriptive README documentation, and well-structured codebases.\n\n"
                f"Review your repository analysis to optimize recruiter visibility."
            )
            actions = [
                {"label": "Analyze GitHub Profile", "route": "/github"},
                {"label": "View Projects", "route": "/projects"},
            ]

        elif intent == "resume":
            answer = (
                f"To strengthen your resume for **{role_display}**, use quantitative impact metrics "
                f"(e.g., 'reduced latency by 30%') and align your technical skills with job descriptions."
            )
            actions = [
                {"label": "Analyze Resume", "route": "/resume"},
            ]

        elif intent == "interview":
            answer = (
                f"For your **{role_display}** interview prep, practice explaining your thought process out loud.\n\n"
                f"Start with clarifying questions, discuss trade-offs, and structure system architectures clearly."
            )
            actions = [
                {"label": "Start Mock Interview", "route": "/interview"},
                {"label": "Practice Communication", "route": "/communication"},
            ]

        elif intent == "roadmap":
            if roadmap.get("current_day") is not None and roadmap.get("total_days") is not None:
                day_info = f"Day {roadmap.get('current_day')} of {roadmap.get('total_days')}"
                answer = (
                    f"You are currently on **{day_info}** of your **{role_display}** roadmap.\n\n"
                    f"Stay consistent with daily tasks to maintain your target completion trajectory."
                )
            else:
                answer = (
                    f"Your **{role_display}** roadmap outlines the step-by-step milestones to prepare for top placement opportunities.\n\n"
                    f"Check your roadmap dashboard to view upcoming milestones and phases."
                )
            actions = [
                {"label": "Open Roadmap", "route": "/roadmap"},
                {"label": "View Today's Tasks", "route": "/tasks"},
            ]

        else:
            answer = f"Hello **{name}**! I am your AI Placement Mentor for **{role_display}**.\n\n"
            if score is not None:
                answer += f"Your current readiness score is **{score}/100**. "
            if tasks:
                answer += f"Today's scheduled focus includes **{tasks[0].get('title', 'learning tasks')}**.\n\n"
            else:
                answer += f"I am here to help you optimize your learning roadmap, DSA skills, resume, and interview prep.\n\n"
            answer += "How can I help guide your placement preparation today?"

            actions = [
                {"label": "View Today's Tasks", "route": "/tasks"},
                {"label": "Check Readiness", "route": "/readiness"},
            ]

        return {
            "answer": answer,
            "intent": intent,
            "context_sources": sources,
            "evidence": evidence,
            "suggested_actions": actions,
            "confidence": confidence,
        }
