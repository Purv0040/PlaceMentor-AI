import asyncio
from app.core.database import db_manager

async def clean_duplicates():
    await db_manager.connect_to_mongo()
    db = db_manager.get_database()
    user_id = '6ad7563bc1a6a279c35ea526'

    # 1. Update Oct 20 tasks to have day_number: 1
    res1 = await db['daily_tasks'].update_many(
        {'user_id': user_id, 'date': '2026-10-20'},
        {'$set': {'day_number': 1}}
    )
    print('Updated Oct 20 tasks day_number:', res1.modified_count)

    # 2. Delete the duplicate Oct 21 LeetCode clones
    res2 = await db['daily_tasks'].delete_many(
        {
            'user_id': user_id,
            'date': '2026-10-21',
            'title': {'$in': ['Invert Binary Tree', 'Number of Islands', 'Largest Rectangle in Histogram']}
        }
    )
    print('Deleted duplicate Oct 21 clones:', res2.deleted_count)

    # 3. Check remaining Day 1 tasks
    remaining_d1 = await db['daily_tasks'].find({'user_id': user_id, 'day_number': 1}).to_list(50)
    print('Remaining Day 1 tasks count:', len(remaining_d1))
    for t in remaining_d1:
        print('  Title:', t.get('title'), '| Day:', t.get('day_number'), '| Date:', t.get('date'), '| Status:', t.get('status'), '| CompletedAt:', t.get('completed_at'))

    await db_manager.close_mongo_connection()

if __name__ == '__main__':
    asyncio.run(clean_duplicates())
