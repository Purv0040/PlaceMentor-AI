# AI Placement Copilot - Backend API

Production-grade FastAPI Backend for **AI Placement Copilot**.

## 📌 Overview

The backend serves as the primary API, data management, and application layer for AI Placement Copilot. It handles:
- User Authentication & Account Management (Phase 2)
- Student Onboarding & Profile Persistence (Phase 3)
- MongoDB Atlas Database Integration (`placementor`)
  - Collections: `users`, `student_profiles`, `resumes`, `github_profiles`, `github_repositories`, `leetcode_profiles`, `projects`, `mentor_conversations`, `mentor_messages`, `achievement_definitions`, `user_achievements`, `notifications`, `notification_preferences`
- Redis Cache & Messaging Infrastructure (`redis://localhost:6379`)
- Resume Intelligence & Management (Phase 4)
- GitHub Intelligence (Phase 5)
- LeetCode Intelligence (Phase 6)
- Project Intelligence (Phase 7)
- Placement Readiness Engine (Phase 8)
- AI Skill Gap Analyzer (Phase 9)
- 90-Day Roadmap + Daily Tasks + Adaptive Planning (Phase 10)
- Mock Interview + Communication Coach (Phase 11)
- AI Placement Mentor (Phase 12)
- Achievements + Notifications (Phase 13)
- Clean integration boundary for external AI microservices (`ai/`)

---

## 🏗️ Architecture & Project Structure

```
Backend/
│
├── app/
│   ├── main.py                  # FastAPI Entrypoint & Lifespan Hooks
│   │
│   ├── core/                    # Core Infrastructure & Settings
│   │   ├── config.py            # Pydantic Settings (.env loader)
│   │   ├── database.py          # Motor AsyncIOMotorClient for MongoDB Atlas
│   │   ├── redis.py             # redis.asyncio Connection Manager
│   │   ├── security.py          # Password Hashing & JWT Token Handlers
│   │   ├── roles.py             # Centralized Target Roles List
│   │   ├── logging.py           # Structured Logger
│   │   └── exceptions.py        # Domain Exceptions
│   │
│   ├── api/                     # REST API Layer
│   │   ├── deps.py              # Dependencies (get_db, get_current_user)
│   │   └── routes/              # API Routers
│   │       ├── auth.py          # /register, /login, /refresh, /me
│   │       ├── onboarding.py    # Onboarding workflow endpoints
│   │       ├── users.py         # Student Profile (/me/profile)
│   │       ├── resume.py        # Resume Management & AI Analysis
│   │       ├── github.py        # GitHub Intelligence endpoints
│   │       ├── leetcode.py      # LeetCode Intelligence endpoints
│   │       ├── projects.py      # Project Intelligence CRUD & AI Analysis
│   │       ├── readiness.py     # Placement Readiness Engine endpoints
│   │       └── skill_gaps.py    # AI Skill Gap Analyzer endpoints
│   │
│   ├── models/                  # Domain Data Models (Pydantic / PyMongo)
│   │   ├── user.py              # User account document model
│   │   ├── profile.py           # StudentProfile document model
│   │   ├── resume.py            # Resume document model
│   │   ├── github.py            # GitHubProfile document model
│   │   ├── leetcode.py          # LeetCodeProfile document model
│   │   ├── project.py           # Project document model
│   │   ├── readiness.py         # ReadinessAnalysis document model
│   │   └── skill_gap.py         # SkillGapAnalysis document model
│   │
│   ├── schemas/                 # Request & Response API Validation Schemas
│   │   ├── auth.py, profile.py, onboarding.py, resume.py, github.py, leetcode.py, project.py, readiness.py, skill_gap.py
│   │
│   ├── repositories/            # Database Access Layer
│   │   ├── user_repository.py
│   │   ├── profile_repository.py
│   │   ├── resume_repository.py
│   │   ├── github_repository.py
│   │   ├── leetcode_repository.py
│   │   ├── project_repository.py
│   │   ├── readiness_repository.py
│   │   └── skill_gap_repository.py
│   │
│   ├── services/                # Business Logic Services
│   │   ├── auth_service.py
│   │   ├── onboarding_service.py
│   │   ├── profile_service.py
│   │   ├── resume_service.py
│   │   ├── github_service.py
│   │   ├── leetcode_service.py
│   │   ├── project_service.py
│   │   ├── readiness_service.py
│   │   └── skill_gap_service.py
│   │
│   ├── engines/                 # Pure Deterministic Scoring Engines
│   │   ├── readiness_engine.py  # 7-Category Weighted Deterministic Scoring Engine
│   │   └── skill_gap_engine.py  # Deterministic Skill Gap Evaluation & Evidence Engine
│   │
│   ├── integrations/            # External Clients (AI microservice, GitHub API, LeetCode GraphQL)
│   │   ├── ai_client.py
│   │   ├── github_client.py
│   │   └── leetcode_client.py
│   │
│   └── middleware/              # RequestID, Error Handler, Auth & Rate Limit
│
├── tests/                       # Pytest Suite (Isolated Test DB Fixture)
│   ├── api/
│   ├── services/
│   ├── repositories/
│   └── integrations/
│
├── .env                         # Local Environment Variables (Git-Ignored)
├── .env.example                 # Environment Template
├── requirements.txt             # Python Dependencies
├── Dockerfile                   # Docker Container Definition
└── README.md                    # Documentation
```

