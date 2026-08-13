"""Contest performance analyzer for LeetCode contest statistics."""

from typing import Dict, Any, Optional, Tuple
from models.leetcode import ContestData


class ContestAnalyzer:
    """Analyzes contest performance, ratings, and percentile rank."""

    @staticmethod
    def analyze_contest(contest_raw: Optional[Dict[str, Any]]) -> Tuple[ContestData, float]:
        """
        Parses raw contest ranking dictionary into ContestData model.
        Returns:
        - ContestData model
        - Contest Performance Score (out of 10)
        """
        if not contest_raw or not isinstance(contest_raw, dict):
            data = ContestData(
                rating=None,
                global_ranking=None,
                total_participants=None,
                top_percentage=None,
                attended_contests=0,
                is_available=False
            )
            return data, 0.0

        attended = contest_raw.get("attendedContestsCount", 0)
        rating = contest_raw.get("rating")
        global_rank = contest_raw.get("globalRanking")
        total_parts = contest_raw.get("totalParticipants")
        top_pct = contest_raw.get("topPercentage")

        if attended == 0 and rating is None:
            data = ContestData(
                rating=None,
                global_ranking=global_rank,
                total_participants=total_parts,
                top_percentage=top_pct,
                attended_contests=0,
                is_available=False
            )
            return data, 0.0

        data = ContestData(
            rating=round(rating, 2) if rating is not None else None,
            global_ranking=global_rank,
            total_participants=total_parts,
            top_percentage=round(top_pct, 2) if top_pct is not None else None,
            attended_contests=attended,
            is_available=True
        )

        # ----------------------------------------------------
        # Contest Performance Score (Max 10)
        # ----------------------------------------------------
        score = 0.0

        # Attended contests count (+3 max)
        if attended >= 10:
            score += 3.0
        elif attended >= 5:
            score += 2.0
        elif attended >= 1:
            score += 1.0

        # Rating evaluation (+7 max)
        if rating is not None:
            if rating >= 1800:
                score += 7.0
            elif rating >= 1600:
                score += 5.0
            elif rating >= 1400:
                score += 3.5
            elif rating >= 1200:
                score += 2.0
            else:
                score += 1.0

        final_contest_score = min(10.0, round(score, 2))
        return data, final_contest_score
