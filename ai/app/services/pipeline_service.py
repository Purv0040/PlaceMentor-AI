"""
End-to-End AI Placement Copilot Pipeline Orchestrator.

Connects all 11 modules sequentially:
Resume Analyzer -> GitHub Analyzer -> LeetCode Analyzer -> Student Profile Engine ->
Skill Gap Engine -> Readiness Engine -> Roadmap Generator -> Daily Task Engine ->
Progress Simulation -> Adaptive Engine -> AI Mentor

Includes synthetic demo data generators for testing and offline demo execution.
"""
import logging
from typing import Optional, List, Dict, Any

from app.schemas.student import StudentProfile, SelfReportedSkill
from app.schemas.resume import (
    ResumeAnalysis,
    ScoreDetail,
    Education,
    Experience,
    Project,
)
from app.schemas.github import (
    GitHubAnalysis,
    GitHubProfileRaw,
    ActivitySummary,
    LanguageDistribution,
    TechCategory,
    ComplexityAnalysis,
)
from app.schemas.leetcode import (
    LeetCodeAnalysis,
    LeetCodeProfileRaw,
    ProblemStatistics,
    DifficultyDistribution,
    TopicAnalysis,
    DataSourceStatus,
    ContestInfo,
)
from app.schemas.skills import ProfileBuildRequest, StudentIntelligenceProfile
from app.schemas.skill_gap import SkillGapRequest, SkillGapAnalysis
from app.schemas.readiness import ReadinessCalculateRequest, PlacementReadinessAnalysis
from app.schemas.roadmap import RoadmapGenerateRequest, PersonalizedRoadmap
from app.schemas.daily_task import TodayTasksRequest, TodayTasksResponse
from app.schemas.adaptive import (
    AdaptiveRoadmapRequest,
    AdaptiveRoadmapResponse,
    StudentProgressPayload,
    StudentPerformancePayload,
)
from app.schemas.mentor import MentorChatRequest, MentorChatResponse, StudentContext
from app.schemas.pipeline import PipelineRunRequest, PipelineRunResponse

from app.analyzers.resume_analyzer import ResumeAnalyzer
from app.engines.github_engine import GitHubIntelligence
from app.engines.leetcode_engine import LeetCodeIntelligence
from app.engines.profile_engine import StudentProfileIntelligenceEngine
from app.engines.skill_gap_engine import SkillGapEngine
from app.engines.readiness_engine import PlacementReadinessEngine
from app.engines.roadmap_engine import PersonalizedRoadmapEngine
from app.engines.task_engine import DailyTaskEngine
from app.engines.adaptive_engine import AdaptiveRoadmapEngine
from app.engines.mentor_engine import PersonalMentorEngine
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


def get_synthetic_resume_text() -> str:
    """Returns realistic but clearly marked synthetic resume text for AI/ML Engineer profile."""
    return """
================================================================================
DEMO RESUME - ALEX MATRIX (SYNTHETIC DATA FOR TESTING)
Target Role: AI/ML Engineer
Email: alex.matrix.demo@synthetic-domain.test | Location: City, State
================================================================================

SUMMARY
Dedicated Computer Science student specializing in Machine Learning and Deep Learning.
Experienced in building neural network models using PyTorch, containerizing services with Docker,
and deploying REST APIs with FastAPI.

EDUCATION
B.Tech in Computer Science & Engineering (2022 - 2026)
Synthetic Institute of Technology (DEMO DATA) | CGPA: 8.4 / 10.0

SKILLS
Programming: Python, C++, SQL, Bash
ML/AI Frameworks: PyTorch, Scikit-Learn, TensorFlow, NumPy, Pandas, OpenCV
Backend & DevOps: FastAPI, Flask, Docker, Git, Linux
CS Fundamentals: Data Structures, Algorithms, Operating Systems, Database Management Systems

PROJECTS
1. Neural Vision Classifier (PyTorch, FastAPI, Docker)
   - Developed a Convolutional Neural Network (CNN) in PyTorch for image classification achieving 92% test accuracy.
   - Built a high-throughput inference service using FastAPI processing 150 requests/sec.
   - Containerized application with Docker and published deployment manifests.

2. NLP Sentiment Analysis Pipeline (Transformers, Scikit-Learn, Python)
   - Fine-tuned BERT model for sentiment analysis on 50,000 text samples achieving 88% F1-score.
   - Implemented text preprocessing, tokenization, and vectorization pipelines using HuggingFace.

EXPERIENCE
AI/ML Research Intern | Synthetic AI Labs (DEMO) (May 2025 - Aug 2025)
- Assisted in training computer vision models for automated defect detection, optimizing inference latency by 25%.
- Authored automated evaluation scripts in Python and prepared technical documentation.
"""


