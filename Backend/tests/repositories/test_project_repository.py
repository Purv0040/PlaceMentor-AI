import pytest
from app.repositories.project_repository import ProjectRepository


@pytest.mark.asyncio
async def test_project_repository_crud(mock_db):
    repo = ProjectRepository(mock_db)
    user_id = "user_repo_test_1"

    # 1. Create project
    doc = await repo.create_project(user_id, {
        "title": "Kernel Scheduler Lab",
        "description": "Custom process scheduler in C.",
        "category": "Systems Programming",
        "technologies": ["C", "Assembly", "Makefile"],
        "is_featured": True
    })

    project_id = doc["id"]
    assert doc["user_id"] == user_id
    assert doc["is_featured"] is True

    # 2. List user projects
    projects = await repo.find_by_user_id(user_id)
    assert len(projects) == 1
    assert projects[0]["title"] == "Kernel Scheduler Lab"

    # 3. Find by ID
    found = await repo.find_by_id(project_id, user_id)
    assert found is not None
    assert found["category"] == "Systems Programming"

    # 4. Update project
    updated = await repo.update_project(project_id, user_id, {"title": "OS Kernel Lab v2"})
    assert updated["title"] == "OS Kernel Lab v2"

    # 5. Toggle featured
    toggled = await repo.toggle_featured(project_id, user_id, False)
    assert toggled["is_featured"] is False

    # 6. Save analysis
    ai_saved = await repo.save_analysis(project_id, user_id, {"score": 88, "evidence_bullets": ["Bullet 1"]})
    assert ai_saved is True

    after_ai = await repo.find_by_id(project_id, user_id)
    assert after_ai["analysis_status"] == "completed"
    assert after_ai["score"] == 88
    assert after_ai["evidenceBullets"] == ["Bullet 1"]

    # 7. Delete project
    deleted = await repo.delete_project(project_id, user_id, soft_delete=True)
    assert deleted is True

    # Archived project should not be in default list
    active_projects = await repo.find_by_user_id(user_id, include_archived=False)
    assert len(active_projects) == 0

    all_projects = await repo.find_by_user_id(user_id, include_archived=True)
    assert len(all_projects) == 1
    assert all_projects[0]["status"] == "archived"
