import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from app.core.security import create_access_token


@pytest.fixture
def other_user_auth_headers(mock_db) -> dict:
    other_user_id = "other_user_999"
    mock_db["users"].docs[other_user_id] = {
        "_id": other_user_id,
        "email": "other@example.com",
        "hashed_password": "hashed_secret",
        "full_name": "Other Student",
        "is_active": True,
        "is_onboarded": False,
    }
    token = create_access_token(subject=other_user_id, extra_claims={"email": "other@example.com"})
    return {"Authorization": f"Bearer {token}"}


def test_tasks_unauthenticated_access(client: TestClient):
    """Ensure tasks endpoints require authentication."""
    assert client.get("/api/v1/tasks/today").status_code == 401
    assert client.get("/api/v1/tasks/progress").status_code == 401
    assert client.get("/api/v1/tasks/streak").status_code == 401
    assert client.post("/api/v1/tasks/generate").status_code == 401
    assert client.get("/api/v1/tasks").status_code == 401
    assert client.post("/api/v1/tasks").status_code == 401
    assert client.get("/api/v1/tasks/task_123").status_code == 401
    assert client.patch("/api/v1/tasks/task_123").status_code == 401
    assert client.patch("/api/v1/tasks/task_123/status").status_code == 401
    assert client.post("/api/v1/tasks/task_123/complete").status_code == 401
    assert client.post("/api/v1/tasks/task_123/skip").status_code == 401


# 1. test_create_task
def test_create_task(client: TestClient, auth_headers: dict):
    res = client.post(
        "/api/v1/tasks",
        json={
            "title": "Learn Graph Algorithms",
            "description": "Understand BFS/DFS on directed graphs",
            "category": "DSA",
            "skill": "Graphs",
            "priority": "HIGH",
            "estimated_minutes": 90,
            "difficulty": "Intermediate"
        },
        headers=auth_headers
    )
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "Learn Graph Algorithms"
    assert data["skill"] == "Graphs"
    assert data["status"] == "pending"
    assert data["completion_percentage"] == 0.0
    assert data["difficulty"] == "Intermediate"
    assert "id" in data


# 2. test_get_all_tasks
def test_get_all_tasks(client: TestClient, auth_headers: dict):
    # Create two tasks
    client.post(
        "/api/v1/tasks",
        json={"title": "Task A", "description": "Desc A", "category": "DSA", "skill": "Trees"},
        headers=auth_headers
    )
    client.post(
        "/api/v1/tasks",
        json={"title": "Task B", "description": "Desc B", "category": "Backend", "skill": "SQL"},
        headers=auth_headers
    )

    res = client.get("/api/v1/tasks", headers=auth_headers)
    assert res.status_code == 200
    tasks = res.json()
    assert len(tasks) >= 2


# 3. test_get_today_tasks
def test_get_today_tasks(client: TestClient, auth_headers: dict):
    res = client.get("/api/v1/tasks/today", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "date" in data
    assert "day_number" in data
    assert "total_tasks" in data
    assert "tasks" in data


# 4. test_get_task_by_id
def test_get_task_by_id(client: TestClient, auth_headers: dict):
    res_create = client.post(
        "/api/v1/tasks",
        json={"title": "Specific Task", "description": "Desc", "category": "DSA", "skill": "DP"},
        headers=auth_headers
    )
    task_id = res_create.json()["id"]

    res_get = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert res_get.status_code == 200
    assert res_get.json()["id"] == task_id
    assert res_get.json()["title"] == "Specific Task"


# 5. test_update_task
def test_update_task(client: TestClient, auth_headers: dict):
    res_create = client.post(
        "/api/v1/tasks",
        json={"title": "Old Title", "description": "Old Desc", "category": "DSA", "skill": "Arrays"},
        headers=auth_headers
    )
    task_id = res_create.json()["id"]

    res_patch = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"title": "Updated Title", "estimated_minutes": 45},
        headers=auth_headers
    )
    assert res_patch.status_code == 200
    data = res_patch.json()
    assert data["title"] == "Updated Title"
    assert data["estimated_minutes"] == 45