def get_synthetic_student_profile() -> StudentProfile:
    """Returns synthetic StudentProfile instance for testing."""
    return StudentProfile(
        name="Alex Matrix (DEMO DATA)",
        email="alex.matrix.demo@synthetic-domain.test",
        target_role="AI/ML Engineer",
        target_companies=["Google", "Meta", "OpenAI"],
        graduation_year=2026,
        degree="B.Tech",
        branch="Computer Science",
        institution="Synthetic Institute of Technology (DEMO)",
        current_semester=7,
        cgpa=8.4,
        experience_level="Internship Experience",
        primary_interests=["Machine Learning", "Deep Learning", "Computer Vision"],
        self_reported_skills=[
            SelfReportedSkill(name="Python", level="Advanced"),
            SelfReportedSkill(name="PyTorch", level="Intermediate"),
            SelfReportedSkill(name="Docker", level="Beginner"),
            SelfReportedSkill(name="Data Structures", level="Intermediate"),
        ]
    )


def get_synthetic_github_analysis() -> GitHubAnalysis:
    """Returns deterministic synthetic GitHubAnalysis for offline / demo pipeline testing."""
    profile = GitHubProfileRaw(
        username="demo-aiml-dev",
        name="Alex Matrix (DEMO)",
        public_repos=8,
        followers=25,
        following=10
    )
    activity = ActivitySummary(
        total_public_repos=8,
        non_fork_repos=7,
        repos_with_readme=7,
        total_stars=18,
        total_forks=4,
        most_starred_repo="neural-vision-classifier",
        most_starred_count=12,
        most_recent_push="2026-09-15T10:00:00Z"
    )
    languages = LanguageDistribution(
        primary_language="Python",
        all_languages=["Python", "Dockerfile", "C++"],
        language_repo_counts={"Python": 6, "Dockerfile": 2, "C++": 1}
    )
    tech_categories = [
        TechCategory(name="Machine Learning", detected=True, evidence=["PyTorch repo", "Scikit-learn usage"]),
        TechCategory(name="Backend", detected=True, evidence=["FastAPI service repo"]),
        TechCategory(name="DevOps", detected=True, evidence=["Dockerfile present"]),
        TechCategory(name="Frontend", detected=False, evidence=[])
    ]
    complexity_analyses = [
        ComplexityAnalysis(repo_name="neural-vision-classifier", complexity_level="advanced", confidence="high", evidence=["Custom CNN architecture", "Docker build setup"]),
        ComplexityAnalysis(repo_name="nlp-sentiment-pipeline", complexity_level="intermediate", confidence="high", evidence=["HuggingFace transformers integration"])
    ]
    return GitHubAnalysis(
        profile=profile,
        activity=activity,
        languages=languages,
        technical_categories=tech_categories,
        complexity_analyses=complexity_analyses,
        strengths=["Strong Python code volume", "Good README documentation coverage (87.5%)", "Demonstrated PyTorch and Docker skills"],
        gaps=["No CI/CD workflows detected", "Limited open source contributions"],
        technical_patterns=["Modular microservice layout", "PyTorch deep learning model structure"],
        recommendations=["Add GitHub Actions CI/CD to ML repositories", "Document API endpoints with Swagger/OpenAPI"],
        evidence_summary="Active GitHub profile with strong evidence of Python, PyTorch, and containerized ML deployments."
    )


