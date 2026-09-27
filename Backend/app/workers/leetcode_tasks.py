from app.workers.celery_app import celery_app


@celery_app.task
def sync_leetcode_background(user_id: str, username: str) -> dict:
    # TODO: Implement async background LeetCode sync in future phase.
    return {"status": "synced", "user_id": user_id, "username": username}
