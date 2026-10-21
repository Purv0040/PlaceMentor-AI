import asyncio
from app.core.database import db_manager

async def deduplicate_all_tasks():
    await db_manager.connect_to_mongo()
    db = db_manager.get_database()
    user_id = '6ad7563bc1a6a279c35ea526'

    # Get active roadmap ID
    active_rm = await db['roadmaps'].find_one({'user_id': user_id}, sort=[('created_at', -1)])
    active_rm_id = str(active_rm['_id']) if active_rm else None
    print('Active roadmap ID:', active_rm_id)

    # Find all tasks for this user
    all_user_tasks = await db['daily_tasks'].find({'user_id': user_id}).to_list(1000)
    print(f'Total tasks for user before cleanup: {len(all_user_tasks)}')

    seen_keys = {}
    to_delete = []

    for t in all_user_tasks:
        day = t.get('day_number') or 1
        title = (t.get('title') or '').strip().lower()
        key = (day, title)
        
        if key not in seen_keys:
            seen_keys[key] = t
        else:
            # Duplicate detected!
            prev = seen_keys[key]
            # If current is completed and prev is not, keep current and delete prev
            curr_completed = t.get('status') == 'completed' or bool(t.get('completed_at'))
            prev_completed = prev.get('status') == 'completed' or bool(prev.get('completed_at'))
            
            if curr_completed and not prev_completed:
                to_delete.append(prev['_id'])
                seen_keys[key] = t
            else:
                to_delete.append(t['_id'])

    print(f'Deleting {len(to_delete)} duplicate task records...')
    if to_delete:
        del_res = await db['daily_tasks'].delete_many({'_id': {'$in': to_delete}})
        print(f'Deleted {del_res.deleted_count} duplicate tasks!')

    remaining = await db['daily_tasks'].find({'user_id': user_id, 'day_number': 1}).to_list(50)
    print(f'Remaining distinct Day 1 tasks: {len(remaining)}')
    for r in remaining:
        print(f"  [{r.get('status')}] {r.get('title')} (Date: {r.get('date')}, CompletedAt: {r.get('completed_at')})")

    await db_manager.close_mongo_connection()

if __name__ == '__main__':
    asyncio.run(deduplicate_all_tasks())
