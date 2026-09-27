import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from app.services.project_service import ProjectService
from app.schemas.project import ProjectCreateRequest, ProjectUpdateRequest
from app.integrations.ai_client import AIClientError


@pytest.mark.asyncio
async def test_normalize_technologies():
    techs = [" python ", "PYTHON", "react.js", "React", "fastapi", "FastAPI"]
    normalized = ProjectService.normalize_technologies(techs)
    assert normalized == ["Python", "React", "FastAPI"]


@pytest.mark.asyncio
async def test_create_and_get_project(mock_db):
    service = ProjectService(mock_db)
    user_id = "user_proj_serv_1"

    req = ProjectCreateRequest(
        title="Distributed Event Bus",
        description="High-throughput messaging broker written in Go implementing AMQP.",
        category="Backend / Systems",
        technologies=["Go", "RabbitMQ", "gRPC", "Docker"],
        architectureTags=["Pub-Sub", "gRPC Streaming"],
        githubUrl="https://github.com/user/event-bus"
    )

    created = await service.create_project(user_id, req)
    assert created["user_id"] == user_id
    assert created["title"] == "Distributed Event Bus"
    assert "Go" in created["technologies"]

    fetched = await service.get_project_by_id(created["id"], user_id)
    assert fetched["title"] == "Distributed Event Bus"


@pytest.mark.asyncio
async def test_get_project_ownership_protection(mock_db):
    service = ProjectService(mock_db)
    user_1 = "user_owner_1"
    user_2 = "user_owner_2"

    req = ProjectCreateRequest(
        title="Private Project",
        description="Only user 1 should see this project."
    )
    created = await service.create_project(user_1, req)

    # User 2 attempting to access User 1's project should raise 404
    with pytest.raises(HTTPException) as exc_info:
        await service.get_project_by_id(created["id"], user_2)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_update_project_marks_analysis_stale(mock_db):
    service = ProjectService(mock_db)
    user_id = "user_proj_serv_3"

    created = await service.create_project(
        user_id,
        ProjectCreateRequest(title="Initial Title", description="Initial description for testing.")
    )

    # Simulate completed AI analysis
    await service.repo.save_analysis(created["id"], user_id, {"score": 90})

    # Update project content
    update_req = ProjectUpdateRequest(title="Updated Title")
    updated = await service.update_project(created["id"], user_id, update_req)

    assert updated["title"] == "Updated Title"
    assert updated["analysis_status"] == "stale"


@pytest.mark.asyncio
async def test_analyze_project_ai_error(mock_db):
    service = ProjectService(mock_db)
    user_id = "user_proj_serv_4"

    created = await service.create_project(
        user_id,
        ProjectCreateRequest(title="AI Test Proj", description="Testing AI exception handling.")
    )

    with patch.object(service.ai_client, "analyze_project", new_callable=AsyncMock) as mock_ai:
        mock_ai.side_effect = AIClientError("AI Service unreachable")
        with pytest.raises(HTTPException) as exc_info:
            await service.analyze_project(created["id"], user_id)
        assert exc_info.value.status_code == 502

    project_after = await service.get_project_by_id(created["id"], user_id)
    assert project_after["analysis_status"] == "failed"
