from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


class CommunicationRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db["communication_analyses"]

    async def create_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        data["created_at"] = data.get("created_at", now)
        result = await self.collection.insert_one(data)
        data["_id"] = str(result.inserted_id)
        if "analysis_id" not in data or not data["analysis_id"]:
            data["analysis_id"] = data["_id"]
            await self.collection.update_one({"_id": result.inserted_id}, {"$set": {"analysis_id": data["_id"]}})
        data["id"] = str(data.get("id") or data["analysis_id"])
        return data

    async def get_by_id(self, analysis_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        or_conds: List[Dict[str, Any]] = [{"analysis_id": analysis_id}, {"_id": analysis_id}, {"id": analysis_id}]
        if ObjectId.is_valid(analysis_id):
            or_conds.append({"_id": ObjectId(analysis_id)})

        query: Dict[str, Any] = {"$or": or_conds}
        if user_id:
            query["user_id"] = user_id

        doc = await self.collection.find_one(query)
        if doc:
            doc["_id"] = str(doc["_id"])
            if "analysis_id" not in doc or not doc["analysis_id"]:
                doc["analysis_id"] = doc["_id"]
            doc["id"] = str(doc.get("id") or doc["analysis_id"])
        return doc

    async def get_history_by_user_id(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        cursor = self.collection.find({"user_id": user_id}).sort("created_at", -1)
        docs = await cursor.to_list(length=limit)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            if "analysis_id" not in doc or not doc["analysis_id"]:
                doc["analysis_id"] = doc["_id"]
            doc["id"] = str(doc.get("id") or doc["analysis_id"])
        return docs
