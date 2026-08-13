"""Unit tests for Consistency Analyzer."""

import time
import json
from services.consistency_analyzer import ConsistencyAnalyzer


def test_consistency_analyzer_valid():
    now_ts = int(time.time())
    calendar = {
        str(now_ts - 86400 * 1): 2,
        str(now_ts - 86400 * 2): 1,
        str(now_ts - 86400 * 10): 3,
        str(now_ts - 86400 * 25): 4,
        str(now_ts - 86400 * 40): 1
    }
    raw_str = json.dumps(calendar)

    data, score = ConsistencyAnalyzer.analyze_consistency(raw_str)

    assert data.is_available is True
    assert data.active_days == 5
    assert data.weekly_activity == 2
    assert data.monthly_activity == 4
    assert score > 0.0


def test_consistency_analyzer_unavailable():
    data, score = ConsistencyAnalyzer.analyze_consistency(None)
    assert data.is_available is False
    assert data.active_days == 0
    assert score == 0.0
