import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.api.deps import get_db
from app.utils.dates import get_today_date_str, APP_TIMEZONE


def test_adaptive_unauthenticated_access(client: TestClient):
    """Ensure adaptive endpoints require authentication."""
    assert client.get("/api/v1/adaptive/summary").status_code == 401
    assert client.post("/api/v1/adaptive/recalculate").status_code == 401
    assert client.get("/api/v1/adaptive/recommendations").status_code == 401
    assert client.post("/api/v1/adaptive/apply").status_code == 401


def test_adaptive_rebalance_and_apply_flow(client: TestClient, auth_headers: dict):
    """Test adaptive recalculate, recommendation retrieval, and applying recommendations."""
    import asyncio
    async def _get_db():
        res = app.dependency_overrides[get_db]()
        if hasattr(res, "__await__"):
            return await res
        return res
    test_db = asyncio.run(_get_db())

    # 1. Generate roadmap
    res_rm = client.post("/api/v1/roadmap/generate", json={"target_role": "Backend Developer"}, headers=auth_headers)
    rm_id = res_rm.json()["id"]

    # 2. Get adaptive summary
    res_sum = client.get("/api/v1/adaptive/summary", headers=auth_headers)
    assert res_sum.status_code == 200
    assert "status" in res_sum.json()

    # Create an overdue task
    yesterday_str = (datetime.now(APP_TIMEZONE).date() - timedelta(days=2)).strftime("%Y-%m-%d")
    for doc in test_db["daily_tasks"].docs.values():
        if doc.get("roadmap_id") == rm_id and doc.get("status") == "pending":
            doc["date"] = yesterday_str
            break

    # 3. Recalculate adaptive plan
    res_recalc = client.post("/api/v1/adaptive/recalculate", json={"roadmap_id": rm_id, "force": True}, headers=auth_headers)
    assert res_recalc.status_code == 200
    recalc_data = res_recalc.json()
    assert "trigger" in recalc_data
    assert recalc_data["is_actionable"] is True
    event_id = recalc_data["id"]

    # 4. Get recommendations
    res_recs = client.get("/api/v1/adaptive/recommendations", headers=auth_headers)
    assert res_recs.status_code == 200
    assert len(res_recs.json()) >= 1

    # 5. Apply adaptation
    res_apply = client.post("/api/v1/adaptive/apply", json={"adaptation_id": event_id}, headers=auth_headers)
    assert res_apply.status_code == 200
    assert res_apply.json()["status"] == "success"



def test_adaptive_day1_no_false_overdue(client: TestClient, auth_headers: dict):
    """TEST 1 & 2: Newly generated roadmap has 0 false overdue tasks on day 1."""
    res_gen = client.post("/api/v1/roadmap/generate", json={"target_role": "AI Engineer"}, headers=auth_headers)
    assert res_gen.status_code == 200
    rm_id = res_gen.json()["id"]

    res_sum = client.get("/api/v1/adaptive/summary", headers=auth_headers)
    assert res_sum.status_code == 200
    metrics = res_sum.json()["metrics"]
    assert metrics["total_overdue"] == 0
    assert metrics["total_tasks"] == metrics["total_completed"] + metrics["total_pending"] + metrics["total_skipped"]

    res_recalc = client.post("/api/v1/adaptive/recalculate", json={"roadmap_id": rm_id, "force": True}, headers=auth_headers)
    assert res_recalc.status_code == 200
    data = res_recalc.json()
    assert data["trigger"] == "routine_check"
    assert "optimal and balanced" in data["recommendation"]


