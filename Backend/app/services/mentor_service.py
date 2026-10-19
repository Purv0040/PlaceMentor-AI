import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status
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

    async def create_conversation(
        self,
        user_id: str,
        title: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new mentor conversation session."""
        conv_id = conversation_id or f"conv_{user_id}_{int(datetime.now(timezone.utc).timestamp())}_{uuid.uuid4().hex[:4]}"
        session_data = {
            "conversation_id": conv_id,
            "user_id": user_id,
            "title": title or "Placement Guidance Session",
            "status": "active",
        }
        return await self.mentor_repo.create_conversation(session_data)

    async def get_user_conversations(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch list of active/archived mentor conversations for authenticated user."""
        return await self.mentor_repo.get_conversations_by_user(user_id, limit=limit)

    async def get_conversation_detail(self, conversation_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch conversation metadata and all messages in chronological order for authenticated user."""
        conv = await self.mentor_repo.get_conversation_by_id(conversation_id, user_id=user_id)
        if not conv:
            return None
        messages = await self.mentor_repo.get_messages_by_conversation(conversation_id)
        conv["messages"] = messages
        return conv

    async def archive_conversation(self, conversation_id: str, user_id: str) -> bool:
        """Mark conversation as archived."""
        # First verify it exists and belongs to user
        conv = await self.mentor_repo.get_conversation_by_id(conversation_id, user_id=user_id)
        if not conv:
            return False
        return await self.mentor_repo.archive_conversation(conversation_id, user_id=user_id)

    async def send_message(
        self,
        user_id: str,
        conversation_id: str,
        message_text: str,
        target_role: Optional[str] = None,
        student_name: Optional[str] = None,
        client_history: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Send a message to the mentor, get context-aware AI guidance, and store conversation memory."""
        if not message_text or not message_text.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Message cannot be empty or whitespace only.",
            )

        clean_message = message_text.strip()

        # 1. Validate conversation ownership and status
        conv = await self.mentor_repo.get_conversation_by_id(conversation_id, user_id=user_id)
        if not conv:
            if conversation_id.startswith("session-") or conversation_id.startswith("local_"):
                conv = await self.create_conversation(
                    user_id=user_id,
                    title=clean_message[:30] + ("..." if len(clean_message) > 30 else ""),
                    conversation_id=conversation_id,
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Mentor conversation not found.",
                )
        elif conv.get("status") == "archived":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot send message to an archived conversation.",
            )

        # 2. Save user message
        user_msg_id = f"msg_user_{int(datetime.now(timezone.utc).timestamp())}_{uuid.uuid4().hex[:4]}"
        user_msg_data = {
            "message_id": user_msg_id,
            "conversation_id": conversation_id,
            "user_id": user_id,
            "role": "user",
            "content": clean_message,
        }
        await self.mentor_repo.add_message(user_msg_data)

        # 3. Build relevant student context
        student_context = await self.context_service.build_student_context(
            user_id,
            target_role_override=target_role,
            student_name_override=student_name
        )

        # 4. Fetch recent conversation memory (prior turns excluding the newly added message)
        recent_messages = await self.mentor_repo.get_messages_by_conversation(conversation_id, limit=12)
        prior_messages = [m for m in recent_messages if m.get("message_id") != user_msg_id]
        if prior_messages:
            history_payload = [
                {"role": m.get("role", "user"), "content": m.get("content", "")}
                for m in prior_messages[-6:]
                if m.get("content")
            ]
        elif client_history:
            history_payload = [
                {
                    "role": m.get("role") or ("user" if m.get("sender") == "user" else "assistant"),
                    "content": m.get("content") or m.get("text", "")
                }
                for m in client_history[-6:]
                if (m.get("content") or m.get("text")) and (m.get("content") or m.get("text", "")).strip() != clean_message
            ]
        else:
            history_payload = []

        # 5. Call AI service or local fallback engine
        ai_payload = {
            "message": clean_message,
            "student_context": student_context,
            "conversation_history": history_payload,
        }

        try:
            ai_res = await self.ai_client.chat_mentor(ai_payload)
        except AIClientError as e:
            err_str = str(e)
            logger.error("AI Service communication error during Mentor Chat: %s", err_str)
            if "429" in err_str or "rate limit" in err_str.lower():
                ai_res = {
                    "answer": "The AI Mentor is currently experiencing high demand (Rate limit reached). Please wait a moment and try asking again.",
                    "intent": "rate_limited",
                    "context_sources": [],
                    "evidence": ["Groq API Rate Limit Reached"],
                    "suggested_actions": ["Retry question in 30 seconds", "What can I do today?"],
                    "confidence": 0.0,
                }
            else:
                from app.engines.mentor_engine import AIMentorEngine
                ai_res = AIMentorEngine().chat(ai_payload)
        except Exception as e:
            logger.error("Unexpected error during AI Mentor generation: %s", e)
            from app.engines.mentor_engine import AIMentorEngine
            ai_res = AIMentorEngine().chat(ai_payload)

        answer = ai_res.get("answer", "I am analyzing your placement metrics. Please check your tasks and skill gaps.")
        intent = ai_res.get("intent", "general_placement")
        sources = ai_res.get("context_sources", ["profile", "readiness"])
        evidence = ai_res.get("evidence", [])
        raw_actions = ai_res.get("suggested_actions") or ai_res.get("recommended_actions") or []
        actions = []
        for a in raw_actions:
            if isinstance(a, str):
                actions.append({"label": a, "route": "/tasks"})
            elif isinstance(a, dict):
                actions.append({"label": a.get("label") or a.get("title") or "Action", "route": a.get("route") or "/tasks"})
        confidence = float(ai_res.get("confidence", 0.85))

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
            title_snippet = clean_message[:30] + ("..." if len(clean_message) > 30 else "")
            await self.mentor_repo.update_conversation_timestamp(conversation_id, title=title_snippet)

        return created_asst_msg

    async def ask_mentor(
        self,
        user_id: str,
        message_text: str,
        conversation_id: Optional[str] = None,
        target_role: Optional[str] = None,
        student_name: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Quick mentor query handler."""
        if not message_text or not message_text.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Message cannot be empty or whitespace only.",
            )

        clean_message = message_text.strip()

        if conversation_id:
            conv = await self.mentor_repo.get_conversation_by_id(conversation_id, user_id=user_id)
            if not conv:
                if conversation_id.startswith("session-") or conversation_id.startswith("local_"):
                    conv = await self.create_conversation(
                        user_id=user_id,
                        title=clean_message[:30] + ("..." if len(clean_message) > 30 else ""),
                        conversation_id=conversation_id,
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Mentor conversation not found.",
                    )
            elif conv.get("status") == "archived":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Cannot send message to an archived conversation.",
                )
        else:
            conv = await self.create_conversation(user_id, title=clean_message[:30] + ("..." if len(clean_message) > 30 else ""))
            conversation_id = conv["conversation_id"]

        asst_msg = await self.send_message(
            user_id=user_id,
            conversation_id=conversation_id,
            message_text=clean_message,
            target_role=target_role,
            student_name=student_name,
            client_history=conversation_history,
        )
        return {
            "answer": asst_msg.get("content", ""),
            "intent": asst_msg.get("intent", "general_placement"),
            "context_sources": asst_msg.get("context_sources", []),
            "evidence": asst_msg.get("evidence", []),
            "suggested_actions": asst_msg.get("suggested_actions", []),
            "confidence": asst_msg.get("confidence", 0.85),
            "conversation_id": conversation_id,
            "created_at": asst_msg.get("created_at"),
            "verified": asst_msg.get("verified", False),
        }
