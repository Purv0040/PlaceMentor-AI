"""Repository quality and technology diversity analyzer for GitHub repositories."""

from typing import List, Dict, Any, Tuple
from models.github import RepositorySummary, GitHubStatistics


class RepositoryAnalyzer:
    """Analyzes GitHub repositories for project quality and tech stack diversity."""

    @staticmethod
    def analyze_repositories(
        raw_repos: List[Dict[str, Any]]
    ) -> Tuple[List[RepositorySummary], GitHubStatistics, Dict[str, int], float, float]:
        """
        Parses raw repository dictionaries and calculates:
        - List of RepositorySummary objects
        - GitHubStatistics object
        - Language distribution dictionary (Language -> count)
        - Repository Quality Score (out of 30)
        - Technology Diversity Score (out of 15)
        """
        summaries: List[RepositorySummary] = []
        languages_count: Dict[str, int] = {}
        total_stars = 0
        total_forks = 0
        non_fork_count = 0
        fork_count = 0
        all_topics = set()

        for repo in raw_repos:
            is_fork = repo.get("fork", False)
            if is_fork:
                fork_count += 1
            else:
                non_fork_count += 1

            stars = repo.get("stargazers_count", 0)
            forks = repo.get("forks_count", 0)
            total_stars += stars
            total_forks += forks

            lang = repo.get("language")
            if lang:
                languages_count[lang] = languages_count.get(lang, 0) + 1

            topics = repo.get("topics", [])
            for t in topics:
                all_topics.add(t.lower())

            license_info = repo.get("license")
            license_name = license_info.get("name") if isinstance(license_info, dict) else None

            summary = RepositorySummary(
                name=repo.get("name", ""),
                full_name=repo.get("full_name", ""),
                description=repo.get("description"),
                is_fork=is_fork,
                created_at=repo.get("created_at"),
                updated_at=repo.get("updated_at"),
                pushed_at=repo.get("pushed_at"),
                size=repo.get("size", 0),
                stargazers_count=stars,
                watchers_count=repo.get("watchers_count", 0),
                forks_count=forks,
                language=lang,
                topics=topics,
                license=license_name,
                has_readme=False,  # Will be populated by readme analyzer / pipeline
                default_branch=repo.get("default_branch", "main"),
                open_issues_count=repo.get("open_issues_count", 0)
            )
            summaries.append(summary)

        # Build GitHubStatistics
        top_languages = sorted(languages_count.keys(), key=lambda l: languages_count[l], reverse=True)[:5]
        statistics = GitHubStatistics(
            total_repos=len(raw_repos),
            non_fork_repos=non_fork_count,
            fork_repos=fork_count,
            total_stars=total_stars,
            total_forks=total_forks,
            unique_topics_count=len(all_topics),
            top_languages=top_languages
        )

        # ----------------------------------------------------
        # 1. Repository Quality Score (Max 30)
        # ----------------------------------------------------
        # Evaluates original work (non-forks), descriptions, licensing, topic tags, sizes, stars.
        repo_quality_score = 0.0

        if non_fork_count >= 5:
            repo_quality_score += 10.0
        elif non_fork_count >= 3:
            repo_quality_score += 7.0
        elif non_fork_count >= 1:
            repo_quality_score += 4.0

        # Repos with detailed descriptions (+6 max)
        repos_with_desc = sum(1 for r in summaries if not r.is_fork and r.description and len(r.description.strip()) > 10)
        if repos_with_desc >= 3:
            repo_quality_score += 6.0
        elif repos_with_desc >= 1:
            repo_quality_score += 3.0

        # Repos with licenses (+4 max)
        repos_with_license = sum(1 for r in summaries if not r.is_fork and r.license)
        if repos_with_license >= 2:
            repo_quality_score += 4.0
        elif repos_with_license >= 1:
            repo_quality_score += 2.0

        # Repos with topics tagged (+4 max)
        repos_with_topics = sum(1 for r in summaries if not r.is_fork and len(r.topics) > 0)
        if repos_with_topics >= 3:
            repo_quality_score += 4.0
        elif repos_with_topics >= 1:
            repo_quality_score += 2.0

        # Repos with substantial codebase size > 100KB (+3 max)
        substantial_repos = sum(1 for r in summaries if not r.is_fork and r.size >= 100)
        if substantial_repos >= 3:
            repo_quality_score += 3.0
        elif substantial_repos >= 1:
            repo_quality_score += 1.5

        # Stars & Community Engagement (+3 max - NOT the only factor!)
        if total_stars >= 20:
            repo_quality_score += 3.0
        elif total_stars >= 5:
            repo_quality_score += 2.0
        elif total_stars >= 1:
            repo_quality_score += 1.0

        final_repo_quality = min(30.0, round(repo_quality_score, 2))

        # ----------------------------------------------------
        # 2. Technology Diversity Score (Max 15)
        # ----------------------------------------------------
        # Evaluates language breadth and domain topic diversity.
        tech_diversity_score = 0.0

        num_languages = len(languages_count)
        if num_languages >= 4:
            tech_diversity_score += 8.0
        elif num_languages >= 2:
            tech_diversity_score += 5.0
        elif num_languages == 1:
            tech_diversity_score += 3.0

        # Unique topic tags breadth (+7 max)
        if len(all_topics) >= 6:
            tech_diversity_score += 7.0
        elif len(all_topics) >= 3:
            tech_diversity_score += 4.5
        elif len(all_topics) >= 1:
            tech_diversity_score += 2.0

        final_tech_diversity = min(15.0, round(tech_diversity_score, 2))

        return summaries, statistics, languages_count, final_repo_quality, final_tech_diversity
