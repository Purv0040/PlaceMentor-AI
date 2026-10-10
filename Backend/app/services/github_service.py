import logging
from datetime import datetime, timezone, timedelta, date
from zoneinfo import ZoneInfo
from typing import Dict, List, Optional, Any, Tuple, Set
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.github_repository import GitHubRepository
from app.integrations.github_client import (
    GitHubAPIClient,
    GitHubUserNotFoundError,
    GitHubRateLimitError,
    GitHubAPIError,
)
from app.integrations.ai_client import AIClient, AIClientError

logger = logging.getLogger(__name__)

# Application standard timezone for day boundaries and streaks
APP_TIMEZONE = ZoneInfo("Asia/Kolkata")


def calculate_repo_quality(repo: Dict[str, Any]) -> Tuple[int, str]:
    """Calculate deterministic repository quality score (0-100) and tier based on verified attributes."""
    score = 0
    # 1. README Documentation (35 pts)
    if repo.get("has_readme"):
        score += 35
    elif repo.get("size", 0) > 0 and repo.get("description"):
        score += 15

    # 2. Descriptive context (25 pts)
    desc = repo.get("description")
    if desc and len(desc.strip()) >= 15:
        score += 25
    elif desc and len(desc.strip()) > 0:
        score += 15

    # 3. Original source / Not a fork (20 pts)
    if not repo.get("is_fork"):
        score += 20
    else:
        score += 5

    # 4. Activity recency based on pushed_at (10 pts)
    pushed_at = repo.get("pushed_at")
    if pushed_at:
        try:
            pushed_dt = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
            days_ago = (datetime.now(timezone.utc) - pushed_dt).days
            if days_ago <= 30:
                score += 10
            elif days_ago <= 90:
                score += 7
            elif days_ago <= 180:
                score += 4
        except Exception:
            score += 4

    # 5. Public community signals (10 pts)
    stars = repo.get("stars", 0)
    forks = repo.get("forks", 0)
    if stars > 0 or forks > 0:
        score += min(10, stars * 2 + forks * 3)

    score = max(0, min(100, score))

    if score >= 80:
        tier = "Production Grade"
    elif score >= 65:
        tier = "Active Project"
    elif score >= 45:
        tier = "Developing"
    else:
        tier = "Early Prototype"

    return score, tier


