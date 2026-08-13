"""Scoring service for LeetCode DSA profile evaluation."""

from models.leetcode import DSAScoreBreakdown


class DSAScorer:
    """Combines individual DSA sub-scores into a transparent score breakdown out of 100."""

    @staticmethod
    def calculate_score(
        problems_solved_score: float,
        difficulty_distribution_score: float,
        topic_coverage_score: float,
        consistency_score: float,
        contest_performance_score: float,
        contest_available: bool = True
    ) -> DSAScoreBreakdown:
        """
        Calculates and validates component DSA sub-scores against maximum weights.
        Total = 100.
        """
        p_score = min(25.0, max(0.0, problems_solved_score))
        d_score = min(20.0, max(0.0, difficulty_distribution_score))
        t_score = min(30.0, max(0.0, topic_coverage_score))
        c_score = min(15.0, max(0.0, consistency_score))
        ct_score = min(10.0, max(0.0, contest_performance_score)) if contest_available else 0.0

        total = round(p_score + d_score + t_score + c_score + ct_score, 2)
        total = min(100.0, max(0.0, total))

        return DSAScoreBreakdown(
            total_score=total,
            problems_solved_score=round(p_score, 2),
            difficulty_distribution_score=round(d_score, 2),
            topic_coverage_score=round(t_score, 2),
            consistency_score=round(c_score, 2),
            contest_performance_score=round(ct_score, 2),
            contest_available=contest_available
        )
