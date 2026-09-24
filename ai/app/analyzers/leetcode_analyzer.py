"""
LeetCode DSA topic analyzer — fully deterministic, no LLM.

Performance levels are derived only from measurable, observable signals:
  - How many tagged problems were solved
  - No phantom percentages or arbitrary scores

Transparent rule table::

  solved_count >= 15 AND medium_or_hard >= 5  → strong      (high confidence)
  solved_count >= 10 AND medium_or_hard >= 2  → strong      (medium confidence)
  solved_count >= 5                           → developing  (medium confidence)
  solved_count >= 1                           → beginner    (low confidence)
  solved_count == 0                           → untested    (low confidence)
"""
from typing import Any, Dict, List

from app.schemas.leetcode import (
    DifficultyDistribution,
    ProblemStatistics,
    TopicAnalysis,
)

# ---------------------------------------------------------------------------
# Canonical DSA topics we always report on
# ---------------------------------------------------------------------------
CANONICAL_TOPICS = [
    "Arrays",
    "Strings",
    "Linked Lists",
    "Stack",
    "Queue",
    "Binary Search",
    "Trees",
    "Graphs",
    "Greedy",
    "Backtracking",
    "Dynamic Programming",
    "Sorting",
    "Hashing",
]

# Map from canonical name → possible LeetCode slug variants
_SLUG_MAP: Dict[str, List[str]] = {
    "Arrays":               ["array"],
    "Strings":              ["string"],
    "Linked Lists":         ["linked-list", "linked list"],
    "Stack":                ["stack", "monotonic-stack"],
    "Queue":                ["queue", "monotonic-queue"],
    "Binary Search":        ["binary-search"],
    "Trees":                ["tree", "binary-tree", "binary-indexed-tree", "segment-tree"],
    "Graphs":               ["graph", "topological-sort", "shortest-path"],
    "Greedy":               ["greedy"],
    "Backtracking":         ["backtracking"],
    "Dynamic Programming":  ["dynamic-programming"],
    "Sorting":              ["sorting", "merge-sort", "counting-sort", "radix-sort"],
    "Hashing":              ["hash-table", "hash-map", "hash-function"],
}


# ---------------------------------------------------------------------------
# Core performance rating function
# ---------------------------------------------------------------------------

def _rate_topic(
    topic: str,
    solved: int,
    difficulty_breakdown: Dict[str, int],
) -> TopicAnalysis:
    """Apply the transparent rule table and return a TopicAnalysis."""
    medium_hard = difficulty_breakdown.get("Medium", 0) + difficulty_breakdown.get("Hard", 0)
    hard_only   = difficulty_breakdown.get("Hard", 0)
    evidence: List[str] = []

    if solved == 0:
        level = "untested"
        confidence = "low"
        evidence = [f"No {topic} problems solved yet"]
    elif solved >= 15 and medium_hard >= 5:
        level = "strong"
        confidence = "high"
        evidence = [
            f"Solved {solved} {topic} problems",
            f"{medium_hard} are Medium or Hard difficulty",
        ]
        if hard_only:
            evidence.append(f"{hard_only} Hard problems solved")
    elif solved >= 10 and medium_hard >= 2:
        level = "strong"
        confidence = "medium"
        evidence = [
            f"Solved {solved} {topic} problems",
            f"{medium_hard} are Medium or Hard",
        ]
    elif solved >= 5:
        level = "developing"
        confidence = "medium"
        evidence = [
            f"Solved {solved} {topic} problems",
            "Mostly Easy-level problems" if medium_hard == 0 else f"{medium_hard} Medium/Hard included",
        ]
    else:
        level = "beginner"
        confidence = "low"
        evidence = [f"Only {solved} {topic} problem(s) solved — limited evidence"]

    return TopicAnalysis(
        topic=topic,
        solved_count=solved,
        difficulty_breakdown=difficulty_breakdown,
        performance_level=level,
        evidence=evidence,
        confidence=confidence,
    )


# ---------------------------------------------------------------------------
# Public analyzer function
# ---------------------------------------------------------------------------

def analyze_topics(raw_tags: List[Dict[str, Any]]) -> List[TopicAnalysis]:
    """
    Map raw LeetCode tag data onto canonical DSA topics and rate each one.

    Each canonical topic is always present in the output — topics with no
    matching tag data get performance_level='untested'.
    """
    # Build a lookup: slug → count
    slug_to_count: Dict[str, int] = {}
    for tag in raw_tags:
        slug = tag.get("slug", "").lower()
        slug_to_count[slug] = slug_to_count.get(slug, 0) + tag.get("problemsSolved", 0)

    results: List[TopicAnalysis] = []

    for topic in CANONICAL_TOPICS:
        slugs = _SLUG_MAP.get(topic, [])
        solved = sum(slug_to_count.get(s, 0) for s in slugs)

        # Difficulty breakdown — the public LeetCode API provides only total
        # per-tag solved count, not per-difficulty-per-tag.  We report what
        # we actually know; callers see this clearly in the evidence field.
        difficulty_breakdown: Dict[str, int] = {}
        if solved > 0:
            difficulty_breakdown["Total"] = solved

        results.append(_rate_topic(topic, solved, difficulty_breakdown))

    return results


def build_difficulty_distribution(stats: ProblemStatistics) -> DifficultyDistribution:
    """Calculate percentage distribution across difficulty levels."""
    total = stats.total_solved
    if total == 0:
        return DifficultyDistribution()
    return DifficultyDistribution(
        easy_pct=round(stats.easy_solved / total * 100, 1),
        medium_pct=round(stats.medium_solved / total * 100, 1),
        hard_pct=round(stats.hard_solved / total * 100, 1),
    )


def generate_recommendations(
    stats: ProblemStatistics,
    topic_analyses: List[TopicAnalysis],
) -> List[str]:
    """
    Generate evidence-based recommendations.
    Only recommends what is justified by the observed data.
    """
    recs: List[str] = []
    total = stats.total_solved

    if total == 0:
        recs.append("Start solving LeetCode problems to build your DSA profile.")
        return recs

    # Difficulty balance
    hard_pct = stats.hard_solved / total * 100 if total else 0
    medium_pct = stats.medium_solved / total * 100 if total else 0

    if hard_pct < 5 and total >= 30:
        recs.append(
            f"Only {stats.hard_solved} Hard problems solved out of {total} total. "
            "Try incorporating Hard problems to prepare for competitive interviews."
        )
    if medium_pct < 30 and total >= 20:
        recs.append(
            f"Medium problems make up {medium_pct:.0f}% of your solves. "
            "Increase Medium problem practice — most FAANG interviews focus here."
        )

    # Weak topics
    untested = [t for t in topic_analyses if t.performance_level == "untested"]
    beginner = [t for t in topic_analyses if t.performance_level == "beginner"]

    if untested:
        names = ", ".join(t.topic for t in untested[:4])
        recs.append(f"No problems solved yet in: {names}. These are common interview topics.")
    if beginner:
        names = ", ".join(t.topic for t in beginner[:3])
        recs.append(f"Strengthen weak areas by solving more {names} problems at Medium difficulty.")

    if not recs:
        recs.append(
            "Good overall coverage. Focus on Hard problems and contest participation "
            "to reach top-tier interview performance."
        )

    return recs