---

## ⚙️ Setup & Local Installation

### 1. Virtual Environment Setup

```bash
cd Backend
python -m venv .venv

# Activate Virtual Environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate Virtual Environment (Linux/macOS)
source .venv/bin/activate
```

### 2. Dependency Installation

```bash
pip install -r requirements.txt
```

---

## 🌐 Environment Variables Configuration

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Configured environment parameters:

```env
MONGODB_URL=mongodb+srv://<username>:<password>@<cluster>/<database>
MONGODB_DATABASE=placementor

REDIS_URL=redis://localhost:6379

AI_SERVICE_URL=http://localhost:8001
LEETCODE_API_URL=https://leetcode.com/graphql

APP_NAME=AI Placement Copilot
APP_ENV=development
DEBUG=true
API_V1_PREFIX=/api/v1

JWT_SECRET_KEY=<YOUR_SECURE_JWT_SECRET_KEY>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

CORS_ORIGINS=["http://localhost:5173"]
```

---

## 🚀 Running FastAPI Backend

```bash
uvicorn app.main:app --reload --port 8000
```

---

## 📖 Swagger Documentation

Interactive OpenAPI docs:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🔑 Phase 2, 3, 4, 5, 6, 7, 8 & 9 API Endpoints

### Authentication (`/api/v1/auth`)
| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Register student user & initialize profile shell | Public |
| `POST` | `/api/v1/auth/login` | Authenticate credentials & issue JWT tokens | Public |
| `POST` | `/api/v1/auth/refresh` | Refresh JWT access token | Public |
| `GET` | `/api/v1/auth/me` | Fetch authenticated user account details | JWT Bearer |

### Onboarding Workflow (`/api/v1/onboarding`)
| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/onboarding` | Fetch current onboarding state & step data | JWT Bearer |
| `POST` | `/api/v1/onboarding` | Initialize onboarding session | JWT Bearer |
| `PUT` | `/api/v1/onboarding` | Update complete onboarding state | JWT Bearer |
| `PATCH` | `/api/v1/onboarding/step` | Save individual step data (steps 1 to 7) | JWT Bearer |
| `POST` | `/api/v1/onboarding/complete` | Finalize onboarding state & set `is_onboarded=True` | JWT Bearer |

### Student Profile (`/api/v1/users/me/profile`)
| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/users/me/profile` | Retrieve student profile | JWT Bearer |
| `PUT` | `/api/v1/users/me/profile` | Replace/Update profile sections | JWT Bearer |
| `PATCH` | `/api/v1/users/me/profile` | Partially update profile sections | JWT Bearer |

### Resume Intelligence & Management (`/api/v1/resume`)
| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/resume/upload` | Upload PDF resume to GridFS and create resume document | JWT Bearer |
| `GET` | `/api/v1/resume` | List all resumes uploaded by authenticated student | JWT Bearer |
| `GET` | `/api/v1/resume/{resume_id}` | Fetch metadata & details for a specific resume | JWT Bearer |
| `GET` | `/api/v1/resume/{resume_id}/file` | Download/Stream stored PDF binary from GridFS | JWT Bearer |
| `POST` | `/api/v1/resume/{resume_id}/analyze` | Trigger AI Resume Analyzer microservice & store result | JWT Bearer |
| `GET` | `/api/v1/resume/{resume_id}/analysis` | Fetch stored AI analysis result for a resume | JWT Bearer |
| `PATCH` | `/api/v1/resume/{resume_id}/activate` | Set specified resume as active (deactivates others) | JWT Bearer |
| `DELETE` | `/api/v1/resume/{resume_id}` | Safely delete resume document and GridFS file binary | JWT Bearer |

### GitHub Intelligence (`/api/v1/github`)
| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/github/connect` | Connect/validate student's GitHub username | JWT Bearer |
| `GET` | `/api/v1/github` | Fetch connected GitHub profile & statistics | JWT Bearer |
| `POST` | `/api/v1/github/sync` | Synchronize profile & repositories from GitHub API | JWT Bearer |
| `GET` | `/api/v1/github/repositories` | Fetch paginated list of synchronized repositories | JWT Bearer |
| `POST` | `/api/v1/github/analyze` | Trigger AI GitHub Intelligence analyzer microservice | JWT Bearer |
| `GET` | `/api/v1/github/analysis` | Fetch stored AI analysis report for GitHub profile | JWT Bearer |
| `DELETE` | `/api/v1/github` | Disconnect GitHub account & remove GitHub profile/repo data | JWT Bearer |

