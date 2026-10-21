import asyncio, sys

sys.stdout.reconfigure(encoding='utf-8')

from app.core.database import get_database

async def inspect():
    db = await get_database()
    msgs = await db['mentor_messages'].find().sort('created_at', -1).limit(6).to_list(6)
    print(f"Found {len(msgs)} total messages in mentor_messages collection:")
    for m in reversed(msgs):
        print(f"Conv ID: {m.get('conversation_id')} | Role: {m.get('role')}\nContent: {m.get('content')}\n---")

asyncio.run(inspect())
