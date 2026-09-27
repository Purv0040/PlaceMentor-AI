from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


class RoadmapRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db["roadmaps"]

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        data["created_at"] = data.get("created_at", now)
        data["updated_at"] = now
        if "_id" in data and isinstance(data["_id"], str):
            try:
                data["_id"] = ObjectId(data["_id"])
            except Exception:
                pass
        result = await self.collection.insert_one(data)
        data["_id"] = str(result.inserted_id)
        data["id"] = data["_id"]
        if "roadmap_id" not in data or not data["roadmap_id"]:
            data["roadmap_id"] = data["_id"]
            await self.collection.update_one({"_id": result.inserted_id}, {"$set": {"roadmap_id": data["_id"]}})
        return data

    async def get_by_id(self, roadmap_id: str) -> Optional[Dict[str, Any]]:
        query: Dict[str, Any] = {"roadmap_id": roadmap_id}
        if ObjectId.is_valid(roadmap_id):
            query = {"$or": [{"_id": ObjectId(roadmap_id)}, {"roadmap_id": roadmap_id}]}
        doc = await self.collection.find_one(query)
        if doc:
            doc["_id"] = str(doc["_id"])
            if "roadmap_id" not in doc or not doc["roadmap_id"]:
                doc["roadmap_id"] = doc["_id"]
            doc["id"] = str(doc.get("id") or doc["_id"])
        return doc

    async def get_active_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        cursor = self.collection.find({"user_id": user_id, "status": "active"}).sort("created_at", -1)
        docs = await cursor.to_list(length=1)
        doc = docs[0] if docs else None
        if doc:
            doc["_id"] = str(doc["_id"])
            if "roadmap_id" not in doc or not doc["roadmap_id"]:
                doc["roadmap_id"] = doc["_id"]
            doc["id"] = str(doc.get("id") or doc["_id"])
        return doc


    async def get_all_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        cursor = self.collection.find({"user_id": user_id}).sort("created_at", -1)
        docs = await cursor.to_list(length=100)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            if "roadmap_id" not in doc or not doc["roadmap_id"]:
                doc["roadmap_id"] = doc["_id"]
            doc["id"] = str(doc.get("id") or doc["_id"])
        return docs

    async def supersede_active_roadmaps(self, user_id: str) -> int:
        now = datetime.now(timezone.utc)
        res = await self.collection.update_many(
            {"user_id": user_id, "status": "active"},
            {"$set": {"status": "superseded", "updated_at": now, "superseded_at": now}}
        )
        return res.modified_count

    async def update(self, roadmap_id: str, user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        data["updated_at"] = now
        query: Dict[str, Any] = {"user_id": user_id, "roadmap_id": roadmap_id}
        if ObjectId.is_valid(roadmap_id):
            query = {"user_id": user_id, "$or": [{"_id": ObjectId(roadmap_id)}, {"roadmap_id": roadmap_id}]}

        await self.collection.update_one(query, {"$set": data})
        return await self.get_by_id(roadmap_id)

    async def delete(self, roadmap_id: str, user_id: str) -> bool:
        query: Dict[str, Any] = {"user_id": user_id, "roadmap_id": roadmap_id}
        if ObjectId.is_valid(roadmap_id):
            query = {"user_id": user_id, "$or": [{"_id": ObjectId(roadmap_id)}, {"roadmap_id": roadmap_id}]}
        res = await self.collection.delete_one(query)
        return res.deleted_count > 0
