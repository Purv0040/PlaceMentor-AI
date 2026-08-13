"""Problem solving and difficulty distribution analyzer for LeetCode statistics."""

from typing import Dict, Any, Tuple
from models.leetcode import ProblemStatistics


class ProblemAnalyzer:
    """Analyzes solved problem counts and difficulty distribution."""

    @staticmethod
    def analyze_problems(raw_ac_submissions: list) -> Tuple[ProblemStatistics, float, float]:
        """
        Parses `submitStatsGlobal.acSubmissionNum` list into ProblemStatistics model.
        Returns:
        - ProblemStatistics model
        - Problems Solved Score (out of 25)
        - Difficulty Distribution Score (out of 20)
        """
        easy = 0
        medium = 0
        hard = 0
        total = 0

        for item in raw_ac_submissions:
            diff = item.get("difficulty", "").lower()
            cnt = item.get("count", 0)
            if diff == "all":
                total = cnt
            elif diff == "easy":
                easy = cnt
            elif diff == "medium":
                medium = cnt
            elif diff == "hard":
                hard = cnt

        # Fallback if 'all' was not explicitly passed
        if total == 0 and (easy + medium + hard) > 0:
            total = easy + medium + hard

        easy_pct = round((easy / total * 100.0), 2) if total > 0 else 0.0
        medium_pct = round((medium / total * 100.0), 2) if total > 0 else 0.0
        hard_pct = round((hard / total * 100.0), 2) if total > 0 else 0.0

        stats = ProblemStatistics(
            total_solved=total,
            easy_solved=easy,
            medium_solved=medium,
            hard_solved=hard,
            easy_percentage=easy_pct,
            medium_percentage=medium_pct,
            hard_percentage=hard_pct
        )

        # ----------------------------------------------------
        # 1. Problems Solved Score (Max 25)
        # ----------------------------------------------------
        if total >= 500:
            problems_score = 25.0
        elif total >= 350:
            problems_score = 20.0 + (total - 350) / 150 * 5.0
        elif total >= 200:
            problems_score = 15.0 + (total - 200) / 150 * 5.0
        elif total >= 100:
            problems_score = 10.0 + (total - 100) / 100 * 5.0
        elif total >= 50:
            problems_score = 5.0 + (total - 50) / 50 * 5.0
        else:
            problems_score = (total / 50.0) * 5.0

        problems_score = min(25.0, round(problems_score, 2))

        # ----------------------------------------------------
        # 2. Difficulty Distribution Score (Max 20)
        # ----------------------------------------------------
        # Evaluates weightage of Medium and Hard problems
        diff_score = 0.0

        if total > 0:
            # Medium problem ratio (+12 max)
            if medium_pct >= 50.0:
                diff_score += 12.0
            elif medium_pct >= 35.0:
                diff_score += 9.0
            elif medium_pct >= 20.0:
                diff_score += 6.0
            else:
                diff_score += (medium_pct / 20.0) * 6.0

            # Hard problem count (+8 max)
            if hard >= 30:
                diff_score += 8.0
            elif hard >= 15:
                diff_score += 6.0
            elif hard >= 5:
                diff_score += 4.0
            elif hard >= 1:
                diff_score += 2.0

        diff_score = min(20.0, round(diff_score, 2))

        return stats, problems_score, diff_score
