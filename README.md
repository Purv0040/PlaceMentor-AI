# AI Placement Copilot (PlaceMentor-AI)

An end-to-end AI-powered placement preparation platform designed to help students evaluate placement readiness, generate role-specific 90-day adaptive roadmaps, practice mock interviews, conduct communication analyses, track daily task progress, and unlock gamified achievements.

---

## 🏗 System Architecture

```
                                 ┌───────────────────────────┐
                                 │      React / Vite SPA     │
                                 │   (Frontend UI Gateway)   │
                                 └─────────────┬─────────────┘
                                               │ HTTP / REST
                                               ▼
                                 ┌───────────────────────────┐
                                 │      FastAPI Backend      │
                                 │   (Auth, DB, Logic, API)  │
                                 └──────┬──────┬──────┬──────┘
                                        │      │      │
                ┌───────────────────────┘      │      └───────────────────────┐
                ▼                              ▼                              ▼
    ┌───────────────────────┐      ┌───────────────────────┐      ┌───────────────────────┐
    │     MongoDB Atlas     │      │         Redis         │      │     AI Microservice   │
    │  (Persistent Database)│      │(Rate Limit & Dedupe)  │      │ (LLM & Intelligence) │
    └───────────────────────┘      └───────────────────────┘      └───────────────────────┘
```

---

## ✨ Features & Completed Modules

- **Phase 1**: Backend Foundation + MongoDB Atlas + Redis
- **Phase 2**: Authentication + JWT & Password Security + User Management
- **Phase 3**: Onboarding + Student Profile Setup
- **Phase 4**: Resume Upload, Parsing & Resume Intelligence
- **Phase 5**: GitHub Integration & Repository Intelligence
- **Phase 6**: LeetCode Profile Integration & Problem Solving Analytics
- **Phase 7**: Project Portfolio Analysis & Complexity Estimator
- **Phase 8**: Placement Readiness Engine (Weighted Readiness Score Calculation)
- **Phase 9**: Skill Gap Analyzer (Role-based benchmark comparison & skill recommendations)
- **Phase 10**: 90-Day Adaptive Roadmap, Daily Tasks & Streak Calculation
- **Phase 11**: AI Mock Interview Generator & Communication Coach
- **Phase 12**: AI Personal Placement Mentor (Conversational Placement Advisor)
- **Phase 13**: Achievement Engine (Gamified Badges) & Notification System
- **Phase 14**: Production Hardening, Rate Limiting, Security Audit, Health Checks, Docker & CI/CD

---

## 📁 Repository Structure

```
PlaceMentor-AI/
├── Backend/                    # FastAPI Backend Application
│   ├── app/
│   │   ├── api/                # REST API Routers & Dependencies
│   │   ├── core/               # Configuration, Security, DB, Redis & Middleware
│   │   ├── engines/            # Readiness, Skill Gap, Roadmap & Achievement Engines
│   │   ├── models/             # PyMongo MongoDB Data Models
│   │   ├── repositories/       # Database Data Access Repositories
│   │   ├── schemas/            # Pydantic Request & Response Validation Schemas
│   │   └── services/           # Business Logic & Service Controllers
│   ├── tests/                  # Pytest Unit & Integration Test Suite
│   ├── Dockerfile
│   └── requirements.txt
├── ai/                         # Python AI Microservice Engine
│   ├── app/                    # LLM Prompt Templates, Analyzers & Role Registries
│   ├── tests/                  # Pytest Suite for AI Intelligence
│   ├── Dockerfile
│   └── requirements.txt
├── Frontend/                   # React + Vite + Tailwind CSS Web Application
│   ├── src/
│   │   ├── components/         # Reusable UI Components
│   │   ├── pages/              # Application View Pages
│   │   └── services/           # Centralized API Integration Clients
│   ├── Dockerfile
│   └── package.json
├── .github/workflows/ci.yml    # GitHub Actions Continuous Integration Workflow
├── docker-compose.yml          # Multi-Container Deployment Orchestration
└── README.md
```

---

## ⚙️ Environment Configuration

Copy `.env.example` templates to `.env` in `Backend/`, `ai/`, and `Frontend/` before starting the services:

### 1. Backend (`Backend/.env`)
```env
MONGODB_URL=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/
MONGODB_DATABASE=placementor
REDIS_URL=redis://localhost:6379
APP_NAME=AI Placement Copilot
APP_ENV=development
DEBUG=true
JWT_SECRET_KEY=your_secure_random_secret_key
CORS_ORIGINS=["http://localhost:5173"]
AI_SERVICE_URL=http://localhost:8001
MAX_RESUME_SIZE_MB=5
```

### 2. AI Service (`ai/.env`)
```env
LLM_PROVIDER=openai
LLM_API_KEY=your_llm_api_key
PORT=8001
ENVIRONMENT=development
```

### 3. Frontend (`Frontend/.env`)
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## 🚀 Running Locally

### Option 1: Docker Compose (Recommended)

Start the complete stack with a single command:
```bash
docker-compose up --build
```
- **Frontend**: `http://localhost`
- **Backend API**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`
- **AI Microservice**: `http://localhost:8001`

### Option 2: Manual Development Setup

1. **Start Redis**:
   ```bash
   redis-server
   ```
2. **Start AI Microservice**:
   ```bash
   cd ai
   pip install -r requirements.txt
   uvicorn app.main:app --port 8001 --reload
   ```
3. **Start Backend Service**:
   ```bash
   cd Backend
   pip install -r requirements.txt
   uvicorn app.main:app --port 8000 --reload
   ```
4. **Start Frontend Application**:
   ```bash
   cd Frontend
   npm install
   npm run dev
   ```

---

## 🧪 Testing & Verification

### Backend Tests
```bash
cd Backend
pytest tests/ -v
```

### AI Service Tests
```bash
cd ai
pytest tests/ -v
```

### Frontend Production Build
```bash
cd Frontend
npm run build
```

---

## 🔒 Security & Hardening Features

- **Strict Access Control**: Server-side user ownership verification on all endpoints.
- **Fail-safe Rate Limiting**: Redis-backed sliding window rate limiter on sensitive authentication & AI routes with graceful fallback on Redis disconnect.
- **Payload Validation**: Strict Pydantic schemas validating all inputs and ObjectIds.
- **No Hardcoded Credentials**: Config files use environment variable overrides with generic fallback values.
- **Structured Logging & Health Checks**: Request correlation IDs (`X-Request-ID`) and status probes (`/health`, `/api/v1/health`).

---

## 📄 License
MIT License
