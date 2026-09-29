from typing import Any, Dict, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


class UserRepository:
    """Repository for the users collection."""

    def __init__(
        self,
        db: AsyncIOMotorDatabase,
    ) -> None:
        self.collection = db["users"]

    # ============================================================
    # GET USER BY ID
    # ============================================================

    async def get_by_id(
        self,
        user_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get a user by string ID or MongoDB ObjectId.

        Args:
            user_id: User ID string.

        Returns:
            User document dictionary or None if not found.
        """

        if not user_id:
            return None

        user_id = str(user_id).strip()

        document = await self.collection.find_one({"_id": user_id})
        if not document and ObjectId.is_valid(user_id):
            document = await self.collection.find_one({"_id": ObjectId(user_id)})

        if not document:
            return None

        return self._serialize_document(document)

    # ============================================================
    # GET USER BY EMAIL
    # ============================================================

    async def get_by_email(
        self,
        email: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get a user by email address.

        Email comparison is normalized to lowercase.
        """

        if not email:
            return None

        normalized_email = email.strip().lower()

        document = await self.collection.find_one(
            {"email": normalized_email}
        )

        if not document:
            return None

        return self._serialize_document(document)

    # ============================================================
    # CREATE USER
    # ============================================================

    async def create(
        self,
        user_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create a new user.

        MongoDB automatically generates the ObjectId if not provided.
        """

        document = user_data.copy()

        # Normalize email if present
        if document.get("email"):
            document["email"] = (
                str(document["email"])
                .strip()
                .lower()
            )

        result = await self.collection.insert_one(document)

        document["_id"] = str(result.inserted_id)

        return self._serialize_document(document)

    # ============================================================
    # UPDATE USER
    # ============================================================

    async def update(
        self,
        user_id: str,
        update_data: Dict[str, Any],
    ) -> bool:
        """
        Update an existing user.

        Only fields present in update_data are updated.
        """

        if not user_id:
            return False

        user_id = str(user_id).strip()

        if not update_data:
            return False

        # Normalize email when updating it
        update_data = update_data.copy()

        if update_data.get("email"):
            update_data["email"] = (
                str(update_data["email"])
                .strip()
                .lower()
            )

        filter_dict: Dict[str, Any] = {"_id": user_id}
        if ObjectId.is_valid(user_id):
            filter_dict = {"$or": [{"_id": user_id}, {"_id": ObjectId(user_id)}]}

        result = await self.collection.update_one(
            filter_dict,
            {
                "$set": update_data
            },
        )

        return result.matched_count > 0 or result.modified_count > 0

    # ============================================================
    # DELETE USER
    # ============================================================

    async def delete(
        self,
        user_id: str,
    ) -> bool:
        """
        Permanently delete a user.
        """

        if not user_id:
            return False

        user_id = str(user_id).strip()

        filter_dict: Dict[str, Any] = {"_id": user_id}
        if ObjectId.is_valid(user_id):
            filter_dict = {"$or": [{"_id": user_id}, {"_id": ObjectId(user_id)}]}

        result = await self.collection.delete_one(
            filter_dict
        )

        return result.deleted_count > 0

    # ============================================================
    # SERIALIZE MONGODB DOCUMENT
    # ============================================================

    @staticmethod
    def _serialize_document(
        document: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Convert MongoDB document into API-friendly dictionary.

        MongoDB:
            {"_id": ObjectId(...)}

        API:
            {"id": "...", "_id": "..."}
        """

        document = document.copy()

        if "_id" in document:
            document["id"] = str(document["_id"])
            document["_id"] = str(document["_id"])

        return document