"""Topic coverage analyzer for LeetCode DSA topics."""

from typing import Dict, List, Any, Tuple
from models.leetcode import WeakTopicItem
from utils.constants import CORE_DSA_TOPICS


class TopicAnalyzer:
    """Analyzes performance across standard DSA topics and identifies weak areas."""

    # Priority mapping for core placement topics when weak
    HIGH_PRIORITY_TOPICS = {"Dynamic Programming", "Graphs", "Trees", "Binary Search", "Hash Table", "Arrays"}
    MEDIUM_PRIORITY_TOPICS = {"Strings", "Linked List", "Stack", "Queue", "Heap"}
    LOW_PRIORITY_TOPICS = {"Greedy", "Backtracking"}

    @classmethod
    def analyze_topics(
        cls,
        tag_problem_counts: Dict[str, Any]
    ) -> Tuple[Dict[str, int], List[str], List[str], List[WeakTopicItem], float]:
        """
        Parses `tagProblemCounts` from LeetCode GraphQL and computes:
        - topic_statistics: Dict[str, int] (Topic -> solved count)
        - strong_topics: List[str]
        - average_topics: List[str]
        - weak_topics: List[WeakTopicItem]
        - topic_coverage_score: float (out of 30)
        """
        topic_stats: Dict[str, int] = {t: 0 for t in CORE_DSA_TOPICS}

        def normalize_tag(name: str) -> str:
            n = name.lower().replace("-", " ").replace("_", " ").strip()
            # Normalize singular/plural
            if n.endswith("s") and not n.endswith("ss"):
                n = n[:-1]
            return n.replace(" ", "")

        if tag_problem_counts:
            # Flatten categories: fundamental, intermediate, advanced
            for cat_key in ("fundamental", "intermediate", "advanced"):
                cat_list = tag_problem_counts.get(cat_key, [])
                if isinstance(cat_list, list):
                    for item in cat_list:
                        tag_name = item.get("tagName", "")
                        count = item.get("problemsSolved", 0)
                        norm_tag = normalize_tag(tag_name)
                        # Match tag_name against CORE_DSA_TOPICS
                        for core_t in CORE_DSA_TOPICS:
                            norm_core = normalize_tag(core_t)
                            if norm_tag == norm_core:
                                topic_stats[core_t] += count

        strong_topics: List[str] = []
        average_topics: List[str] = []
        weak_topics: List[WeakTopicItem] = []

        total_coverage_points = 0.0

        for topic in CORE_DSA_TOPICS:
            count = topic_stats.get(topic, 0)

            if count >= 15:
                strong_topics.append(topic)
                total_coverage_points += 2.3  # Max ~30 for 13 topics
            elif count >= 5:
                average_topics.append(topic)
                total_coverage_points += 1.2
            else:
                # Weak topic
                if count >= 1:
                    total_coverage_points += 0.4

                # Determine priority
                if topic in cls.HIGH_PRIORITY_TOPICS:
                    priority = "HIGH"
                elif topic in cls.MEDIUM_PRIORITY_TOPICS:
                    priority = "MEDIUM"
                else:
                    priority = "LOW"

                weak_topics.append(WeakTopicItem(
                    topic=topic,
                    score=float(count),
                    priority=priority
                ))

        # Sort weak_topics so HIGH priority items come first
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        weak_topics.sort(key=lambda item: priority_order.get(item.priority, 3))

        topic_coverage_score = min(30.0, round(total_coverage_points, 2))

        return topic_stats, strong_topics, average_topics, weak_topics, topic_coverage_score
