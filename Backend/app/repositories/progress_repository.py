from datetime import datetime, timezone
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase


class ProgressRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db["progress_records"]

    async def get_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.collection.find_one({"user_id": user_id})
        if doc:
            doc["_id"] = str(doc["_id"])
            if not doc.get("id"):
                doc["id"] = str(doc["_id"])
        return doc

    async def save_or_update(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        data["updated_at"] = now
        await self.collection.update_one({"user_id": user_id}, {"$set": data}, upsert=True)
        res = await self.get_by_user_id(user_id)
        return res or data

