import pytest
from app.services.onboarding_service import OnboardingService
from app.repositories.profile_repository import ProfileRepository
from app.repositories.user_repository import UserRepository
from app.schemas.onboarding import OnboardingStepUpdate
from app.schemas.profile import PersonalInfoSchema, CareerInfoSchema


@pytest.mark.asyncio
async def test_get_onboarding_state(mock_db):
    profile_repo = ProfileRepository(mock_db)
    user_repo = UserRepository(mock_db)
    service = OnboardingService(profile_repo, user_repo)

    state = await service.get_onboarding_state("user_svc_1")
    assert state["user_id"] == "user_svc_1"
    assert state["onboarding"]["completed"] is False


@pytest.mark.asyncio
async def test_save_step_data(mock_db):
    profile_repo = ProfileRepository(mock_db)
    user_repo = UserRepository(mock_db)
    service = OnboardingService(profile_repo, user_repo)

    step_update = OnboardingStepUpdate(
        step_number=1,
        profile=PersonalInfoSchema(
            name="Test Student",
            college="CSPIT",
            degree="B.Tech IT",
            graduationYear="2026"
        )
    )

    updated = await service.save_step_data("user_svc_2", step_update)
    assert updated["personal"]["name"] == "Test Student"
    assert 1 in updated["onboarding"]["completed_steps"]
