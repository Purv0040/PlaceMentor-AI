import asyncio, json
from app.core.database import get_database
from app.services.task_service import TaskService
from app.utils.dates import get_today_date_str

async def inspect():
    db = await get_database()
    user = await db['users'].find_one({'email': '1@gmail.com'})
    uid = str(user['_id'])
    
    today_str = get_today_date_str()
    print("Today date string:", today_str)
    
    t_svc = TaskService(db)
    today_res = await t_svc.get_today_tasks(uid)
    print("=== GET_TODAY_TASKS RESULT ===")
    print(f"Total: {today_res.get('total_tasks')}, Completed: {today_res.get('completed_tasks')}, Pending: {today_res.get('pending_tasks')}")
    for t in today_res.get('tasks', []):
        print(f"  Day: {t.get('day_number')} | Title: {t.get('title')} | Status: {t.get('status')} | Date: {t.get('date')}")

asyncio.run(inspect())
