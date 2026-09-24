# AI Placement Copilot - AI Service Layer

Standalone AI microservice for the AI Placement Copilot application. Built with **FastAPI**, **Pydantic v2**, and a hybrid **Deterministic + LLM Architecture** to deliver evidence-grounded, explainable, and adaptive career placement guidance for college students.

---

## 1. Architecture

The AI layer follows a clean, decoupled microservices pattern:

```
                  +-------------------------------+
                  |       FastAPI Application     |
                  |          (app/main.py)        |
                  +---------------+---------------+
                                  |
            +---------------------+---------------------+
            |                                           |
+-----------v-----------+                   +-----------v-----------+
|  Deterministic Engines |                   |   LLM / AI Services   |
| (Scoring, Rules, Math)|                   |  (LLMService / OpenAI)|
+-----------+-----------+                   +-----------+-----------+
            |                                           |
            +---------------------+---------------------+
                                  |
                     +------------v------------+
                     | End-to-End Pipeline     |
                     |  Orchestration Service  |
                     +-------------------------+
```

### Key Architectural Principles
- **Decoupled Data Sources**: GitHub and LeetCode API interactions are isolated behind abstract service clients (`GitHubService`, `LeetCodeProvider`), protecting business logic from provider breaking changes.
- **Evidence-Grounded Intelligence**: No fabricated student stats. All metrics are computed from observable evidence or explicitly marked as `insufficient_data` / `Untested`.
- **Hybrid Scoring**: Mathematical, explainable formulas drive ATS scoring, readiness calculations, gap prioritization, and day budgeting; LLMs are reserved for natural language parsing, narrative interpretation, and context-aware mentoring.

---

## 2. AI Pipeline

The end-to-end AI placement copilot pipeline connects 11 specialized modules sequentially:

```
Resume Analyzer
       ↓
GitHub Analyzer
       ↓
LeetCode Analyzer
       ↓
Student Profile Engine
       ↓
Skill Gap Engine
       ↓
Readiness Engine
       ↓
Roadmap Generator
       ↓
Daily Task Engine
       ↓
Progress Simulation
       ↓
Adaptive Engine
       ↓
AI Mentor
```

1. **Resume Analyzer**: Parses PDF / text resumes into structured Pydantic schemas, calculating ATS formatting, impact, and project scores.
2. **GitHub Analyzer**: Ingests public repositories, computing tech stack distributions, project complexity, and code quality.
3. **LeetCode Analyzer**: Analyzes problem counts across 13 canonical DSA topics and difficulty levels.
4. **Student Profile Engine**: Merges multi-source evidence into a single normalized `StudentIntelligenceProfile` across 14 categories.
5. **Skill Gap Engine**: Compares student capabilities against canonical target role benchmarks (AI/ML Engineer, Backend Developer, etc.).
6. **Placement Readiness Engine**: Computes explainable placement readiness scores (0-100) across 7 weighted categories.
7. **Roadmap Generator**: Constructs a 90-day, 3-phase preparation plan strictly bounded by daily study time constraints.
8. **Daily Task Engine**: Dynamically prioritizes today's action items based on overdue tasks, prerequisites, and target role gaps.
9. **Progress Simulation**: Tracks task completion status and performance metrics.
10. **Adaptive Engine**: Detects student behavior state (`ON_TRACK`, `BEHIND`, `AHEAD`, `STRUGGLING`, `IMPROVING`) and adjusts the roadmap while preserving completed tasks.
11. **AI Mentor**: Interrogates the LLM using topic-routed student context to answer queries like *"What should I focus on today?"*.

---

## 3. Folder Structure