### LeetCode Intelligence (`/api/v1/leetcode`)
| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/leetcode/connect` | Connect & validate student's LeetCode username | JWT Bearer |
| `GET` | `/api/v1/leetcode` | Fetch connected LeetCode profile & synchronized statistics | JWT Bearer |
| `POST` | `/api/v1/leetcode/sync` | Synchronize profile, solved problems, topics & contest rating | JWT Bearer |
| `GET` | `/api/v1/leetcode/statistics` | Fetch factual problem-solving statistics and contest ranking | JWT Bearer |
| `GET` | `/api/v1/leetcode/activity` | Fetch recent submission activity list | JWT Bearer |
| `POST` | `/api/v1/leetcode/analyze` | Trigger existing AI LeetCode Analyzer microservice | JWT Bearer |
| `GET` | `/api/v1/leetcode/analysis` | Fetch stored AI LeetCode Intelligence analysis | JWT Bearer |
| `DELETE` | `/api/v1/leetcode` | Disconnect LeetCode profile and remove saved statistics | JWT Bearer |

### Project Intelligence (`/api/v1/projects`)
| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/projects` | Create a new portfolio project | JWT Bearer |
| `GET` | `/api/v1/projects` | List all projects belonging to authenticated student | JWT Bearer |
| `GET` | `/api/v1/projects/{project_id}` | Fetch single project details by ID with ownership check | JWT Bearer |
| `PUT` | `/api/v1/projects/{project_id}` | Replace/Update complete project details | JWT Bearer |
| `PATCH` | `/api/v1/projects/{project_id}` | Partially update project fields | JWT Bearer |
| `DELETE` | `/api/v1/projects/{project_id}` | Soft delete (`status='archived'`) or remove project | JWT Bearer |
| `PATCH` | `/api/v1/projects/{project_id}/featured` | Toggle project `is_featured` state | JWT Bearer |
| `POST` | `/api/v1/projects/{project_id}/analyze` | Trigger AI Project Intelligence analysis & AST code audit | JWT Bearer |
| `GET` | `/api/v1/projects/{project_id}/analysis` | Fetch stored AI Project Intelligence report | JWT Bearer |

### Placement Readiness Engine (`/api/v1/readiness`)
| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/readiness/analyze` | Synthesize multi-module student telemetry & calculate readiness | JWT Bearer |
| `GET` | `/api/v1/readiness` | Retrieve latest computed readiness analysis snapshot | JWT Bearer |
| `GET` | `/api/v1/readiness/summary` | Retrieve lightweight readiness summary for dashboard | JWT Bearer |
| `GET` | `/api/v1/readiness/history` | Retrieve historical readiness calculation snapshots | JWT Bearer |
| `GET` | `/api/v1/readiness/{analysis_id}` | Retrieve specific historical readiness analysis snapshot by ID | JWT Bearer |

### AI Skill Gap Analyzer (`/api/v1/skill-gaps`)
| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/skill-gaps/analyze` | Synthesize telemetry & calculate role skill gaps with AI recommendations | JWT Bearer |
| `GET` | `/api/v1/skill-gaps` | Retrieve latest computed skill gap analysis snapshot | JWT Bearer |
| `GET` | `/api/v1/skill-gaps/summary` | Retrieve lightweight skill gap summary for dashboard | JWT Bearer |
| `GET` | `/api/v1/skill-gaps/history` | Retrieve historical skill gap calculation snapshots | JWT Bearer |
| `GET` | `/api/v1/skill-gaps/{analysis_id}` | Retrieve specific historical skill gap analysis snapshot by ID | JWT Bearer |