# 6. test_update_task_status
def test_update_task_status(client: TestClient, auth_headers: dict):
    res_create = client.post(
        "/api/v1/tasks",
        json={"title": "Status Task", "description": "Desc", "category": "DSA", "skill": "Recursion"},
        headers=auth_headers
    )
    task_id = res_create.json()["id"]

    # In progress
    res_prog = client.patch(
        f"/api/v1/tasks/{task_id}/status",
        json={"status": "in_progress"},
        headers=auth_headers
    )
    assert res_prog.status_code == 200
    assert res_prog.json()["status"] == "in_progress"
    assert res_prog.json()["completion_percentage"] == 50.0


# 7. test_complete_task
def test_complete_task(client: TestClient, auth_headers: dict):
    res_create = client.post(
        "/api/v1/tasks",
        json={"title": "Complete Me", "description": "Desc", "category": "Backend", "skill": "REST API"},
        headers=auth_headers
    )
    task_id = res_create.json()["id"]

    res_comp = client.post(
        f"/api/v1/tasks/{task_id}/complete",
        json={"actual_minutes": 50, "notes": "Completed successfully"},
        headers=auth_headers
    )
    assert res_comp.status_code == 200
    data = res_comp.json()
    assert data["status"] == "completed"
    assert data["completion_percentage"] == 100.0
    assert data["actual_minutes"] == 50
    assert data["completed_at"] is not None


# 8. test_skip_pending_task
def test_skip_pending_task(client: TestClient, auth_headers: dict):
    res_create = client.post(
        "/api/v1/tasks",
        json={"title": "Skip Me", "description": "Desc", "category": "Backend", "skill": "Docker"},
        headers=auth_headers
    )
    task_id = res_create.json()["id"]

    res_skip = client.post(
        f"/api/v1/tasks/{task_id}/skip",
        json={"reason": "Already know this"},
        headers=auth_headers
    )
    assert res_skip.status_code == 200
    data = res_skip.json()
    assert data["status"] == "skipped"
    assert data["completion_percentage"] == 0.0
    assert data["completed_at"] is None
    assert "Skipped: Already know this" in (data["notes"] or "")


# 9. test_cannot_skip_completed_task
def test_cannot_skip_completed_task(client: TestClient, auth_headers: dict):
    res_create = client.post(
        "/api/v1/tasks",
        json={"title": "Cannot Skip Done", "description": "Desc", "category": "Backend", "skill": "FastAPI"},
        headers=auth_headers
    )
    task_id = res_create.json()["id"]

    # Complete it first
    res_comp = client.post(f"/api/v1/tasks/{task_id}/complete", json={}, headers=auth_headers)
    assert res_comp.status_code == 200

    # Attempt to skip
    res_skip = client.post(f"/api/v1/tasks/{task_id}/skip", json={"reason": "try skip"}, headers=auth_headers)
    assert res_skip.status_code == 400
    assert "Completed tasks cannot be skipped" in res_skip.text