```
ai/
├── README.md                           # Documentation
├── requirements.txt                    # Project dependencies
├── .env.example                        # Environment variables template
├── app/                                # Application package
│   ├── main.py                         # FastAPI routes and server initialization
│   ├── analyzers/                      # Feature analyzers
│   │   ├── resume_analyzer.py          # Resume parsing orchestrator
│   │   ├── github_analyzer.py          # GitHub repository & complexity analyzer
│   │   └── leetcode_analyzer.py        # LeetCode topic & difficulty analyzer
│   ├── engines/                        # Deterministic & AI engines
│   │   ├── profile_engine.py           # Unified 14-category Student Profile Engine
│   │   ├── skill_gap_engine.py         # Role benchmark & gap calculator
│   │   ├── readiness_engine.py         # 7-category deterministic readiness engine
│   │   ├── roadmap_engine.py           # 90-day time-bounded roadmap generator
│   │   ├── task_engine.py              # Daily task prioritizer engine
│   │   ├── adaptive_engine.py          # Behavior state & roadmap adaptation engine
│   │   ├── mentor_engine.py            # AI mentor context builder & chat engine
│   │   ├── github_engine.py            # GitHub intelligence orchestrator
│   │   └── leetcode_engine.py          # LeetCode intelligence orchestrator
│   ├── role_requirements/              # Target role benchmark definitions
│   │   ├── roles.py                    # Role loader & taxonomy rules
│   │   └── definitions/                # Canonical requirements per target role
│   ├── schemas/                        # Pydantic v2 data models
│   │   ├── common.py                   # Common API requests & responses
│   │   ├── student.py                  # Self-reported student profile schema
│   │   ├── resume.py                   # Resume analysis schema
│   │   ├── github.py                   # GitHub analysis schema
│   │   ├── leetcode.py                 # LeetCode analysis schema
│   │   ├── skills.py                   # Unified profile & normalized skill schema
│   │   ├── skill_gap.py                # Skill gap analysis schema
│   │   ├── readiness.py                # Placement readiness analysis schema
│   │   ├── roadmap.py                  # 90-day roadmap schema
│   │   ├── daily_task.py               # Today's tasks response schema
│   │   ├── adaptive.py                 # Adaptive roadmap response schema
│   │   ├── mentor.py                   # AI mentor chat schema
│   │   └── pipeline.py                 # End-to-end pipeline schema
│   ├── services/                       # Third-party & provider integration clients
│   │   ├── llm_service.py              # Abstract LLM client (OpenAI / Gemini / Mock)
│   │   ├── github_service.py           # GitHub REST API v3 client
│   │   ├── leetcode_service.py         # LeetCode GraphQL provider client
│   │   ├── parser_service.py           # PDF text extraction service
│   │   └── pipeline_service.py         # End-to-end pipeline orchestrator service
│   └── utils/                          # Taxonomy and utility functions
│       └── tech_taxonomy.py            # Tech skill normalization taxonomy
└── tests/                              # Comprehensive test suite
    ├── test_api.py                     # Health & basic API tests
    ├── test_resume_analyzer.py         # Resume parsing tests
    ├── test_github_intelligence.py     # GitHub intelligence tests
    ├── test_leetcode_intelligence.py   # LeetCode intelligence tests
    ├── test_profile_intelligence.py    # Student profile engine tests
    ├── test_skill_gap_engine.py        # Skill gap engine tests
    ├── test_readiness_engine.py        # Placement readiness engine tests
    ├── test_roadmap_engine.py          # 90-day roadmap engine tests
    ├── test_daily_task_engine.py       # Daily task engine tests
    ├── test_adaptive_engine.py         # Adaptive engine tests
    ├── test_mentor_engine.py           # AI mentor tests
    └── test_end_to_end_integration.py  # Complete 11-step pipeline integration test
```

---

## 4. Environment Variables

Copy `.env.example` to `.env` and adjust the variables as required:

```env
# LLM Provider Configuration ('mock', 'openai', or 'gemini')
LLM_PROVIDER=mock
LLM_API_KEY=your_llm_api_key_here

# Third-Party Service Credentials (Optional)
GITHUB_TOKEN=your_github_personal_access_token_here
```

---

## 5. API Endpoints

### Pipeline & Orchestration
- `GET /health` — Health check endpoint.
- `POST /api/ai/pipeline/run` — Run the full 11-step end-to-end AI placement copilot pipeline.
- `GET /api/ai/pipeline/demo` — Run the end-to-end pipeline with a synthetic AI/ML Engineer profile (120 min/day).

### Module Endpoints
- `POST /api/ai/resume/analyze` — Upload PDF resume for structured analysis.
- `POST /api/ai/resume/analyze-text` — Analyze extracted raw text resume.
- `POST /api/ai/github/analyze` — Analyze public GitHub profile.
- `POST /api/ai/leetcode/analyze` — Analyze public LeetCode profile.
- `POST /api/ai/profile/build` — Build unified 14-category `StudentIntelligenceProfile`.
- `POST /api/ai/skills/analyze` — Calculate skill gaps against target role benchmarks.
- `POST /api/ai/readiness/calculate` — Compute deterministic placement readiness scores across 7 categories.
- `POST /api/ai/roadmap/generate` — Generate 90-day, 3-phase time-constrained preparation roadmap.
- `POST /api/ai/tasks/today` — Calculate today's prioritized action items.
- `POST /api/ai/roadmap/adapt` — Run adaptive roadmap engine based on student progress.
- `POST /api/ai/mentor/chat` — Chat with Personal AI Placement Mentor using dynamic context routing.

---

## 6. How Each AI Module Works

