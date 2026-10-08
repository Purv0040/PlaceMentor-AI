"""
Debug script to verify timezone/date root cause.

This script instruments the failing tests to capture exact datetime values
at key points in the flow.
"""
import sys
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.api.deps import get_db
from app.utils.dates import get_today_date_str, APP_TIMEZONE


def debug_test_adaptive_day1_no_false_overdue():
    """TEST 1 & 2: Capture timezone/date values during day 1 false overdue test."""
    print("\n" + "="*80)
    print("DEBUG: test_adaptive_day1_no_false_overdue")
    print("="*80)
    
    # Setup
    from app.core.security import create_access_token
    client = TestClient(app)
    user_id = "debug_user_001"
    token = create_access_token(subject=user_id, extra_claims={"email": "debug@test.com"})
    auth_headers = {"Authorization": f"Bearer {token}"}
    
    # Seed user in mock db
    import asyncio
    async def _get_db():
        res = app.dependency_overrides[get_db]()
        if hasattr(res, "__await__"):
            return await res
        return res
    mock_db = asyncio.run(_get_db())
    mock_db["users"].docs[user_id] = {
        "_id": user_id,
        "email": "debug@test.com",
        "hashed_password": "hashed",
        "full_name": "Debug User",
        "is_active": True,
        "is_onboarded": False,
    }
    
    # 1. Capture timezone info BEFORE any API calls
    print("\n[BASELINE] Timezone Information:")
    print(f"  APP_TIMEZONE: {APP_TIMEZONE}")
    print(f"  get_today_date_str(): {get_today_date_str()}")
    utc_now = datetime.now(timezone.utc)
    app_now = datetime.now(APP_TIMEZONE)
    print(f"  datetime.now(timezone.utc): {utc_now} (date: {utc_now.date()})")
    print(f"  datetime.now(APP_TIMEZONE): {app_now} (date: {app_now.date()})")
    print(f"  Timezone offset: {(app_now.utcoffset())}")
    
    # 2. Generate roadmap (this creates start_date)
    print("\n[API] POST /api/v1/roadmap/generate")
    res_gen = client.post("/api/v1/roadmap/generate", json={"target_role": "AI Engineer"}, headers=auth_headers)
    assert res_gen.status_code == 200, f"Roadmap generation failed: {res_gen.text}"
    rm_data = res_gen.json()
    rm_id = rm_data["id"]
    print(f"  Created roadmap ID: {rm_id}")
    
    # 3. Inspect roadmap in mock_db
    roadmap_doc = mock_db["roadmaps"].docs.get(rm_id)
    if roadmap_doc:
        start_date_value = roadmap_doc.get("start_date")
        print(f"\n[ROADMAP_DOC] start_date field:")
        print(f"  Type: {type(start_date_value)}")
        print(f"  Value: {start_date_value}")
        if isinstance(start_date_value, datetime):
            print(f"  .date(): {start_date_value.date()}")
            print(f"  .tzinfo: {start_date_value.tzinfo}")
        elif isinstance(start_date_value, str):
            try:
                parsed = datetime.fromisoformat(start_date_value.replace("Z", "+00:00"))
                print(f"  Parsed: {parsed}")
                print(f"  Parsed.date(): {parsed.date()}")
                print(f"  Parsed.tzinfo: {parsed.tzinfo}")
            except Exception as e:
                print(f"  Failed to parse: {e}")
    
    # 4. Get today's tasks to inspect day_number calculation
    print("\n[API] GET /api/v1/tasks/today")
    res_today = client.get("/api/v1/tasks/today", headers=auth_headers)
    assert res_today.status_code == 200, f"Failed to get today's tasks: {res_today.text}"
    today_data = res_today.json()
    print(f"  total_tasks: {today_data['total_tasks']}")
    print(f"  day_number: {today_data['day_number']}")
    print(f"  date: {today_data['date']}")
    
    # Inspect first task's day_number
    if today_data["tasks"]:
        first_task = today_data["tasks"][0]
        print(f"\n[FIRST_TASK_GENERATED]:")
        print(f"  id: {first_task.get('id')}")
        print(f"  title: {first_task.get('title')}")
        print(f"  day_number: {first_task.get('day_number')}")
        print(f"  date: {first_task.get('date')}")
        
        # Check if this task exists in mock_db to see its source
        task_id = first_task.get('id')
        task_doc = mock_db["daily_tasks"].docs.get(task_id)
        if task_doc:
            print(f"  [IN_MOCK_DB] day_number: {task_doc.get('day_number')}")
    
    # 5. Get adaptive summary (this will calculate overdue)
    print("\n[API] GET /api/v1/adaptive/summary")
    res_sum = client.get("/api/v1/adaptive/summary", headers=auth_headers)
    assert res_sum.status_code == 200, f"Failed to get adaptive summary: {res_sum.text}"
    metrics = res_sum.json()["metrics"]
    print(f"  total_tasks: {metrics['total_tasks']}")
    print(f"  total_overdue: {metrics['total_overdue']}")
    print(f"  total_completed: {metrics['total_completed']}")
    print(f"  total_pending: {metrics['total_pending']}")
    
    # 6. Check if any task dates are before today
    print("\n[TASK_DATES_ANALYSIS]:")
    today_date = datetime.now(APP_TIMEZONE).date()
    print(f"  APP_TIMEZONE today: {today_date}")
    for task in today_data["tasks"][:3]:  # First 3 tasks
        task_date_str = task.get("date")
        print(f"    Task '{task.get('title')}': date='{task_date_str}', day_number={task.get('day_number')}")
        try:
            task_date = datetime.strptime(task_date_str[:10], "%Y-%m-%d").date()
            is_overdue = task_date < today_date
            print(f"      Parsed date: {task_date}, is_overdue: {is_overdue}")
        except Exception as e:
            print(f"      Failed to parse: {e}")
    
    # 7. Recalculate and check trigger
    print("\n[API] POST /api/v1/adaptive/recalculate")
    res_recalc = client.post("/api/v1/adaptive/recalculate", json={"roadmap_id": rm_id, "force": True}, headers=auth_headers)
    assert res_recalc.status_code == 200, f"Recalculate failed: {res_recalc.text}"
    recalc_data = res_recalc.json()
    print(f"  trigger: {recalc_data['trigger']}")
    print(f"  recommendation: {recalc_data.get('recommendation', '')[:80]}...")
    print(f"  is_actionable: {recalc_data['is_actionable']}")
    
    # EXPECTED: trigger == "routine_check" and total_overdue == 0
    print("\n[VERIFICATION]:")
    print(f"  ✓ total_overdue == 0? {metrics['total_overdue'] == 0}")
    print(f"  ✓ trigger == 'routine_check'? {recalc_data['trigger'] == 'routine_check'}")
    
    if metrics["total_overdue"] != 0 or recalc_data["trigger"] != "routine_check":
        print("\n⚠️  TEST WOULD FAIL!")
        print("ROOT CAUSE HYPOTHESIS: Timezone mismatch between roadmap start_date (UTC) and adaptive calculation (APP_TIMEZONE)")
    else:
        print("\n✅ TEST WOULD PASS")