# 10. test_progress_before_completion
def test_progress_before_completion(client: TestClient, auth_headers: dict):
    # Create pending task
    client.post(
        "/api/v1/tasks",
        json={"title": "Pending Task", "description": "Desc", "category": "AI", "skill": "CNN"},
        headers=auth_headers
    )

    res = client.get("/api/v1/tasks/progress", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "total_tasks" in data
    assert data["completed_tasks"] == 0
    assert data["completion_percentage"] == 0.0
    # Pending task skill should NOT appear in top_skills_completed
    assert "CNN" not in data["top_skills_completed"]


# 11. test_progress_after_completion
def test_progress_after_completion(client: TestClient, auth_headers: dict):
    res_create = client.post(
        "/api/v1/tasks",
        json={"title": "Completed Task", "description": "Desc", "category": "Programming", "skill": "Python"},
        headers=auth_headers
    )
    task_id = res_create.json()["id"]

    # Complete it
    client.post(f"/api/v1/tasks/{task_id}/complete", json={}, headers=auth_headers)

    res = client.get("/api/v1/tasks/progress", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["completed_tasks"] >= 1
    assert data["completion_percentage"] > 0
    assert "Python" in data["top_skills_completed"]


# 12. test_top_skills_completed_only_uses_completed_tasks
def test_top_skills_completed_only_uses_completed_tasks(client: TestClient, auth_headers: dict):
    # Task 1: pending skill = CNN
    client.post(
        "/api/v1/tasks",
        json={"title": "CNN Task", "description": "Desc", "category": "AI", "skill": "CNN"},
        headers=auth_headers
    )
    # Task 2: completed skill = PyTorch
    res2 = client.post(
        "/api/v1/tasks",
        json={"title": "PyTorch Task", "description": "Desc", "category": "AI", "skill": "PyTorch"},
        headers=auth_headers
    )
    client.post(f"/api/v1/tasks/{res2.json()['id']}/complete", json={}, headers=auth_headers)

    res = client.get("/api/v1/tasks/progress", headers=auth_headers)
    assert res.status_code == 200
    top_skills = res.json()["top_skills_completed"]
    assert "PyTorch" in top_skills
    assert "CNN" not in top_skills


# 13. test_streak_before_completion
def test_streak_before_completion(client: TestClient, auth_headers: dict):
    # When user has not completed tasks today
    res = client.get("/api/v1/tasks/streak", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "current_streak" in data
    assert "longest_streak" in data
    assert "is_active_today" in data


# 14. test_streak_after_completion
def test_streak_after_completion(client: TestClient, auth_headers: dict):
    res_create = client.post(
        "/api/v1/tasks",
        json={"title": "Streak Task", "description": "Desc", "category": "DSA", "skill": "Hashing"},
        headers=auth_headers
    )
    task_id = res_create.json()["id"]
    client.post(f"/api/v1/tasks/{task_id}/complete", json={}, headers=auth_headers)

    res = client.get("/api/v1/tasks/streak", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["current_streak"] >= 1
    assert data["is_active_today"] is True


# 15. test_generate_tasks_from_active_roadmap
def test_generate_tasks_from_active_roadmap(client: TestClient, auth_headers: dict):
    # 1. Generate roadmap
    res_rm = client.post(
        "/api/v1/roadmap/generate",
        json={"target_role": "Backend Developer"},
        headers=auth_headers
    )
    assert res_rm.status_code == 200

    # 2. Call tasks generate
    res_gen = client.post("/api/v1/tasks/generate", headers=auth_headers)
    assert res_gen.status_code == 200
    data = res_gen.json()
    assert "tasks" in data
    assert data["total_tasks"] >= 1
    for t in data["tasks"]:
        assert t["roadmap_id"] is not None


# 16. test_generate_is_idempotent
def test_generate_is_idempotent(client: TestClient, auth_headers: dict):
    client.post(
        "/api/v1/roadmap/generate",
        json={"target_role": "Backend Developer"},
        headers=auth_headers
    )
    res_1 = client.post("/api/v1/tasks/generate", headers=auth_headers)
    count_1 = res_1.json()["total_tasks"]

    res_2 = client.post("/api/v1/tasks/generate", headers=auth_headers)
    count_2 = res_2.json()["total_tasks"]

    assert count_1 == count_2


# 17. test_generate_does_not_duplicate_tasks
def test_generate_does_not_duplicate_tasks(client: TestClient, auth_headers: dict):
    client.post(
        "/api/v1/roadmap/generate",
        json={"target_role": "Backend Developer"},
        headers=auth_headers
    )
    client.post("/api/v1/tasks/generate", headers=auth_headers)
    client.post("/api/v1/tasks/generate", headers=auth_headers)

    res_all = client.get("/api/v1/tasks", headers=auth_headers)
    titles = [t["title"] for t in res_all.json()]
    # No duplicate titles for today's generated tasks
    assert len(titles) == len(set(titles))


# 18. test_user_cannot_access_other_users_task
def test_user_cannot_access_other_users_task(client: TestClient, auth_headers: dict, other_user_auth_headers: dict):
    res_create = client.post(
        "/api/v1/tasks",
        json={"title": "Private Task", "description": "Secret", "category": "DSA", "skill": "DP"},
        headers=auth_headers
    )
    task_id = res_create.json()["id"]

    # User 2 tries to access user 1's task
    res_other = client.get(f"/api/v1/tasks/{task_id}", headers=other_user_auth_headers)
    assert res_other.status_code == 404


# 19. test_user_cannot_update_other_users_task
def test_user_cannot_update_other_users_task(client: TestClient, auth_headers: dict, other_user_auth_headers: dict):
    res_create = client.post(
        "/api/v1/tasks",
        json={"title": "Original Title", "description": "Desc", "category": "DSA", "skill": "DP"},
        headers=auth_headers
    )
    task_id = res_create.json()["id"]

    # User 2 tries to update
    res_patch = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"title": "Hacked Title"},
        headers=other_user_auth_headers
    )
    assert res_patch.status_code == 404


# 20. test_user_cannot_complete_other_users_task
def test_user_cannot_complete_other_users_task(client: TestClient, auth_headers: dict, other_user_auth_headers: dict):
    res_create = client.post(
        "/api/v1/tasks",
        json={"title": "Uncompleted Task", "description": "Desc", "category": "DSA", "skill": "DP"},
        headers=auth_headers
    )
    task_id = res_create.json()["id"]

    # User 2 tries to complete
    res_comp = client.post(f"/api/v1/tasks/{task_id}/complete", json={}, headers=other_user_auth_headers)
    assert res_comp.status_code == 404


# 21. test_user_cannot_skip_other_users_task
def test_user_cannot_skip_other_users_task(client: TestClient, auth_headers: dict, other_user_auth_headers: dict):
    res_create = client.post(
        "/api/v1/tasks",
        json={"title": "Unskipped Task", "description": "Desc", "category": "DSA", "skill": "DP"},
        headers=auth_headers
    )
    task_id = res_create.json()["id"]

    # User 2 tries to skip
    res_skip = client.post(f"/api/v1/tasks/{task_id}/skip", json={}, headers=other_user_auth_headers)
    assert res_skip.status_code == 404


# 22. test_patch_difficulty_if_editable
def test_patch_difficulty_if_editable(client: TestClient, auth_headers: dict):
    res_create = client.post(
        "/api/v1/tasks",
        json={"title": "Difficulty Task", "description": "Desc", "category": "DSA", "skill": "Bit Manipulation", "difficulty": "Medium"},
        headers=auth_headers
    )
    task_id = res_create.json()["id"]

    res_patch = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"difficulty": "Hard"},
        headers=auth_headers
    )
    assert res_patch.status_code == 200
    assert res_patch.json()["difficulty"] == "Hard"


