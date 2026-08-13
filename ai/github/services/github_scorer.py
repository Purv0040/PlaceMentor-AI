"""Scoring service for GitHub profile analysis."""

from models.github import GitHubScoreBreakdown


class GitHubScorer:
    """Combines individual sub-scores into a transparent score breakdown out of 100."""

    @staticmethod
    def calculate_score(
        repo_quality_score: float,
        activity_score: float,
        documentation_score: float,
        tech_diversity_score: float,
        profile_completeness_score: float
    ) -> GitHubScoreBreakdown:
        """
        Calculates and validates component sub-scores against maximum weights.
        Total = 100.
        """
        r_score = min(30.0, max(0.0, repo_quality_score))
        a_score = min(25.0, max(0.0, activity_score))
        d_score = min(20.0, max(0.0, documentation_score))
        t_score = min(15.0, max(0.0, tech_diversity_score))
        p_score = min(10.0, max(0.0, profile_completeness_score))

        total = round(r_score + a_score + d_score + t_score + p_score, 2)
        total = min(100.0, max(0.0, total))

        return GitHubScoreBreakdown(
            total_score=total,
            repository_quality=round(r_score, 2),
            activity=round(a_score, 2),
            documentation=round(d_score, 2),
            technology_diversity=round(t_score, 2),
            profile_completeness=round(p_score, 2)
        )
