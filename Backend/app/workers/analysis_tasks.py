from app.workers.celery_app import celery_app


@celery_app.task
def run_readiness_analysis_background(user_id: str) -> dict:
    # TODO: Implement async background readiness score calculation in future phase.
    return {"status": "calculated", "user_id": user_id}
