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
            "github": ["github", "git", "commit", "repo", "repository", "code"],
            "leetcode": ["leetcode", "dsa", "algorithm", "problem", "solve", "tree", "graph", "dp"],
            "projects": ["project", "architecture", "microservice", "portfolio", "build"],
            "readiness": ["readiness", "score", "ready", "assessment", "tier"],
            "skill_gap": ["skill", "gap", "missing", "weakness", "learn", "study"],
            "daily_plan": ["today", "now", "task", "schedule", "work on", "do"],
            "roadmap": ["roadmap", "phase", "week", "month", "plan"],
            "interview": ["interview", "mock", "technical interview", "behavioral"],
            "communication": ["communication", "clarity", "speech", "english", "filler", "wpm"],
            "progress": ["progress", "streak", "improving", "level"],
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

        target_role = context.get("target_role") or "Backend Developer"
        profile = context.get("profile") or {}
        name = profile.get("name") or "Student"
        readiness = context.get("readiness") or {}
        score = readiness.get("overall_score") or 78
        gaps = context.get("skill_gaps", {}).get("top_gaps") or ["System Design", "Redis Caching"]
        tasks = context.get("today_tasks", {}).get("pending_tasks") or []
        first_task = tasks[0]["title"] if tasks else "Solve Graph Algorithms & Trace BFS/DFS"

        sources = [intent, "profile", "readiness"]
        evidence = [
            f"Target Role: {target_role}",
            f"Current Readiness Score: {score}/100",
            f"Top Priority Skill Gap: {gaps[0] if gaps else 'Core Computer Science'}",
        ]

        if intent == "daily_plan":
            answer = (
                f"Hello **{name}**! Today is focused on advancing your **{target_role}** readiness.\n\n"
                f"Your top priority task today is: **{first_task}**.\n\n"
                f"Completing this directly targets your key skill gap in **{gaps[0] if gaps else 'Core Concepts'}**."
            )
            actions = [
                {"label": "View Today's Tasks", "route": "/tasks"},
                {"label": "Open 90-Day Roadmap", "route": "/roadmap"},
            ]
        elif intent == "readiness":
            answer = (
                f"Your overall Placement Readiness score is currently **{score}/100** for **{target_role}**.\n\n"
                f"Your candidate telemetry shows solid progress. To push your score into Tier-1 candidate parity (85+), "
                f"focus on resolving your top skill gaps: **{', '.join(str(g) for g in gaps[:2])}**."
            )
            actions = [
                {"label": "Analyze Placement Readiness", "route": "/readiness"},
                {"label": "Review Skill Gaps", "route": "/skill-gaps"},
            ]
        elif intent == "skill_gap":
            answer = (
                f"Based on your telemetry, your primary skill gaps for **{target_role}** are:\n"
                f"1. **{gaps[0] if len(gaps)>0 else 'System Design'}**\n"
                f"{f'2. **{gaps[1]}**' if len(gaps)>1 else ''}\n\n"
                f"We recommend dedicating today's study block to these specific topics."
            )
            actions = [
                {"label": "View Skill Gap Report", "route": "/skill-gaps"},
                {"label": "Adapt Roadmap", "route": "/roadmap"},
            ]
        elif intent == "interview":
            answer = (
                f"For your **{target_role}** interview prep, focus on structuring your technical explanations clearly.\n\n"
                f"Start with the core architectural answer before delving into trade-offs or implementation details. "
                f"You can practice a live adaptive session in the Mock Interview module anytime."
            )
            actions = [
                {"label": "Start Mock Interview", "route": "/interview"},
                {"label": "Practice Communication", "route": "/communication"},
            ]
        else:
            answer = (
                f"Hello **{name}**! I am your AI Placement Copilot for **{target_role}**.\n\n"
                f"Your current readiness score is **{score}/100**. Today's focus is on completing your scheduled tasks "
                f"and addressing key technical gaps like **{gaps[0] if gaps else 'System Architecture'}**.\n\n"
                f"How can I help guide your preparation right now?"
            )
            actions = [
                {"label": "View Today's Tasks", "route": "/tasks"},
                {"label": "View Skill Gaps", "route": "/skill-gaps"},
            ]

        return {
            "answer": answer,
            "intent": intent,
            "context_sources": sources,
            "evidence": evidence,
            "suggested_actions": actions,
            "confidence": 0.92,
        }
