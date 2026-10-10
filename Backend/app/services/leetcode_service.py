import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.leetcode_repository import LeetCodeRepository
from app.repositories.task_repository import TaskRepository
from app.integrations.leetcode_client import (
    LeetCodeAPIClient,
    LeetCodeUserNotFoundError,
    LeetCodeAPIError,
)
from app.integrations.ai_client import AIClient, AIClientError
from app.utils.dates import get_today_date_str, APP_TIMEZONE

logger = logging.getLogger(__name__)

# Standard 14 DSA topic catalog with realistic interview targets, weights, and high-yield problems
DSA_TOPIC_CATALOG = {
    "Arrays": {
        "target": 45,
        "interview_weight": "Fundamental (15%)",
        "aliases": ["array", "arrays"],
        "problems": [
            {"title": "Two Sum", "difficulty": "Easy", "url": "https://leetcode.com/problems/two-sum/"},
            {"title": "Best Time to Buy and Sell Stock", "difficulty": "Easy", "url": "https://leetcode.com/problems/best-time-to-buy-and-sell-stock/"},
            {"title": "Subarray Sum Equals K", "difficulty": "Medium", "url": "https://leetcode.com/problems/subarray-sum-equals-k/"},
            {"title": "Product of Array Except Self", "difficulty": "Medium", "url": "https://leetcode.com/problems/product-of-array-except-self/"},
            {"title": "Trapping Rain Water", "difficulty": "Hard", "url": "https://leetcode.com/problems/trapping-rain-water/"},
        ],
    },
    "Strings": {
        "target": 25,
        "interview_weight": "Medium (8%)",
        "aliases": ["string", "strings"],
        "problems": [
            {"title": "Valid Anagram", "difficulty": "Easy", "url": "https://leetcode.com/problems/valid-anagram/"},
            {"title": "Longest Substring Without Repeating Characters", "difficulty": "Medium", "url": "https://leetcode.com/problems/longest-substring-without-repeating-characters/"},
            {"title": "Group Anagrams", "difficulty": "Medium", "url": "https://leetcode.com/problems/group-anagrams/"},
            {"title": "Minimum Window Substring", "difficulty": "Hard", "url": "https://leetcode.com/problems/minimum-window-substring/"},
        ],
    },
    "Linked Lists": {
        "target": 20,
        "interview_weight": "Medium (8%)",
        "aliases": ["linked list", "linked-list"],
        "problems": [
            {"title": "Reverse Linked List", "difficulty": "Easy", "url": "https://leetcode.com/problems/reverse-linked-list/"},
            {"title": "Merge Two Sorted Lists", "difficulty": "Easy", "url": "https://leetcode.com/problems/merge-two-sorted-lists/"},
            {"title": "Linked List Cycle", "difficulty": "Easy", "url": "https://leetcode.com/problems/linked-list-cycle/"},
            {"title": "LRU Cache", "difficulty": "Medium", "url": "https://leetcode.com/problems/lru-cache/"},
            {"title": "Merge k Sorted Lists", "difficulty": "Hard", "url": "https://leetcode.com/problems/merge-k-sorted-lists/"},
        ],
    },
    "Stacks and Queues": {
        "target": 20,
        "interview_weight": "Medium (8%)",
        "aliases": ["stack", "queue", "monotonic stack"],
        "problems": [
            {"title": "Valid Parentheses", "difficulty": "Easy", "url": "https://leetcode.com/problems/valid-parentheses/"},
            {"title": "Min Stack", "difficulty": "Medium", "url": "https://leetcode.com/problems/min-stack/"},
            {"title": "Daily Temperatures", "difficulty": "Medium", "url": "https://leetcode.com/problems/daily-temperatures/"},
            {"title": "Largest Rectangle in Histogram", "difficulty": "Hard", "url": "https://leetcode.com/problems/largest-rectangle-in-histogram/"},
        ],
    },
    "Binary Search": {
        "target": 20,
        "interview_weight": "High (10%)",
        "aliases": ["binary search", "binary-search"],
        "problems": [
            {"title": "Binary Search", "difficulty": "Easy", "url": "https://leetcode.com/problems/binary-search/"},
            {"title": "Search in Rotated Sorted Array", "difficulty": "Medium", "url": "https://leetcode.com/problems/search-in-rotated-sorted-array/"},
            {"title": "Find Minimum in Rotated Sorted Array", "difficulty": "Medium", "url": "https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/"},
            {"title": "Median of Two Sorted Arrays", "difficulty": "Hard", "url": "https://leetcode.com/problems/median-of-two-sorted-arrays/"},
        ],
    },
    "Trees and Binary Search Trees": {
        "target": 30,
        "interview_weight": "High (12%)",
        "aliases": ["tree", "binary tree", "binary search tree"],
        "problems": [
            {"title": "Invert Binary Tree", "difficulty": "Easy", "url": "https://leetcode.com/problems/invert-binary-tree/"},
            {"title": "Maximum Depth of Binary Tree", "difficulty": "Easy", "url": "https://leetcode.com/problems/maximum-depth-of-binary-tree/"},
            {"title": "Lowest Common Ancestor of a BST", "difficulty": "Medium", "url": "https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-search-tree/"},
            {"title": "Validate Binary Search Tree", "difficulty": "Medium", "url": "https://leetcode.com/problems/validate-binary-search-tree/"},
            {"title": "Binary Tree Maximum Path Sum", "difficulty": "Hard", "url": "https://leetcode.com/problems/binary-tree-maximum-path-sum/"},
        ],
    },
    "Graphs": {
        "target": 25,
        "interview_weight": "High (12%)",
        "aliases": ["graph", "breadth-first search", "depth-first search", "union find", "topological sort"],
        "problems": [
            {"title": "Number of Islands", "difficulty": "Medium", "url": "https://leetcode.com/problems/number-of-islands/"},
            {"title": "Course Schedule", "difficulty": "Medium", "url": "https://leetcode.com/problems/course-schedule/"},
            {"title": "Clone Graph", "difficulty": "Medium", "url": "https://leetcode.com/problems/clone-graph/"},
            {"title": "Pacific Atlantic Water Flow", "difficulty": "Medium", "url": "https://leetcode.com/problems/pacific-atlantic-water-flow/"},
            {"title": "Word Ladder", "difficulty": "Hard", "url": "https://leetcode.com/problems/word-ladder/"},
        ],
    },
    "Backtracking": {
        "target": 15,
        "interview_weight": "Medium (6%)",
        "aliases": ["backtracking"],
        "problems": [
            {"title": "Subsets", "difficulty": "Medium", "url": "https://leetcode.com/problems/subsets/"},
            {"title": "Combination Sum", "difficulty": "Medium", "url": "https://leetcode.com/problems/combination-sum/"},
            {"title": "Permutations", "difficulty": "Medium", "url": "https://leetcode.com/problems/permutations/"},
            {"title": "N-Queens", "difficulty": "Hard", "url": "https://leetcode.com/problems/n-queens/"},
        ],
    },
    "Greedy Algorithms": {
        "target": 20,
        "interview_weight": "Medium (6%)",
        "aliases": ["greedy"],
        "problems": [
            {"title": "Maximum Subarray", "difficulty": "Medium", "url": "https://leetcode.com/problems/maximum-subarray/"},
            {"title": "Jump Game", "difficulty": "Medium", "url": "https://leetcode.com/problems/jump-game/"},
            {"title": "Gas Station", "difficulty": "Medium", "url": "https://leetcode.com/problems/gas-station/"},
            {"title": "Candy", "difficulty": "Hard", "url": "https://leetcode.com/problems/candy/"},
        ],
    },
    "Dynamic Programming": {
        "target": 30,
        "interview_weight": "Critical (15%)",
        "aliases": ["dynamic programming", "memoization"],
        "problems": [
            {"title": "Climbing Stairs", "difficulty": "Easy", "url": "https://leetcode.com/problems/climbing-stairs/"},
            {"title": "House Robber", "difficulty": "Medium", "url": "https://leetcode.com/problems/house-robber/"},
            {"title": "Coin Change", "difficulty": "Medium", "url": "https://leetcode.com/problems/coin-change/"},
            {"title": "Longest Increasing Subsequence", "difficulty": "Medium", "url": "https://leetcode.com/problems/longest-increasing-subsequence/"},
            {"title": "Edit Distance", "difficulty": "Medium", "url": "https://leetcode.com/problems/edit-distance/"},
        ],
    },
    "Matrix": {
        "target": 15,
        "interview_weight": "Fundamental (5%)",
        "aliases": ["matrix"],
        "problems": [
            {"title": "Set Matrix Zeroes", "difficulty": "Medium", "url": "https://leetcode.com/problems/set-matrix-zeroes/"},
            {"title": "Spiral Matrix", "difficulty": "Medium", "url": "https://leetcode.com/problems/spiral-matrix/"},
            {"title": "Rotate Image", "difficulty": "Medium", "url": "https://leetcode.com/problems/rotate-image/"},
        ],
    },
    "Sorting": {
        "target": 20,
        "interview_weight": "Fundamental (5%)",
        "aliases": ["sorting"],
        "problems": [
            {"title": "Merge Intervals", "difficulty": "Medium", "url": "https://leetcode.com/problems/merge-intervals/"},
            {"title": "Sort Colors", "difficulty": "Medium", "url": "https://leetcode.com/problems/sort-colors/"},
            {"title": "Top K Frequent Elements", "difficulty": "Medium", "url": "https://leetcode.com/problems/top-k-frequent-elements/"},
            {"title": "Kth Largest Element in an Array", "difficulty": "Medium", "url": "https://leetcode.com/problems/kth-largest-element-in-an-array/"},
        ],
    },
    "Enumeration": {
        "target": 15,
        "interview_weight": "Fundamental (5%)",
        "aliases": ["enumeration"],
        "problems": [
            {"title": "Palindrome Number", "difficulty": "Easy", "url": "https://leetcode.com/problems/palindrome-number/"},
            {"title": "Sequential Digits", "difficulty": "Medium", "url": "https://leetcode.com/problems/sequential-digits/"},
            {"title": "Next Greater Element III", "difficulty": "Medium", "url": "https://leetcode.com/problems/next-greater-element-iii/"},
        ],
    },
    "Simulation": {
        "target": 15,
        "interview_weight": "Medium (5%)",
        "aliases": ["simulation"],
        "problems": [
            {"title": "Fizz Buzz", "difficulty": "Easy", "url": "https://leetcode.com/problems/fizz-buzz/"},
            {"title": "Spiral Matrix II", "difficulty": "Medium", "url": "https://leetcode.com/problems/spiral-matrix-ii/"},
            {"title": "Game of Life", "difficulty": "Medium", "url": "https://leetcode.com/problems/game-of-life/"},
            {"title": "Robot Bounded In Circle", "difficulty": "Medium", "url": "https://leetcode.com/problems/robot-bounded-in-circle/"},
        ],
    },
}


