import pytest
from app.repositories.profile_repository import ProfileRepository


@pytest.mark.asyncio
async def test_create_and_get_profile(mock_db):
    repo = ProfileRepository(mock_db)
    created = await repo.create_profile("user_repo_1", {"personal.name": "Repo Student"})
    assert created["user_id"] == "user_repo_1"

    fetched = await repo.get_by_user_id("user_repo_1")
    assert fetched is not None
    assert fetched["personal"]["name"] == "Repo Student"


@pytest.mark.asyncio
async def test_update_profile_repo(mock_db):
    repo = ProfileRepository(mock_db)
    await repo.create_profile("user_repo_2")

    updated = await repo.update_profile("user_repo_2", {"personal.name": "Updated Name"})
    assert updated["personal"]["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_complete_onboarding_repo(mock_db):
    repo = ProfileRepository(mock_db)
    await repo.create_profile("user_repo_3")

    success = await repo.complete_onboarding("user_repo_3")
    assert success is True

    fetched = await repo.get_by_user_id("user_repo_3")
    assert fetched["onboarding"]["completed"] is True