def get_synthetic_leetcode_analysis() -> LeetCodeAnalysis:
    """Returns deterministic synthetic LeetCodeAnalysis for offline / demo pipeline testing."""
    profile = LeetCodeProfileRaw(
        username="demo_leetcode_ml",
        ranking=45000,
        reputation=120
    )
    stats = ProblemStatistics(
        total_solved=150,
        easy_solved=75,
        medium_solved=65,
        hard_solved=10,
        total_questions=3000,
        acceptance_rate=62.5
    )
    difficulty_dist = DifficultyDistribution(
        easy_pct=50.0,
        medium_pct=43.33,
        hard_pct=6.67
    )
    topic_analysis = [
        TopicAnalysis(topic="Arrays", solved_count=35, difficulty_breakdown={"Easy": 15, "Medium": 18, "Hard": 2}, performance_level="strong", evidence=["Solved 35 Array problems"], confidence="high"),
        TopicAnalysis(topic="Strings", solved_count=25, difficulty_breakdown={"Easy": 12, "Medium": 11, "Hard": 2}, performance_level="strong", evidence=["Solved 25 String problems"], confidence="high"),
        TopicAnalysis(topic="Binary Search", solved_count=15, difficulty_breakdown={"Easy": 5, "Medium": 8, "Hard": 2}, performance_level="developing", evidence=["Solved 15 Binary Search problems"], confidence="medium"),
        TopicAnalysis(topic="Trees", solved_count=20, difficulty_breakdown={"Easy": 8, "Medium": 10, "Hard": 2}, performance_level="developing", evidence=["Solved 20 Tree problems"], confidence="medium"),
        TopicAnalysis(topic="Dynamic Programming", solved_count=5, difficulty_breakdown={"Easy": 2, "Medium": 3, "Hard": 0}, performance_level="beginner", evidence=["Only 5 DP problems solved"], confidence="high"),
        TopicAnalysis(topic="Graphs", solved_count=4, difficulty_breakdown={"Easy": 2, "Medium": 2, "Hard": 0}, performance_level="beginner", evidence=["Only 4 Graph problems solved"], confidence="high")
    ]
    return LeetCodeAnalysis(
        profile=profile,
        problem_statistics=stats,
        difficulty_distribution=difficulty_dist,
        topic_analysis=topic_analysis,
        strong_topics=["Arrays", "Strings"],
        weak_topics=["Dynamic Programming", "Graphs"],
        contest=ContestInfo(rating=1580.0, global_ranking=35000, attended_contests=8),
        recent_activity=[],
        recommendations=[
            "Focus on Dynamic Programming patterns (Knapsack, LCS, DP on Trees)",
            "Practice Graph traversal algorithms (BFS, DFS, Dijkstra)",
            "Increase Hard problem count to 25+"
        ],
        data_source_status=DataSourceStatus(
            provider="SyntheticLeetCodeProvider",
            profile_available=True,
            problems_available=True,
            topics_available=True,
            contest_available=True,
            recent_activity_available=False
        )
    )


