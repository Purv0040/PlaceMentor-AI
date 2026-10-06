from app.workers.celery_app import celery_app


@celery_app.task
def process_resume_background(
    resume_id: str,
) -> dict:
    """
    Background resume processing placeholder.

    Actual resume analysis currently happens
    through ResumeService.analyze_resume().
    """

    return {
        "status": "processed",
        "resume_id": resume_id,
    }