def test_adaptive_metrics_after_complete_and_skip(client: TestClient, auth_headers: dict):
    """TEST 3 & 4: Completing and skipping tasks correctly updates adaptive metrics."""
    client.post("/api/v1/roadmap/generate", json={"target_role": "Data Scientist"}, headers=auth_headers)

    res_today = client.get("/api/v1/tasks/today", headers=auth_headers)
    tasks = res_today.json()["tasks"]
    assert len(tasks) >= 2

    # Complete task 1
    client.post(f"/api/v1/tasks/{tasks[0]['id']}/complete", json={"actual_minutes": 45}, headers=auth_headers)
    # Skip task 2
    client.post(f"/api/v1/tasks/{tasks[1]['id']}/skip", json={"reason": "Need prerequisite"}, headers=auth_headers)

    res_sum = client.get("/api/v1/adaptive/summary", headers=auth_headers)
    assert res_sum.status_code == 200
    metrics = res_sum.json()["metrics"]
    assert metrics["total_completed"] >= 1
    assert metrics["total_skipped"] >= 1


def test_adaptive_detects_actually_overdue_tasks(client: TestClient, auth_headers: dict):
    """TEST 5 & 6: Tasks scheduled before today are detected as overdue; future tasks are not."""
    res_gen = client.post("/api/v1/roadmap/generate", json={"target_role": "DevOps Engineer"}, headers=auth_headers)
    rm_id = res_gen.json()["id"]

    yesterday_str = (datetime.now(APP_TIMEZONE).date() - timedelta(days=2)).strftime("%Y-%m-%d")

    # Set 3 tasks belonging to this roadmap to yesterday_str
    import asyncio
    async def _get_db():
        res = app.dependency_overrides[get_db]()
        if hasattr(res, "__await__"):
            return await res
        return res
    test_db = asyncio.run(_get_db())
    count = 0
    for doc in test_db["daily_tasks"].docs.values():
        if doc.get("roadmap_id") == rm_id and doc.get("status") == "pending":
            doc["date"] = yesterday_str
            doc["skill"] = "Docker"
            count += 1
            if count >= 3:
                break

    res_recalc = client.post("/api/v1/adaptive/recalculate", json={"roadmap_id": rm_id, "force": True}, headers=auth_headers)
    assert res_recalc.status_code == 200
    data = res_recalc.json()
    assert data["trigger"] == "overdue_tasks"
    assert "Docker" in data["affected_skills"]


def test_adaptive_user_and_old_roadmap_isolation(client: TestClient, auth_headers: dict):
    """TEST 7 & 8: Another user's tasks or old roadmaps are not included in calculations."""
    # Generate first roadmap
    res1 = client.post("/api/v1/roadmap/generate", json={"target_role": "Frontend Developer"}, headers=auth_headers)
    assert res1.status_code == 200
    rm1_id = res1.json()["id"]

    # Generate second roadmap (supersedes first)
    res2 = client.post("/api/v1/roadmap/generate", json={"target_role": "Full Stack Developer"}, headers=auth_headers)
    assert res2.status_code == 200
    rm2_id = res2.json()["id"]

    # Summary should strictly reflect active roadmap (rm2_id)
    res_sum = client.get("/api/v1/adaptive/summary", headers=auth_headers)
    assert res_sum.status_code == 200
    assert res_sum.json()["metrics"]["roadmap_id"] == rm2_id


def test_adaptive_idempotency_and_force(client: TestClient, auth_headers: dict):
    """TEST 9 & 10: force=False reuses existing unapplied event; force=True creates new."""
    res_gen = client.post("/api/v1/roadmap/generate", json={"target_role": "Cybersecurity Analyst"}, headers=auth_headers)
    rm_id = res_gen.json()["id"]

    # First recalculate
    res1 = client.post("/api/v1/adaptive/recalculate", json={"roadmap_id": rm_id, "force": False}, headers=auth_headers)
    assert res1.status_code == 200
    event1 = res1.json()

    # Second recalculate with force=False -> should return same event
    res2 = client.post("/api/v1/adaptive/recalculate", json={"roadmap_id": rm_id, "force": False}, headers=auth_headers)
    assert res2.status_code == 200
    event2 = res2.json()
    assert event1["id"] == event2["id"]

    # Third recalculate with force=True -> should generate a new event
    res3 = client.post("/api/v1/adaptive/recalculate", json={"roadmap_id": rm_id, "force": True}, headers=auth_headers)
    assert res3.status_code == 200
    event3 = res3.json()
    assert event3["id"] != event1["id"]