class EndToEndPipelineOrchestrator:
    """
    Main End-to-End Pipeline Orchestrator.
    Connects all 11 AI layer modules into a unified placement copilot pipeline.
    """

    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service or LLMService()
        self.resume_analyzer = ResumeAnalyzer()
        self.github_intelligence = GitHubIntelligence()
        self.leetcode_intelligence = LeetCodeIntelligence()
        self.profile_engine = StudentProfileIntelligenceEngine()
        self.skill_gap_engine = SkillGapEngine(llm_service=self.llm_service)
        self.readiness_engine = PlacementReadinessEngine()
        self.roadmap_engine = PersonalizedRoadmapEngine(llm_service=self.llm_service)
        self.daily_task_engine = DailyTaskEngine(llm_service=self.llm_service)
        self.adaptive_engine = AdaptiveRoadmapEngine(llm_service=self.llm_service)
        self.mentor_engine = PersonalMentorEngine(llm_service=self.llm_service)

    def run_pipeline(self, request: Optional[PipelineRunRequest] = None) -> PipelineRunResponse:
        """
        Executes the 11-step AI placement copilot end-to-end flow.
        """
        req = request or PipelineRunRequest()
        target_role = req.target_role or "AI/ML Engineer"
        available_time = req.available_time or 120

        logger.info(f"=== Starting End-to-End Pipeline for target role: '{target_role}', available time: {available_time} min/day ===")

        # Step 1: Analyze resume
        logger.info("Step 1/11: Analyzing resume...")
        resume_text = req.resume_text or get_synthetic_resume_text()
        resume_analysis: ResumeAnalysis = self.resume_analyzer.analyze_text(resume_text)

        # Step 2: Analyze GitHub
        logger.info("Step 2/11: Analyzing GitHub profile...")
        if req.github_username:
            try:
                github_analysis: GitHubAnalysis = self.github_intelligence.analyze(req.github_username)
            except Exception as e:
                logger.warning(f"GitHub fetch failed for '{req.github_username}': {e}. Falling back to synthetic profile.")
                github_analysis = get_synthetic_github_analysis()
        else:
            github_analysis = get_synthetic_github_analysis()

        # Step 3: Analyze LeetCode
        logger.info("Step 3/11: Analyzing LeetCode profile...")
        if req.leetcode_username:
            try:
                leetcode_analysis: LeetCodeAnalysis = self.leetcode_intelligence.analyze(req.leetcode_username)
            except Exception as e:
                logger.warning(f"LeetCode fetch failed for '{req.leetcode_username}': {e}. Falling back to synthetic profile.")
                leetcode_analysis = get_synthetic_leetcode_analysis()
        else:
            leetcode_analysis = get_synthetic_leetcode_analysis()

        # Step 4: Build unified student profile
        logger.info("Step 4/11: Building unified student intelligence profile...")
        student_profile = req.student_profile or get_synthetic_student_profile()
        profile_req = ProfileBuildRequest(
            student_profile=student_profile,
            resume_analysis=resume_analysis,
            github_analysis=github_analysis,
            leetcode_analysis=leetcode_analysis
        )
        unified_profile: StudentIntelligenceProfile = self.profile_engine.build_profile(profile_req)

        # Step 5: Calculate skill gaps
        logger.info("Step 5/11: Calculating skill gaps...")
        skill_gaps: SkillGapAnalysis = self.skill_gap_engine.analyze_gaps(
            target_role=target_role,
            profile=unified_profile,
            profile_request=profile_req
        )

        # Step 6: Calculate placement readiness
        logger.info("Step 6/11: Calculating placement readiness...")
        readiness_req = ReadinessCalculateRequest(
            target_role=target_role,
            profile=unified_profile,
            resume_analysis=resume_analysis,
            github_analysis=github_analysis,
            leetcode_analysis=leetcode_analysis,
            skill_gaps=skill_gaps
        )
        readiness: PlacementReadinessAnalysis = self.readiness_engine.calculate_readiness(readiness_req)

        # Step 7: Generate 90-day roadmap
        logger.info("Step 7/11: Generating 90-day personalized roadmap...")
        roadmap_req = RoadmapGenerateRequest(
            profile=unified_profile,
            skill_gaps=skill_gaps,
            readiness=readiness,
            target_role=target_role,
            available_minutes_per_day=available_time
        )
        roadmap: PersonalizedRoadmap = self.roadmap_engine.generate_roadmap(roadmap_req)

        # Step 8: Generate today's tasks
        logger.info("Step 8/11: Generating today's tasks...")
        today_req = TodayTasksRequest(
            roadmap=roadmap,
            current_day=1,
            completed_tasks=[],
            missed_tasks=[],
            available_time=available_time,
            target_role=target_role,
            skill_gaps=skill_gaps
        )
        today_tasks: TodayTasksResponse = self.daily_task_engine.get_today_tasks(today_req)

        # Step 9: Simulate completed tasks
        logger.info("Step 9/11: Simulating completed tasks...")
        simulated_completed_tasks: List[str] = []
        if today_tasks.tasks:
            simulated_completed_tasks = [today_tasks.tasks[0].id]

        # Step 10: Run adaptive engine
        logger.info("Step 10/11: Running adaptive roadmap engine...")
        adaptive_req = AdaptiveRoadmapRequest(
            roadmap=roadmap,
            progress=StudentProgressPayload(
                completed_tasks=simulated_completed_tasks,
                missed_tasks=[],
                completion_rate=100.0 if simulated_completed_tasks else 0.0,
                current_day=1
            ),
            performance=StudentPerformancePayload(
                available_time=available_time,
                dsa_performance={"accuracy": 85.0, "weak_topics": ["Dynamic Programming"]}
            )
        )
        adapted_roadmap: AdaptiveRoadmapResponse = self.adaptive_engine.adapt_roadmap(adaptive_req)

        # Step 11: Ask AI mentor
        logger.info("Step 11/11: Interrogating AI Mentor ('What should I focus on today?')...")
        student_context = StudentContext(
            target_role=target_role,
            profile=unified_profile.model_dump(),
            resume_analysis=resume_analysis.model_dump(),
            github_analysis=github_analysis.model_dump(),
            leetcode_analysis=leetcode_analysis.model_dump(),
            skill_gaps=skill_gaps.model_dump(),
            readiness=readiness.model_dump(),
            roadmap=roadmap.model_dump(),
            today_tasks=today_tasks.model_dump(),
            progress={"completed_tasks": simulated_completed_tasks, "completion_rate": 100.0}
        )

        mentor_req = MentorChatRequest(
            message="What should I focus on today?",
            student_context=student_context
        )
        mentor_response: MentorChatResponse = self.mentor_engine.chat(mentor_req)

        logger.info("=== End-to-End Pipeline Execution Completed Successfully ===")

        return PipelineRunResponse(
            target_role=target_role,
            available_time=available_time,
            step_1_resume_analysis=resume_analysis,
            step_2_github_analysis=github_analysis,
            step_3_leetcode_analysis=leetcode_analysis,
            step_4_unified_profile=unified_profile,
            step_5_skill_gaps=skill_gaps,
            step_6_readiness=readiness,
            step_7_roadmap=roadmap,
            step_8_today_tasks=today_tasks,
            step_9_simulated_completed_tasks=simulated_completed_tasks,
            step_10_adapted_roadmap=adapted_roadmap,
            step_11_mentor_response=mentor_response
        )