def debug_test_generate_tasks_day_number():
    """TEST 3: Capture day_number assignment during task generation."""
    print("\n" + "="*80)
    print("DEBUG: test_generate_tasks_with_active_roadmap_mocked")
    print("="*80)
    
    from app.core.security import create_access_token
    client = TestClient(app)
    user_id = "debug_user_002"
    token = create_access_token(subject=user_id, extra_claims={"email": "debug2@test.com"})
    auth_headers = {"Authorization": f"Bearer {token}"}
    
    # Setup
    import asyncio
    async def _get_db():
        res = app.dependency_overrides[get_db]()
        if hasattr(res, "__await__"):
            return await res
        return res
    mock_db = asyncio.run(_get_db())
    mock_db["users"].docs[user_id] = {
        "_id": user_id,
        "email": "debug2@test.com",
        "hashed_password": "hashed",
        "full_name": "Debug User 2",
        "is_active": True,
        "is_onboarded": False,
    }
    
    # Seed roadmap with a task that has day=1
    roadmap_id = "roadmap_debug_123"
    print(f"\n[BASELINE] Timezone Information:")
    print(f"  APP_TIMEZONE: {APP_TIMEZONE}")
    print(f"  datetime.now(timezone.utc): {datetime.now(timezone.utc)}")
    print(f"  datetime.now(APP_TIMEZONE): {datetime.now(APP_TIMEZONE)}")
    
    mock_db["roadmaps"].docs[roadmap_id] = {
        "_id": roadmap_id,
        "roadmap_id": roadmap_id,
        "user_id": user_id,
        "status": "active",
        "start_date": datetime.now(timezone.utc).isoformat(),  # Note: UTC!
        "phases": [
            {
                "phase_number": 1,
                "title": "Phase 1: Foundation",
                "tasks": [
                    {
                        "id": "rm_task_1",
                        "day": 1,  # Explicitly day 1
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
    
    print(f"\n[ROADMAP_SEED]:")
    print(f"  roadmap_id: {roadmap_id}")
    print(f"  start_date: {datetime.now(timezone.utc).isoformat()}")
    print(f"  task day: 1")
    
    # Generate tasks
    print(f"\n[API] POST /api/v1/tasks/generate")
    res_gen = client.post("/api/v1/tasks/generate", headers=auth_headers)
    assert res_gen.status_code == 200, f"Generate failed: {res_gen.text}"
    data = res_gen.json()
    
    print(f"  total_tasks: {data['total_tasks']}")
    
    # Find the generated task
    generated = [t for t in data["tasks"] if t["title"] == "Learn Binary Search"]
    if generated:
        gen_task = generated[0]
        print(f"\n[GENERATED_TASK]:")
        print(f"  title: {gen_task['title']}")
        print(f"  day_number: {gen_task['day_number']}")
        print(f"  date: {gen_task['date']}")
        print(f"  roadmap_id: {gen_task['roadmap_id']}")
        
        print(f"\n[VERIFICATION]:")
        print(f"  ✓ day_number == 1? {gen_task['day_number'] == 1}")
        
        if gen_task['day_number'] != 1:
            print(f"\n⚠️  TEST WOULD FAIL!")
            print(f"ROOT CAUSE HYPOTHESIS: day_number is {gen_task['day_number']} instead of 1")
            print("This suggests task_service.py is calculating day_number from roadmap date mismatch")
        else:
            print(f"\n✅ TEST WOULD PASS")
    else:
        print("\n⚠️  Generated task not found!")


if __name__ == "__main__":
    try:
        debug_test_adaptive_day1_no_false_overdue()
        debug_test_generate_tasks_day_number()
        print("\n" + "="*80)
        print("DEBUG COMPLETE")
        print("="*80)
    except Exception as e:
        print(f"\n❌ DEBUG FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