class LeetCodeService:
    """Service layer orchestrating LeetCode profile connection, synchronization, and AI analysis."""

    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        leetcode_client: Optional[LeetCodeAPIClient] = None,
        ai_client: Optional[AIClient] = None,
    ) -> None:
        self.db = db
        self.repo = LeetCodeRepository(db)
        self.task_repo = TaskRepository(db)
        self.leetcode_client = leetcode_client or LeetCodeAPIClient()
        self.ai_client = ai_client or AIClient()

    async def connect_leetcode(self, user_id: str, username: str) -> Dict[str, Any]:
        """Validate LeetCode profile username with GraphQL provider, perform immediate initial sync, and save."""
        clean_user = username.strip().lstrip("@")
        if not clean_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="LeetCode username cannot be empty."
            )

        # Validate username with LeetCode GraphQL provider
        try:
            profile_info = await self.leetcode_client.get_user_profile(clean_user)
        except LeetCodeUserNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"LeetCode user '{clean_user}' not found on LeetCode."
            )
        except LeetCodeAPIError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"LeetCode data provider error: {str(e)}"
            )

        # Immediately fetch statistics, topics, contest, and recent submissions for complete data
        solved_stats = {}
        topic_stats = []
        contest_info = {}
        recent_subs = []
        try:
            solved_stats = await self.leetcode_client.get_solved_problems(clean_user)
            topic_stats = await self.leetcode_client.get_topic_tags(clean_user)
            contest_info = await self.leetcode_client.get_contest_info(clean_user) or {}
            recent_subs = await self.leetcode_client.get_recent_submissions(clean_user, limit=20)
        except Exception as e:
            logger.warning("Partial sync during connect_leetcode for %s: %s", clean_user, e)

        # Upsert profile in DB
        created_or_updated = await self.repo.upsert_leetcode_profile(
            user_id=user_id,
            leetcode_username=profile_info["username"],
            profile_info=profile_info,
            statistics=solved_stats,
            contest_info=contest_info,
            topic_stats=topic_stats,
            recent_activity=recent_subs
        )
        await self.repo.update_sync_status(user_id, "synced", is_success=True)
        logger.info("User %s successfully connected LeetCode account '%s' with %d solved", user_id, profile_info["username"], solved_stats.get("total_solved", 0))
        return created_or_updated

    async def get_leetcode_profile(self, user_id: str) -> Dict[str, Any]:
        """Retrieve LeetCode profile for user enriched with dynamic plan, focus areas, and readiness."""
        profile = await self.repo.find_by_user_id(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LeetCode profile not connected for this user."
            )

        # Self-healing: if statistics, topic_statistics, recent_activity, or streak is missing, auto-sync from LeetCode
        if (
            not profile.get("topic_statistics")
            or not profile.get("statistics")
            or not profile.get("recent_activity")
            or not profile.get("submission_calendar")
            or "current_streak" not in profile.get("statistics", {})
        ):
            try:
                profile = await self.sync_leetcode(user_id)
            except Exception as e:
                logger.warning("Auto-sync during get_leetcode_profile for user %s failed: %s", user_id, e)

        # Dynamically evaluate current streak relative to today's date
        if profile.get("statistics") and profile.get("submission_calendar"):
            try:
                import json
                raw_cal = profile.get("submission_calendar")
                cal_dict = json.loads(raw_cal) if isinstance(raw_cal, str) else raw_cal
                if isinstance(cal_dict, dict):
                    from datetime import datetime, timezone, timedelta
                    try:
                        from zoneinfo import ZoneInfo
                        tz = ZoneInfo("Asia/Kolkata")
                    except Exception:
                        tz = timezone(timedelta(hours=5, minutes=30))
                    dates = set(datetime.fromtimestamp(int(ts), tz).date() for ts in cal_dict.keys())
                    today = datetime.now(tz).date()
                    yesterday = today - timedelta(days=1)
                    current_streak = 0
                    check_date = today if today in dates else (yesterday if yesterday in dates else None)
                    while check_date and check_date in dates:
                        current_streak += 1
                        check_date -= timedelta(days=1)
                    profile["statistics"]["current_streak"] = current_streak
            except Exception as e:
                logger.warning("Error evaluating dynamic streak: %s", e)

        # Enrich profile with dynamic components safely
        try:
            profile["daily_plan"] = await self.get_daily_practice_plan(user_id)
        except Exception as e:
            logger.warning("Failed to populate daily plan for user %s: %s", user_id, e)
            profile["daily_plan"] = None

        try:
            profile["focus_areas"] = await self.get_focus_areas(user_id)
        except Exception as e:
            logger.warning("Failed to populate focus areas for user %s: %s", user_id, e)
            profile["focus_areas"] = []

        try:
            profile["readiness_breakdown"] = await self.get_readiness_breakdown(user_id)
        except Exception as e:
            logger.warning("Failed to populate readiness breakdown for user %s: %s", user_id, e)
            profile["readiness_breakdown"] = None

        try:
            profile["activity_history"] = await self.get_activity_history(user_id, days=30)
        except Exception as e:
            logger.warning("Failed to populate activity history for user %s: %s", user_id, e)
            profile["activity_history"] = None

        return profile

    async def sync_leetcode(self, user_id: str) -> Dict[str, Any]:
        """Synchronize LeetCode profile, problem statistics, topics, and contest rating."""
        existing = await self.repo.find_by_user_id(user_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No LeetCode account connected. Please connect your LeetCode account first."
            )

        username = existing["leetcode_username"]
        await self.repo.update_sync_status(user_id, "syncing")

        try:
            # 1. Fetch fresh profile info
            profile_info = await self.leetcode_client.get_user_profile(username)

            # 2. Fetch solved problem statistics
            solved_stats = await self.leetcode_client.get_solved_problems(username)

            # 3. Fetch topic statistics & contest ranking (graceful fallback if unavailable)
            topic_stats = await self.leetcode_client.get_topic_tags(username)
            contest_info = await self.leetcode_client.get_contest_info(username)
            recent_subs = await self.leetcode_client.get_recent_submissions(username, limit=20)

            # 4. Update profile in database
            updated = await self.repo.upsert_leetcode_profile(
                user_id=user_id,
                leetcode_username=profile_info["username"],
                profile_info=profile_info,
                statistics=solved_stats,
                contest_info=contest_info or {},
                topic_stats=topic_stats,
                recent_activity=recent_subs
            )
            await self.repo.update_sync_status(user_id, "synced", is_success=True)

            logger.info("Successfully synchronized LeetCode data for user %s (%d solved)", user_id, solved_stats.get("total_solved", 0))
            return await self.get_leetcode_profile(user_id)

        except (LeetCodeUserNotFoundError, LeetCodeAPIError) as e:
            error_msg = str(e)
            logger.error("Failed to sync LeetCode profile for user %s: %s", user_id, error_msg)
            await self.repo.update_sync_status(user_id, "failed", error=error_msg)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"LeetCode sync failed: {error_msg}"
            )
        except Exception as e:
            error_msg = f"Unexpected sync failure: {str(e)}"
            logger.error(error_msg)
            await self.repo.update_sync_status(user_id, "failed", error=error_msg)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )

    async def get_leetcode_statistics(self, user_id: str) -> Dict[str, Any]:
        """Fetch problem-solving statistics and contest ranking."""
        profile = await self.repo.find_by_user_id(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LeetCode profile not connected for this user."
            )
        return {
            "user_id": user_id,
            "leetcode_username": profile["leetcode_username"],
            "statistics": profile.get("statistics", {}),
            "contest": profile.get("contest", {}),
            "topic_statistics": profile.get("topic_statistics", [])
        }

    async def get_leetcode_activity(self, user_id: str) -> Dict[str, Any]:
        """Fetch recent submission activity."""
        profile = await self.repo.find_by_user_id(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LeetCode profile not connected for this user."
            )
        return {
            "user_id": user_id,
            "leetcode_username": profile["leetcode_username"],
            "recent_activity": profile.get("recent_activity", [])
        }

    async def get_focus_areas(self, user_id: str) -> List[Dict[str, Any]]:
        """Analyze actual user performance across the 14 DSA topics and return prioritized recommendations."""
        profile = await self.repo.find_by_user_id(user_id)
        if not profile:
            return []

        user_topics = profile.get("topic_statistics", [])
        # Build normalized lookup for user topic tag solves
        lookup: Dict[str, int] = {}
        for item in user_topics:
            name = (item.get("tagName") or "").strip().lower()
            slug = (item.get("slug") or "").strip().lower()
            solves = item.get("problemsSolved") or 0
            if name:
                lookup[name] = max(lookup.get(name, 0), solves)
            if slug:
                lookup[slug] = max(lookup.get(slug, 0), solves)

        recent = profile.get("recent_activity", [])
        solved_titles = {s.get("title", "").strip().lower() for s in recent if s.get("title")}

        focus_areas: List[Dict[str, Any]] = []

        for topic_name, config in DSA_TOPIC_CATALOG.items():
            # Match count across aliases
            solved_count = 0
            for alias in config["aliases"]:
                alias_clean = alias.strip().lower()
                if alias_clean in lookup:
                    solved_count = max(solved_count, lookup[alias_clean])

            target = config["target"]
            # Strictly bounded mastery 0-100%
            mastery_pct = min(100, max(0, int(round((solved_count / target) * 100))))

            # Determine priority based on mastery and weight
            weight = config["interview_weight"]
            if mastery_pct < 45 and ("Critical" in weight or "High" in weight):
                priority = "High"
            elif mastery_pct < 65:
                priority = "Medium"
            else:
                priority = "Low"

            # Recommended action
            if mastery_pct == 0:
                recommended_action = f"Start foundational problems in {topic_name}. Essential for screenings."
            elif mastery_pct < 50:
                deficit = target - solved_count
                recommended_action = f"Solve {deficit} more problems in {topic_name} to meet the interview benchmark."
            elif mastery_pct < 100:
                recommended_action = f"Progress to Medium/Hard challenges to solidify {topic_name} patterns."
            else:
                recommended_action = f"Benchmark target met ({solved_count}/{target}). Practice periodic revision."

            # Filter out already solved problems if possible
            suggested = []
            for prob in config["problems"]:
                if prob["title"].strip().lower() not in solved_titles:
                    suggested.append(prob)
                if len(suggested) == 3:
                    break
            if not suggested:
                suggested = config["problems"][:3]

            focus_areas.append({
                "topic": topic_name,
                "problems_solved": solved_count,
                "target": target,
                "mastery_percentage": mastery_pct,
                "priority": priority,
                "interview_weight": weight,
                "recommended_action": recommended_action,
                "suggested_problems": suggested
            })

        # Priority order: High priority first, then Medium, then Low, sorted by mastery ascending
        priority_map = {"High": 1, "Medium": 2, "Low": 3}
        focus_areas.sort(key=lambda x: (priority_map.get(x["priority"], 4), x["mastery_percentage"]))
        return focus_areas

    async def get_daily_practice_plan(self, user_id: str) -> Dict[str, Any]:
        """Fetch or dynamically generate today's DSA practice tasks persisted in daily_tasks collection."""
        today_str = get_today_date_str()
        existing_tasks = await self.task_repo.get_by_user_and_date(user_id, today_str)

        # Distinguish dedicated LeetCode practice tasks from generic roadmap milestones
        def is_practice_task(t: Dict[str, Any]) -> bool:
            res = (t.get("resource") or t.get("resource_url") or "").lower()
            return (
                t.get("is_leetcode") is True
                or t.get("metadata", {}).get("type") == "leetcode_practice"
                or "leetcode.com/problems/" in res
            )

        practice_tasks = [t for t in existing_tasks if is_practice_task(t)]

        # If no dedicated LeetCode practice tasks exist for today, generate and persist 3 recommended tasks based on weak topics
        if not practice_tasks:
            focus_areas = await self.get_focus_areas(user_id)
            profile = await self.repo.find_by_user_id(user_id)
            recent = (profile or {}).get("recent_activity", [])
            solved_titles = {s.get("title", "").strip().lower() for s in recent if s.get("title")}

            # Prioritize weak topics with low mastery & high interview weight
            weak_topics = [f for f in focus_areas if f.get("priority") in ["High", "Medium"]]
            if not weak_topics:
                weak_topics = focus_areas

            selected_problems: List[Dict[str, Any]] = []
            selected_titles: set = set()
            difficulties_needed = ["Easy", "Medium", "Hard"]
            topic_idx = 0

            for diff in difficulties_needed:
                problem_found = None
                for _ in range(len(weak_topics)):
                    current_topic = weak_topics[topic_idx % len(weak_topics)]
                    topic_idx += 1
                    for p in current_topic.get("suggested_problems", []):
                        p_title = p.get("title", "").strip().lower()
                        if (
                            p.get("difficulty") == diff
                            and p_title not in solved_titles
                            and p_title not in selected_titles
                        ):
                            problem_found = {**p, "topic": current_topic["topic"]}
                            selected_titles.add(p_title)
                            break
                    if problem_found:
                        break

                if not problem_found and weak_topics:
                    # Fallback to any unsolved problem across weak topics
                    for curr in weak_topics:
                        for p in curr.get("suggested_problems", []):
                            p_title = p.get("title", "").strip().lower()
                            if p_title not in selected_titles and p_title not in solved_titles:
                                problem_found = {**p, "topic": curr["topic"]}
                                selected_titles.add(p_title)
                                break
                        if problem_found:
                            break

                if problem_found:
                    selected_problems.append(problem_found)

            # Persist generated tasks to MongoDB
            new_task_docs = []
            for prob in selected_problems[:3]:
                task_id = f"lc_task_{uuid.uuid4().hex[:12]}"
                new_task_docs.append({
                    "task_id": task_id,
                    "id": task_id,
                    "user_id": str(user_id),
                    "date": today_str,
                    "category": "DSA",
                    "title": prob["title"],
                    "description": f"Master {prob['topic']} ({prob['difficulty']}) on LeetCode for technical interview readiness.",
                    "difficulty": prob["difficulty"],
                    "topic": prob["topic"],
                    "status": "pending",
                    "resource": prob["url"],
                    "resource_url": prob["url"],
                    "estimated_minutes": 30 if prob["difficulty"] != "Hard" else 45,
                    "is_leetcode": True,
                    "metadata": {"type": "leetcode_practice", "topic": prob["topic"]},
                })

            if new_task_docs:
                created = await self.task_repo.create_many(new_task_docs)
                practice_tasks = created

        # Format into clean API items
        formatted_tasks = []
        for t in practice_tasks:
            tid = str(t.get("task_id") or t.get("id") or t.get("_id"))
            formatted_tasks.append({
                "task_id": tid,
                "title": t.get("title", "DSA Problem"),
                "difficulty": t.get("difficulty", "Medium"),
                "topic": t.get("topic", "DSA"),
                "status": t.get("status", "pending"),
                "resource_url": t.get("resource_url") or t.get("resource") or "https://leetcode.com",
                "estimated_minutes": t.get("estimated_minutes", 30),
            })

        completed_count = sum(1 for t in formatted_tasks if t["status"] == "completed")
        target_count = max(3, len(formatted_tasks))
        remaining_count = max(0, target_count - completed_count)

        return {
            "date": today_str,
            "target_count": target_count,
            "completed_count": completed_count,
            "remaining_count": remaining_count,
            "tasks": formatted_tasks
        }

    async def toggle_practice_task(self, user_id: str, task_id: str) -> Dict[str, Any]:
        """Toggle completion status of a daily DSA practice task and return updated plan."""
        task = await self.task_repo.get_by_id(task_id, user_id)
        if not task:
            # Fallback search by task_id in collection directly
            task = await self.task_repo.collection.find_one({
                "$or": [{"task_id": task_id}, {"id": task_id}, {"_id": task_id}],
                "user_id": str(user_id)
            })

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task '{task_id}' not found."
            )

        new_status = "completed" if task.get("status") != "completed" else "pending"
        update_data = {
            "status": new_status,
            "completed_at": datetime.now(timezone.utc) if new_status == "completed" else None
        }
        await self.task_repo.update(task_id, user_id, update_data)
        logger.info("User %s toggled DSA task %s to %s", user_id, task_id, new_status)
        return await self.get_daily_practice_plan(user_id)

    async def get_activity_history(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Compute problems solved per day from real submission calendar and accepted submissions (7, 30, or 90 days)."""
        profile = await self.repo.find_by_user_id(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LeetCode profile not connected."
            )

        days = 90 if days > 60 else (7 if days <= 14 else 30)
        recent_activity = profile.get("recent_activity", [])
        contest = profile.get("contest", {})
        contest_rating = contest.get("rating")
        contest_history = contest.get("history", [])

        # 1. Parse real submissionCalendar (has all active days and counts)
        calendar_by_date: Dict[str, int] = {}
        raw_cal = profile.get("submission_calendar") or profile.get("profile", {}).get("submission_calendar")
        oldest_cal_date = None

        if raw_cal:
            try:
                import json
                cal_data = json.loads(raw_cal) if isinstance(raw_cal, str) else raw_cal
                if isinstance(cal_data, dict):
                    cal_timestamps = []
                    for ts_str, count in cal_data.items():
                        try:
                            ts_int = int(ts_str)
                            cal_timestamps.append(ts_int)
                            dt = datetime.fromtimestamp(ts_int, APP_TIMEZONE)
                            d_str = dt.strftime("%Y-%m-%d")
                            calendar_by_date[d_str] = int(count)
                        except Exception:
                            continue
                    if cal_timestamps:
                        oldest_cal_date = datetime.fromtimestamp(min(cal_timestamps), APP_TIMEZONE).date()
            except Exception as e:
                logger.warning("Error parsing submission_calendar: %s", e)

        # 2. Merge with recent_activity (contains problem titles and timestamps)
        recent_timestamps = []
        for sub in recent_activity:
            raw_ts = sub.get("timestamp")
            if not raw_ts:
                continue
            try:
                ts_int = int(raw_ts)
                recent_timestamps.append(ts_int)
                dt = datetime.fromtimestamp(ts_int, APP_TIMEZONE)
                d_str = dt.strftime("%Y-%m-%d")
                calendar_by_date[d_str] = max(calendar_by_date.get(d_str, 0), 1)
            except Exception:
                continue

        now_local = datetime.now(APP_TIMEZONE).date()
        start_date = now_local - timedelta(days=days - 1)

        data_points = []
        total_in_period = 0

        # Build contest rating lookup by date if historical contest rankings exist
        contest_rating_by_date: Dict[str, float] = {}
        if contest_history:
            for item in contest_history:
                start_time = item.get("contest", {}).get("startTime")
                r = item.get("rating")
                if start_time and r:
                    c_date = datetime.fromtimestamp(int(start_time), APP_TIMEZONE).strftime("%Y-%m-%d")
                    contest_rating_by_date[c_date] = round(float(r), 1)

        last_known_rating = round(float(contest_rating), 1) if contest_rating else None

        for i in range(days):
            cur_date = start_date + timedelta(days=i)
            cur_str = cur_date.strftime("%Y-%m-%d")
            day_label = cur_date.strftime("%b %d")

            unique_solved = calendar_by_date.get(cur_str, 0)
            total_in_period += unique_solved

            if not raw_cal and not recent_timestamps:
                point_status = "no_data_available"
            elif oldest_cal_date and cur_date < oldest_cal_date:
                point_status = "unrecorded"
            else:
                point_status = "active" if unique_solved > 0 else "verified_zero"

            if cur_str in contest_rating_by_date:
                last_known_rating = contest_rating_by_date[cur_str]

            data_points.append({
                "date": cur_str,
                "day": day_label,
                "problems_solved": unique_solved,
                "submissions": unique_solved,
                "status": point_status,
                "contest_rating": last_known_rating
            })

        return {
            "days": days,
            "data_points": data_points,
            "total_solved_in_period": total_in_period,
            "total_submissions_in_period": total_in_period,
            "period_start": start_date.strftime("%Y-%m-%d"),
            "period_end": now_local.strftime("%Y-%m-%d"),
            "has_contest_history": contest_rating is not None or len(contest_history) > 0
        }


    async def get_readiness_breakdown(self, user_id: str) -> Dict[str, Any]:
        """Compute mathematically grounded interview readiness score with rubric breakdown, strengths, and gaps."""
        profile = await self.repo.find_by_user_id(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LeetCode profile not connected."
            )

        stats = profile.get("statistics", {})
        contest = profile.get("contest", {})
        focus_areas = await self.get_focus_areas(user_id)

        easy_solved = stats.get("easy_solved", 0)
        medium_solved = stats.get("medium_solved", 0)
        hard_solved = stats.get("hard_solved", 0)
        contest_rating = contest.get("rating") or 0.0

        # Deterministic scoring rubric:
        # Easy: up to 20 pts (0.15 pts / problem)
        easy_pts = min(20.0, round(easy_solved * 0.15, 2))
        # Medium: up to 45 pts (0.40 pts / problem)
        medium_pts = min(45.0, round(medium_solved * 0.40, 2))
        # Hard: up to 35 pts (0.70 pts / problem)
        hard_pts = min(35.0, round(hard_solved * 0.70, 2))

        # Core topic coverage: up to 15 pts (1.5 pts per core topic with >= 5 problems solved)
        core_covered = sum(1 for f in focus_areas if f["problems_solved"] >= 5)
        coverage_pts = min(15.0, round(core_covered * 1.5, 2))

        # Contest bonus: +5 for rating >= 1600, +10 for rating >= 1800
        contest_bonus = 0.0
        if contest_rating >= 1800:
            contest_bonus = 10.0
        elif contest_rating >= 1600:
            contest_bonus = 5.0

        raw_score = easy_pts + medium_pts + hard_pts + coverage_pts + contest_bonus
        # Bound between 25 and 98 to avoid deceptive 100% guarantees
        final_score = min(98, max(25, int(round(raw_score))))

        strengths: List[str] = []
        gaps: List[str] = []

        if medium_solved >= 100:
            strengths.append(f"Strong Medium problem volume ({medium_solved} solved) meeting Tier-1 bar.")
        elif medium_solved >= 50:
            strengths.append(f"Consistent Medium problem foundation ({medium_solved} solved).")
        else:
            gaps.append(f"Medium problem volume below target ({medium_solved}/100 benchmark).")

        if hard_solved >= 25:
            strengths.append(f"Proven advanced problem-solving skill ({hard_solved} Hard solved).")
        else:
            gaps.append(f"Hard problem exposure needs expansion ({hard_solved}/25 benchmark).")

        if core_covered >= 10:
            strengths.append(f"Broad topic breadth across {core_covered}/14 essential DSA patterns.")
        else:
            gaps.append(f"Gaps in topic coverage ({core_covered}/14 core topics adequately practiced).")

        if contest_bonus > 0:
            strengths.append(f"Active contest rating of {int(contest_rating)} (+{int(contest_bonus)} pts bonus).")

        explanation = (
            f"Readiness score of {final_score}/100 is dynamically derived from verified problem volume "
            f"({easy_solved} Easy, {medium_solved} Medium, {hard_solved} Hard), breadth across "
            f"{core_covered} DSA topic categories, and contest performance."
        )

        return {
            "readiness_score": final_score,
            "target_tier": "Tier-1 Technical Screening",
            "easy_pts": easy_pts,
            "medium_pts": medium_pts,
            "hard_pts": hard_pts,
            "coverage_pts": coverage_pts,
            "contest_bonus": contest_bonus,
            "strengths": strengths,
            "gaps": gaps,
            "explanation": explanation,
            "disclaimer": "Calibrated for algorithmic screening cutoffs. Does not guarantee placement outcomes."
        }

    async def analyze_leetcode(self, user_id: str) -> Dict[str, Any]:
        """Trigger AI LeetCode Analyzer microservice for the connected profile."""
        profile = await self.get_leetcode_profile(user_id)
        username = profile["leetcode_username"]

        sync_status = profile.get("sync", {}).get("status")
        if sync_status not in ["synced", "completed"]:
            try:
                profile = await self.sync_leetcode(user_id)
            except Exception as e:
                logger.warning("Auto-sync prior to LeetCode analysis failed: %s", e)

        try:
            analysis_result = await self.ai_client.analyze_leetcode(username)
        except AIClientError as e:
            logger.error("AI LeetCode analysis failed for user %s: %s", user_id, e)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI LeetCode analysis failed: {str(e)}"
            )

        saved = await self.repo.save_analysis(user_id, analysis_result, version="1.0")
        if not saved:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save LeetCode analysis result."
            )

        return await self.get_leetcode_profile(user_id)

    async def get_leetcode_analysis(self, user_id: str) -> Dict[str, Any]:
        """Get stored LeetCode AI analysis payload."""
        profile = await self.repo.find_by_user_id(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LeetCode profile not connected for this user."
            )
        analysis = profile.get("analysis")
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LeetCode AI analysis has not been generated yet. Please trigger analysis first."
            )
        return {
            "user_id": user_id,
            "leetcode_username": profile["leetcode_username"],
            "analysis_version": profile.get("analysis_version", "1.0"),
            "analyzed_at": profile.get("updated_at"),
            "analysis": analysis
        }

    async def disconnect_leetcode(self, user_id: str) -> bool:
        """Disconnect and delete LeetCode profile for authenticated user."""
        existing = await self.repo.find_by_user_id(user_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No LeetCode account connected."
            )
        deleted = await self.repo.delete_by_user_id(user_id)
        logger.info("Disconnected LeetCode profile for user %s", user_id)
        return deleted

