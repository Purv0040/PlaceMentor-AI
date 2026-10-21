import asyncio, json
from app.core.database import get_database

async def inspect():
    db = await get_database()
    user = await db['users'].find_one({'email': '1@gmail.com'})
    uid = str(user['_id'])
    
    roadmap = await db['roadmaps'].find_one({'user_id': uid, 'status': 'active'})
    if not roadmap:
        roadmap = await db['roadmaps'].find_one({'user_id': uid})
    
    if not roadmap:
        print("No roadmap found!")
        return
        
    print(f"Roadmap ID: {roadmap.get('_id')}")
    print(f"Roadmap Title: {roadmap.get('title')}")
    print(f"Target Role: {roadmap.get('target_role')}")
    print(f"all_tasks len: {len(roadmap.get('all_tasks', []))}")
    for t in roadmap.get('all_tasks', [])[:10]:
        print(f"  Day {t.get('day')}: {t.get('title')} | category: {t.get('category')} | status: {t.get('status')}")
        
    phases = roadmap.get('phases', [])
    print(f"Phases count: {len(phases)}")
    if phases:
        p1_tasks = phases[0].get('tasks', [])
        print(f"Phase 1 tasks count: {len(p1_tasks)}")
        for t in p1_tasks[:10]:
            print(f"  Phase1 Day {t.get('day')}: {t.get('title')}")

asyncio.run(inspect())
