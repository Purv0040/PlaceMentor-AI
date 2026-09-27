import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

DEFAULT_ACHIEVEMENTS_SEED = [
    {
        "code": "FIRST_STEP",
        "title": "Onboarding Pioneer",
        "description": "Completed student profile setup and initial onboarding assessment.",
        "category": "Onboarding",
        "icon": "how_to_reg",
        "color": "text-blue-400 bg-blue-500/10 border-blue-500/20",
        "points": 100,
        "rarity": "common",
        "required_count": 1,
        "route": "/profile",
        "action_label": "View Profile",
    },
    {
        "code": "FIRST_RESUME",
        "title": "ATS Resume Verified",
        "description": "Uploaded and completed ATS analysis for primary resume.",
        "category": "Milestones",
        "icon": "description",
        "color": "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
        "points": 150,
        "rarity": "common",
        "required_count": 80,
        "route": "/resume",
        "action_label": "Review Resume",
    },
    {
        "code": "GITHUB_CONNECTED",
        "title": "Production Grade GitHub",
        "description": "Connected GitHub profile and synchronized repositories.",
        "category": "Consistency",
        "icon": "account_tree",
        "color": "text-indigo-400 bg-indigo-500/10 border-indigo-500/20",
        "points": 200,
        "rarity": "uncommon",
        "required_count": 1,
        "route": "/github",
        "action_label": "GitHub Intelligence",
    },
    {
        "code": "LEETCODE_CONNECTED",
        "title": "Knight Rank Problem Solver",
        "description": "Connected LeetCode account and synchronized problem solving metrics.",
        "category": "DSA & Code",
        "icon": "terminal",
        "color": "text-purple-400 bg-purple-500/10 border-purple-500/20",
        "points": 300,
        "rarity": "rare",
        "required_count": 300,
        "route": "/leetcode",
        "action_label": "LeetCode Analytics",
    },
    {
        "code": "FIRST_PROJECT",
        "title": "Portfolio Builder",
        "description": "Created and audited first software portfolio project.",
        "category": "System Design",
        "icon": "inventory_2",
        "color": "text-sky-400 bg-sky-500/10 border-sky-500/20",
        "points": 150,
        "rarity": "common",
        "required_count": 1,
        "route": "/projects",
        "action_label": "View Projects",
    },
    {
        "code": "PROJECT_BUILDER",
        "title": "System Architect Portfolio",
        "description": "Audited 3+ full-stack software projects.",
        "category": "System Design",
        "icon": "account_tree",
        "color": "text-sky-400 bg-sky-500/10 border-sky-500/20",
        "points": 250,
        "rarity": "rare",
        "required_count": 3,
        "route": "/projects",
        "action_label": "Projects Audit",
    },
    {
        "code": "ROADMAP_STARTED",
        "title": "90-Day Sprint Initiated",
        "description": "Generated personalized 90-day preparation roadmap.",
        "category": "Milestones",
        "icon": "map",
        "color": "text-amber-400 bg-amber-500/10 border-amber-500/20",
        "points": 100,
        "rarity": "common",
        "required_count": 1,
        "route": "/roadmap",
        "action_label": "View Roadmap",
    },
    {
        "code": "TASK_STARTER",
        "title": "First Task Completed",
        "description": "Completed first daily preparation task.",
        "category": "Consistency",
        "icon": "check_circle",
        "color": "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
        "points": 50,
        "rarity": "common",
        "required_count": 1,
        "route": "/tasks",
        "action_label": "View Tasks",
    },
    {
        "code": "TASK_10",
        "title": "Task Conqueror (10 Tasks)",
        "description": "Successfully completed 10 preparation tasks.",
        "category": "Consistency",
        "icon": "task_alt",
        "color": "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
        "points": 150,
        "rarity": "uncommon",
        "required_count": 10,
        "route": "/tasks",
        "action_label": "View Tasks",
    },
    {
        "code": "WEEK_WARRIOR",
        "title": "7-Day Streak Master",
        "description": "Maintained an active 7-day preparation streak.",
        "category": "Consistency",
        "icon": "local_fire_department",
        "color": "text-amber-400 bg-amber-500/10 border-amber-500/20",
        "points": 250,
        "rarity": "rare",
        "required_count": 7,
        "route": "/tasks",
        "action_label": "Daily Tasks",
    },
    {
        "code": "FIRST_INTERVIEW",
        "title": "Mock Interview Passed",
        "description": "Completed first AI mock interview session.",
        "category": "Interview & STAR",
        "icon": "videocam",
        "color": "text-purple-400 bg-purple-500/10 border-purple-500/20",
        "points": 250,
        "rarity": "uncommon",
        "required_count": 1,
        "route": "/mock-interview",
        "action_label": "Mock Interview",
    },
    {
        "code": "COMMUNICATION_START",
        "title": "Verbal Clarity Practice",
        "description": "Completed speech analysis in Communication Lab.",
        "category": "Interview & STAR",
        "icon": "mic",
        "color": "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
        "points": 150,
        "rarity": "common",
        "required_count": 1,
        "route": "/communication",
        "action_label": "Communication Lab",
    },
    {
        "code": "READINESS_TIER_1",
        "title": "Tier-1 Diagnostic Cleared",
        "description": "Achieved overall Placement Readiness score of 75+.",
        "category": "Milestones",
        "icon": "verified_user",
        "color": "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
        "points": 350,
        "rarity": "milestone",
        "required_count": 75,
        "route": "/placement-readiness",
        "action_label": "Placement Readiness",
    },
]


