import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.communication_repository import CommunicationRepository
from app.repositories.profile_repository import ProfileRepository
from app.integrations.ai_client import AIClient, AIClientError

logger = logging.getLogger(__name__)


class CommunicationService:
    def __init__(self, db: AsyncIOMotorDatabase, ai_client: Optional[AIClient] = None) -> None:
        self.comm_repo = CommunicationRepository(db)
        self.profile_repo = ProfileRepository(db)
        self.ai_client = ai_client or AIClient()

    async def analyze_communication(self, user_id: str, question: str, answer: str) -> Dict[str, Any]:
        """Analyze student speech/text articulation for clarity, structure, conciseness, and filler words."""
        profile = await self.profile_repo.get_by_user_id(user_id) or {}
        target_role = profile.get("target_role") or "Backend Developer"

        analysis_id = f"comm_{user_id}_{int(datetime.now(timezone.utc).timestamp())}_{uuid.uuid4().hex[:4]}"

        payload = {
            "question": question,
            "answer": answer,
            "target_role": target_role,
        }

        try:
            res = await self.ai_client.analyze_communication(payload)
        except AIClientError as e:
            logger.warning("AI Service unavailable for communication analysis (%s), using local fallback.", e)
            from app.engines.communication_engine import AICommunicationEngine
            res = AICommunicationEngine().analyze_communication(payload)

        doc_data = {
            "analysis_id": analysis_id,
            "user_id": user_id,
            "question": question,
            "answer": answer,
            "clarity": res.get("clarity", 75),
            "structure": res.get("structure", 75),
            "conciseness": res.get("conciseness", 75),
            "technical_explanation": res.get("technical_explanation", 75),
            "confidence_indicators": res.get("confidence_indicators", 75),
            "filler_words_count": res.get("filler_words_count", 0),
            "speaking_pace_wpm": res.get("speaking_pace_wpm", 145),
            "overall_score": res.get("overall_score", 75),
            "strengths": res.get("strengths", []),
            "improvements": res.get("improvements", []),
            "improved_answer_structure": res.get("improved_answer_structure", ""),
            "actionable_suggestions": res.get("actionable_suggestions", []),
            "coaching_feedback": res.get("coaching_feedback", ""),
            "created_at": datetime.now(timezone.utc),
        }

        return await self.comm_repo.create_analysis(doc_data)

    async def get_summary(self, user_id: str) -> Dict[str, Any]:
        """Calculate aggregate performance metrics & recurring feedback across communication history."""
        history = await self.comm_repo.get_history_by_user_id(user_id, limit=50)
        if not history:
            return {
                "user_id": user_id,
                "total_analyses": 0,
                "average_overall_score": 75.0,
                "average_clarity": 75.0,
                "average_structure": 75.0,
                "average_conciseness": 75.0,
                "average_speaking_pace": 145.0,
                "recurring_improvements": ["Start with main answer before giving implementation details."],
                "top_strengths": ["Clear baseline technical terminology."],
            }

        n = len(history)
        total_overall = sum(h.get("overall_score", 75) for h in history)
        total_clarity = sum(h.get("clarity", 75) for h in history)
        total_structure = sum(h.get("structure", 75) for h in history)
        total_conciseness = sum(h.get("conciseness", 75) for h in history)
        total_wpm = sum(h.get("speaking_pace_wpm", 145) for h in history)

        all_improvements = []
        all_strengths = []
        for h in history:
            all_improvements.extend(h.get("improvements", []))
            all_strengths.extend(h.get("strengths", []))

        recurring_imp = list(dict.fromkeys(all_improvements))[:3]
        top_str = list(dict.fromkeys(all_strengths))[:3]

        return {
            "user_id": user_id,
            "total_analyses": n,
            "average_overall_score": round(total_overall / n, 1),
            "average_clarity": round(total_clarity / n, 1),
            "average_structure": round(total_structure / n, 1),
            "average_conciseness": round(total_conciseness / n, 1),
            "average_speaking_pace": round(total_wpm / n, 1),
            "recurring_improvements": recurring_imp,
            "top_strengths": top_str,
        }

    async def get_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        return await self.comm_repo.get_history_by_user_id(user_id, limit=limit)

    async def get_by_id(self, analysis_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.comm_repo.get_by_id(analysis_id, user_id=user_id)