1. **Resume Analyzer**: Uses PyMuPDF to extract text, followed by structured LLM parsing to identify skills, experience, projects, and weak bullet points. Computes deterministic ATS metrics for impact, skills, and formatting.
2. **GitHub Intelligence**: Fetches public repositories, languages, and commit history via GitHub API. Runs deterministic keyword & framework taxonomy rules to analyze project complexity and technology stack distributions.
3. **LeetCode Intelligence**: Queries public LeetCode GraphQL endpoints for problem counts across 13 topics. Classifies topics into `strong`, `moderate`, `beginner`, or `untested` based on strict percentage thresholds.
4. **Student Profile Engine**: Merges evidence across all inputs into 14 normalized profile categories. Detects conflicts between self-reported skills and code/repo evidence with transparent resolution rules.
5. **Skill Gap Engine**: Matches student capabilities against role requirements (e.g. AI/ML Engineer). Determines gap levels (`None`, `Low`, `Medium`, `High`, `Critical`) and calculates priority ratings.
6. **Placement Readiness Engine**: Evaluates 7 core dimensions (Resume, DSA, GitHub, Projects, CS Fundamentals, Communication, Interview). Uses weighted averages with confidence penalties for missing evidence.
7. **Roadmap Generator**: Creates a 3-phase 90-day study plan. Bounds daily workload strictly within `available_minutes_per_day` (e.g., 120 min/day).
8. **Daily Task Engine**: Filters out completed tasks and selects today's highest-priority items according to gap severity and prerequisite order.
9. **Adaptive Engine**: Analyzes task completion rates (e.g. >=80% = `ON_TRACK`, <50% = `STRUGGLING`). Reschedules lower-priority tasks while preserving completed tasks.
10. **AI Mentor Engine**: Filters `StudentContext` using keyword-based intent classification (`ContextBuilder`) to select relevant context, generating evidence-backed advice without token bloat.

---

## 7. How Deterministic Logic Differs from LLM Logic

| Aspect | Deterministic Logic | LLM / Generative Logic |
| :--- | :--- | :--- |
| **Used For** | ATS scoring, readiness math, gap priority ratings, daily time budgeting, behavior state detection. | Resume PDF extraction, repository complexity narrative, task explanation, mentor conversation. |
| **Predictability** | 100% deterministic (same input produces identical mathematical output every time). | Generative output guided by Pydantic schema validation and JSON repair loops. |
| **Hallucination Risk** | Zero (governed strictly by code algorithms and transparent formulas). | Eliminated via strict schema enforcement (`LLMService.generate_structured`) and evidence grounding. |
| **Explainability** | Fully transparent breakdown with explicit step-by-step scoring formulas. | Evidence-backed recommendations referencing actual profile evidence strings. |

---

## 8. How to Run Tests

Ensure your virtual environment is active, then execute:

```bash
pytest
```

Running `pytest` executes all **112 test cases**, including unit tests for every module and the full 11-step integration test (`tests/test_end_to_end_integration.py`).

---

## 9. Example API Requests/Responses

### Run End-to-End Demo (`GET /api/ai/pipeline/demo`)

#### Response (`200 OK`)
```json
{
  "target_role": "AI/ML Engineer",
  "available_time": 120,
  "step_1_resume_analysis": {
    "overall_score": 82,
    "suggestions": ["Add missing sections if applicable."]
  },
  "step_4_unified_profile": {
    "overall_readiness_level": "Developing",
    "executive_summary": "Student shows strong foundational Python and PyTorch skills..."
  },
  "step_6_readiness": {
    "target_role": "AI/ML Engineer",
    "overall_score": 74,
    "readiness_label": "Developing"
  },
  "step_7_roadmap": {
    "total_days": 90,
    "total_tasks": 45
  },
  "step_11_mentor_response": {
    "answer": "Based on your 90-day roadmap and current profile as an AI/ML Engineer, today you should focus on practicing Dynamic Programming on LeetCode...",
    "evidence": ["LeetCode weak topic: Dynamic Programming"],
    "confidence": 0.92
  }
}
```

### Ask AI Mentor (`POST /api/ai/mentor/chat`)

#### Request Payload
```json
{
  "message": "What should I focus on today?",
  "student_context": {
    "target_role": "AI/ML Engineer",
    "skill_gaps": { "gaps": [] },
    "today_tasks": { "tasks": [] }
  }
}
```

#### Response (`200 OK`)
```json
{
  "answer": "Today, focus on completing your PyTorch Model Optimization task and solving 2 Medium Array problems on LeetCode.",
  "evidence": ["Target Role: AI/ML Engineer", "Available Time: 120 min"],
  "recommended_actions": ["Complete PyTorch task", "Solve LeetCode problems"],
  "related_skills": ["PyTorch", "DSA"],
  "confidence": 0.90
}
```

---

## 10. Known Limitations

1. **Unofficial LeetCode API**: LeetCode lacks an official public API; data is retrieved via public GraphQL endpoints. If LeetCode modifies its GraphQL schema, missing fields are safely reported as `DataSourceStatus.notes`.
2. **GitHub API Rate Limits**: Unauthenticated GitHub REST requests are capped at 60 requests/hour by GitHub. Set `GITHUB_TOKEN` in `.env` for higher rate limits (5,000 req/hour).
3. **Standalone Microservice Scope**: The AI service is currently focused on core intelligence, algorithms, and microservice APIs. Persistent storage (MongoDB) and user interface (Frontend) integration are managed outside this standalone service layer.
