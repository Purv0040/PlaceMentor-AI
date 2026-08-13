"""Profile completeness analyzer for GitHub user profile."""

from typing import Dict, Any
from models.github import GitHubProfile


class ProfileAnalyzer:
    """Analyzes completeness of GitHub user profile."""

    @staticmethod
    def analyze_profile(profile_data: Dict[str, Any]) -> tuple[GitHubProfile, float]:
        """
        Parses raw profile dictionary into a GitHubProfile model and computes completeness score out of 10.
        """
        profile = GitHubProfile(
            username=profile_data.get("login", ""),
            name=profile_data.get("name"),
            bio=profile_data.get("bio"),
            followers=profile_data.get("followers", 0),
            following=profile_data.get("following", 0),
            public_repos=profile_data.get("public_repos", 0),
            public_gists=profile_data.get("public_gists", 0),
            created_at=profile_data.get("created_at"),
            updated_at=profile_data.get("updated_at"),
            avatar_url=profile_data.get("avatar_url"),
            html_url=profile_data.get("html_url"),
            company=profile_data.get("company"),
            location=profile_data.get("location"),
            blog=profile_data.get("blog"),
            email=profile_data.get("email")
        )

        score = 0.0

        # Name completeness (+2)
        if profile.name and len(profile.name.strip()) > 0:
            score += 2.0

        # Bio completeness (+2.5)
        if profile.bio and len(profile.bio.strip()) > 10:
            score += 2.5
        elif profile.bio and len(profile.bio.strip()) > 0:
            score += 1.0

        # Avatar present (+1.0)
        if profile.avatar_url:
            score += 1.0

        # Contact/Social info (+2.5 total: location, blog/email, company)
        if profile.location and len(profile.location.strip()) > 0:
            score += 1.0
        if profile.blog or profile.email:
            score += 1.0
        if profile.company:
            score += 0.5

        # Followers indicator (+2.0)
        if profile.followers >= 5:
            score += 2.0
        elif profile.followers > 0:
            score += 1.0

        final_score = min(10.0, round(score, 2))
        return profile, final_score
