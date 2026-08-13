"""Submission activity and consistency analyzer for LeetCode profile."""

import json
import time
from typing import Optional, Tuple
from models.leetcode import ConsistencyData
from utils.logger import logger


class ConsistencyAnalyzer:
    """Analyzes submission calendar for weekly, monthly, and overall consistency."""

    @staticmethod
    def analyze_consistency(submission_calendar_raw: Optional[str]) -> Tuple[ConsistencyData, float]:
        """
        Parses submission calendar JSON string (timestamp string -> submission count).
        Returns:
        - ConsistencyData model
        - Consistency Score (out of 15)
        """
        if not submission_calendar_raw:
            data = ConsistencyData(
                active_days=0,
                weekly_activity=0,
                monthly_activity=0,
                recent_activity_score=0.0,
                consistency_score=0.0,
                is_available=False
            )
            return data, 0.0

        try:
            calendar_dict = json.loads(submission_calendar_raw)
            if not isinstance(calendar_dict, dict):
                raise ValueError("Invalid calendar format")
        except Exception as exc:
            logger.warning(f"Failed to parse submission calendar string: {exc}")
            data = ConsistencyData(
                active_days=0,
                weekly_activity=0,
                monthly_activity=0,
                recent_activity_score=0.0,
                consistency_score=0.0,
                is_available=False
            )
            return data, 0.0

        now_ts = int(time.time())
        seven_days_sec = 7 * 86400
        thirty_days_sec = 30 * 86400

        active_days = len(calendar_dict)
        weekly_activity = 0
        monthly_activity = 0

        for ts_str, count in calendar_dict.items():
            try:
                ts = int(ts_str)
                diff = now_ts - ts
                if diff <= seven_days_sec:
                    weekly_activity += 1
                if diff <= thirty_days_sec:
                    monthly_activity += 1
            except ValueError:
                continue

        # ----------------------------------------------------
        # Consistency Score (Max 15)
        # ----------------------------------------------------
        # 1. Total active days component (Max 7)
        if active_days >= 100:
            total_active_pts = 7.0
        elif active_days >= 50:
            total_active_pts = 5.0
        elif active_days >= 20:
            total_active_pts = 3.0
        elif active_days >= 5:
            total_active_pts = 1.5
        else:
            total_active_pts = (active_days / 5.0) * 1.5

        # 2. Recent monthly activity component (Max 5)
        if monthly_activity >= 15:
            monthly_pts = 5.0
        elif monthly_activity >= 8:
            monthly_pts = 3.5
        elif monthly_activity >= 3:
            monthly_pts = 2.0
        else:
            monthly_pts = (monthly_activity / 3.0) * 2.0

        # 3. Weekly activity component (Max 3)
        if weekly_activity >= 4:
            weekly_pts = 3.0
        elif weekly_activity >= 2:
            weekly_pts = 2.0
        elif weekly_activity >= 1:
            weekly_pts = 1.0
        else:
            weekly_pts = 0.0

        recent_activity_score = min(10.0, round(monthly_pts + weekly_pts, 2))
        final_consistency_score = min(15.0, round(total_active_pts + monthly_pts + weekly_pts, 2))

        data = ConsistencyData(
            active_days=active_days,
            weekly_activity=weekly_activity,
            monthly_activity=monthly_activity,
            recent_activity_score=recent_activity_score,
            consistency_score=final_consistency_score,
            is_available=True
        )

        return data, final_consistency_score
