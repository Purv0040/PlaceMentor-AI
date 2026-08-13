"""Main orchestration pipeline for LeetCode Analyzer."""

from typing import List, Optional, Dict

from models.leetcode import (
    LeetCodeAnalyzeResponse,
    ProblemStatistics,
    ConsistencyData,
    ContestData,
    DSAScoreBreakdown,
    WeakTopicItem,
    LeetCodeSuggestion
)
from services.leetcode_client import LeetCodeClient
from services.problem_analyzer import ProblemAnalyzer
from services.topic_analyzer import TopicAnalyzer
from services.consistency_analyzer import ConsistencyAnalyzer
from services.contest_analyzer import ContestAnalyzer
from services.dsa_scorer import DSAScorer
from utils.logger import logger


class LeetCodePipeline:
    """Orchestrates LeetCode data collection, component analysis, DSA scoring, and suggestion generation."""

    def __init__(self, client: Optional[LeetCodeClient] = None):
        self.client = client or LeetCodeClient()

    def generate_suggestions(
        self,
        problem_stats: ProblemStatistics,
        weak_topics: List[WeakTopicItem],
        consistency: ConsistencyData,
        contest_data: ContestData,
        score: DSAScoreBreakdown,
        topic_stats: Dict[str, int]
    ) -> List[LeetCodeSuggestion]:
        """Generates prioritized, rule-based recommendations for DSA skill improvement."""
        suggestions: List[LeetCodeSuggestion] = []

        # 1. Total Problems Solved Suggestions
        if problem_stats.total_solved < 150:
            suggestions.append(LeetCodeSuggestion(
                priority="HIGH",
                category="DIFFICULTY",
                message=f"Increase total solved problem count from {problem_stats.total_solved} to at least 250+ standard DSA questions.",
                impact="Essential to build pattern recognition for online coding assessments of Tier-1 and Tier-2 product companies."
            ))

        # 2. Difficulty Distribution Suggestions
        if problem_stats.medium_percentage < 40.0 and problem_stats.total_solved > 20:
            suggestions.append(LeetCodeSuggestion(
                priority="HIGH",
                category="DIFFICULTY",
                message=f"Your Medium problem ratio is currently {problem_stats.medium_percentage:.1f}%. Target solving at least 50-60% Medium difficulty questions.",
                impact="Most Indian tech interview coding rounds focus heavily on Medium difficulty problem patterns."
            ))

        if problem_stats.hard_solved < 10 and problem_stats.total_solved >= 150:
            suggestions.append(LeetCodeSuggestion(
                priority="MEDIUM",
                category="DIFFICULTY",
                message="Practice at least 15-20 Hard difficulty problems in Dynamic Programming and Graphs.",
                impact="Hard problems differentiate candidates for top-tier SDE roles."
            ))

        # 3. Topic-Specific Practice Suggestions (DP, Graph, Trees, etc.)
        dp_count = topic_stats.get("Dynamic Programming", 0)
        if dp_count < 15:
            suggestions.append(LeetCodeSuggestion(
                priority="HIGH",
                category="TOPIC",
                message=f"Focused Dynamic Programming practice recommended (currently solved: {dp_count}). Target 20+ DP problems covering 1D/2D DP.",
                impact="Dynamic Programming is one of the highest-frequency topics in Indian tech placement tests."
            ))

        graph_count = topic_stats.get("Graphs", 0)
        if graph_count < 15:
            suggestions.append(LeetCodeSuggestion(
                priority="HIGH",
                category="TOPIC",
                message=f"Focused Graph practice recommended (currently solved: {graph_count}). Practice BFS, DFS, Dijkstra, and Topological Sort.",
                impact="Graph algorithms are frequently asked in technical coding interviews and machine coding rounds."
            ))

        tree_count = topic_stats.get("Trees", 0)
        if tree_count < 15:
            suggestions.append(LeetCodeSuggestion(
                priority="MEDIUM",
                category="TOPIC",
                message=f"Increase Tree and Binary Search Tree problem practice (currently solved: {tree_count}).",
                impact="Trees form fundamental building blocks for algorithmic problem solving."
            ))

        # 4. Consistency Suggestions
        if consistency.is_available and consistency.monthly_activity < 10:
            suggestions.append(LeetCodeSuggestion(
                priority="HIGH",
                category="CONSISTENCY",
                message="Establish a regular DSA practice schedule of at least 1-2 problems daily.",
                impact="Consistent practice improves retention and problem-solving speed under timed constraints."
            ))

        # 5. Contest Suggestions
        if not contest_data.is_available or contest_data.attended_contests < 3:
            suggestions.append(LeetCodeSuggestion(
                priority="MEDIUM",
                category="CONTEST",
                message="Participate regularly in LeetCode Weekly and Biweekly contests to simulate real test pressure.",
                impact="Contests improve speed, accuracy, and ranking under strict timed exam environments."
            ))

        return suggestions

    async def run(self, username: str) -> LeetCodeAnalyzeResponse:
        """Executes full LeetCode analysis pipeline for a given username."""
        logger.info(f"Starting LeetCode analysis for user: {username}")

        # 1. Collect user data via GraphQL
        data = await self.client.get_user_data(username)
        matched_user = data.get("matchedUser", {})
        contest_raw = data.get("userContestRanking")

        # 2. Problem & Difficulty Analysis
        submit_stats = matched_user.get("submitStatsGlobal", {})
        ac_submissions = submit_stats.get("acSubmissionNum", [])
        problem_stats, problems_score, diff_score = ProblemAnalyzer.analyze_problems(ac_submissions)

        # 3. Topic Analysis
        tag_counts = matched_user.get("tagProblemCounts", {})
        topic_stats, strong_topics, average_topics, weak_topics, topic_score = (
            TopicAnalyzer.analyze_topics(tag_counts)
        )

        # 4. Consistency Analysis
        calendar_raw = matched_user.get("submissionCalendar")
        consistency_data, consistency_score = ConsistencyAnalyzer.analyze_consistency(calendar_raw)

        # 5. Contest Analysis
        contest_data, contest_score = ContestAnalyzer.analyze_contest(contest_raw)

        # 6. DSA Score Breakdown
        dsa_score = DSAScorer.calculate_score(
            problems_solved_score=problems_score,
            difficulty_distribution_score=diff_score,
            topic_coverage_score=topic_score,
            consistency_score=consistency_score,
            contest_performance_score=contest_score,
            contest_available=contest_data.is_available
        )

        # 7. Suggestions Generation
        suggestions = self.generate_suggestions(
            problem_stats=problem_stats,
            weak_topics=weak_topics,
            consistency=consistency_data,
            contest_data=contest_data,
            score=dsa_score,
            topic_stats=topic_stats
        )

        logger.info(f"Completed LeetCode analysis for {username}. Total Score: {dsa_score.total_score}")

        return LeetCodeAnalyzeResponse(
            success=True,
            username=username,
            problem_statistics=problem_stats,
            topic_statistics=topic_stats,
            weak_topics=weak_topics,
            consistency=consistency_data,
            contest_data=contest_data,
            dsa_score=dsa_score,
            suggestions=suggestions
        )
