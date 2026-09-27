import logging
import re
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class AICommunicationEngine:
    """Local fallback communication articulation engine when standalone AI service is unavailable."""

    def __init__(self, llm_service: Optional[Any] = None) -> None:
        self.llm_service = llm_service

    def _get_val(self, data: Any, key: str, default: Any = None) -> Any:
        if isinstance(data, dict):
            return data.get(key, default)
        return getattr(data, key, default)

    def analyze_communication(self, request: Any) -> Dict[str, Any]:
        answer = self._get_val(request, "answer", "")
        words = answer.strip().split()
        word_count = len(words)

        filler_pattern = r"\b(um|uh|like|basically|actually|you know|sort of|kind of)\b"
        filler_matches = re.findall(filler_pattern, answer.lower())

        clarity = min(95, max(50, 65 + min(20, word_count // 5)))
        structure = 75 if word_count > 15 else 55
        conciseness = max(40, 90 - max(0, word_count - 60))
        tech_exp = 80 if any(kw in answer.lower() for kw in ["python", "api", "database", "service", "code", "architecture"]) else 65
        overall = int((clarity * 0.3) + (structure * 0.25) + (conciseness * 0.2) + (tech_exp * 0.25))

        improvements_list = [
            "State the core answer first before elaborating on details.",
            "Pause briefly instead of using filler words."
        ]
        improved_struct_str = "1. Main Takeaway: Directly answer the question.\n2. Technical Context: Describe key design choices.\n3. Outcome: State measurable results."

        return {
            "clarity": clarity,
            "clarity_score": clarity,
            "structure": structure,
            "structure_score": structure,
            "conciseness": conciseness,
            "conciseness_score": conciseness,
            "technical_explanation": tech_exp,
            "technical_explanation_score": tech_exp,
            "confidence_indicators": 80,
            "filler_words_count": len(filler_matches),
            "filler_word_count": len(filler_matches),
            "speaking_pace_wpm": 135,
            "estimated_wpm": 135,
            "overall_score": overall,
            "overall_communication_score": overall,
            "strengths": ["Used relevant technical terminology.", "Provided clear answer context."],
            "improvements": improvements_list,
            "weaknesses": ["Could improve concise phrasing and reduce filler words."],
            "actionable_improvements": improvements_list,
            "actionable_suggestions": improvements_list,
            "improved_answer_structure": improved_struct_str,
            "coaching_feedback": "Solid response articulation. Focus on delivering the core answer first.",
        }
