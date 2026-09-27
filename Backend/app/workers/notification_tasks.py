from app.workers.celery_app import celery_app


@celery_app.task
def send_notification_background(user_id: str, message: str) -> dict:
    # TODO: Implement async background notification delivery in future phase.
    return {"status": "sent", "user_id": user_id}
