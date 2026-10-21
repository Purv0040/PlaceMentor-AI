import asyncio, json
from app.core.database import get_database
from app.services.mentor_context_service import MentorContextService

async def inspect():
    db = await get_database()
    user = await db['users'].find_one({'email': '1@gmail.com'})
    uid = str(user['_id'])
    
    ctx_svc = MentorContextService(db)
    ctx = await ctx_svc.build_student_context(uid)
    print("=== TODAY TASKS IN CONTEXT ===")
    print(json.dumps(ctx.get('today_tasks'), indent=2))

asyncio.run(inspect())
