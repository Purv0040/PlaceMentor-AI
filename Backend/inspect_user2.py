import asyncio
from bson import ObjectId
from app.core.database import get_database

async def inspect():
    db = await get_database()
    uid = "6ad85d599865cd6fb408a513"
    user = await db['users'].find_one({'_id': ObjectId(uid)}) if ObjectId.is_valid(uid) else None
    if not user:
        user = await db['users'].find_one({'id': uid})
    print("User for 6ad85d599865cd6fb408a513:", user)
    
    # Check tasks for this user
    tasks = await db['daily_tasks'].find({'user_id': uid}).to_list(100)
    print(f"Tasks count for {uid}: {len(tasks)}")
    for t in tasks:
        print(f"  Day: {t.get('day_number')} | Title: {t.get('title')} | Status: {t.get('status')} | Category: {t.get('category')}")
        
    # Check roadmap for this user
    roadmap = await db['roadmaps'].find_one({'user_id': uid})
    print("Roadmap for this user:", roadmap.get('title') if roadmap else "None")
    if roadmap:
        print("Roadmap all_tasks count:", len(roadmap.get('all_tasks', [])))
        for t in roadmap.get('all_tasks', [])[:5]:
            print(f"  Day {t.get('day')}: {t.get('title')}")

asyncio.run(inspect())
