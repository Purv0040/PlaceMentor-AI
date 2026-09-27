from app.workers.celery_app import celery_app


@celery_app.task
def sync_github_background(user_id: str, username: str) -> dict:
    # TODO: Implement async background GitHub sync in future phase.
    return {"status": "synced", "user_id": user_id, "username": username}
