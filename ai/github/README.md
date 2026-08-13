# GitHub Analyzer (Phase 2 - AI Placement Copilot)

An intelligent, modular microservice that evaluates GitHub profiles, repositories, documentation, technology diversity, and commit activity for Indian computer science students.

---

## 📌 Project Overview
The **GitHub Analyzer** collects public data from GitHub via an abstraction layer over the official GitHub REST API. It performs transparent, rule-based component evaluations, scores candidate GitHub profiles out of **100**, identifies project and documentation weaknesses, and generates prioritized, actionable suggestions.

The output from this module will later be consumed by **Phase 3** (Skill Gap Engine + Company Readiness + Recommendation Engine).

---

## 🏗 Architecture & Folder Structure

```
ai/github/
├── api/
│   └── github.py            # FastAPI REST router (/api/v1/github/analyze)
├── services/
│   ├── github_client.py     # GitHub API HTTP client abstraction (httpx)
│   ├── profile_analyzer.py  # Profile completeness scoring (Max 10)
│   ├── repository_analyzer.py # Repo quality (Max 30) & Tech diversity (Max 15)
│   ├── readme_analyzer.py    # Documentation & README quality evaluation (Max 20)
│   ├── activity_analyzer.py  # Push recency & commit activity signals (Max 25)
│   ├── github_scorer.py     # Score aggregation & component breakdown
│   └── github_pipeline.py  # Full analysis pipeline & suggestion generation
├── models/
│   └── github.py            # Pydantic v2 data models & response schemas
├── utils/
│   ├── constants.py         # Scoring weights & detection keywords
│   ├── exceptions.py        # Domain-specific custom exceptions
│   └── logger.py           # Structured logging configuration
├── tests/
│   ├── test_github_client.py
│   ├── test_profile_analyzer.py
│   ├── test_repository_analyzer.py
│   ├── test_readme_analyzer.py
│   ├── test_activity_analyzer.py
│   ├── test_github_scorer.py
│   ├── test_github_suggestions.py
│   ├── test_github_pipeline.py
│   └── test_github_api.py
├── config.py                # Pydantic Settings
├── main.py                  # FastAPI app entry point
├── requirements.txt         # Project dependencies
├── README.md                # Documentation
└── .env.example             # Environment template
```

---

## 📊 Scoring Methodology

Total Score: **100 Points**

| Pillar | Max Score | Evaluation Criteria |
| :--- | :---: | :--- |
| **Repository Quality** | 30 | Original non-fork repositories, descriptions, licensing, topic tags, repository size. *(Stars are NOT treated as sole quality indicator)* |
| **Activity Signals** | 25 | Recent commit pushes (`pushed_at`), active repository update frequency, public activity events. |
| **Documentation** | 20 | README availability, project description, installation guide, usage instructions, features, stack details, screenshots, license. |
| **Technology Diversity** | 15 | Unique programming languages used, breadth of technical domains and topic tags. |
| **Profile Completeness** | 10 | Profile name, professional bio, avatar, contact links (blog/location/company), follower metrics. |

---

## ⚡ Installation & Setup

1. **Navigate to directory**:
   ```bash
   cd ai/github
   ```

2. **Create & activate virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   *Optionally configure `GITHUB_TOKEN` to increase GitHub API rate limits from 60 req/hr to 5,000 req/hr.*

---

## 🚀 Running the Service

Start the FastAPI application server:
```bash
python main.py
```
Or with Uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

Interactive Swagger API Documentation available at:
`http://localhost:8001/docs`

---

## 📡 API Endpoints

### 1. Health Check
`GET /health`

### 2. Analyze GitHub Profile
`POST /api/v1/github/analyze`

**Request Body**:
```json
{
  "username": "octocat"
}
```

**Response Example**:
```json
{
  "success": true,
  "username": "octocat",
  "profile": {
    "username": "octocat",
    "name": "The Octocat",
    "bio": "Building open-source developer tools.",
    "followers": 9800,
    "following": 9,
    "public_repos": 8,
    "avatar_url": "https://avatars.githubusercontent.com/u/583231?v=4"
  },
  "repositories": [
    {
      "name": "Hello-World",
      "full_name": "octocat/Hello-World",
      "description": "My first repository on GitHub!",
      "is_fork": false,
      "stargazers_count": 2200,
      "language": "C",
      "topics": ["octocat", "sample"],
      "has_readme": true
    }
  ],
  "languages": {
    "C": 1,
    "Ruby": 2
  },
  "statistics": {
    "total_repos": 8,
    "non_fork_repos": 6,
    "fork_repos": 2,
    "total_stars": 2350,
    "total_forks": 400,
    "unique_topics_count": 5,
    "top_languages": ["Ruby", "C"]
  },
  "score": {
    "total_score": 82.5,
    "repository_quality": 26.0,
    "activity": 22.5,
    "documentation": 16.0,
    "technology_diversity": 10.0,
    "profile_completeness": 8.0
  },
  "suggestions": [
    {
      "priority": "HIGH",
      "category": "DOCUMENTATION",
      "message": "Enhance project README files with Installation steps, Usage guide, Features list, and Screenshots.",
      "impact": "Rich documentation with visual previews increases recruiter engagement by up to 3x."
    }
  ]
}
```

---

## 🧪 Testing

All unit tests use `pytest` and mock GitHub API responses to ensure offline, independent testability.

Run tests:
```bash
pytest
```

---

## 🔗 External API Limitations & Resilience
- **Unauthenticated Rate Limits**: GitHub limits unauthenticated requests to 60 requests per hour per IP. Providing a `GITHUB_TOKEN` in `.env` increases rate limit to 5,000 requests per hour.
- **Graceful Error Handling**: 
  - User not found -> `404 Not Found` (`GitHubUserNotFoundError`)
  - Rate limit reached -> `429 Rate Limit Exceeded` (`GitHubRateLimitError`)
  - Network error -> `502 Bad Gateway` (`GitHubAPIError`)

---

## 🔮 Future Integration with Phase 3
The JSON output from `POST /api/v1/github/analyze` provides structured tech stack distribution, repo quality scores, and documentation readiness metrics. Phase 3 (Skill Gap Engine & Company Readiness) will ingest these data fields to evaluate candidate suitability for target companies (e.g. Tier-1 product companies vs. high-growth startups).
