import asyncio
from app.core.database import get_database

async def inspect():
    db = await get_database()
    cid = "6ad85ed49865cd6fb408a8f6"
    print(f"Messages for conversation {cid}:")
    msgs = await db['mentor_messages'].find({'conversation_id': cid}).sort('created_at', 1).to_list(100)
    for m in msgs:
        print(f"[{m.get('role')}]: {m.get('content')}\n")

asyncio.run(inspect())
