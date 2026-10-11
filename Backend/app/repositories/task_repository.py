import math
from datetime import date, datetime, timezone
from typing import Optional, Dict, Any, List

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


class TaskRepository:
    """
    Repository for daily_tasks collection.

    Responsibilities:
    - MongoDB CRUD operations
    - User-scoped task access
    - Task filtering
    - Task status updates
    - Index creation
    - Consistent serialization of MongoDB documents
    """

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db["daily_tasks"]

    # ============================================================
    # INTERNAL HELPERS
    # ============================================================

    @staticmethod
    def _as_datetime(value: Any) -> Optional[datetime]:
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time(), tzinfo=timezone.utc)
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return None
        return None

    @staticmethod
    def _as_bounded_int(value: Any, default: int, minimum: int, maximum: int) -> int:
        try:
            number = int(value)
        except (TypeError, ValueError, OverflowError):
            return default
        return max(minimum, min(number, maximum))

    @staticmethod
    def _serialize_document(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Convert MongoDB document into API-friendly dictionary.
        """
        if not doc:
            return None

        mongo_id = str(doc.get("_id") or doc.get("task_id") or "unknown-task")
        doc["_id"] = mongo_id
        doc["task_id"] = str(doc.get("task_id") or mongo_id)
        doc["id"] = str(doc.get("id") or doc["task_id"])
        doc["user_id"] = str(doc.get("user_id") or "unknown-user")
        if doc.get("roadmap_id") is not None:
            doc["roadmap_id"] = str(doc["roadmap_id"])

        # Older task records may predate fields now required by the API schema.
        # Fill them when reading so one legacy document cannot make GET /tasks
        # fail response validation for the entire collection.
        created_at = TaskRepository._as_datetime(doc.get("created_at"))
        updated_at = TaskRepository._as_datetime(doc.get("updated_at"))
        fallback_date = (created_at or datetime.now(timezone.utc)).date().isoformat()
        date_value = doc.get("date")
        if isinstance(date_value, datetime):
            date_value = date_value.date().isoformat()
        elif isinstance(date_value, date):
            date_value = date_value.isoformat()
        try:
            datetime.strptime(str(date_value), "%Y-%m-%d")
            doc["date"] = str(date_value)
        except (TypeError, ValueError):
            doc["date"] = fallback_date

        doc["day_number"] = TaskRepository._as_bounded_int(doc.get("day_number"), 1, 1, 365)
        for field, fallback in (
            ("title", "Untitled task"),
            ("description", ""),
            ("category", "General"),
            ("priority", "MEDIUM"),
            ("difficulty", "Intermediate"),
            ("status", "pending"),
        ):
            value = doc.get(field)
            doc[field] = str(value) if value not in (None, "") else fallback
        doc["skill"] = str(doc.get("skill") or doc["category"] or "Core")
        doc["estimated_minutes"] = TaskRepository._as_bounded_int(doc.get("estimated_minutes"), 60, 1, 1440)
        actual_minutes = doc.get("actual_minutes")
        try:
            doc["actual_minutes"] = (
                max(0, min(int(actual_minutes), 1440))
                if actual_minutes is not None
                else None
            )
        except (TypeError, ValueError, OverflowError):
            doc["actual_minutes"] = None
        try:
            percentage = float(doc.get("completion_percentage", 0.0))
        except (TypeError, ValueError, OverflowError):
            percentage = 0.0
        doc["completion_percentage"] = min(100.0, max(0.0, percentage)) if math.isfinite(percentage) else 0.0
        doc["completed_at"] = TaskRepository._as_datetime(doc.get("completed_at"))
        doc["created_at"] = created_at
        doc["updated_at"] = updated_at
        if not isinstance(doc.get("resource"), dict):
            doc["resource"] = None
        if doc.get("notes") is not None:
            doc["notes"] = str(doc["notes"])

        return doc

    @staticmethod
    def _serialize_documents(
        docs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Serialize multiple MongoDB documents.
        """
        return [
            TaskRepository._serialize_document(doc)
            for doc in docs
            if doc is not None
        ]

    def _build_query(
        self,
        task_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Build a user-scoped task lookup query.

        Supports:
        - custom task_id
        - string MongoDB _id
        - ObjectId MongoDB _id
        """

        task_id = str(task_id)
        user_id = str(user_id)

        conditions: List[Dict[str, Any]] = [
            {"task_id": task_id},
            {"_id": task_id},
        ]

        if ObjectId.is_valid(task_id):
            conditions.append(
                {"_id": ObjectId(task_id)}
            )

        return {
            "user_id": user_id,
            "$or": conditions,
        }

    # ============================================================
    # CREATE
    # ============================================================

    async def create(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create one task.
        """

        now = datetime.now(timezone.utc)

        document = dict(data)

        document["created_at"] = document.get(
            "created_at",
            now
        )

        document["updated_at"] = now

        result = await self.collection.insert_one(document)

        document["_id"] = str(result.inserted_id)

        # Generate fallback task_id if service did not provide one.
        if not document.get("task_id"):
            document["task_id"] = document["_id"]

            await self.collection.update_one(
                {"_id": result.inserted_id},
                {
                    "$set": {
                        "task_id": document["task_id"]
                    }
                }
            )

        document["id"] = str(
            document.get("id")
            or document["task_id"]
        )

        return document

    # ============================================================
    # CREATE MANY
    # ============================================================

    async def create_many(
        self,
        tasks_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Create multiple tasks.
        """

        if not tasks_data:
            return []

        now = datetime.now(timezone.utc)

        documents = []

        for task in tasks_data:
            document = dict(task)

            document["created_at"] = document.get(
                "created_at",
                now
            )

            document["updated_at"] = now

            documents.append(document)

        results = await self.collection.insert_many(documents)

        inserted_tasks: List[Dict[str, Any]] = []

        for index, inserted_id in enumerate(
            results.inserted_ids
        ):
            document = documents[index]

            document["_id"] = str(inserted_id)

            if not document.get("task_id"):
                document["task_id"] = document["_id"]

                await self.collection.update_one(
                    {"_id": inserted_id},
                    {
                        "$set": {
                            "task_id": document["task_id"]
                        }
                    }
                )

            document["id"] = str(
                document.get("id")
                or document["task_id"]
            )

            inserted_tasks.append(document)

        return inserted_tasks

    # ============================================================
    # GET BY ID
    # ============================================================

    async def get_by_id(
        self,
        task_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a task belonging to a specific user.

        Returns None if:
        - task does not exist
        - task belongs to another user
        """

        query = self._build_query(
            task_id,
            user_id
        )

        document = await self.collection.find_one(query)

        return self._serialize_document(document)

    # ============================================================
    # GET BY USER + DATE
    # ============================================================

    async def get_by_user_and_date(
        self,
        user_id: str,
        date_str: str
    ) -> List[Dict[str, Any]]:
        """
        Get all tasks for a user on a specific date.
        """

        query = {
            "user_id": str(user_id),
            "date": date_str,
        }

        cursor = self.collection.find(query)

        documents = await cursor.to_list(
            length=500
        )

        return self._serialize_documents(
            documents
        )

    # ============================================================
    # GET BY ROADMAP
    # ============================================================

    async def get_by_roadmap_id(
        self,
        roadmap_id: str,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all tasks belonging to a roadmap
        for a specific user.
        """

        query = {
            "user_id": str(user_id),
            "roadmap_id": str(roadmap_id),
        }

        cursor = self.collection.find(query)

        documents = await cursor.to_list(
            length=1000
        )

        return self._serialize_documents(
            documents
        )

    # ============================================================
    # GET ALL BY USER
    # ============================================================

    async def get_all_by_user(
        self,
        user_id: str,
        status: Optional[str] = None,
        category: Optional[str] = None,
        date_str: Optional[str] = None,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:
        """
        Get tasks for a user with optional filters.
        """

        query: Dict[str, Any] = {
            "user_id": str(user_id)
        }

        if status:
            query["status"] = status

        if category:
            query["category"] = category

        if date_str:
            query["date"] = date_str

        cursor = (
            self.collection
            .find(query)
            .sort("created_at", -1)
        )

        documents = await cursor.to_list(
            length=limit
        )

        return self._serialize_documents(
            documents
        )

    # ============================================================
    # UPDATE
    # ============================================================

    async def update(
        self,
        task_id: str,
        user_id: str,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update task fields.

        User ownership is always enforced.
        """

        if not data:
            return await self.get_by_id(
                task_id,
                user_id
            )

        update_data = dict(data)

        update_data["updated_at"] = (
            datetime.now(timezone.utc)
        )

        # Status-dependent fields.
        if "status" in update_data:

            status = update_data["status"]

            if status == "completed":
                update_data[
                    "completion_percentage"
                ] = 100.0

                update_data[
                    "completed_at"
                ] = update_data.get(
                    "completed_at"
                ) or datetime.now(timezone.utc)

            elif status == "in_progress":
                update_data[
                    "completion_percentage"
                ] = 50.0

                update_data[
                    "completed_at"
                ] = None

            elif status in (
                "pending",
                "skipped",
            ):
                update_data[
                    "completion_percentage"
                ] = 0.0

                update_data[
                    "completed_at"
                ] = None

        query = self._build_query(
            task_id,
            user_id
        )

        result = await self.collection.update_one(
            query,
            {
                "$set": update_data
            }
        )

        if result.matched_count == 0:
            return None

        return await self.get_by_id(
            task_id,
            user_id
        )

    # ============================================================
    # UPDATE STATUS
    # ============================================================

    async def update_status(
        self,
        task_id: str,
        user_id: str,
        status: str,
        actual_minutes: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Update task status and related fields.

        Transition validation is intentionally handled
        by TaskService. This repository only persists
        the requested state.
        """

        now = datetime.now(timezone.utc)

        update_data: Dict[str, Any] = {
            "status": status,
            "updated_at": now,
        }

        if status == "completed":

            update_data[
                "completion_percentage"
            ] = 100.0

            update_data[
                "completed_at"
            ] = now

        elif status == "in_progress":

            update_data[
                "completion_percentage"
            ] = 50.0

            update_data[
                "completed_at"
            ] = None

        elif status in (
            "pending",
            "skipped",
        ):

            update_data[
                "completion_percentage"
            ] = 0.0

            update_data[
                "completed_at"
            ] = None

        if actual_minutes is not None:
            update_data[
                "actual_minutes"
            ] = actual_minutes

        if notes is not None:
            update_data[
                "notes"
            ] = notes

        query = self._build_query(
            task_id,
            user_id
        )

        result = await self.collection.update_one(
            query,
            {
                "$set": update_data
            }
        )

        if result.matched_count == 0:
            return None

        return await self.get_by_id(
            task_id,
            user_id
        )

    # ============================================================
    # DELETE
    # ============================================================

    async def delete(
        self,
        task_id: str,
        user_id: str
    ) -> bool:
        """
        Delete a task belonging to the user.
        """

        query = self._build_query(
            task_id,
            user_id
        )

        result = await self.collection.delete_one(
            query
        )

        return result.deleted_count > 0

    # ============================================================
    # INDEXES
    # ============================================================

    async def create_indexes(self) -> None:
        """
        Create indexes required by Tasks API.
        """

        try:
            await self.collection.create_index(
                "user_id"
            )

            await self.collection.create_index(
                "task_id"
            )

            await self.collection.create_index(
                [
                    ("user_id", 1),
                    ("date", 1),
                ]
            )

            await self.collection.create_index(
                [
                    ("user_id", 1),
                    ("status", 1),
                ]
            )

            await self.collection.create_index(
                [
                    ("user_id", 1),
                    ("category", 1),
                ]
            )

            await self.collection.create_index(
                [
                    ("user_id", 1),
                    ("roadmap_id", 1),
                ]
            )

            await self.collection.create_index(
                [
                    ("user_id", 1),
                    ("roadmap_id", 1),
                    ("date", 1),
                ]
            )

            await self.collection.create_index(
                [
                    ("user_id", 1),
                    ("roadmap_id", 1),
                    ("day_number", 1),
                ]
            )

        except Exception:
            # Index creation should not prevent
            # application startup.
            pass
