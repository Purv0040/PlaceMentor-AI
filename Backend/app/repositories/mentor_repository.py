import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class MentorRepository:
    """Repository handling raw MongoDB queries for mentor_conversations and mentor_messages."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self.conversations = db["mentor_conversations"]
        self.messages = db["mentor_messages"]

    async def ensure_indexes(self) -> None:
        """Create indexes for performance and queries."""
        try:
            await self.conversations.create_index("user_id")
            await self.conversations.create_index([("user_id", 1), ("updated_at", -1)])
            await self.messages.create_index("conversation_id")
            await self.messages.create_index([("conversation_id", 1), ("created_at", 1)])
            logger.info("MentorRepository indexes created/verified.")
        except Exception as e:
            logger.warning("Error creating indexes in MentorRepository: %s", e)

    def _convert_doc(self, doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not doc:
            return None
        doc = dict(doc)
        if "_id" in doc:
            doc["id"] = str(doc["_id"])
            doc["_id"] = str(doc["_id"])
        return doc

    async def create_conversation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new conversation session record."""
        await self.ensure_indexes()
        now = datetime.now(timezone.utc)
        data["created_at"] = data.get("created_at", now)
        data["updated_at"] = now
        data["last_message_at"] = now
        result = await self.conversations.insert_one(data)
        data["_id"] = str(result.inserted_id)
        data["id"] = str(data.get("id") or data["conversation_id"])
        return data

    async def get_conversations_by_user(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch user's conversation list sorted newest first."""
        cursor = self.conversations.find({"user_id": user_id, "status": {"$ne": "deleted"}}).sort("updated_at", -1)
        docs = await cursor.to_list(length=limit)
        return [self._convert_doc(d) for d in docs if d]

    async def get_conversation_by_id(self, conversation_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetch single conversation by ID with optional user ownership validation."""
        or_conds: List[Dict[str, Any]] = [{"conversation_id": conversation_id}, {"_id": conversation_id}, {"id": conversation_id}]
        if ObjectId.is_valid(conversation_id):
            or_conds.append({"_id": ObjectId(conversation_id)})

        query: Dict[str, Any] = {"$or": or_conds}
        if user_id:
            query["user_id"] = user_id

        doc = await self.conversations.find_one(query)
        return self._convert_doc(doc)

    async def update_conversation_timestamp(self, conversation_id: str, title: Optional[str] = None) -> None:
        """Update last_message_at and updated_at for conversation."""
        now = datetime.now(timezone.utc)
        update_dict: Dict[str, Any] = {"updated_at": now, "last_message_at": now}
        if title:
            update_dict["title"] = title

        or_conds: List[Dict[str, Any]] = [{"conversation_id": conversation_id}, {"_id": conversation_id}, {"id": conversation_id}]
        if ObjectId.is_valid(conversation_id):
            or_conds.append({"_id": ObjectId(conversation_id)})

        await self.conversations.update_one({"$or": or_conds}, {"$set": update_dict})

    async def archive_conversation(self, conversation_id: str, user_id: str) -> bool:
        """Mark conversation status as archived."""
        or_conds: List[Dict[str, Any]] = [{"conversation_id": conversation_id}, {"_id": conversation_id}, {"id": conversation_id}]
        if ObjectId.is_valid(conversation_id):
            or_conds.append({"_id": ObjectId(conversation_id)})

        result = await self.conversations.update_one(
            {"user_id": user_id, "$or": or_conds},
            {"$set": {"status": "archived", "updated_at": datetime.now(timezone.utc)}}
        )
        return result.modified_count > 0 or result.matched_count > 0

    async def add_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save a new user or assistant message to mentor_messages collection."""
        await self.ensure_indexes()
        data["created_at"] = data.get("created_at", datetime.now(timezone.utc))
        result = await self.messages.insert_one(data)
        data["_id"] = str(result.inserted_id)
        data["id"] = str(data.get("id") or data["message_id"])

        await self.update_conversation_timestamp(data["conversation_id"])
        return data

    async def get_messages_by_conversation(self, conversation_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch all messages in a conversation sorted chronologically."""
        or_conds: List[Dict[str, Any]] = [{"conversation_id": conversation_id}]
        cursor = self.messages.find({"$or": or_conds}).sort("created_at", 1)
        docs = await cursor.to_list(length=limit)
        return [self._convert_doc(d) for d in docs if d]
