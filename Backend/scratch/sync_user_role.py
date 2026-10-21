import asyncio, sys
from bson import ObjectId
sys.path.append('.')
from app.core.database import get_database

async def sync():
    db = await get_database()
    uid = '6ad85d599865cd6fb408a513'
    
    # 1. Update user document targetRole
    await db['users'].update_one(
        {'_id': ObjectId(uid)},
        {'$set': {'targetRole': 'Software Engineer', 'target_role': 'Software Engineer'}}
    )
    
    # 2. Update student_profiles target_role
    await db['student_profiles'].update_one(
        {'user_id': uid},
        {'$set': {'target_role': 'Software Engineer', 'current_role': 'Software Engineer'}},
        upsert=True
    )
    
    # 3. Mark Software Engineer roadmap as active
    await db['roadmaps'].update_many(
        {'user_id': uid},
        {'$set': {'status': 'superseded'}}
    )
    await db['roadmaps'].update_one(
        {'_id': ObjectId('6ad85d609865cd6fb408a515')},
        {'$set': {'status': 'active', 'is_active': True}}
    )
    
    # 4. Clean up tasks from superseded roadmaps in daily_tasks
    superseded_rm_ids = [
        '6ad85da89865cd6fb408a5d5',
        '6ad85dae9865cd6fb408a650',
        '6ad85dbf9865cd6fb408a706',
        '6ad85dd09865cd6fb408a781',
        '6ad85de09865cd6fb408a7fb',
        '6ad85deb9865cd6fb408a876'
    ]
    res_del = await db['daily_tasks'].delete_many({
        'user_id': uid,
        'roadmap_id': {'$in': superseded_rm_ids}
    })
    print(f'Deleted {res_del.deleted_count} tasks from superseded roadmaps.')
    
    # 5. Check remaining tasks for user
    remaining = await db['daily_tasks'].find({'user_id': uid}).to_list(100)
    print(f'Remaining tasks in daily_tasks for {uid}: {len(remaining)}')
    
    print('Sync completed successfully!')

asyncio.run(sync())
