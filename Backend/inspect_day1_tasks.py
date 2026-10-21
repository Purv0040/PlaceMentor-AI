import asyncio, json
from app.core.database import get_database

async def inspect():
    db = await get_database()
    user = await db['users'].find_one({'email': '1@gmail.com'})
    uid = str(user['_id'])
    
    # 1. Check daily_tasks for day 1
    tasks_day1 = await db['daily_tasks'].find({'user_id': uid, 'day_number': 1}).to_list(100)
    print(f'Total Day 1 tasks in daily_tasks: {len(tasks_day1)}')
    for t in tasks_day1:
        print(f"  ID: {t.get('_id')} | Title: {t.get('title')} | Completed: {t.get('completed')} | Status: {t.get('status')} | Category: {t.get('category')}")

asyncio.run(inspect())