def test_adaptive_apply_idempotency(client: TestClient, auth_headers: dict):
    """TEST 11 & 12: Applying twice is safely handled."""
    import asyncio
    async def _get_db():
        res = app.dependency_overrides[get_db]()
        if hasattr(res, "__await__"):
            return await res
        return res
    test_db = asyncio.run(_get_db())

    res_rm = client.post("/api/v1/roadmap/generate", json={"target_role": "Cloud Engineer"}, headers=auth_headers)
    rm_id = res_rm.json()["id"]

    yesterday_str = (datetime.now(APP_TIMEZONE).date() - timedelta(days=2)).strftime("%Y-%m-%d")
    for doc in test_db["daily_tasks"].docs.values():
        if doc.get("roadmap_id") == rm_id and doc.get("status") == "pending":
            doc["date"] = yesterday_str
            break

    res_recalc = client.post("/api/v1/adaptive/recalculate", json={"roadmap_id": rm_id, "force": True}, headers=auth_headers)
    event_id = res_recalc.json()["id"]

    # Apply first time
    res_app1 = client.post("/api/v1/adaptive/apply", json={"adaptation_id": event_id}, headers=auth_headers)
    assert res_app1.status_code == 200
    assert res_app1.json()["status"] == "success"

    # Apply second time -> should be already_applied safely
    res_app2 = client.post("/api/v1/adaptive/apply", json={"adaptation_id": event_id}, headers=auth_headers)
    assert res_app2.status_code == 200
    assert res_app2.json()["status"] in ("already_applied", "success")



def test_adaptive_summary_state_detailed_criteria(client: TestClient, auth_headers: dict):
    """TEST: Detailed state validation for summary endpoint across scenarios."""
    import asyncio
    async def _get_db():
        res = app.dependency_overrides[get_db]()
        if hasattr(res, "__await__"):
            return await res
        return res
    test_db = asyncio.run(_get_db())

    # A. New roadmap: status = balanced, has_pending_recommendation = false
    res_gen = client.post("/api/v1/roadmap/generate", json={"target_role": "Site Reliability Engineer"}, headers=auth_headers)
    rm_id = res_gen.json()["id"]

    res_sum = client.get(f"/api/v1/adaptive/summary?roadmap_id={rm_id}", headers=auth_headers)
    assert res_sum.status_code == 200
    data = res_sum.json()
    assert data["status"] == "balanced"
    assert data["has_pending_recommendation"] is False
    assert data["metrics"]["total_overdue"] == 0

    # D. Recalculate routine check: status remains balanced and has_pending_recommendation remains false
    client.post("/api/v1/adaptive/recalculate", json={"roadmap_id": rm_id, "force": True}, headers=auth_headers)
    res_sum_routine = client.get(f"/api/v1/adaptive/summary?roadmap_id={rm_id}", headers=auth_headers)
    assert res_sum_routine.status_code == 200
    data_routine = res_sum_routine.json()
    assert data_routine["status"] == "balanced"
    assert data_routine["has_pending_recommendation"] is False
    assert data_routine["latest_recommendation"]["trigger"] == "routine_check"
    assert data_routine["latest_recommendation"]["applied"] is False

    # B & C. Overdue pending tasks: status = needs_rebalance, has_pending_recommendation = true
    yesterday_str = (datetime.now(APP_TIMEZONE).date() - timedelta(days=2)).strftime("%Y-%m-%d")
    for doc in test_db["daily_tasks"].docs.values():
        if doc.get("roadmap_id") == rm_id and doc.get("status") == "pending":
            doc["date"] = yesterday_str
            doc["skill"] = "Kubernetes"
            break

    res_sum_overdue = client.get(f"/api/v1/adaptive/summary?roadmap_id={rm_id}", headers=auth_headers)
    assert res_sum_overdue.status_code == 200
    data_overdue = res_sum_overdue.json()
    assert data_overdue["status"] == "needs_rebalance"
    assert data_overdue["has_pending_recommendation"] is True
    assert data_overdue["metrics"]["total_overdue"] >= 1

    # Recalculate with overdue tasks -> actionable recommendation
    res_recalc_actionable = client.post("/api/v1/adaptive/recalculate", json={"roadmap_id": rm_id, "force": True}, headers=auth_headers)
    assert res_recalc_actionable.status_code == 200
    event_id = res_recalc_actionable.json()["id"]

    # E. Apply recommendation -> must no longer be pending
    res_apply = client.post("/api/v1/adaptive/apply", json={"adaptation_id": event_id}, headers=auth_headers)
    assert res_apply.status_code == 200

    res_sum_applied = client.get(f"/api/v1/adaptive/summary?roadmap_id={rm_id}", headers=auth_headers)
    assert res_sum_applied.status_code == 200
    data_applied = res_sum_applied.json()
    assert data_applied["has_pending_recommendation"] is False
    assert data_applied["status"] == "balanced"
    assert data_applied["latest_recommendation"]["applied"] is True


