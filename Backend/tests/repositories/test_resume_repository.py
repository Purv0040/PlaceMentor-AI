import pytest
import pytest_asyncio
from app.repositories.resume_repository import ResumeRepository

@pytest.mark.asyncio
async def test_resume_repository_crud(mock_db):
    repo = ResumeRepository(mock_db)
    await repo.ensure_indexes()

    user_id = "user_test_123"

    # 1. Create resume
    doc = {
        "user_id": user_id,
        "file": {
            "filename": "test.pdf",
            "content_type": "application/pdf",
            "size": 100,
            "storage_type": "gridfs",
            "file_id": "file_123"
        },
        "status": "uploaded",
        "is_active": True,
        "parsed_data": {},
        "analysis": {},
        "analysis_version": "1.0"
    }

    created = await repo.create_resume(doc)
    assert created["id"] is not None
    resume_id = created["id"]

    # 2. Find by ID
    found = await repo.find_by_id(resume_id, user_id)
    assert found is not None
    assert found["file"]["filename"] == "test.pdf"

    # 3. Find active
    active = await repo.find_active_by_user(user_id)
    assert active is not None
    assert active["id"] == resume_id

    # 4. Save analysis
    analysis_dict = {"overall_score": 85, "suggestions": ["Add Redis"]}
    saved = await repo.save_analysis(resume_id, user_id, analysis_dict)
    assert saved is True

    updated = await repo.find_by_id(resume_id, user_id)
    assert updated["status"] == "completed"
    assert updated["analysis"]["overall_score"] == 85

    # 5. Delete resume
    deleted = await repo.delete_resume(resume_id, user_id)
    assert deleted is True

    assert await repo.find_by_id(resume_id, user_id) is None
