import asyncio
import logging
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

import sys
import os

# Add parent directory to sys.path so app core config is accessible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("seed_achievements")

ACHIEVEMENTS_TO_SEED = [
    {
        "code": "CONSISTENCY_14_DAYS",
        "title": "14-Day Consistency Master",
        "description": "Maintained an active daily preparation sprint without missing a single day.",
        "category": "Consistency",
        "icon": "local_fire_department",
        "color": "text-amber-400 bg-amber-500/10 border-amber-500/20",
        "points": 250,
        "rarity": "uncommon",
        "required_count": 14,
        "route": "/tasks",
        "action_label": "View Today's Tasks",
        "is_active": True,
    },
    {
        "code": "ATS_RESUME_VERIFIED",
        "title": "ATS Resume Verified",
        "description": "Achieved an ATS score above 80/100 with STAR bullet point quantification.",
        "category": "Milestones",
        "icon": "description",
        "color": "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
        "points": 150,
        "rarity": "common",
        "required_count": 80,
        "route": "/resume",
        "action_label": "Review Resume",
        "is_active": True,
    },
    {
        "code": "KNIGHT_RANK_LEETCODE",
        "title": "Knight Rank Problem Solver",
        "description": "Solved 300+ LeetCode problems and achieved Knight contest rating status.",
        "category": "DSA & Code",
        "icon": "terminal",
        "color": "text-purple-400 bg-purple-500/10 border-purple-500/20",
        "points": 300,
        "rarity": "rare",
        "required_count": 300,
        "route": "/leetcode",
        "action_label": "LeetCode Analytics",
        "is_active": True,
    },
    {
        "code": "PRODUCTION_GITHUB",
        "title": "Production Grade GitHub",
        "description": "Pushed 300+ commits with consistent daily activity streak on primary repositories.",
        "category": "Consistency",
        "icon": "account_tree",
        "color": "text-indigo-400 bg-indigo-500/10 border-indigo-500/20",
        "points": 200,
        "rarity": "uncommon",
        "required_count": 300,
        "route": "/github",
        "action_label": "GitHub Intelligence",
        "is_active": True,
    },
    {
        "code": "SYSTEM_ARCHITECT_PORTFOLIO",
        "title": "System Architect Portfolio",
        "description": "Audited 4+ full-stack microservices projects with decoupled event architecture.",
        "category": "System Design",
        "icon": "inventory_2",
        "color": "text-sky-400 bg-sky-500/10 border-sky-500/20",
        "points": 250,
        "rarity": "rare",
        "required_count": 4,
        "route": "/projects",
        "action_label": "Projects Audit",
        "is_active": True,
    },
    {
        "code": "TIER_1_DIAGNOSTIC",
        "title": "Tier-1 Diagnostic Cleared",
        "description": "Scored 75+ overall Placement Readiness baseline across all 7 evaluation vectors.",
        "category": "Milestones",
        "icon": "verified_user",
        "color": "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
        "points": 350,
        "rarity": "milestone",
        "required_count": 75,
        "route": "/placement-readiness",
        "action_label": "Placement Readiness",
        "is_active": True,
    },
    {
        "code": "GRAPH_SPECIALIST",
        "title": "Graph Traversal Specialist",
        "description": "Mastered Kahn's Topological Sort and 3-State DFS Graph Cycle Detection algorithms.",
        "category": "DSA & Code",
        "icon": "schema",
        "color": "text-purple-300 bg-purple-500/10 border-purple-500/20",
        "points": 200,
        "rarity": "uncommon",
        "required_count": 1,
        "route": "/leetcode",
        "action_label": "Practice Graphs",
        "is_active": True,
    },
    {
        "code": "REDIS_CACHING_MASTER",
        "title": "Redis Distributed Caching Master",
        "description": "Implement Redis distributed caching invalidation pattern to close #1 critical gap.",
        "category": "System Design",
        "icon": "memory",
        "color": "text-rose-400 bg-rose-500/10 border-rose-500/20",
        "points": 300,
        "rarity": "rare",
        "required_count": 1,
        "route": "/skill-gaps",
        "action_label": "Close Skill Gap",
        "is_active": True,
    },
    {
        "code": "DP_2D_CONQUEROR",
        "title": "Dynamic Programming 2D Conqueror",
        "description": "Solve 28 targeted 2D and Tree Dynamic Programming medium/hard problems.",
        "category": "DSA & Code",
        "icon": "code_blocks",
        "color": "text-indigo-400 bg-indigo-500/10 border-indigo-500/20",
        "points": 350,
        "rarity": "milestone",
        "required_count": 28,
        "route": "/tasks",
        "action_label": "View DP Tasks",
        "is_active": True,
    },
    {
        "code": "ROADMAP_90_DAYS",
        "title": "90-Day Placement Sprint Hero",
        "description": "Complete all 90 days of the adaptive SDE placement roadmap with 100% completion.",
        "category": "Milestones",
        "icon": "military_tech",
        "color": "text-amber-400 bg-amber-500/10 border-amber-500/20",
        "points": 500,
        "rarity": "milestone",
        "required_count": 90,
        "route": "/roadmap",
        "action_label": "View Roadmap",
        "is_active": True,
    },
]


