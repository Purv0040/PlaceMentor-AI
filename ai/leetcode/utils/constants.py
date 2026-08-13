"""Constants and scoring weights for LeetCode Analyzer."""

from typing import List

# Maximum component weights (Total 100)
WEIGHT_PROBLEMS_SOLVED: float = 25.0
WEIGHT_DIFFICULTY_DISTRIBUTION: float = 20.0
WEIGHT_TOPIC_COVERAGE: float = 30.0
WEIGHT_CONSISTENCY: float = 15.0
WEIGHT_CONTEST_PERFORMANCE: float = 10.0

# Official 13 core DSA topics required for Indian tech placement analysis
CORE_DSA_TOPICS: List[str] = [
    "Arrays",
    "Strings",
    "Hash Table",
    "Linked List",
    "Stack",
    "Queue",
    "Binary Search",
    "Trees",
    "Graphs",
    "Heap",
    "Greedy",
    "Backtracking",
    "Dynamic Programming"
]

# GraphQL API URL
LEETCODE_GRAPHQL_URL: str = "https://leetcode.com/graphql"
