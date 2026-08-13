# LeetCode Analyzer (Phase 2 - AI Placement Copilot)

An intelligent, modular microservice that evaluates Data Structures & Algorithms (DSA) profile metrics, difficulty distribution, 13 core topic proficiencies, practice consistency, and contest rankings for Indian computer science students.

---

## 📌 Project Overview
The **LeetCode Analyzer** collects public user metrics from LeetCode via a GraphQL API client abstraction. It evaluates problem-solving depth, checks topic coverage across 13 foundational DSA domains, evaluates practice consistency, cleanly handles missing contest data without hallucination, and generates prioritized improvement recommendations.

The output from this module will later be consumed by **Phase 3** (Skill Gap Engine + Company Readiness + Recommendation Engine).

---

## 🏗 Architecture & Folder Structure

```
ai/leetcode/
├── api/
│   └── leetcode.py            # FastAPI REST router (/api/v1/leetcode/analyze)
├── services/
│   ├── leetcode_client.py     # LeetCode GraphQL API client abstraction
│   ├── problem_analyzer.py    # Total solved & difficulty distribution (Max 25 & 20)
│   ├── topic_analyzer.py      # 13 core DSA topic coverage & weak topic detector (Max 30)
│   ├── consistency_analyzer.py# Activity calendar & weekly/monthly consistency (Max 15)
│   ├── contest_analyzer.py    # Contest rating & ranking evaluation (Max 10)
│   ├── dsa_scorer.py          # Score aggregation & component breakdown
│   └── leetcode_pipeline.py   # Full analysis pipeline & suggestion generation
├── models/
│   └── leetcode.py            # Pydantic v2 data models & response schemas
├── utils/
│   ├── constants.py           # Scoring weights & 13 core DSA topics taxonomy
│   ├── exceptions.py          # Custom domain exception definitions
│   └── logger.py              # Structured logging configuration
├── tests/
│   ├── test_leetcode_client.py
│   ├── test_problem_analyzer.py
│   ├── test_topic_analyzer.py
│   ├── test_consistency_analyzer.py
│   ├── test_contest_analyzer.py
│   ├── test_dsa_scorer.py
│   ├── test_leetcode_suggestions.py
│   ├── test_leetcode_pipeline.py
│   └── test_leetcode_api.py
├── config.py                  # Pydantic Settings
├── main.py                    # FastAPI application entry point
├── requirements.txt           # Project dependencies
├── README.md                  # Documentation
└── .env.example               # Environment configuration template
```

---

## 📊 Scoring Methodology

Total Score: **100 Points**

| Pillar | Max Score | Evaluation Criteria |
| :--- | :---: | :--- |
| **Topic Coverage** | 30 | Solved depth across 13 core DSA topics: Arrays, Strings, Hash Table, Linked List, Stack, Queue, Binary Search, Trees, Graphs, Heap, Greedy, Backtracking, Dynamic Programming. |
| **Problems Solved** | 25 | Total solved volume benchmarked against Indian tech placement standards (100+, 250+, 500+). |
| **Difficulty Distribution** | 20 | Percentage ratio of Easy, Medium, and Hard problems (Medium ratio target ~50-60%, Hard target 15-20%). |
| **Practice Consistency** | 15 | Submission calendar activity across active days, weekly volume, and monthly frequency. |
| **Contest Performance** | 10 | Contest rating, percentile rank, and attended contest count. *(Clearly marked unavailable if candidate has not participated)* |

---

## ⚡ Installation & Setup

1. **Navigate to directory**:
   ```bash
   cd ai/leetcode
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

---

## 🚀 Running the Service

Start the FastAPI application server:
```bash
python main.py
```
Or with Uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

Interactive Swagger API Documentation available at:
`http://localhost:8002/docs`

---

## 📡 API Endpoints

### 1. Health Check
`GET /health`

### 2. Analyze LeetCode Profile
`POST /api/v1/leetcode/analyze`

**Request Body**:
```json
{
  "username": "tourist"
}
```

**Response Example**:
```json
{
  "success": true,
  "username": "tourist",
  "problem_statistics": {
    "total_solved": 420,
    "easy_solved": 120,
    "medium_solved": 230,
    "hard_solved": 70,
    "easy_percentage": 28.57,
    "medium_percentage": 54.76,
    "hard_percentage": 16.67
  },
  "topic_statistics": {
    "Arrays": 85,
    "Dynamic Programming": 45,
    "Graphs": 32,
    "Trees": 40,
    "Binary Search": 25,
    "Backtracking": 8,
    "Heap": 12
  },
  "weak_topics": [
    {
      "topic": "Backtracking",
      "score": 8.0,
      "priority": "LOW"
    }
  ],
  "consistency": {
    "active_days": 180,
    "weekly_activity": 5,
    "monthly_activity": 22,
    "recent_activity_score": 8.0,
    "consistency_score": 14.5,
    "is_available": true
  },
  "contest_data": {
    "rating": 1850.5,
    "global_ranking": 4200,
    "total_participants": 120000,
    "top_percentage": 3.5,
    "attended_contests": 18,
    "is_available": true
  },
  "dsa_score": {
    "total_score": 88.5,
    "problems_solved_score": 22.3,
    "difficulty_distribution_score": 20.0,
    "topic_coverage_score": 24.5,
    "consistency_score": 14.5,
    "contest_performance_score": 7.2,
    "contest_available": true
  },
  "suggestions": [
    {
      "priority": "MEDIUM",
      "category": "TOPIC",
      "message": "Practice at least 15-20 Hard difficulty problems in Dynamic Programming and Graphs.",
      "impact": "Hard problems differentiate candidates for top-tier SDE roles."
    }
  ]
}
```

---

## 🧪 Testing

All unit tests use `pytest` with mocked LeetCode GraphQL responses to ensure offline, deterministic execution.

Run tests:
```bash
pytest
```

---

## 🔗 External API Limitations & Resilience
- **GraphQL Data Availability**: LeetCode's public GraphQL endpoint provides problem counts, tag breakdowns, and contest rankings.
- **Graceful Fallbacks**:
  - User not found -> `404 Not Found` (`LeetCodeUserNotFoundError`)
  - Network timeout / unreachable API -> `503 Service Unavailable` (`LeetCodeDataUnavailableError`)
  - Missing contest data -> contest metrics return `is_available: false` with zero contest weight score without crashing or inventing scores.

---

## 🔮 Future Integration with Phase 3
The output from `POST /api/v1/leetcode/analyze` provides detailed topic strengths, weak topics list, and total DSA score. Phase 3 (Skill Gap Engine & Company Readiness) will cross-reference these weak topics against specific company hiring criteria (e.g. Amazon DP/Graph requirement vs. Microsoft Tree/LinkedList requirement) to build personalized 90-day learning roadmaps.
