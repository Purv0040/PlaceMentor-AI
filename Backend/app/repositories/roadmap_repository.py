from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


class RoadmapRepository:

    def __init__(
        self,
        db: AsyncIOMotorDatabase,
    ) -> None:
        self.collection = db["roadmaps"]

    @staticmethod
    def _serialize_document(
        document: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """
        Convert MongoDB ObjectId to string.

        Datetime values are intentionally preserved as datetime objects.
        Pydantic/FastAPI will serialize them in API responses.
        """

        if not document:
            return document

        document["_id"] = str(document["_id"])

        if not document.get("roadmap_id"):
            document["roadmap_id"] = document["_id"]

        document["id"] = str(
            document.get("id")
            or document["_id"]
        )

        return document

    @classmethod
    def _serialize_documents(
        cls,
        documents: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:

        return [
            cls._serialize_document(doc)
            for doc in documents
        ]

    async def create(
        self,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:

        # Never mutate caller's dictionary directly.
        data = dict(data)

        now = datetime.now(timezone.utc)

        data["created_at"] = data.get(
            "created_at",
            now,
        )

        data["updated_at"] = now

        existing_id = data.get("_id")

        if existing_id and isinstance(existing_id, str):
            if ObjectId.is_valid(existing_id):
                data["_id"] = ObjectId(existing_id)
            else:
                data.pop("_id", None)

        result = await self.collection.insert_one(data)

        document_id = result.inserted_id

        data["_id"] = str(document_id)

        if not data.get("roadmap_id"):
            data["roadmap_id"] = str(document_id)

            await self.collection.update_one(
                {"_id": document_id},
                {
                    "$set": {
                        "roadmap_id": str(document_id)
                    }
                },
            )

        data["id"] = str(
            data.get("id")
            or document_id
        )

        return data

    async def get_by_id(
        self,
        roadmap_id: str,
    ) -> Optional[Dict[str, Any]]:

        query: Dict[str, Any]

        if ObjectId.is_valid(roadmap_id):

            query = {
                "$or": [
                    {
                        "_id": ObjectId(roadmap_id)
                    },
                    {
                        "roadmap_id": roadmap_id
                    },
                    {
                        "id": roadmap_id
                    },
                ]
            }

        else:

            query = {
                "$or": [
                    {
                        "roadmap_id": roadmap_id
                    },
                    {
                        "id": roadmap_id
                    },
                ]
            }

        document = await self.collection.find_one(
            query
        )

        return self._serialize_document(
            document
        )

    async def get_active_by_user_id(
        self,
        user_id: str,
    ) -> Optional[Dict[str, Any]]:

        cursor = (
            self.collection
            .find(
                {
                    "user_id": str(user_id),
                    "status": "active",
                }
            )
            .sort(
                "created_at",
                -1,
            )
            .limit(1)
        )

        documents = await cursor.to_list(
            length=1
        )

        if not documents:
            return None

        return self._serialize_document(
            documents[0]
        )

    async def get_all_by_user_id(
        self,
        user_id: str,
    ) -> List[Dict[str, Any]]:

        cursor = (
            self.collection
            .find(
                {
                    "user_id": str(user_id)
                }
            )
            .sort(
                "created_at",
                -1,
            )
        )

        documents = await cursor.to_list(
            length=100
        )

        return self._serialize_documents(
            documents
        )

    async def supersede_active_roadmaps(
        self,
        user_id: str,
    ) -> int:

        now = datetime.now(timezone.utc)

        result = await self.collection.update_many(
            {
                "user_id": str(user_id),
                "status": "active",
            },
            {
                "$set": {
                    "status": "superseded",
                    "updated_at": now,
                    "superseded_at": now,
                }
            },
        )

        return result.modified_count

    async def update(
        self,
        roadmap_id: str,
        user_id: str,
        data: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:

        data = dict(data)

        data["updated_at"] = datetime.now(
            timezone.utc
        )

        user_id = str(user_id)

        if ObjectId.is_valid(roadmap_id):

            query = {
                "user_id": user_id,
                "$or": [
                    {
                        "_id": ObjectId(roadmap_id)
                    },
                    {
                        "roadmap_id": roadmap_id
                    },
                    {
                        "id": roadmap_id
                    },
                ],
            }

        else:

            query = {
                "user_id": user_id,
                "$or": [
                    {
                        "roadmap_id": roadmap_id
                    },
                    {
                        "id": roadmap_id
                    },
                ],
            }

        result = await self.collection.update_one(
            query,
            {
                "$set": data
            },
        )

        if result.matched_count == 0:
            return None

        return await self.get_by_id(
            roadmap_id
        )

    async def delete(
        self,
        roadmap_id: str,
        user_id: str,
    ) -> bool:

        user_id = str(user_id)

        if ObjectId.is_valid(roadmap_id):

            query = {
                "user_id": user_id,
                "$or": [
                    {
                        "_id": ObjectId(roadmap_id)
                    },
                    {
                        "roadmap_id": roadmap_id
                    },
                    {
                        "id": roadmap_id
                    },
                ],
            }

        else:

            query = {
                "user_id": user_id,
                "$or": [
                    {
                        "roadmap_id": roadmap_id
                    },
                    {
                        "id": roadmap_id
                    },
                ],
            }

        result = await self.collection.delete_one(
            query
        )

        return result.deleted_count > 0

    async def create_indexes(self) -> None:
        """
        Create useful indexes for roadmap queries.
        """

        await self.collection.create_index(
            [
                ("user_id", 1),
                ("status", 1),
                ("created_at", -1),
            ]
        )

        await self.collection.create_index(
            [
                ("roadmap_id", 1)
            ]
        )

        await self.collection.create_index(
            [
                ("user_id", 1),
                ("roadmap_id", 1),
            ]
        )