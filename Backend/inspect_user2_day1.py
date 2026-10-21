import asyncio, sys
sys.stdout.reconfigure(encoding='utf-8')
from app.core.database import get_database

async def inspect():
    db = await get_database()
    uid = "6ad85d599865cd6fb408a513"
    tasks_d1 = await db['daily_tasks'].find({'user_id': uid, 'day_number': 1}).to_list(100)
    print(f"Total Day 1 daily_tasks for {uid}: {len(tasks_d1)}")
    for t in tasks_d1:
        print(f"  Title: {t.get('title')} | Status: {t.get('status')} | Date: {t.get('date') or t.get('assigned_date')} | Category: {t.get('category')}")

asyncio.run(inspect())
