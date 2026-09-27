import pytest
from fastapi.testclient import TestClient

PLACEHOLDER_MODULES = [
    ("auth", "/api/v1/auth/test"),
    ("users", "/api/v1/users/test"),
    ("onboarding", "/api/v1/onboarding/test"),
    ("skill_gaps", "/api/v1/skill-gaps/test"),
    ("roadmap", "/api/v1/roadmap/test"),
    ("tasks", "/api/v1/tasks/test"),
    ("progress", "/api/v1/progress/test"),
    ("interviews", "/api/v1/interviews/test"),
    ("communication", "/api/v1/communication/test"),
    ("mentor", "/api/v1/mentor/test"),
    ("achievements", "/api/v1/achievements/test"),
    ("notifications", "/api/v1/notifications/test"),
    ("settings", "/api/v1/settings/test"),
]


@pytest.mark.parametrize("module,path", PLACEHOLDER_MODULES)
def test_placeholder_endpoints(client: TestClient, module: str, path: str) -> None:
    response = client.get(path)
    assert response.status_code == 200, f"Failed on {module} at {path}"
    data = response.json()
    assert data["status"] == "success"
    assert data["module"] == module