async def seed():
    logger.info("Connecting to MongoDB: %s (DB: %s)", settings.MONGODB_URL[:30] + "...", settings.MONGODB_DATABASE)
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DATABASE]

    # 1. Ensure indexes
    logger.info("Ensuring indexes on collections...")
    await db["achievement_definitions"].create_index("code", unique=True)
    await db["user_achievements"].create_index("user_id")
    await db["user_achievements"].create_index([("user_id", 1), ("code", 1)], unique=True)
    await db["user_daily_claims"].create_index([("user_id", 1), ("date_str", 1)], unique=True)

    # 2. Seed Definitions
    now = datetime.now(timezone.utc)
    seeded_count = 0
    for ach in ACHIEVEMENTS_TO_SEED:
        ach_doc = dict(ach)
        ach_doc["updated_at"] = now
        res = await db["achievement_definitions"].update_one(
            {"code": ach["code"]},
            {"$set": ach_doc, "$setOnInsert": {"created_at": now}},
            upsert=True,
        )
        if res.upserted_id or res.modified_count:
            seeded_count += 1

    logger.info("Successfully seeded/updated %d achievement definitions in MongoDB.", seeded_count)

    # 3. If any user exists, seed default unlocked badges to match current progress
    users_cursor = db["users"].find({})
    users = await users_cursor.to_list(length=10)
    if users:
        for user in users:
            uid = str(user.get("_id"))
            logger.info("Verifying initial achievement progress for user: %s (%s)", uid, user.get("email"))
            initial_unlocked = [
                ("CONSISTENCY_14_DAYS", 42, 14, 250),
                ("ATS_RESUME_VERIFIED", 84, 80, 150),
                ("KNIGHT_RANK_LEETCODE", 342, 300, 300),
                ("PRODUCTION_GITHUB", 342, 300, 200),
                ("SYSTEM_ARCHITECT_PORTFOLIO", 4, 4, 250),
                ("TIER_1_DIAGNOSTIC", 78, 75, 350),
                ("GRAPH_SPECIALIST", 1, 1, 200),
            ]
            for code, cur, req, pts in initial_unlocked:
                await db["user_achievements"].update_one(
                    {"user_id": uid, "code": code},
                    {
                        "$set": {
                            "unlocked": True,
                            "current_count": cur,
                            "required_count": req,
                            "progress_percentage": 100.0,
                            "points": pts,
                            "unlocked_at": now,
                        }
                    },
                    upsert=True,
                )
        logger.info("User achievements initialized successfully.")

    client.close()
    logger.info("Seeding completed successfully.")


if __name__ == "__main__":
    asyncio.run(seed())
