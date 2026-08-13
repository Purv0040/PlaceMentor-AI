"""Unit tests for Topic Analyzer."""

from services.topic_analyzer import TopicAnalyzer
from utils.constants import CORE_DSA_TOPICS


def test_topic_analyzer():
    raw_tag_counts = {
        "fundamental": [
            {"tagName": "Array", "problemsSolved": 30},
            {"tagName": "String", "problemsSolved": 20}
        ],
        "intermediate": [
            {"tagName": "Dynamic Programming", "problemsSolved": 18},
            {"tagName": "Tree", "problemsSolved": 16}
        ],
        "advanced": [
            {"tagName": "Graph", "problemsSolved": 2}
        ]
    }

    topic_stats, strong, average, weak, score = TopicAnalyzer.analyze_topics(raw_tag_counts)

    assert len(topic_stats) == len(CORE_DSA_TOPICS)
    assert topic_stats["Arrays"] == 30
    assert topic_stats["Dynamic Programming"] == 18
    assert "Arrays" in strong
    assert "Dynamic Programming" in strong

    # Check weak topics format
    assert len(weak) > 0
    graph_weak = next((item for item in weak if item.topic == "Graphs"), None)
    assert graph_weak is not None
    assert graph_weak.topic == "Graphs"
    assert graph_weak.score == 2.0
    assert graph_weak.priority in ("HIGH", "MEDIUM", "LOW")
    assert score > 0.0