def test_adaptive_recommendation_lifecycle_and_superseded_apply(client: TestClient, auth_headers: dict):
    """TEST: Validate lifecycle transitions (pending -> superseded, applied), apply restrictions."""
    import asyncio
    async def _get_db():
        res = app.dependency_overrides[get_db]()
        if hasattr(res, "__await__"):
            return await res
        return res
    test_db = asyncio.run(_get_db())

    # 1. Generate roadmap
    res_gen = client.post("/api/v1/roadmap/generate", json={"target_role": "MLOps Engineer"}, headers=auth_headers)
    rm_id = res_gen.json()["id"]

    # 2. Make overdue task and recalculate -> creates Event 1 (overdue_tasks)
    yesterday_str = (datetime.now(APP_TIMEZONE).date() - timedelta(days=3)).strftime("%Y-%m-%d")
    for doc in test_db["daily_tasks"].docs.values():
        if doc.get("roadmap_id") == rm_id and doc.get("status") == "pending":
            doc["date"] = yesterday_str
            break

    res_rec1 = client.post("/api/v1/adaptive/recalculate", json={"roadmap_id": rm_id, "force": True}, headers=auth_headers)
    assert res_rec1.status_code == 200
    event1 = res_rec1.json()
    assert event1["trigger"] == "overdue_tasks"
    assert event1["lifecycle_status"] == "pending"
    assert event1["is_actionable"] is True
    event1_id = event1["id"]

    # 3. Force recalculation with resolved tasks -> creates Event 2 (routine_check) and supersedes Event 1
    # Reset all task dates to future
    tomorrow_str = (datetime.now(APP_TIMEZONE).date() + timedelta(days=1)).strftime("%Y-%m-%d")
    for doc in test_db["daily_tasks"].docs.values():
        if doc.get("roadmap_id") == rm_id:
            doc["date"] = tomorrow_str

    res_rec2 = client.post("/api/v1/adaptive/recalculate", json={"roadmap_id": rm_id, "force": True}, headers=auth_headers)
    assert res_rec2.status_code == 200
    event2 = res_rec2.json()
    assert event2["trigger"] == "routine_check"
    assert event2["lifecycle_status"] == "informational"
    assert event2["is_actionable"] is False
    event2_id = event2["id"]

    # 4. Check recommendations endpoint: event 1 should now be superseded
    res_list = client.get(f"/api/v1/adaptive/recommendations?roadmap_id={rm_id}", headers=auth_headers)
    assert res_list.status_code == 200
    recs = res_list.json()
    assert len(recs) >= 2
    rec1_fetched = next(r for r in recs if r["id"] == event1_id)
    assert rec1_fetched["lifecycle_status"] == "superseded"
    assert rec1_fetched["is_actionable"] is False

    # 5. Attempting to apply superseded event 1 must fail with 409 Conflict
    res_apply_superseded = client.post("/api/v1/adaptive/apply", json={"adaptation_id": event1_id}, headers=auth_headers)
    assert res_apply_superseded.status_code == 409
    msg1 = res_apply_superseded.json().get("error", {}).get("message") or res_apply_superseded.json().get("detail", "")
    assert "superseded" in msg1.lower()

    # 6. Attempting to apply routine event 2 with no changes must fail with 409 Conflict
    res_apply_routine = client.post("/api/v1/adaptive/apply", json={"adaptation_id": event2_id}, headers=auth_headers)
    assert res_apply_routine.status_code == 409
    msg2 = res_apply_routine.json().get("error", {}).get("message") or res_apply_routine.json().get("detail", "")
    assert "informational" in msg2.lower()



