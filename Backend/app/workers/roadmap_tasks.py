from app.workers.celery_app import celery_app


@celery_app.task
def generate_roadmap_background(user_id: str) -> dict:
    # TODO: Implement async background roadmap generation in future phase.
    return {"status": "generated", "user_id": user_id}
