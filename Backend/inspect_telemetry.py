import asyncio
import os
import json
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import Settings
from app.services.skill_gap_service import SkillGapService
from app.engines.skill_gap_engine import DeterministicSkillGapEngine

async def main():
    settings = Settings()
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DATABASE]
    user = await db.users.find_one({"email": "1@gmail.com"})
    user_id = str(user["_id"])
    
    service = SkillGapService(db)
    # Check what profile, resume, github, leetcode, projects, tasks exist
    profile = await service.profile_repo.get_by_user_id(user_id)
    resume = await service.resume_repo.find_active_by_user(user_id)
    github = await service.github_repo.find_by_user_id(user_id)
    leetcode = await service.leetcode_repo.find_by_user_id(user_id)
    projects = await service.project_repo.find_by_user_id(user_id)
    tasks = await service.task_repo.get_all_by_user(user_id)

    print("Profile exists:", bool(profile), "Technical skills:", profile.get("technical_skills") if profile else None)
    print("Resume exists:", bool(resume))
    print("GitHub exists:", bool(github))
    print("LeetCode exists:", bool(leetcode), "Total solved:", leetcode.get("statistics", {}).get("total_solved") if leetcode else None)
    print("Projects count:", len(projects) if projects else 0)
    print("Tasks count:", len(tasks) if tasks else 0)
    completed_tasks = [t for t in (tasks or []) if t.get("status") in ("completed", "done")]
    print("Completed tasks count:", len(completed_tasks))
    for t in completed_tasks[:5]:
        print("  - Completed task:", t.get("title"), "skill:", t.get("skill"), "category:", t.get("category"))

    inv = service.engine.build_skill_inventory(
        profile_data=profile,
        resume_data=resume,
        github_data=github,
        leetcode_data=leetcode,
        projects_list=projects,
        tasks_list=tasks
    )
    print("\nInventory skills count:", len(inv))
    for k, v in list(inv.items())[:15]:
        print(f"  {v['skill']}: level={v['current_level']} ({v['current_level_num']}/4), sources={list(v['evidence_sources'])}")

asyncio.run(main())