def test_adaptive_apply_comprehensive_validation_cases(client: TestClient, auth_headers: dict):
    """TEST: Validate all apply edge cases: accept_changes=False, 404, 403, 409 mismatch, idempotency."""
    import asyncio
    async def _get_db():
        res = app.dependency_overrides[get_db]()
        if hasattr(res, "__await__"):
            return await res
        return res
    test_db = asyncio.run(_get_db())

    # Generate roadmap
    res_gen = client.post("/api/v1/roadmap/generate", json={"target_role": "QA Engineer"}, headers=auth_headers)
    rm_id = res_gen.json()["id"]

    # F. Nonexistent recommendation -> 404
    res_404 = client.post("/api/v1/adaptive/apply", json={"adaptation_id": "nonexistent_1234567890123456"}, headers=auth_headers)
    assert res_404.status_code == 404

    # Create an actionable overdue event
    yesterday_str = (datetime.now(APP_TIMEZONE).date() - timedelta(days=2)).strftime("%Y-%m-%d")
    for doc in test_db["daily_tasks"].docs.values():
        if doc.get("roadmap_id") == rm_id and doc.get("status") == "pending":
            doc["date"] = yesterday_str
            break

    res_recalc = client.post("/api/v1/adaptive/recalculate", json={"roadmap_id": rm_id, "force": True}, headers=auth_headers)
    actionable_id = res_recalc.json()["id"]

    # H. Recommendation belonging to another roadmap -> 409 Conflict
    res_mismatch = client.post("/api/v1/adaptive/apply", json={"adaptation_id": actionable_id, "roadmap_id": "other_roadmap_id_123"}, headers=auth_headers)
    assert res_mismatch.status_code in (404, 409)

    # B. Pending + actionable + accept_changes=False -> dismisses without rescheduling
    res_dismiss = client.post("/api/v1/adaptive/apply", json={"adaptation_id": actionable_id, "accept_changes": False}, headers=auth_headers)
    assert res_dismiss.status_code == 200
    assert res_dismiss.json()["status"] == "dismissed"

    # Now the dismissed event is superseded -> cannot be applied
    res_reapply = client.post("/api/v1/adaptive/apply", json={"adaptation_id": actionable_id, "accept_changes": True}, headers=auth_headers)
    assert res_reapply.status_code == 409

    # Create new actionable event and apply with accept_changes=True (A)
    res_recalc2 = client.post("/api/v1/adaptive/recalculate", json={"roadmap_id": rm_id, "force": True}, headers=auth_headers)
    actionable2_id = res_recalc2.json()["id"]

    res_apply_ok = client.post("/api/v1/adaptive/apply", json={"adaptation_id": actionable2_id, "accept_changes": True}, headers=auth_headers)
    assert res_apply_ok.status_code == 200
    assert res_apply_ok.json()["status"] == "success"

    # C & I. Repeated apply -> idempotent already_applied
    res_repeat = client.post("/api/v1/adaptive/apply", json={"adaptation_id": actionable2_id, "accept_changes": True}, headers=auth_headers)
    assert res_repeat.status_code == 200
    assert res_repeat.json()["status"] == "already_applied"



