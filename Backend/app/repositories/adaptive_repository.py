from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


class AdaptiveRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db["adaptation_events"]

    async def create_event(self, data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        data["created_at"] = data.get("created_at", now)
        result = await self.collection.insert_one(data)
        data["_id"] = str(result.inserted_id)
        data["id"] = str(data.get("id") or data["_id"])
        await self.collection.update_one({"_id": result.inserted_id}, {"$set": {"id": data["id"]}})
        return data

    async def get_by_user_id(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        cursor = self.collection.find({"user_id": user_id}).sort("created_at", -1)
        docs = await cursor.to_list(length=limit)
        for d in docs:
            d["_id"] = str(d["_id"])
            d["id"] = str(d.get("id") or d["_id"])
        return docs

    async def get_latest_unapplied_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        cursor = self.collection.find({"user_id": user_id, "applied": False}).sort("created_at", -1)
        docs = await cursor.to_list(length=1)
        doc = docs[0] if docs else None
        if doc:
            doc["_id"] = str(doc["_id"])
            doc["id"] = str(doc.get("id") or doc["_id"])
        return doc


    async def mark_applied(self, event_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        or_conditions: List[Dict[str, Any]] = [{"_id": event_id}, {"id": event_id}]
        if ObjectId.is_valid(event_id):
            or_conditions.append({"_id": ObjectId(event_id)})
        query: Dict[str, Any] = {"user_id": user_id, "$or": or_conditions}
        await self.collection.update_one(query, {"$set": {"applied": True, "applied_at": datetime.now(timezone.utc)}})
        doc = await self.collection.find_one(query)
        if doc:
            doc["_id"] = str(doc["_id"])
            doc["id"] = str(doc.get("id") or doc["_id"])
        return doc
