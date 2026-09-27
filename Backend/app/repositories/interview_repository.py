from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


class InterviewRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.sessions = db["interviews"]
        self.questions = db["interview_questions"]

    async def create_session(self, data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        data["created_at"] = data.get("created_at", now)
        data["updated_at"] = now
        result = await self.sessions.insert_one(data)
        data["_id"] = str(result.inserted_id)
        if "interview_id" not in data or not data["interview_id"]:
            data["interview_id"] = data["_id"]
            await self.sessions.update_one({"_id": result.inserted_id}, {"$set": {"interview_id": data["_id"]}})
        data["id"] = str(data.get("id") or data["interview_id"])
        return data

    async def get_session_by_id(self, interview_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        or_conds: List[Dict[str, Any]] = [{"interview_id": interview_id}, {"_id": interview_id}, {"id": interview_id}]
        if ObjectId.is_valid(interview_id):
            or_conds.append({"_id": ObjectId(interview_id)})

        query: Dict[str, Any] = {"$or": or_conds}
        if user_id:
            query["user_id"] = user_id

        doc = await self.sessions.find_one(query)
        if doc:
            doc["_id"] = str(doc["_id"])
            if "interview_id" not in doc or not doc["interview_id"]:
                doc["interview_id"] = doc["_id"]
            doc["id"] = str(doc.get("id") or doc["interview_id"])
        return doc

    async def get_active_session_by_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        cursor = self.sessions.find({"user_id": user_id, "status": "active"}).sort("created_at", -1)
        docs = await cursor.to_list(length=1)
        doc = docs[0] if docs else None
        if doc:
            doc["_id"] = str(doc["_id"])
            if "interview_id" not in doc or not doc["interview_id"]:
                doc["interview_id"] = doc["_id"]
            doc["id"] = str(doc.get("id") or doc["interview_id"])
        return doc

    async def update_session(self, interview_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        update_data["updated_at"] = now
        or_conds: List[Dict[str, Any]] = [{"interview_id": interview_id}, {"_id": interview_id}, {"id": interview_id}]
        if ObjectId.is_valid(interview_id):
            or_conds.append({"_id": ObjectId(interview_id)})

        query = {"user_id": user_id, "$or": or_conds}
        await self.sessions.update_one(query, {"$set": update_data})
        return await self.get_session_by_id(interview_id, user_id)

    async def get_history_by_user_id(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        cursor = self.sessions.find({"user_id": user_id}).sort("created_at", -1)
        docs = await cursor.to_list(length=limit)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            if "interview_id" not in doc or not doc["interview_id"]:
                doc["interview_id"] = doc["_id"]
            doc["id"] = str(doc.get("id") or doc["interview_id"])
        return docs

    # --- Questions Collection methods ---

    async def create_question(self, data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        data["created_at"] = data.get("created_at", now)
        result = await self.questions.insert_one(data)
        data["_id"] = str(result.inserted_id)
        if "question_id" not in data or not data["question_id"]:
            data["question_id"] = data["_id"]
            await self.questions.update_one({"_id": result.inserted_id}, {"$set": {"question_id": data["_id"]}})
        data["id"] = str(data.get("id") or data["question_id"])
        return data

    async def get_questions_for_interview(self, interview_id: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {"interview_id": interview_id}
        if user_id:
            query["user_id"] = user_id
        cursor = self.questions.find(query).sort("question_number", 1)
        docs = await cursor.to_list(length=100)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            if "question_id" not in doc or not doc["question_id"]:
                doc["question_id"] = doc["_id"]
            doc["id"] = str(doc.get("id") or doc["question_id"])
        return docs

    async def update_question_answer(
        self, question_id: str, user_id: str, answer: str, evaluation: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        or_conds: List[Dict[str, Any]] = [{"question_id": question_id}, {"_id": question_id}, {"id": question_id}]
        if ObjectId.is_valid(question_id):
            or_conds.append({"_id": ObjectId(question_id)})

        query = {"user_id": user_id, "$or": or_conds}
        update_data = {
            "answer": answer,
            "answer_submitted_at": now,
            "evaluation": evaluation,
        }
        await self.questions.update_one(query, {"$set": update_data})
        
        doc = await self.questions.find_one(query)
        if doc:
            doc["_id"] = str(doc["_id"])
            doc["id"] = str(doc.get("id") or doc.get("question_id") or doc["_id"])
        return doc