def calculate_event_metrics(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate commit counts, active streak, and weekly cadence from public events in Asia/Kolkata timezone."""
    now_local = datetime.now(APP_TIMEZONE)
    today_local = now_local.date()
    yesterday_local = today_local - timedelta(days=1)

    push_events = [e for e in events if e.get("type") == "PushEvent"]

    total_commits = 0
    commits_30d = 0
    commit_dates: Set[date] = set()
    last_active_dt = None

    weekly_buckets = [0] * 6
    week_labels = [f"W{i + 1}" for i in range(6)]

    for e in push_events:
        created_str = e.get("created_at")
        payload = e.get("payload", {})
        count = payload.get("size")
        if count is None:
            count = len(payload.get("commits", []))
        if count == 0:
            count = 1

        total_commits += count

        if created_str:
            try:
                # Convert UTC timestamp to local Asia/Kolkata time
                dt_raw = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                dt_local = dt_raw.astimezone(APP_TIMEZONE)
                event_date = dt_local.date()
                commit_dates.add(event_date)

                if last_active_dt is None or dt_local > last_active_dt:
                    last_active_dt = dt_local

                days_ago = (today_local - event_date).days
                if 0 <= days_ago <= 30:
                    commits_30d += count

                # Bucket into 6 rolling 7-day windows (42 days total)
                if 0 <= days_ago < 42:
                    week_idx = 5 - (days_ago // 7)
                    if 0 <= week_idx < 6:
                        weekly_buckets[week_idx] += count
            except Exception:
                pass

    active_streak = 0
    longest_streak = 0

    if commit_dates:
        # Current streak: only active if the developer committed today or yesterday
        if today_local in commit_dates or yesterday_local in commit_dates:
            check_date = today_local if today_local in commit_dates else yesterday_local
            while check_date in commit_dates:
                active_streak += 1
                check_date -= timedelta(days=1)

        # Longest streak across the 90-day window
        sorted_dates = sorted(commit_dates)
        current_run = 0
        prev_date = None
        for d in sorted_dates:
            if prev_date is None or d == prev_date + timedelta(days=1):
                current_run += 1
            else:
                current_run = 1
            prev_date = d
            if current_run > longest_streak:
                longest_streak = current_run

    weekly_activity = [
        {"week": week_labels[i], "commits": weekly_buckets[i]}
        for i in range(6)
    ]

    return {
        "total_commits": total_commits,
        "commits_30d": commits_30d,
        "active_streak": active_streak,
        "longest_streak": longest_streak,
        "last_active_date": last_active_dt.isoformat() if last_active_dt else None,
        "weekly_activity": weekly_activity,
    }


def calculate_language_distribution(data: Any) -> List[Dict[str, Any]]:
    """
    Calculate deterministic language distribution with exact 100% integer rounding
    using the Largest Remainder (Hare-Niemeyer) method.
    Accepts either a dict of {language: count/bytes} or a list of repository dicts.
    """
    if isinstance(data, list):
        lang_counts: Dict[str, int] = {}
        for r in data:
            if isinstance(r, dict):
                langs = r.get("languages")
                if isinstance(langs, dict) and langs:
                    for l_name, l_bytes in langs.items():
                        if isinstance(l_bytes, (int, float)) and l_bytes > 0:
                            lang_counts[l_name] = lang_counts.get(l_name, 0) + int(l_bytes)
                elif r.get("language"):
                    l_name = r["language"]
                    lang_counts[l_name] = lang_counts.get(l_name, 0) + 1
    elif isinstance(data, dict):
        lang_counts = {k: int(v) for k, v in data.items() if isinstance(v, (int, float)) and v > 0}
    else:
        return []

    total = sum(lang_counts.values())
    if total == 0:
        return []

    items = []
    int_sum = 0
    for name, count in sorted(lang_counts.items(), key=lambda x: x[1], reverse=True):
        raw_pct = (count / total) * 100
        int_pct = int(raw_pct)
        remainder = raw_pct - int_pct
        int_sum += int_pct
        items.append({
            "name": name,
            "count": count,
            "percentage": int_pct,
            "remainder": remainder
        })

    # Distribute the deficit to the items with largest remainders so sum is exactly 100%
    deficit = 100 - int_sum
    if deficit > 0:
        items_by_remainder = sorted(range(len(items)), key=lambda i: items[i]["remainder"], reverse=True)
        for i in range(min(deficit, len(items))):
            items[items_by_remainder[i]]["percentage"] += 1

    return [{
        "name": item["name"],
        "count": item["count"],
        "bytes": item["count"],
        "percentage": item["percentage"]
    } for item in items]



def calculate_impact_and_quality(
    repos: List[Dict[str, Any]],
    event_metrics: Dict[str, Any]
) -> Tuple[int, Dict[str, Any], int, List[str], List[str]]:
    """
    Calculate deterministic GitHub Impact Score (0-100) and Repo Quality Index.
    
    Formula:
      - 35% Repository Quality (Canonical Portfolio Average Quality)
      - 25% Activity & Freshness (recency of code pushes)
      - 20% Language Breadth (diversity of programming languages)
      - 20% Community Engagement (stars and forks)
    """
    if not repos:
        breakdown = {
            "repository_quality": {"score": 0, "weight": 35, "evidence": "No repositories available", "eligible_repos": 0, "status": "unavailable"},
            "activity_freshness": {"score": 0, "weight": 25, "evidence": "No recent activity", "status": "unavailable"},
            "language_breadth": {"score": 0, "weight": 20, "evidence": "No languages detected", "status": "unavailable"},
            "community_engagement": {"score": 0, "weight": 20, "evidence": "No stars or forks recorded", "status": "unavailable"}
        }
        return 0, breakdown, 0, [], ["No public repositories found to audit. Create or publish repositories to establish your impact score."]

    non_fork_repos = [r for r in repos if not r.get("is_fork")]
    eval_repos = non_fork_repos if non_fork_repos else repos
    n = len(eval_repos)

    # 1. Repository Quality (35% weight): Canonical Portfolio-wide Average Quality
    quality_scores = [calculate_repo_quality(r)[0] for r in eval_repos]
    repo_quality_score = round(sum(quality_scores) / len(quality_scores)) if quality_scores else 0
    quality_subscore = repo_quality_score

    readme_count = sum(1 for r in eval_repos if r.get("has_readme"))
    desc_count = sum(1 for r in eval_repos if r.get("description") and len(r["description"].strip()) > 0)
    readme_ratio = readme_count / n
    desc_ratio = desc_count / n

    # 2. Activity & Freshness (25%)
    now = datetime.now(timezone.utc)
    min_days_ago = None
    for r in eval_repos:
        p_at = r.get("pushed_at")
        if p_at:
            try:
                dt = datetime.fromisoformat(p_at.replace("Z", "+00:00"))
                days = (now - dt).days
                if min_days_ago is None or days < min_days_ago:
                    min_days_ago = days
            except Exception:
                pass

    if min_days_ago is None:
        activity_subscore = 20
        activity_evidence = "No repository push date available"
    elif min_days_ago <= 7:
        activity_subscore = 100
        activity_evidence = f"Pushed code {min_days_ago} days ago (Active this week)"
    elif min_days_ago <= 30:
        activity_subscore = 85
        activity_evidence = f"Pushed code {min_days_ago} days ago (Active this month)"
    elif min_days_ago <= 90:
        activity_subscore = 65
        activity_evidence = f"Most recent push was {min_days_ago} days ago"
    elif min_days_ago <= 180:
        activity_subscore = 45
        activity_evidence = f"Most recent push was {min_days_ago} days ago (>3 months)"
    else:
        activity_subscore = 25
        activity_evidence = f"Most recent push was {min_days_ago} days ago (>6 months)"

    # 3. Language Breadth (20%)
    distinct_langs = set(r["language"] for r in eval_repos if r.get("language"))
    lang_count = len(distinct_langs)
    if lang_count >= 4:
        lang_subscore = 100
    elif lang_count == 3:
        lang_subscore = 85
    elif lang_count == 2:
        lang_subscore = 70
    elif lang_count == 1:
        lang_subscore = 50
    else:
        lang_subscore = 20
    lang_evidence = f"{lang_count} primary language{'s' if lang_count != 1 else ''} ({', '.join(sorted(distinct_langs)) if distinct_langs else 'None'})"

    # 4. Community Engagement (20%)
    total_stars = sum(r.get("stars", 0) for r in eval_repos)
    total_forks = sum(r.get("forks", 0) for r in eval_repos)
    engagement_pts = total_stars * 10 + total_forks * 15
    if engagement_pts > 0:
        comm_subscore = min(100, max(30, engagement_pts))
    else:
        comm_subscore = 30 if n > 0 else 0
    comm_evidence = f"{total_stars} star{'s' if total_stars != 1 else ''}, {total_forks} fork{'s' if total_forks != 1 else ''}"

    # Overall impact score (0-100)
    impact_score = round(
        0.35 * quality_subscore +
        0.25 * activity_subscore +
        0.20 * lang_subscore +
        0.20 * comm_subscore
    )
    impact_score = max(0, min(100, impact_score))

    breakdown = {
        "repository_quality": {
            "score": quality_subscore,
            "weight": 35,
            "evidence": f"Average score across {n} eligible repositories. {readme_count}/{n} have verified READMEs ({round(readme_ratio * 100)}%), {desc_count}/{n} have descriptions ({round(desc_ratio * 100)}%).",
            "eligible_repos": n,
            "status": "available"
        },
        "activity_freshness": {
            "score": activity_subscore,
            "weight": 25,
            "evidence": activity_evidence,
            "status": "available" if min_days_ago is not None else "unavailable"
        },
        "language_breadth": {
            "score": lang_subscore,
            "weight": 20,
            "evidence": lang_evidence,
            "status": "available" if lang_count > 0 else "unavailable"
        },
        "community_engagement": {
            "score": comm_subscore,
            "weight": 20,
            "evidence": comm_evidence,
            "status": "available"
        }
    }

    # Average repo quality
    quality_scores = [calculate_repo_quality(r)[0] for r in eval_repos]
    avg_quality = round(sum(quality_scores) / len(quality_scores)) if quality_scores else 0

    # Evidence-based strengths & improvements
    strengths = []
    improvements = []

    if readme_ratio >= 0.7:
        strengths.append(f"Strong documentation: {round(readme_ratio * 100)}% of repositories include READMEs.")
    if desc_ratio >= 0.7:
        strengths.append("High context clarity: Most projects feature informative descriptions.")
    if lang_count >= 2:
        strengths.append(f"Multi-language versatility across {lang_count} stacks ({', '.join(sorted(distinct_langs))}).")
    if min_days_ago is not None and min_days_ago <= 30:
        strengths.append(f"Consistent cadence: Active code pushed within the last {min_days_ago} days.")
    if total_stars >= 5:
        strengths.append(f"Public community adoption: Earned {total_stars} stars across original repositories.")

    if readme_count < n:
        missing_readme = n - readme_count
        improvements.append(f"Add README documentation to {missing_readme} repositor{'ies' if missing_readme > 1 else 'y'}.")
    if desc_count < n:
        missing_desc = n - desc_count
        improvements.append(f"Provide concise project summaries on {missing_desc} repositor{'ies' if missing_desc > 1 else 'y'}.")
    if min_days_ago is not None and min_days_ago > 60:
        improvements.append("Repository freshness is declining; push periodic updates or commit bug fixes.")
    if total_stars == 0 and total_forks == 0:
        improvements.append("Increase project visibility by sharing repositories and adding topic tags.")

    if not strengths:
        strengths.append("Repository baseline established on GitHub.")

    return impact_score, breakdown, avg_quality, strengths, improvements


class GitHubService:
    """Service layer orchestrating GitHub profile connection, synchronization, and AI intelligence."""

    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        github_client: Optional[GitHubAPIClient] = None,
        ai_client: Optional[AIClient] = None
    ) -> None:
        self.db = db
        self.repo = GitHubRepository(db)
        self.github_client = github_client or GitHubAPIClient()
        self.ai_client = ai_client or AIClient()

    async def connect_github(self, user_id: str, username: str) -> Dict[str, Any]:
        """Validate GitHub profile username with API and save connection for authenticated user."""
        clean_user = username.strip().lstrip("@")
        if not clean_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GitHub username cannot be empty."
            )

        # Validate with GitHub API
        try:
            profile_info = await self.github_client.get_user_profile(clean_user)
        except GitHubUserNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"GitHub user '{clean_user}' not found on GitHub."
            )
        except GitHubRateLimitError:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="GitHub API rate limit hit. Please try again later."
            )
        except GitHubAPIError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"GitHub API error: {str(e)}"
            )

        # Upsert profile in DB
        created_or_updated = await self.repo.upsert_github_profile(
            user_id=user_id,
            github_username=profile_info["login"],
            profile_info=profile_info
        )
        logger.info("User %s successfully connected GitHub account '%s'", user_id, profile_info["login"])
        return created_or_updated

    async def get_github_profile(self, user_id: str) -> Dict[str, Any]:
        """Retrieve GitHub profile for user."""
        profile = await self.repo.find_by_user_id(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="GitHub profile not connected for this user."
            )
        return profile

    async def sync_github(self, user_id: str) -> Dict[str, Any]:
        """Synchronize GitHub profile and repositories from GitHub API."""
        existing = await self.repo.find_by_user_id(user_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No GitHub account connected. Please connect your GitHub account first."
            )

        username = existing["github_username"]
        await self.repo.update_sync_status(user_id, "syncing")

        try:
            # 1. Fetch fresh profile
            profile_info = await self.github_client.get_user_profile(username)

            # 2. Fetch public repositories
            repos = await self.github_client.get_user_repos(username, page=1, per_page=100)

            # 3. Fetch public events for commit and streak calculation
            events = await self.github_client.get_user_events(username, per_page=100)
            event_metrics = calculate_event_metrics(events)

            # 4. Calculate deterministic statistics and score each repository
            lang_counts: Dict[str, int] = {}
            total_stars = 0
            total_forks = 0
            forked_repos = 0
            non_fork_repos = 0
            with_readme = 0
            with_description = 0

            for r in repos:
                is_fork = r.get("is_fork", False)
                if is_fork:
                    forked_repos += 1
                else:
                    non_fork_repos += 1
                    if r.get("has_readme"):
                        with_readme += 1
                    desc = r.get("description")
                    if desc and len(desc.strip()) > 0:
                        with_description += 1

                total_stars += r.get("stars", 0)
                total_forks += r.get("forks", 0)

                lang = r.get("language")
                if lang and not is_fork:
                    lang_counts[lang] = lang_counts.get(lang, 0) + 1

                # Calculate individual repository quality score & tier
                q_score, q_tier = calculate_repo_quality(r)
                r["ast_score"] = q_score
                r["quality_score"] = q_score
                r["quality_tier"] = q_tier

            primary_lang = max(lang_counts, key=lang_counts.__getitem__) if lang_counts else None
            language_dist = calculate_language_distribution(lang_counts)

            # 5. Compute overall GitHub Impact Score and Repo Quality Index
            impact_score, impact_breakdown, repo_quality_index, strengths, improvements = calculate_impact_and_quality(
                repos, event_metrics
            )

            stats = {
                "total_repositories": len(repos),
                "public_repositories": profile_info.get("public_repos", len(repos)),
                "forked_repositories": forked_repos,
                "non_fork_repositories": non_fork_repos,
                "total_stars": total_stars,
                "total_forks": total_forks,
                "repos_with_readme": with_readme,
                "repos_with_description": with_description,
                "primary_language": primary_lang,
                "languages": lang_counts,
                "language_distribution": language_dist,
                "impact_score": impact_score,
                "repo_quality_score": repo_quality_index,
                "total_recent_commits": event_metrics["total_commits"],
                "commits_last_30_days": event_metrics["commits_30d"],
                "active_streak_days": event_metrics["active_streak"],
                "longest_streak_days": event_metrics["longest_streak"],
                "last_active_date": event_metrics["last_active_date"],
                "weekly_activity": event_metrics["weekly_activity"],
                "impact_breakdown": impact_breakdown,
                "strengths": strengths,
                "improvements": improvements,
                "data_scope": {
                    "timezone": "Asia/Kolkata",
                    "commits": "Public PushEvents within the last 90 days (GitHub REST API)",
                    "coverage": f"100% of public repositories analyzed ({len(repos)} repos)",
                    "eligible_repos_count": non_fork_repos if non_fork_repos > 0 else len(repos)
                }
            }

            # 6. Save repositories in DB
            profile_id = str(existing["id"])
            await self.repo.upsert_repositories(user_id, profile_id, repos)

            # 7. Save updated profile with stats & set sync status
            updated_profile = await self.repo.upsert_github_profile(
                user_id=user_id,
                github_username=profile_info["login"],
                profile_info=profile_info,
                statistics=stats
            )
            await self.repo.update_sync_status(user_id, "synced", is_success=True)

            logger.info("Successfully synchronized GitHub data for user %s (%d repos, impact score: %d)", user_id, len(repos), impact_score)
            return await self.get_github_profile(user_id)

        except (GitHubUserNotFoundError, GitHubRateLimitError, GitHubAPIError) as e:
            error_msg = str(e)
            logger.error("Failed to sync GitHub profile for user %s: %s", user_id, error_msg)
            await self.repo.update_sync_status(user_id, "failed", error=error_msg)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"GitHub sync failed: {error_msg}"
            )
        except Exception as e:
            error_msg = f"Unexpected sync failure: {str(e)}"
            logger.error(error_msg)
            await self.repo.update_sync_status(user_id, "failed", error=error_msg)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )

    async def get_github_repositories(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 50
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Fetch paginated list of user's synchronized GitHub repositories."""
        skip = (page - 1) * limit
        repos = await self.repo.find_repositories_by_user_id(user_id, skip=skip, limit=limit)
        total = await self.repo.count_repositories_by_user_id(user_id)
        return repos, total

    async def analyze_github(self, user_id: str) -> Dict[str, Any]:
        """Trigger AI analysis for the user's connected GitHub profile."""
        profile = await self.get_github_profile(user_id)
        username = profile["github_username"]

        sync_status = profile.get("sync", {}).get("status")
        if sync_status not in ["synced", "completed"]:
            # Auto-trigger sync if not synced yet
            try:
                profile = await self.sync_github(user_id)
            except Exception as e:
                logger.warning("Auto-sync prior to analysis failed: %s", e)

        try:
            analysis_result = await self.ai_client.analyze_github(username)
        except AIClientError as e:
            logger.error("AI GitHub analysis failed for user %s: %s", user_id, e)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI GitHub analysis failed: {str(e)}"
            )

        saved = await self.repo.save_analysis(user_id, analysis_result, version="1.0")
        if not saved:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save GitHub analysis result."
            )

        return await self.get_github_profile(user_id)

    async def get_github_analysis(self, user_id: str) -> Dict[str, Any]:
        """Get stored GitHub AI analysis result."""
        profile = await self.get_github_profile(user_id)
        analysis = profile.get("analysis")
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="GitHub AI analysis has not been generated yet. Please trigger analysis first."
            )
        return {
            "user_id": user_id,
            "github_username": profile["github_username"],
            "analysis_version": profile.get("analysis_version", "1.0"),
            "analyzed_at": profile.get("updated_at"),
            "analysis": analysis
        }

    async def disconnect_github(self, user_id: str) -> bool:
        """Disconnect and delete GitHub profile and repo data for user."""
        existing = await self.repo.find_by_user_id(user_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No GitHub account connected."
            )
        deleted = await self.repo.delete_by_user_id(user_id)
        logger.info("Disconnected GitHub profile for user %s", user_id)
        return deleted
