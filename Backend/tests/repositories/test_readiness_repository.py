import pytest
from app.repositories.readiness_repository import ReadinessRepository


@pytest.mark.asyncio
async def test_readiness_repository_crud(mock_db):
    repo = ReadinessRepository(mock_db)
    user_id = "user_repo_readiness_1"

    # 1. Create analysis
    doc = await repo.create_analysis(user_id, {
        "target_role": "Backend Developer",
        "overall_score": 78,
        "readiness_label": "Advanced",
        "scored_categories_count": 5
    })

    analysis_id = doc["id"]
    assert doc["user_id"] == user_id
    assert doc["overall_score"] == 78

    # 2. Get latest
    latest = await repo.get_latest_by_user(user_id)
    assert latest is not None
    assert latest["id"] == analysis_id

    # 3. Get history
    history = await repo.get_history_by_user(user_id, limit=5)
    assert len(history) == 1
    assert history[0]["id"] == analysis_id

    # 4. Get by ID
    by_id = await repo.get_by_id(analysis_id, user_id=user_id)
    assert by_id is not None
    assert by_id["target_role"] == "Backend Developer"
