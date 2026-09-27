from typing import Optional, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


class UserRepository:
    """Repository layer for User collection in MongoDB."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db["users"]

    async def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.collection.find_one({"_id": user_id})
        if not doc and ObjectId.is_valid(user_id):
            doc = await self.collection.find_one({"_id": ObjectId(user_id)})
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        doc = await self.collection.find_one({"email": email})
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def create(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        if "_id" in user_data and user_data["_id"] is None:
            del user_data["_id"]
        result = await self.collection.insert_one(user_data)
        user_data["_id"] = str(result.inserted_id)
        return user_data

    async def update(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        filter_dict: Dict[str, Any] = {"_id": user_id}
        if ObjectId.is_valid(user_id):
            filter_dict = {"$or": [{"_id": user_id}, {"_id": ObjectId(user_id)}]}
        result = await self.collection.update_one(filter_dict, {"$set": update_data})
        return result.modified_count > 0 or result.matched_count > 0
