"""Main orchestration pipeline for GitHub Analyzer."""

from typing import List, Optional, Dict, Any

from models.github import (
    GitHubAnalyzeResponse,
    GitHubScoreBreakdown,
    GitHubSuggestion,
    RepositorySummary,
    GitHubProfile
)
from services.github_client import GitHubClient
from services.profile_analyzer import ProfileAnalyzer
from services.repository_analyzer import RepositoryAnalyzer
from services.readme_analyzer import READMEAnalyzer
from services.activity_analyzer import ActivityAnalyzer
from services.github_scorer import GitHubScorer
from utils.logger import logger


class GitHubPipeline:
    """Orchestrates GitHub data collection, component analysis, scoring, and suggestion generation."""

    def __init__(self, client: Optional[GitHubClient] = None):
        self.client = client or GitHubClient()

    def generate_suggestions(
        self,
        profile: GitHubProfile,
        repositories: List[RepositorySummary],
        score: GitHubScoreBreakdown,
        languages: Dict[str, int]
    ) -> List[GitHubSuggestion]:
        """Generates prioritized, actionable suggestions based on profile analysis."""
        suggestions: List[GitHubSuggestion] = []

        # 1. Profile Completeness Suggestions
        if score.profile_completeness < 7.0:
            if not profile.bio or len(profile.bio.strip()) < 10:
                suggestions.append(GitHubSuggestion(
                    priority="HIGH",
                    category="PROFILE",
                    message="Add a concise professional bio to your GitHub profile stating your tech stack and career aspirations.",
                    impact="Recruiters assess your GitHub bio to quickly identify your core domain and background."
                ))
            if not profile.name:
                suggestions.append(GitHubSuggestion(
                    priority="MEDIUM",
                    category="PROFILE",
                    message="Update your profile display name to match your full name on your resume.",
                    impact="Helps automated recruiter tools cross-reference your GitHub profile with your job application."
                ))
            if not profile.location or not profile.blog:
                suggestions.append(GitHubSuggestion(
                    priority="LOW",
                    category="PROFILE",
                    message="Add your location, LinkedIn profile URL, or personal portfolio link to your GitHub profile.",
                    impact="Provides complete candidate context for recruiters evaluating your online presence."
                ))

        # 2. Repository Quality & Descriptions
        non_forks = [r for r in repositories if not r.is_fork]
        if not non_forks:
            suggestions.append(GitHubSuggestion(
                priority="HIGH",
                category="REPOSITORY",
                message="Publish original repositories instead of only starring or forking external projects.",
                impact="Campus recruiters look for original code contributions to judge software development ability."
            ))
        else:
            missing_desc = [r for r in non_forks if not r.description or len(r.description.strip()) == 0]
            if missing_desc:
                names = ", ".join([r.name for r in missing_desc[:3]])
                suggestions.append(GitHubSuggestion(
                    priority="HIGH",
                    category="REPOSITORY",
                    message=f"Add project descriptions to your repositories ({names}).",
                    impact="Clear descriptions immediately explain what your application solves and its tech stack."
                ))

            missing_license = [r for r in non_forks if not r.license]
            if len(missing_license) >= 2:
                suggestions.append(GitHubSuggestion(
                    priority="MEDIUM",
                    category="REPOSITORY",
                    message="Add open-source licenses (e.g. MIT or Apache-2.0) to your original projects.",
                    impact="Demonstrates open-source awareness and standard industry project structure."
                ))

        # 3. Documentation & README Suggestions
        if score.documentation < 14.0:
            missing_readme_repos = [r for r in non_forks if not r.has_readme]
            if missing_readme_repos:
                names = ", ".join([r.name for r in missing_readme_repos[:3]])
                suggestions.append(GitHubSuggestion(
                    priority="HIGH",
                    category="DOCUMENTATION",
                    message=f"Create structured README.md files for repositories: {names}.",
                    impact="Projects with clear documentation receive significantly higher evaluations during interview code reviews."
                ))
            else:
                suggestions.append(GitHubSuggestion(
                    priority="HIGH",
                    category="DOCUMENTATION",
                    message="Enhance project README files with Installation steps, Usage guide, Features list, and Screenshots.",
                    impact="Rich documentation with visual previews increases recruiter engagement by up to 3x."
                ))

        # 4. Activity & Commit Signals Suggestions
        if score.activity < 15.0:
            suggestions.append(GitHubSuggestion(
                priority="HIGH",
                category="ACTIVITY",
                message="Maintain consistent commit activity by pushing code regularly to GitHub.",
                impact="Frequent activity signals passion, consistency, and active problem-solving skills."
            ))

        # 5. Topics & Tech Stack Diversity Suggestions
        if score.technology_diversity < 10.0:
            if len(languages) <= 2:
                suggestions.append(GitHubSuggestion(
                    priority="MEDIUM",
                    category="TOPICS",
                    message="Diversify your technical stack by building projects using backend frameworks, databases, or frontend libraries.",
                    impact="Shows versatility across modern software engineering stacks required for Indian tech roles."
                ))
            suggestions.append(GitHubSuggestion(
                priority="MEDIUM",
                category="TOPICS",
                message="Add relevant GitHub topic tags (e.g., 'fastapi', 'react', 'machine-learning') to your repositories.",
                impact="Topic tags increase project discoverability and demonstrate keyword alignment with job roles."
            ))

        return suggestions

    async def run(self, username: str) -> GitHubAnalyzeResponse:
        """Executes full GitHub analysis for a given username."""
        logger.info(f"Starting GitHub analysis for user: {username}")

        # 1. Collect profile and repos
        profile_raw = await self.client.get_user_profile(username)
        repos_raw = await self.client.get_user_repositories(username)
        events_raw = await self.client.get_user_events(username)

        # 2. Profile Analysis
        profile, profile_score = ProfileAnalyzer.analyze_profile(profile_raw)

        # 3. Repository Analysis
        repos, stats, languages, repo_quality_score, tech_diversity_score = (
            RepositoryAnalyzer.analyze_repositories(repos_raw)
        )

        # 4. README Analysis for top repositories
        readme_map: Dict[str, Optional[str]] = {}
        non_forks = [r for r in repos if not r.is_fork][:5]
        for repo in non_forks:
            readme_text = await self.client.get_repository_readme(username, repo.name)
            readme_map[repo.name] = readme_text

        doc_score = READMEAnalyzer.analyze_documentation(repos, readme_map)

        # 5. Activity Analysis
        activity_score = ActivityAnalyzer.analyze_activity(repos, events_raw)

        # 6. Score Computation
        score_breakdown = GitHubScorer.calculate_score(
            repo_quality_score=repo_quality_score,
            activity_score=activity_score,
            documentation_score=doc_score,
            tech_diversity_score=tech_diversity_score,
            profile_completeness_score=profile_score
        )

        # 7. Suggestions Generation
        suggestions = self.generate_suggestions(profile, repos, score_breakdown, languages)

        logger.info(f"Completed GitHub analysis for {username}. Total Score: {score_breakdown.total_score}")

        return GitHubAnalyzeResponse(
            success=True,
            username=username,
            profile=profile,
            repositories=repos,
            languages=languages,
            statistics=stats,
            score=score_breakdown,
            suggestions=suggestions
        )
