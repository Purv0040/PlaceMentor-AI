import logging
import random
import uuid
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class AIInterviewEngine:
    """Local fallback interview engine when standalone AI service is unavailable."""

    def __init__(self, llm_service: Optional[Any] = None) -> None:
        self.llm_service = llm_service

    def _get_val(self, data: Any, key: str, default: Any = None) -> Any:
        if isinstance(data, dict):
            return data.get(key, default)
        return getattr(data, key, default)

    def generate_question(self, request: Any) -> Dict[str, Any]:
        target_role = self._get_val(request, "target_role", "Backend Developer")
        interview_type = self._get_val(request, "interview_type", "technical")
        q_num = self._get_val(request, "question_number", 1)
        difficulty = self._get_val(request, "difficulty", "medium")

        default_questions = {
            "technical": [
                ("How would you design a scalable RESTful API with authentication and rate limiting?", "APIs & System Architecture"),
                ("Explain how database indexes improve query performance and when they might degrade performance.", "Databases"),
                ("What strategies do you use for caching database queries using Redis?", "Caching"),
            ],
            "behavioral": [
                ("Describe a situation where you had to debug a complex issue under tight deadlines.", "Problem Solving"),
                ("Tell me about a time you had a technical disagreement with a teammate and how you resolved it.", "Teamwork"),
            ],
            "hr": [
                ("Why are you interested in this target role and what are your key technical strengths?", "Culture Fit"),
                ("Where do you see your technical skillset evolving over the next two years?", "Career Growth"),
            ]
        }

        q_pool = default_questions.get(interview_type, default_questions["technical"])
        selected_q, category = q_pool[(q_num - 1) % len(q_pool)]

        return {
            "question_id": f"q_{q_num}_{uuid.uuid4().hex[:6]}",
            "question_number": q_num,
            "question": selected_q,
            "category": category,
            "skill": category,
            "difficulty": difficulty,
            "expected_focus": "Factual correctness and clear technical articulation",
            "hint": "Focus on step-by-step reasoning and trade-offs.",
        }

    def evaluate_answer(self, request: Any) -> Dict[str, Any]:
        ans = self._get_val(request, "answer", "")
        length = len(ans.strip())

        score = min(90, max(50, 60 + (length // 15)))

        return {
            "score": score,
            "correctness": score,
            "relevance": min(100, score + 5),
            "clarity": score,
            "depth": max(40, score - 5),
            "technical_accuracy": score,
            "communication_quality": score,
            "strengths": ["Identified core technical concepts clearly.", "Good logical flow."],
            "weaknesses": ["Could include more specific real-world examples."],
            "improvement_suggestions": ["Elaborate on trade-offs and edge cases."],
            "is_passable": score >= 60,
        }

    def complete_interview(self, request: Any) -> Dict[str, Any]:
        evals = self._get_val(request, "evaluations", [])
        scores = []
        for e in evals:
            sc = e.get("score") if isinstance(e, dict) else getattr(e, "score", 70)
            scores.append(sc or 70)
        scores = scores or [75]
        avg_score = int(sum(scores) / len(scores))

        return {
            "overall_score": avg_score,
            "category_scores": {
                "technical": min(100, avg_score + 2),
                "communication": avg_score,
                "problem_solving": max(50, avg_score - 2),
            },
            "strengths": ["Demonstrated clear technical fundamentals."],
            "weaknesses": ["Practice structuring system architecture answers systematically."],
            "recommendations": ["Review Redis caching strategies and database indexing."],
            "skill_gaps": [],
            "communication_feedback": {"clarity": avg_score, "structure": avg_score},
        }
