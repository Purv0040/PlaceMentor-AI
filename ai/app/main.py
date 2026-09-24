from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.schemas.common import (
    GitHubRequest,
    LeetCodeRequest,
    TestRequest,
    TestResponse,
    TextRequest,
)
from app.schemas.resume import ResumeAnalysis
from app.schemas.github import GitHubAnalysis
from app.schemas.leetcode import LeetCodeAnalysis
from app.schemas.skills import ProfileBuildRequest, StudentIntelligenceProfile
from app.schemas.skill_gap import SkillGapRequest, SkillGapAnalysis
from app.schemas.readiness import ReadinessCalculateRequest, PlacementReadinessAnalysis
from app.schemas.roadmap import RoadmapGenerateRequest, PersonalizedRoadmap
from app.schemas.daily_task import TodayTasksRequest, TodayTasksResponse
from app.schemas.adaptive import AdaptiveRoadmapRequest, AdaptiveRoadmapResponse
from app.schemas.mentor import MentorChatRequest, MentorChatResponse
from app.schemas.pipeline import PipelineRunRequest, PipelineRunResponse
from app.services.llm_service import LLMService
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
from app.services.pipeline_service import EndToEndPipelineOrchestrator
from app.services.parser_service import PDFExtractionError
from app.services.github_service import (
    GitHubAPIError,
    GitHubRateLimitError,
    GitHubUserNotFoundError,
)
from app.services.leetcode_service import (
    LeetCodeAPIError,
    LeetCodeUserNotFoundError,
)

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AI Placement Copilot - AI Service",
    description="Microservice handling AI operations for PlaceMentor",
    version="0.8.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialise services at startup
llm_service = LLMService()
resume_analyzer = ResumeAnalyzer()
github_intelligence = GitHubIntelligence()
leetcode_intelligence = LeetCodeIntelligence()
profile_intelligence_engine = StudentProfileIntelligenceEngine()
skill_gap_engine = SkillGapEngine(llm_service=llm_service)
readiness_engine = PlacementReadinessEngine()
roadmap_engine = PersonalizedRoadmapEngine(llm_service=llm_service)
daily_task_engine = DailyTaskEngine(llm_service=llm_service)
adaptive_roadmap_engine = AdaptiveRoadmapEngine(llm_service=llm_service)
mentor_engine = PersonalMentorEngine(llm_service=llm_service)
pipeline_orchestrator = EndToEndPipelineOrchestrator(llm_service=llm_service)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "ai-placement-copilot"}


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------

@app.post("/api/ai/test", response_model=TestResponse)
async def test_ai_endpoint(request: TestRequest):
    """Test endpoint to verify AI connectivity and structured output."""
    try:
        return llm_service.generate_structured(
            prompt=request.message,
            response_model=TestResponse,
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ---------------------------------------------------------------------------
# Resume
# ---------------------------------------------------------------------------

@app.post("/api/ai/resume/analyze", response_model=ResumeAnalysis)
async def analyze_resume_pdf(file: UploadFile = File(...)):
    """Upload a PDF resume and receive a structured analysis."""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    try:
        contents = await file.read()
        return resume_analyzer.analyze_pdf(contents)
    except PDFExtractionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"AI extraction failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/ai/resume/analyze-text", response_model=ResumeAnalysis)
