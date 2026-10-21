import asyncio, sys
sys.stdout.reconfigure(encoding='utf-8')
from app.core.database import get_database

async def inspect():
    db = await get_database()
    uid = "6ad85d599865cd6fb408a513"
    tasks = await db['daily_tasks'].find({'user_id': uid}).to_list(200)
    print(f"Total tasks for {uid}: {len(tasks)}")
    for t in tasks:
        print(f"  Day: {t.get('day_number')} | Title: {t.get('title')} | Status: {t.get('status')} | Category: {t.get('category')} | roadmap_id: {t.get('roadmap_id')}")

asyncio.run(inspect())
