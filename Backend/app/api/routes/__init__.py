from fastapi import APIRouter
from app.api.routes import (
    auth,
    users,
    onboarding,
    resume,
    github,
    leetcode,
    projects,
    readiness,
    skill_gaps,
    roadmap,
    tasks,
    progress,
    adaptive,
    interviews,
    communication,
    mentor,
    achievements,
    notifications,
    settings,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(onboarding.router, prefix="/onboarding", tags=["Onboarding"])
api_router.include_router(resume.router, prefix="/resume", tags=["Resume"])
api_router.include_router(github.router, prefix="/github", tags=["GitHub Integration"])
api_router.include_router(leetcode.router, prefix="/leetcode", tags=["LeetCode Integration"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(readiness.router, prefix="/readiness", tags=["Readiness"])
api_router.include_router(skill_gaps.router, prefix="/skill-gaps", tags=["Skill Gaps"])
api_router.include_router(roadmap.router, prefix="/roadmap", tags=["Roadmap"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(progress.router, prefix="/progress", tags=["Progress Tracking"])
api_router.include_router(adaptive.router, prefix="/adaptive", tags=["Adaptive Planning"])
api_router.include_router(interviews.router, prefix="/interviews", tags=["Mock Interviews"])
api_router.include_router(communication.router, prefix="/communication", tags=["Communication Analysis"])
api_router.include_router(mentor.router, prefix="/mentor", tags=["AI Mentor"])
api_router.include_router(achievements.router, prefix="/achievements", tags=["Achievements"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(settings.router, prefix="/settings", tags=["Settings"])