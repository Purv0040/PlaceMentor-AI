import asyncio, json
from app.core.database import get_database

async def inspect():
    db = await get_database()
    user = await db['users'].find_one({'email': '1@gmail.com'})
    uid = str(user['_id'])
    
    # Search across all daily_tasks for this user
    cursor = db['daily_tasks'].find({'user_id': uid, 'title': {'$regex': 'Maximum Depth', '$options': 'i'}})
    docs = await cursor.to_list(100)
    print(f"Found {len(docs)} tasks with 'Maximum Depth':")
    for d in docs:
        print(f"  Day: {d.get('day_number')} | Title: {d.get('title')} | Status: {d.get('status')} | Date: {d.get('date') or d.get('assigned_date')}")

    # Check mentor conversations message history to see what was sent to LLM
    convs = await db['mentor_conversations'].find({'user_id': uid}).to_list(10)
    print(f"Found {len(convs)} mentor conversations")
    for c in convs:
        print(f"Conv ID: {c.get('_id')} | Title: {c.get('title')}")
        msgs = await db['mentor_messages'].find({'conversation_id': str(c.get('_id'))}).sort('created_at', -1).limit(6).to_list(10)
        for m in reversed(msgs):
            print(f"  [{m.get('role')}]: {m.get('content')[:100]}...")

asyncio.run(inspect())