async def analyze_resume_text(request: TextRequest):
    """Development/testing endpoint — analyze already-extracted resume text."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    try:
        return resume_analyzer.analyze_text(request.text)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"AI extraction failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ---------------------------------------------------------------------------
# GitHub
# ---------------------------------------------------------------------------

@app.post("/api/ai/github/analyze", response_model=GitHubAnalysis)
async def analyze_github(request: GitHubRequest):
    """Analyze a public GitHub profile."""
    try:
        return github_intelligence.analyze(request.username)
    except GitHubUserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except GitHubRateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except GitHubAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"AI interpretation failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ---------------------------------------------------------------------------
# LeetCode
# ---------------------------------------------------------------------------

@app.post("/api/ai/leetcode/analyze", response_model=LeetCodeAnalysis)
async def analyze_leetcode(request: LeetCodeRequest):
    """
    Analyze a public LeetCode profile.

    Input:  { "username": "example" }
    Output: Validated LeetCodeAnalysis JSON.

    The response always includes `data_source_status` so the caller knows
    exactly which fields were available and which were not.
    """
    try:
        return leetcode_intelligence.analyze(request.username)
    except LeetCodeUserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except LeetCodeAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ---------------------------------------------------------------------------
# Student Profile Intelligence
# ---------------------------------------------------------------------------

@app.post("/api/ai/profile/build", response_model=StudentIntelligenceProfile)
async def build_student_profile(request: ProfileBuildRequest):
    """
    Build a unified, evidence-grounded StudentIntelligenceProfile across 14 categories.
    Combines ResumeAnalysis, GitHubAnalysis, LeetCodeAnalysis, and StudentProfile.
    """
    try:
        return profile_intelligence_engine.build_profile(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build intelligence profile: {str(e)}")


# ---------------------------------------------------------------------------
# Skill Gap Engine
# ---------------------------------------------------------------------------

@app.post("/api/ai/skills/analyze", response_model=SkillGapAnalysis)
async def analyze_skill_gaps(request: SkillGapRequest):
    """
    Determine what skills the student needs to improve for their target role.

    Input:
    {
      "target_role": "AI/ML Engineer",
      "profile": {}
    }
    """
    try:
        return skill_gap_engine.analyze_gaps(
            target_role=request.target_role,
            profile=request.profile,
            profile_request=request.profile_request,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skill gap analysis failed: {str(e)}")


# ---------------------------------------------------------------------------
# Placement Readiness Engine
# ---------------------------------------------------------------------------

@app.post("/api/ai/readiness/calculate", response_model=PlacementReadinessAnalysis)
async def calculate_placement_readiness(request: ReadinessCalculateRequest):
    """
    Generate an explainable placement readiness score from available student evidence.
    Evaluates 7 categories: Resume, DSA, GitHub, Projects, CS Fundamentals, Communication, Interview.
    """
    try:
        return readiness_engine.calculate_readiness(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Readiness calculation failed: {str(e)}")


# ---------------------------------------------------------------------------
# 90-Day Personalized Roadmap Generator
# ---------------------------------------------------------------------------

@app.post("/api/ai/roadmap/generate", response_model=PersonalizedRoadmap)
async def generate_personalized_roadmap(request: RoadmapGenerateRequest):
    """
    Generate a validated, phase-structured 90-day placement preparation roadmap.

    Input:
    {
      "profile": {},
      "skill_gaps": {},
      "readiness": {},
      "target_role": "AI/ML Engineer",
      "available_minutes_per_day": 120
    }
    """
    try:
        return roadmap_engine.generate_roadmap(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Roadmap generation failed: {str(e)}")


# ---------------------------------------------------------------------------
# Daily Task Engine
# ---------------------------------------------------------------------------

@app.post("/api/ai/tasks/today", response_model=TodayTasksResponse)
async def get_today_tasks(request: TodayTasksRequest):
    """
    Determine today's prioritized, evidence-backed tasks from roadmap and current progress.

    Input:
    {
      "roadmap": {},
      "current_day": 10,
      "completed_tasks": ["task_d1_1"],
      "missed_tasks": ["task_d5_1"],
      "available_time": 120,
      "target_role": "Backend Developer"
    }
    """
    try:
        return daily_task_engine.get_today_tasks(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Daily task calculation failed: {str(e)}")


# ---------------------------------------------------------------------------
# Adaptive Roadmap Engine
# ---------------------------------------------------------------------------

@app.post("/api/ai/roadmap/adapt", response_model=AdaptiveRoadmapResponse)
async def adapt_roadmap(request: AdaptiveRoadmapRequest):
    """
    Dynamically adapt a 90-day placement preparation roadmap according to student behavior.

    Input:
    {
      "roadmap": {},
      "progress": {
        "completed_tasks": ["task_d1_1"],
        "missed_tasks": ["task_d2_1"],
        "completion_rate": 65.0,
        "current_day": 10
      },
      "performance": {
        "available_time": 120,
        "dsa_performance": {"accuracy": 55.0, "weak_topics": ["Dynamic Programming"]}
      }
    }
    """
    try:
        return adaptive_roadmap_engine.adapt_roadmap(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Roadmap adaptation failed: {str(e)}")


# ---------------------------------------------------------------------------
# Personal AI Placement Mentor
# ---------------------------------------------------------------------------

@app.post("/api/ai/mentor/chat", response_model=MentorChatResponse)
async def mentor_chat(request: MentorChatRequest):
    """
    Chat with the Personal AI Placement Mentor.
    Uses a dynamic ContextBuilder to focus the LLM on relevant student profile metrics.

    Input:
    {
      "message": "What should I focus on today?",
      "student_context": { ... }
    }
    """
    try:
        return mentor_engine.chat(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mentor chat failed: {str(e)}")


# ---------------------------------------------------------------------------
# End-to-End AI Placement Copilot Pipeline
# ---------------------------------------------------------------------------

@app.post("/api/ai/pipeline/run", response_model=PipelineRunResponse)
async def run_end_to_end_pipeline(request: Optional[PipelineRunRequest] = None):
    """
    Executes the full 11-step AI placement copilot end-to-end integration flow:
    Resume -> GitHub -> LeetCode -> Profile -> Skill Gaps -> Readiness -> 90-Day Roadmap -> Today's Tasks -> Simulate Completed Tasks -> Adaptive Engine -> AI Mentor
    """
    try:
        return pipeline_orchestrator.run_pipeline(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"End-to-end pipeline execution failed: {str(e)}")


@app.get("/api/ai/pipeline/demo", response_model=PipelineRunResponse)
async def run_end_to_end_demo():
    """
    Triggers an end-to-end demo execution using a synthetic student profile (AI/ML Engineer, 120 min/day).
    """
    try:
        return pipeline_orchestrator.run_pipeline(PipelineRunRequest())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"End-to-end demo execution failed: {str(e)}")


