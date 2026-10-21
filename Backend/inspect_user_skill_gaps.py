import asyncio
import os
import json
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import Settings
from app.services.skill_gap_service import SkillGapService
from app.engines.skill_gap_engine import DeterministicSkillGapEngine

async def main():
    settings = Settings()
    mongo_uri = settings.MONGODB_URI
    client = AsyncIOMotorClient(mongo_uri)
    db = client[settings.MONGODB_DATABASE]
    user = await db.users.find_one({"email": "1@gmail.com"})
    if not user:
        print("User 1@gmail.com not found, listing all users:")
        users = await db.users.find().to_list(10)
        for u in users:
            print(f"User: {u.get('email')}, id={u.get('_id')}")
        return

    user_id = str(user["_id"])
    print(f"Found user: {user.get('email')}, id={user_id}, target_role={user.get('target_role')}")
    
    # Check latest skill gaps doc in collection
    sg_doc = await db.skill_gaps.find_one({"user_id": user_id}, sort=[("updated_at", -1)])
    if sg_doc:
        print("\n--- Current DB Skill Gap Doc ---")
        print("Target Role:", sg_doc.get("target_role"))
        print("Overall Coverage:", sg_doc.get("overall_coverage"))
        print("Total Audited:", sg_doc.get("total_audited"))
        print("Confidence Index:", sg_doc.get("confidence_index"))
        print("Gaps Count:", len(sg_doc.get("priority_gaps", [])))
        print("Category Coverage:", json.dumps(sg_doc.get("category_coverage", []), indent=2))
        print("Top 3 Gaps:", json.dumps(sg_doc.get("priority_gaps", [])[:3], indent=2))
    else:
        print("No skill gap doc in DB for user")

    # Run fresh analyze
    service = SkillGapService(db)
    analysis = await service.analyze_skill_gaps(user_id, target_role_override="AI/ML Engineer")
    print("\n--- Fresh Analyzed Skill Gap ---")
    print("Target Role:", analysis.get("target_role"))
    print("Overall Coverage:", analysis.get("overall_coverage"))
    print("Total Audited:", analysis.get("total_audited"))
    print("Confidence Index:", analysis.get("confidence_index"))
    print("Gaps Count:", len(analysis.get("priority_gaps", [])))
    print("Category Coverage:", json.dumps(analysis.get("category_coverage", []), indent=2))

asyncio.run(main())
