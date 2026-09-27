import pytest
from app.repositories.leetcode_repository import LeetCodeRepository


@pytest.mark.asyncio
async def test_upsert_find_delete_leetcode_profile(mock_db):
    repo = LeetCodeRepository(mock_db)
    user_id = "user_repo_1"

    # 1. Profile initially not found
    doc = await repo.find_by_user_id(user_id)
    assert doc is None

    # 2. Upsert profile
    created = await repo.upsert_leetcode_profile(
        user_id=user_id,
        leetcode_username="repo_user_lc",
        profile_info={"username": "repo_user_lc", "ranking": 1000}
    )
    assert created["user_id"] == user_id
    assert created["leetcode_username"] == "repo_user_lc"

    # 3. Find profile
    found = await repo.find_by_user_id(user_id)
    assert found is not None
    assert found["profile"]["ranking"] == 1000

    # 4. Update sync status
    ok = await repo.update_sync_status(user_id, "synced", is_success=True)
    assert ok is True

    synced_doc = await repo.find_by_user_id(user_id)
    assert synced_doc["sync"]["status"] == "synced"

    # 5. Save AI analysis
    ai_saved = await repo.save_analysis(user_id, {"analysis": "sample analysis"})
    assert ai_saved is True

    # 6. Delete profile
    deleted = await repo.delete_by_user_id(user_id)
    assert deleted is True

    assert await repo.find_by_user_id(user_id) is None
