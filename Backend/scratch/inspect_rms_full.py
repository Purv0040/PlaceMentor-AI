import asyncio, sys
sys.path.append('.')
from app.core.database import get_database

async def check():
    db = await get_database()
    rms = await db['roadmaps'].find({'user_id': '6ad85d599865cd6fb408a513'}).to_list(20)
    for r in rms:
        print('--- ROADMAP ---')
        print('ID:', r.get('_id'))
        print('Title:', r.get('title'))
        print('Role:', r.get('target_role'))
        print('Status:', r.get('status'))
        print('Created:', r.get('created_at'))
        all_t = r.get('all_tasks', [])
        d1 = [t for t in all_t if t.get('day') == 1]
        print('Day 1 task count:', len(d1))
        for t in d1:
            print('  D1 Task:', t.get('title'), '| status:', t.get('status'))

asyncio.run(check())
