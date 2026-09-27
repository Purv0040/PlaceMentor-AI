import pytest
from app.repositories.skill_gap_repository import SkillGapRepository


@pytest.mark.asyncio
async def test_skill_gap_repository_crud(mock_db):
    """Test SkillGapRepository insert, fetch latest, get by id, history, and delete."""
    repo = SkillGapRepository(mock_db)
    await repo.init_indexes()

    user_id = "test_user_repo_skill_gap"
    analysis_payload = {
        "target_role": "Backend Developer",
        "overall_coverage": 75,
        "confidence_index": "90%",
        "total_audited": 20,
        "summary": {"total_required_skills": 9, "skills_aligned": 6, "skills_developing": 1, "skills_weak": 1, "skills_missing": 1},
        "skills": [{"skill": "Python", "gap_type": "aligned"}],
        "priority_gaps": [{"id": "gap-1", "skill": "Redis", "priority": "High"}]
    }

    # 1. Create analysis
    doc = await repo.create_analysis(user_id, analysis_payload)
    assert doc["id"] is not None
    assert doc["user_id"] == user_id
    assert doc["overall_coverage"] == 75

    # 2. Get latest by user
    latest = await repo.get_latest_by_user(user_id)
    assert latest is not None
    assert latest["id"] == doc["id"]

    # 3. Get by ID
    by_id = await repo.get_by_id(doc["id"], user_id=user_id)
    assert by_id is not None
    assert by_id["target_role"] == "Backend Developer"

    # 4. Get history
    history = await repo.get_history_by_user(user_id, limit=5)
    assert len(history) == 1

    # 5. Delete by user
    deleted = await repo.delete_by_user_id(user_id)
    assert deleted is True

    # 6. Verify empty after delete
    assert await repo.get_latest_by_user(user_id) is None