class AchievementRepository:
    """Repository handling raw MongoDB queries for achievement_definitions and user_achievements."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self.definitions = db["achievement_definitions"]
        self.user_achievements = db["user_achievements"]

    async def ensure_indexes(self) -> None:
        """Create database indexes."""
        try:
            await self.definitions.create_index("code", unique=True)
            await self.user_achievements.create_index("user_id")
            await self.user_achievements.create_index([("user_id", 1), ("code", 1)], unique=True)
            logger.info("AchievementRepository indexes created/verified.")
        except Exception as e:
            logger.warning("Error creating indexes in AchievementRepository: %s", e)

    def _convert_doc(self, doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not doc:
            return None
        doc = dict(doc)
        if "_id" in doc:
            doc["id"] = str(doc["_id"])
            doc["_id"] = str(doc["_id"])
        return doc

    async def seed_definitions_if_empty(self) -> List[Dict[str, Any]]:
        """Seed default achievement definitions if none exist."""
        await self.ensure_indexes()
        count = await self.definitions.count_documents({})
        if count == 0:
            now = datetime.now(timezone.utc)
            for item in DEFAULT_ACHIEVEMENTS_SEED:
                item["created_at"] = now
                item["is_active"] = True
                try:
                    await self.definitions.insert_one(dict(item))
                except Exception:
                    pass
        cursor = self.definitions.find({"is_active": True})
        docs = await cursor.to_list(length=100)
        return [self._convert_doc(d) for d in docs if d]

    async def get_all_definitions(self) -> List[Dict[str, Any]]:
        """Fetch all active achievement definitions."""
        return await self.seed_definitions_if_empty()

    async def get_user_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """Fetch all unlocked achievements for user."""
        cursor = self.user_achievements.find({"user_id": user_id})
        docs = await cursor.to_list(length=100)
        return [self._convert_doc(d) for d in docs if d]

    async def unlock_achievement(self, user_id: str, achievement_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Save unlocked achievement for user if not already unlocked."""
        await self.ensure_indexes()
        code = achievement_data.get("code")
        existing = await self.user_achievements.find_one({"user_id": user_id, "code": code})
        if existing:
            return None  # Already unlocked

        now = datetime.now(timezone.utc)
        achievement_data["user_id"] = user_id
        achievement_data["unlocked"] = True
        achievement_data["unlocked_at"] = achievement_data.get("unlocked_at", now)

        result = await self.user_achievements.insert_one(achievement_data)
        achievement_data["_id"] = str(result.inserted_id)
        achievement_data["id"] = str(result.inserted_id)
        return self._convert_doc(achievement_data)
