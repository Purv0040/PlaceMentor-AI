import asyncio, json
from app.core.database import get_database

async def inspect():
    db = await get_database()
    user = await db['users'].find_one({'email': '1@gmail.com'})
    if not user:
        print('User 1@gmail.com not found')
        return
    uid = str(user['_id'])
    print(f'User ID: {uid}')
    
    # 1. Check daily_tasks collection
    tasks = await db['daily_tasks'].find({'user_id': uid}).to_list(100)
    print(f'Total daily_tasks in DB: {len(tasks)}')
    for t in tasks:
        print(f"  Day: {t.get('day_number')} | Title: {t.get('title')} | Completed: {t.get('completed')} | Assigned: {t.get('assigned_date')} | Category: {t.get('category')}")
        
    # 2. Check roadmap
    roadmap = await db['roadmaps'].find_one({'user_id': uid, 'status': 'active'})
    if not roadmap:
        roadmap = await db['roadmaps'].find_one({'user_id': uid})
    if roadmap:
        print(f"Roadmap ID: {roadmap.get('_id')}, current_day: {roadmap.get('current_day')}")
        days = roadmap.get('roadmap', {}).get('days', []) or roadmap.get('days', [])
        print(f"Total days in roadmap: {len(days)}")
        if days:
            day1 = next((d for d in days if d.get('day') == 1 or d.get('day_number') == 1), days[0])
            print("Day 1 roadmap tasks:")
            for task in day1.get('tasks', []):
                print(f"    - {task.get('title') or task.get('task_name')} (completed: {task.get('completed')})")

asyncio.run(inspect())
