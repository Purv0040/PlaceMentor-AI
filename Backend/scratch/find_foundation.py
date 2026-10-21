import asyncio, sys
sys.path.append('.')
from app.core.database import get_database

async def check():
    db = await get_database()
    tasks = await db['daily_tasks'].find({'title': {'$regex': 'Foundation Module 1'}}).to_list(10)
    for t in tasks:
        print('TASK:', t.get('_id'), t.get('user_id'), t.get('roadmap_id'), t.get('title'), t.get('status'), t.get('day_number'))
    
    rms = await db['roadmaps'].find({'all_tasks.title': {'$regex': 'Foundation Module 1'}}).to_list(10)
    for r in rms:
        print('ROADMAP:', r.get('_id'), r.get('user_id'), r.get('title'), r.get('status'), r.get('target_role'))

asyncio.run(check())
