import pytest
from unittest.mock import AsyncMock
from typing import Generator, Dict, Any, Optional
from fastapi.testclient import TestClient
from app.main import app
from app.api.deps import get_db, get_current_user
from app.core.database import get_gridfs_bucket
from app.core.security import create_access_token


class AsyncMockCollection:
    """In-memory async mock for MongoDB collection to ensure tests NEVER touch real database."""

    def __init__(self) -> None:
        self.docs: Dict[str, Dict[str, Any]] = {}

    async def create_index(self, keys, **kwargs) -> str:
        return "mock_index"

    async def find_one(self, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for doc in self.docs.values():
            match = True
            for k, v in filter_dict.items():
                if k == "$or" and isinstance(v, list):
                    or_match = False
                    for cond in v:
                        cond_ok = True
                        for ck, cv in cond.items():
                            if str(doc.get(ck)) != str(cv):
                                cond_ok = False
                                break
                        if cond_ok:
                            or_match = True
                            break
                    if not or_match:
                        match = False
                        break
                else:
                    parts = k.split(".")
                    curr = doc
                    for p in parts:
                        if isinstance(curr, dict) and p in curr:
                            curr = curr[p]
                        else:
                            curr = None
                            break
                    if str(curr) != str(v):
                        match = False
                        break
            if match:
                res = dict(doc)
                return res
        return None

    async def insert_one(self, document: Dict[str, Any]):
        doc_id = str(document.get("_id") or f"mock_id_{len(self.docs) + 1}")
        document["_id"] = doc_id
        self.docs[doc_id] = dict(document)

        class InsertResult:
            inserted_id = doc_id

        return InsertResult()

    async def insert_many(self, documents: list):
        """Bulk insert – returns an InsertManyResult-like object with inserted_ids."""
        ids = []
        for document in documents:
            doc_id = str(document.get("_id") or f"mock_id_{len(self.docs) + 1}")
            document["_id"] = doc_id
            self.docs[doc_id] = dict(document)
            ids.append(doc_id)

        class InsertManyResult:
            inserted_ids = ids

        return InsertManyResult()

    async def count_documents(self, filter_dict: Dict[str, Any] = None) -> int:
        """Count documents matching filter_dict (or all docs if None)."""
        if not filter_dict:
            return len(self.docs)
        count = 0
        for doc in self.docs.values():
            match = True
            for k, v in filter_dict.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                count += 1
        return count

    async def update_one(self, filter_dict: Dict[str, Any], update_dict: Dict[str, Any], upsert: bool = False):
        existing = await self.find_one(filter_dict)
        if not existing and upsert:
            existing = dict(filter_dict)
            if "_id" not in existing:
                existing["_id"] = f"mock_id_{len(self.docs) + 1}"
            self.docs[existing["_id"]] = existing

        if existing:
            doc_id = existing["_id"]
            target = self.docs[doc_id]

            if "$set" in update_dict:
                for k, v in update_dict["$set"].items():
                    parts = k.split(".")
                    curr = target
                    for part in parts[:-1]:
                        if part not in curr or not isinstance(curr[part], dict):
                            curr[part] = {}
                        curr = curr[part]
                    curr[parts[-1]] = v

        class UpdateResult:
            modified_count = 1 if existing else 0
            matched_count = 1 if existing else 0

        return UpdateResult()

    async def update_many(self, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]):
        count = 0
        for doc in list(self.docs.values()):
            match = True
            for k, v in filter_dict.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match and "$set" in update_dict:
                for k, v in update_dict["$set"].items():
                    doc[k] = v
                count += 1

        class UpdateResult:
            modified_count = count
            matched_count = count

        return UpdateResult()

    async def delete_one(self, filter_dict: Dict[str, Any]):
        doc = await self.find_one(filter_dict)
        if doc and "_id" in doc:
            doc_id = doc["_id"]
            if doc_id in self.docs:
                del self.docs[doc_id]

        class DeleteResult:
            deleted_count = 1 if doc else 0

        return DeleteResult()

    def find(self, filter_dict: Dict[str, Any]):
        matched = []
        for doc in self.docs.values():
            match = True
            for k, v in filter_dict.items():
                if k == "$or" and isinstance(v, list):
                    or_match = False
                    for cond in v:
                        cond_ok = True
                        for ck, cv in cond.items():
                            if isinstance(cv, dict) and "$ne" in cv:
                                if str(doc.get(ck)) == str(cv["$ne"]):
                                    cond_ok = False
                                    break
                            elif str(doc.get(ck)) != str(cv):
                                cond_ok = False
                                break
                        if cond_ok:
                            or_match = True
                            break
                    if not or_match:
                        match = False
                        break
                elif isinstance(v, dict) and "$ne" in v:
                    if str(doc.get(k)) == str(v["$ne"]):
                        match = False
                        break
                else:
                    if str(doc.get(k)) != str(v):
                        match = False
                        break
            if match:
                matched.append(dict(doc))

        class MockCursor:
            def __init__(self, data):
                self.data = data

            def sort(self, key, direction=1):
                self.data.sort(key=lambda x: x.get(key, ""), reverse=(direction < 0))
                return self

            def skip(self, n):
                self.data = self.data[n:]
                return self

            def limit(self, n):
                self.data = self.data[:n]
                return self

            async def to_list(self, length=100):
                return self.data[:length]

        return MockCursor(matched)


class AsyncMockDatabase:
    """In-memory async mock for Motor Database."""

    def __init__(self) -> None:
        self.collections: Dict[str, AsyncMockCollection] = {}

    def __getitem__(self, collection_name: str) -> AsyncMockCollection:
        if collection_name not in self.collections:
            self.collections[collection_name] = AsyncMockCollection()
        return self.collections[collection_name]


@pytest.fixture
def mock_db() -> AsyncMockDatabase:
    return AsyncMockDatabase()


@pytest.fixture
def client(mock_db: AsyncMockDatabase) -> Generator[TestClient, None, None]:
    """Test client fixture with mocked isolated database to protect production Atlas data."""
    async def override_get_db():
        return mock_db

    async def override_get_gridfs():
        files: Dict[str, bytes] = {}

        async def mock_upload(filename, source, metadata=None):
            file_id = f"mock_file_id_{len(files) + 1}"
            files[file_id] = source
            return file_id

        async def mock_download(file_id, stream):
            data = files.get(str(file_id), b"%PDF-1.4 test resume pdf content")
            stream.write(data)

        mock_gridfs = AsyncMock()
        mock_gridfs.upload_from_stream = AsyncMock(side_effect=mock_upload)
        mock_gridfs.download_to_stream = AsyncMock(side_effect=mock_download)
        mock_gridfs.delete = AsyncMock()
        return mock_gridfs

    # Seed test user in mock DB
    test_user_id = "test_user_123"
    mock_db["users"].docs[test_user_id] = {
        "_id": test_user_id,
        "email": "student@example.com",
        "hashed_password": "hashed_secret",
        "full_name": "Test Student",
        "is_active": True,
        "is_onboarded": False,
    }

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_gridfs_bucket] = override_get_gridfs

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers() -> Dict[str, str]:
    """Return valid Authorization header with JWT token for test user."""
    token = create_access_token(subject="test_user_123", extra_claims={"email": "student@example.com"})
    return {"Authorization": f"Bearer {token}"}
