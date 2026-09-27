import pytest
from app.services.profile_service import ProfileService
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import ProfileUpdate, PersonalInfoSchema, CareerInfoSchema


@pytest.mark.asyncio
async def test_get_or_create_profile(mock_db):
    profile_repo = ProfileRepository(mock_db)
    service = ProfileService(profile_repo)

    profile = await service.get_or_create_profile("user_psvc_1", user_email="student@cspit.ac.in", user_name="Student One")
    assert profile["user_id"] == "user_psvc_1"
    assert profile["personal"]["name"] == "Student One"


@pytest.mark.asyncio
async def test_update_profile(mock_db):
    profile_repo = ProfileRepository(mock_db)
    service = ProfileService(profile_repo)

    await service.get_or_create_profile("user_psvc_2")

    update_obj = ProfileUpdate(
        career=CareerInfoSchema(targetRole="Backend Developer", companyTier="Tier-1 Product")
    )
    updated = await service.update_profile("user_psvc_2", update_obj)
    assert updated["career"]["targetRole"] == "Backend Developer"
