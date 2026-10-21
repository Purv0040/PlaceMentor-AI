import asyncio
from bson import ObjectId
from app.core.database import get_database

async def inspect():
    db = await get_database()
    uid = "6ad85d599865cd6fb408a513"
    u = await db['users'].find_one({'_id': ObjectId(uid)})
    sp = await db['student_profiles'].find_one({'user_id': uid})
    print("User targetRole:", u.get('targetRole') or u.get('target_role'))
    print("Student Profile target_role:", sp.get('target_role') if sp else "None")

asyncio.run(inspect())