# 24. test_create_task_persists_notes (Requirement 12)
def test_create_task_persists_notes(client: TestClient, auth_headers: dict):
    res = client.post(
        "/api/v1/tasks",
        json={
            "title": "CNN Implementation",
            "description": "Implement Conv2D from scratch",
            "category": "AI",
            "skill": "CNN",
            "notes": "Complete the CNN implementation using PyTorch",
        },
        headers=auth_headers
    )
    assert res.status_code == 201
    data = res.json()
    assert data["notes"] == "Complete the CNN implementation using PyTorch"

    # Verify retrieval
    res_get = client.get(f"/api/v1/tasks/{data['id']}", headers=auth_headers)
    assert res_get.status_code == 200
    assert res_get.json()["notes"] == "Complete the CNN implementation using PyTorch"


# 25. test_top_skills_completed_pending_in_progress_completed (Requirement 1)
def test_top_skills_completed_pending_in_progress_completed(client: TestClient, auth_headers: dict):
    # CNN -> pending
    client.post(
        "/api/v1/tasks",
        json={"title": "CNN Task", "description": "Desc", "category": "AI", "skill": "CNN"},
        headers=auth_headers
    )
    # Python -> in_progress
    res_py = client.post(
        "/api/v1/tasks",
        json={"title": "Python Task", "description": "Desc", "category": "Programming", "skill": "Python"},
        headers=auth_headers
    )
    client.patch(
        f"/api/v1/tasks/{res_py.json()['id']}/status",
        json={"status": "in_progress"},
        headers=auth_headers
    )
    # FastAPI -> completed
    res_fa = client.post(
        "/api/v1/tasks",
        json={"title": "FastAPI Task", "description": "Desc", "category": "Backend", "skill": "FastAPI"},
        headers=auth_headers
    )
    client.post(f"/api/v1/tasks/{res_fa.json()['id']}/complete", json={}, headers=auth_headers)

    res = client.get("/api/v1/tasks/progress", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_tasks"] >= 3
    assert data["completed_tasks"] == 1
    assert data["top_skills_completed"] == ["FastAPI"]


# 26. test_skip_state_transitions_all_cases (Requirement 3)
def test_skip_state_transitions_all_cases(client: TestClient, auth_headers: dict):
    # Case 1: PENDING -> SKIPPED
    res1 = client.post(
        "/api/v1/tasks",
        json={"title": "Pending to Skip", "description": "Desc", "category": "AI", "skill": "ML"},
        headers=auth_headers
    )
    task1_id = res1.json()["id"]
    res_skip1 = client.post(f"/api/v1/tasks/{task1_id}/skip", json={"reason": "Not needed"}, headers=auth_headers)
    assert res_skip1.status_code == 200
    data1 = res_skip1.json()
    assert data1["status"] == "skipped"
    assert data1["completion_percentage"] == 0.0
    assert data1["completed_at"] is None

    # Case 2: IN_PROGRESS -> SKIPPED
    res2 = client.post(
        "/api/v1/tasks",
        json={"title": "In Progress to Skip", "description": "Desc", "category": "AI", "skill": "NLP"},
        headers=auth_headers
    )
    task2_id = res2.json()["id"]
    client.patch(f"/api/v1/tasks/{task2_id}/status", json={"status": "in_progress"}, headers=auth_headers)
    res_skip2 = client.post(f"/api/v1/tasks/{task2_id}/skip", headers=auth_headers)
    assert res_skip2.status_code == 200
    data2 = res_skip2.json()
    assert data2["status"] == "skipped"
    assert data2["completion_percentage"] == 0.0
    assert data2["completed_at"] is None

    # Case 3: COMPLETED -> SKIPPED (Must be REJECTED)
    res3 = client.post(
        "/api/v1/tasks",
        json={"title": "Completed to Skip", "description": "Desc", "category": "AI", "skill": "CV"},
        headers=auth_headers
    )
    task3_id = res3.json()["id"]
    client.post(f"/api/v1/tasks/{task3_id}/complete", headers=auth_headers)
    res_skip3 = client.post(f"/api/v1/tasks/{task3_id}/skip", headers=auth_headers)
    assert res_skip3.status_code == 400
    assert "Completed tasks cannot be skipped" in res_skip3.text

    # Also test PATCH on completed task cannot set status to skipped
    res_patch3 = client.patch(f"/api/v1/tasks/{task3_id}", json={"status": "skipped"}, headers=auth_headers)
    assert res_patch3.status_code == 400

    # Case 4: SKIPPED -> COMPLETED (Reopening/completion)
    res4 = client.post(
        "/api/v1/tasks",
        json={"title": "Skipped to Complete", "description": "Desc", "category": "AI", "skill": "RL"},
        headers=auth_headers
    )
    task4_id = res4.json()["id"]
    client.post(f"/api/v1/tasks/{task4_id}/skip", headers=auth_headers)
    res_comp4 = client.post(f"/api/v1/tasks/{task4_id}/complete", json={"notes": "Done after all"}, headers=auth_headers)
    assert res_comp4.status_code == 200
    data4 = res_comp4.json()
    assert data4["status"] == "completed"
    assert data4["completion_percentage"] == 100.0
    assert data4["completed_at"] is not None


# 27. test_today_summary_counts (Requirement 7)
def test_today_summary_counts(client: TestClient, auth_headers: dict):
    # Create 1 completed and 1 pending task for today
    res1 = client.post(
        "/api/v1/tasks",
        json={"title": "Today Completed", "description": "Desc", "category": "DSA", "skill": "Stack"},
        headers=auth_headers
    )
    client.post(f"/api/v1/tasks/{res1.json()['id']}/complete", headers=auth_headers)

    client.post(
        "/api/v1/tasks",
        json={"title": "Today Pending", "description": "Desc", "category": "DSA", "skill": "Queue"},
        headers=auth_headers
    )

    res_today = client.get("/api/v1/tasks/today", headers=auth_headers)
    assert res_today.status_code == 200
    data = res_today.json()
    assert data["total_tasks"] >= 2
    assert data["completed_tasks"] >= 1
    assert data["pending_tasks"] >= 1


# 28. test_generate_requires_active_roadmap (Requirement 8)
def test_generate_requires_active_roadmap(client: TestClient, auth_headers: dict):
    # With no active roadmap
    res = client.post("/api/v1/tasks/generate", headers=auth_headers)
    assert res.status_code == 400
    assert "No active roadmap found" in res.text



# 29. test_generate_tasks_with_active_roadmap_mocked(client: TestClient, auth_headers: dict, mock_db):
def test_generate_tasks_with_active_roadmap_mocked(client: TestClient, auth_headers: dict, mock_db):
    # Seed active roadmap in mock_db
    user_id = "test_user_123"
    roadmap_id = "roadmap_abc_123"
    mock_db["roadmaps"].docs[roadmap_id] = {
        "_id": roadmap_id,
        "roadmap_id": roadmap_id,
        "user_id": user_id,
        "status": "active",
        "start_date": datetime.now().astimezone().isoformat(),
        "phases": [
            {
                "phase_number": 1,
                "title": "Phase 1: Foundation",
                "tasks": [
                    {
                        "id": "rm_task_1",
                        "day": 1,
                        "title": "Learn Binary Search",
                        "description": "Master lower and upper bound binary search",
                        "category": "DSA",
                        "skill": "Binary Search",
                        "priority": "HIGH",
                        "estimated_minutes": 60,
                        "difficulty": "Medium"
                    }
                ]
            }
        ]
    }

    # Generate
    res_gen = client.post("/api/v1/tasks/generate", headers=auth_headers)
    assert res_gen.status_code == 200
    data = res_gen.json()
    assert data["total_tasks"] >= 1
    generated = [t for t in data["tasks"] if t["title"] == "Learn Binary Search"]
    assert len(generated) == 1
    assert generated[0]["roadmap_id"] == roadmap_id
    assert generated[0]["day_number"] == 1

    # Idempotent generation
    res_gen2 = client.post("/api/v1/tasks/generate", headers=auth_headers)
    assert res_gen2.status_code == 200
    assert res_gen2.json()["total_tasks"] == data["total_tasks"]


# 30. test_get_tasks_multi_filters (Requirement 10)
def test_get_tasks_multi_filters(client: TestClient, auth_headers: dict):
    client.post(
        "/api/v1/tasks",
        json={"title": "DL Task", "description": "Desc", "category": "Deep Learning", "skill": "Backprop"},
        headers=auth_headers
    )
    client.post(
        "/api/v1/tasks",
        json={"title": "DSA Task", "description": "Desc", "category": "DSA", "skill": "Heaps"},
        headers=auth_headers
    )

    res_dl = client.get("/api/v1/tasks?category=Deep%20Learning", headers=auth_headers)
    assert res_dl.status_code == 200
    tasks = res_dl.json()
    assert all(t["category"] == "Deep Learning" for t in tasks)
    assert any(t["title"] == "DL Task" for t in tasks)

    res_pending = client.get("/api/v1/tasks?status=pending", headers=auth_headers)
    assert res_pending.status_code == 200
    assert all(t["status"] == "pending" for t in res_pending.json())


# 31. test_error_handling_invalid_inputs (Requirement 15)
def test_error_handling_invalid_inputs(client: TestClient, auth_headers: dict):
    # Invalid task ID
    assert client.get("/api/v1/tasks/non_existent_id", headers=auth_headers).status_code == 404
    assert client.patch("/api/v1/tasks/non_existent_id", json={"title": "New"}, headers=auth_headers).status_code == 404
    assert client.post("/api/v1/tasks/non_existent_id/complete", headers=auth_headers).status_code == 404
    assert client.post("/api/v1/tasks/non_existent_id/skip", headers=auth_headers).status_code == 404

    # Invalid estimated_minutes (< 1)
    res_inv = client.post(
        "/api/v1/tasks",
        json={"title": "Inv", "description": "Desc", "category": "AI", "skill": "Math", "estimated_minutes": -5},
        headers=auth_headers
    )
    assert res_inv.status_code == 422


# 32. test_full_required_lifecycle (Requirement 16)
def test_full_required_lifecycle(client: TestClient, auth_headers: dict):
    """
    Lifecycle test:
    CREATE -> GET -> PATCH -> STATUS=in_progress -> COMPLETE -> PROGRESS -> STREAK -> TODAY
    CREATE -> SKIP
    COMPLETE -> SKIP (must be rejected)
    """
    # 1. CREATE
    res_c = client.post(
        "/api/v1/tasks",
        json={
            "title": "Lifecycle Task",
            "description": "Full end-to-end verification",
            "category": "System Design",
            "skill": "Caching",
            "priority": "HIGH",
            "estimated_minutes": 60,
            "difficulty": "Medium",
            "notes": "Initial lifecycle notes"
        },
        headers=auth_headers
    )
    assert res_c.status_code == 201
    task = res_c.json()
    task_id = task["id"]
    assert task["notes"] == "Initial lifecycle notes"
    assert task["status"] == "pending"

    # 2. GET
    res_g = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert res_g.status_code == 200
    assert res_g.json()["title"] == "Lifecycle Task"

    # 3. PATCH
    res_p = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"difficulty": "Hard", "estimated_minutes": 90},
        headers=auth_headers
    )
    assert res_p.status_code == 200
    assert res_p.json()["difficulty"] == "Hard"
    assert res_p.json()["estimated_minutes"] == 90

    # 4. STATUS = in_progress
    res_s = client.patch(
        f"/api/v1/tasks/{task_id}/status",
        json={"status": "in_progress"},
        headers=auth_headers
    )
    assert res_s.status_code == 200
    assert res_s.json()["status"] == "in_progress"
    assert res_s.json()["completion_percentage"] == 50.0

    # 5. COMPLETE
    res_done = client.post(
        f"/api/v1/tasks/{task_id}/complete",
        json={"actual_minutes": 85, "notes": "Completed and understood caching"},
        headers=auth_headers
    )
    assert res_done.status_code == 200
    done_data = res_done.json()
    assert done_data["status"] == "completed"
    assert done_data["completion_percentage"] == 100.0
    assert done_data["actual_minutes"] == 85
    assert done_data["notes"] == "Completed and understood caching"
    assert done_data["completed_at"] is not None

    # 6. PROGRESS
    res_prog = client.get("/api/v1/tasks/progress", headers=auth_headers)
    assert res_prog.status_code == 200
    prog_data = res_prog.json()
    assert prog_data["completed_tasks"] >= 1
    assert "Caching" in prog_data["top_skills_completed"]

    # 7. STREAK
    res_strk = client.get("/api/v1/tasks/streak", headers=auth_headers)
    assert res_strk.status_code == 200
    strk_data = res_strk.json()
    assert strk_data["current_streak"] >= 1
    assert strk_data["is_active_today"] is True

    # 8. TODAY
    res_tdy = client.get("/api/v1/tasks/today", headers=auth_headers)
    assert res_tdy.status_code == 200
    tdy_data = res_tdy.json()
    assert tdy_data["completed_tasks"] >= 1

    # 9. CREATE -> SKIP
    res_c2 = client.post(
        "/api/v1/tasks",
        json={"title": "To Skip", "description": "Desc", "category": "DSA", "skill": "Trie"},
        headers=auth_headers
    )
    task2_id = res_c2.json()["id"]
    res_sk = client.post(f"/api/v1/tasks/{task2_id}/skip", json={"reason": "Skip reason"}, headers=auth_headers)
    assert res_sk.status_code == 200
    assert res_sk.json()["status"] == "skipped"
    assert res_sk.json()["completion_percentage"] == 0.0

    # 10. COMPLETE -> SKIP (REJECTED)
    res_sk_rej = client.post(f"/api/v1/tasks/{task_id}/skip", headers=auth_headers)
    assert res_sk_rej.status_code == 400

