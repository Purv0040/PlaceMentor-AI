from app.workers.celery_app import celery_app


@celery_app.task
def process_resume_background(resume_id: str) -> dict:
    # TODO: Implement async background resume processing in future phase.
    return {"status": "processed", "resume_id": resume_id}
