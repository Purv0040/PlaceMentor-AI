import asyncio
from app.core.database import get_database

async def inspect():
    db = await get_database()
    uid = "6ad85d599865cd6fb408a513"
    rms = await db['roadmaps'].find({'user_id': uid}).to_list(10)
    print(f"Total roadmaps for {uid}: {len(rms)}")
    for r in rms:
        print(f"  ID: {r.get('_id')} | Title: {r.get('title')} | Status: {r.get('status')} | Role: {r.get('target_role')}")

asyncio.run(inspect())
