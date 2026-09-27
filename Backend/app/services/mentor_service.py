import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.mentor_repository import MentorRepository
from app.services.mentor_context_service import MentorContextService
from app.integrations.ai_client import AIClient, AIClientError

logger = logging.getLogger(__name__)


class MentorService:
    def __init__(self, db: AsyncIOMotorDatabase, ai_client: Optional[AIClient] = None) -> None:
        self.mentor_repo = MentorRepository(db)
        self.context_service = MentorContextService(db)
        self.ai_client = ai_client or AIClient()

    async def create_conversation(self, user_id: str, title: Optional[str] = None) -> Dict[str, Any]:
        """Create a new mentor conversation session."""
        conv_id = f"conv_{user_id}_{int(datetime.now(timezone.utc).timestamp())}_{uuid.uuid4().hex[:4]}"
        session_data = {
            "conversation_id": conv_id,
            "user_id": user_id,
            "title": title or "Placement Guidance Session",
            "status": "active",
        }
        return await self.mentor_repo.create_conversation(session_data)

    async def get_user_conversations(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch list of active/archived mentor conversations for user."""
        return await self.mentor_repo.get_conversations_by_user(user_id, limit=limit)

    async def get_conversation_detail(self, conversation_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch conversation metadata and all messages in chronological order."""
        conv = await self.mentor_repo.get_conversation_by_id(conversation_id, user_id=user_id)
        if not conv:
            return None
        messages = await self.mentor_repo.get_messages_by_conversation(conversation_id)
        conv["messages"] = messages
        return conv

    async def archive_conversation(self, conversation_id: str, user_id: str) -> bool:
        """Mark conversation as archived."""
        return await self.mentor_repo.archive_conversation(conversation_id, user_id=user_id)

    async def send_message(
        self,
        user_id: str,
        conversation_id: str,
        message_text: str,
    ) -> Dict[str, Any]:
        """Send a message to the mentor, get context-aware AI guidance, and store conversation memory."""
        # 1. Validate conversation ownership
        conv = await self.mentor_repo.get_conversation_by_id(conversation_id, user_id=user_id)
        if not conv:
            raise ValueError("Conversation session not found.")

        # 2. Save user message
        user_msg_id = f"msg_user_{int(datetime.now(timezone.utc).timestamp())}_{uuid.uuid4().hex[:4]}"
        user_msg_data = {
            "message_id": user_msg_id,
            "conversation_id": conversation_id,
            "user_id": user_id,
            "role": "user",
            "content": message_text,
        }
        await self.mentor_repo.add_message(user_msg_data)

        # 3. Build relevant student context
        student_context = await self.context_service.build_student_context(user_id)

        # 4. Fetch recent conversation memory (last 5 messages)
        recent_messages = await self.mentor_repo.get_messages_by_conversation(conversation_id, limit=10)
        history_payload = [
            {"role": m.get("role", "user"), "content": m.get("content", "")}
            for m in recent_messages[-5:]
            if m.get("content")
        ]

        # 5. Call AI service or local fallback engine
        ai_payload = {
            "message": message_text,
            "student_context": student_context,
            "conversation_history": history_payload,
        }

        try:
            ai_res = await self.ai_client.chat_mentor(ai_payload)
        except AIClientError as e:
            logger.warning("AI Service unavailable for Mentor Chat (%s), using local fallback engine.", e)
            from app.engines.mentor_engine import AIMentorEngine
            ai_res = AIMentorEngine().chat(ai_payload)

        answer = ai_res.get("answer", "I am analyzing your placement metrics. Please check your tasks and skill gaps.")
        intent = ai_res.get("intent", "general_placement")
        sources = ai_res.get("context_sources", ["profile", "readiness"])
        evidence = ai_res.get("evidence", [])
        actions = ai_res.get("suggested_actions", [])
        confidence = ai_res.get("confidence", 0.9)

        # 6. Save assistant message
        asst_msg_id = f"msg_ai_{int(datetime.now(timezone.utc).timestamp())}_{uuid.uuid4().hex[:4]}"
        asst_msg_data = {
            "message_id": asst_msg_id,
            "conversation_id": conversation_id,
            "user_id": user_id,
            "role": "assistant",
            "content": answer,
            "intent": intent,
            "context_sources": sources,
            "evidence": evidence,
            "suggested_actions": actions,
            "confidence": confidence,
        }
        created_asst_msg = await self.mentor_repo.add_message(asst_msg_data)

        # 7. Update conversation title if first turn
        if len(recent_messages) <= 2:
            title_snippet = message_text[:30] + ("..." if len(message_text) > 30 else "")
            await self.mentor_repo.update_conversation_timestamp(conversation_id, title=title_snippet)

        return created_asst_msg

    async def ask_mentor(self, user_id: str, message_text: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Quick mentor query handler."""
        if not conversation_id:
            conv = await self.create_conversation(user_id, title=message_text[:30])
            conversation_id = conv["conversation_id"]

        asst_msg = await self.send_message(user_id=user_id, conversation_id=conversation_id, message_text=message_text)
        return {
            "answer": asst_msg.get("content", ""),
            "intent": asst_msg.get("intent", "general_placement"),
            "context_sources": asst_msg.get("context_sources", []),
            "evidence": asst_msg.get("evidence", []),
            "suggested_actions": asst_msg.get("suggested_actions", []),
            "confidence": asst_msg.get("confidence", 0.9),
            "conversation_id": conversation_id,
            "created_at": asst_msg.get("created_at"),
        }