### Mock Interview (`/api/v1/interviews`)
| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/interviews` | Start a new role-grounded mock interview session | JWT Bearer |
| `GET` | `/api/v1/interviews/history` | Fetch student mock interview session history | JWT Bearer |
| `GET` | `/api/v1/interviews/{interview_id}` | Fetch single interview session details by ID | JWT Bearer |
| `GET` | `/api/v1/interviews/{interview_id}/current` | Fetch active question for ongoing interview | JWT Bearer |
| `GET` | `/api/v1/interviews/{interview_id}/questions` | Fetch all questions and submitted answers for session | JWT Bearer |
| `POST` | `/api/v1/interviews/{interview_id}/answer` | Submit candidate answer, evaluate response, and adaptively get next question | JWT Bearer |
| `POST` | `/api/v1/interviews/{interview_id}/complete` | Finalize interview session and compute final overall scores | JWT Bearer |

### Communication Coach (`/api/v1/communication`)
| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/communication/analyze` | Analyze answer for verbal clarity, structure, conciseness, and filler words | JWT Bearer |
| `GET` | `/api/v1/communication/summary` | Fetch aggregate communication practice summary & recurring feedback | JWT Bearer |
| `GET` | `/api/v1/communication/history` | Fetch practice history of communication analyses | JWT Bearer |
| `GET` | `/api/v1/communication/{analysis_id}` | Fetch specific communication analysis details by ID | JWT Bearer |

### AI Placement Mentor (`/api/v1/mentor`)
| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/mentor/conversations` | Create a new AI Mentor conversation session | JWT Bearer |
| `GET` | `/api/v1/mentor/conversations` | Fetch list of active/archived mentor conversations for authenticated student | JWT Bearer |
| `GET` | `/api/v1/mentor/conversations/{conversation_id}` | Fetch conversation session metadata and full message history | JWT Bearer |
| `POST` | `/api/v1/mentor/conversations/{conversation_id}/messages` | Send query to mentor, load context, execute AI/fallback, & save memory | JWT Bearer |
| `DELETE` | `/api/v1/mentor/conversations/{conversation_id}` | Archive a mentor conversation session | JWT Bearer |
| `POST` | `/api/v1/mentor/ask` | Quick single-query AI Mentor endpoint | JWT Bearer |

### Achievements System (`/api/v1/achievements`)
| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/achievements` | Return all achievement definitions with user progress & unlock state | JWT Bearer |
| `GET` | `/api/v1/achievements/unlocked` | Return unlocked achievements for authenticated user | JWT Bearer |
| `GET` | `/api/v1/achievements/progress` | Return achievement progress summary statistics (XP, level, completion %) | JWT Bearer |
| `POST` | `/api/v1/achievements/check` | Manually evaluate user achievements & return newly unlocked items | JWT Bearer |
| `GET` | `/api/v1/achievements/{achievement_id}` | Retrieve single achievement details by ID or code | JWT Bearer |

### Notification System (`/api/v1/notifications`)
| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/notifications` | Fetch notification history for authenticated student | JWT Bearer |
| `GET` | `/api/v1/notifications/unread` | Fetch unread notifications for student | JWT Bearer |
| `GET` | `/api/v1/notifications/count` | Fetch total unread notifications count `{ "unread_count": N }` | JWT Bearer |
| `PATCH` | `/api/v1/notifications/{notification_id}/read` | Mark single notification as read | JWT Bearer |
| `POST` | `/api/v1/notifications/read-all` | Mark all unread notifications as read | JWT Bearer |
| `DELETE` | `/api/v1/notifications/{notification_id}` | Delete a notification | JWT Bearer |
| `GET` | `/api/v1/notifications/preferences` | Retrieve user notification settings | JWT Bearer |
| `PUT` | `/api/v1/notifications/preferences` | Update user notification settings | JWT Bearer |

---

## 📊 Skill Gap Analysis Logic

The AI Skill Gap Analyzer evaluates current empirical student evidence against target role benchmarks:

1. **Skill Inventory Aggregation**: Aggregates skills and evidence from Student Profile, active Resume, GitHub repositories, LeetCode topic statistics, and audited Projects.
2. **Evidence Level Classification**:
   - `none`: No detected evidence.
   - `mentioned`: Stated in profile or resume keyword list.
   - `demonstrated`: Applied in a project codebase, repository, or problem solve.
   - `strong_evidence`: Verified across multiple independent modules (e.g. project + resume + GitHub code).
3. **Deterministic Gap Types**:
   - `ALIGNED`: Current competency satisfies or exceeds role level requirement.
   - `DEVELOPING`: Basic competency exists but requires 1 level advancement for Tier-1 parity.
   - `WEAK`: Competency is 2+ levels below target role requirement.
   - `MISSING`: No verified telemetry exists for a required core skill.
4. **2x2 Priority Matrix**:
   - `Quick Wins`: High Impact / Low Effort
   - `Major Projects`: High Impact / High Effort
   - `Fill-Ins`: Low Impact / Low Effort
   - `Long-Term`: Low Impact / High Effort

---

## 🧪 Running Tests

Run full test suite (uses in-memory mock DB fixture to protect production Atlas database):

```bash
pytest
```
