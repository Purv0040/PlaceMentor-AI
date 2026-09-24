# PlaceMentor AI — System Architecture & Integration Guide

This document outlines the final frontend architecture, routing hierarchy, context state management layer, centralized services, mock AI pipeline, and future backend integration boundaries for PlaceMentor AI.

---

## 1. System Overview

PlaceMentor AI is built as a single-page React application powered by Vite, TailwindCSS, and Lucide/Material Symbols icons. It follows an executive SaaS obsidian dark-mode design system.

```
+-----------------------------------------------------------------------+
|                              App Shell                                |
| (AppLayout: Sidebar, Sticky Header, UserMenuDropdown, MobileNav)      |
+-----------------------------------------------------------------------+
|                                                                       |
|  [AuthContext]   [UserContext]   [OnboardingContext]  [PlanningContext] |
|                                                                       |
|  +-----------------------------------------------------------------+  |
|  |                         Application Pages                       |  |
|  |  Dashboard | Resume | GitHub | LeetCode | Projects             |  |
|  |  Readiness | Skill Gaps | Roadmap | Tasks | Progress            |  |
|  |  Mock Interview | Communication | AI Mentor                    |  |
|  |  Achievements | Profile | Settings                              |  |
|  +-----------------------------------------------------------------+  |
|                                                                       |
|  +-----------------------------------------------------------------+  |
|  |                         Services Layer                          |  |
|  |  authService | aiService | readinessService | planningService   |  |
|  |  mentorService | profileService | achievementService           |  |
|  |  githubService | leetcodeService | settingsService              |  |
|  +-----------------------------------------------------------------+  |
+-----------------------------------------------------------------------+
```

---

## 2. Route Hierarchy

### **Public Routes** (`PublicLayout`)
- `/` — Landing Page (Hero, Telemetry Engine, Complete Platform Suite)
- `/login` — Candidate Sign In
- `/signup` — Account Registration
- `/forgot-password` — Password Reset Request

### **Onboarding Stepper Routes** (`OnboardingLayout`)
- `/onboarding` — Step 0: Welcome Overview
- `/onboarding/profile` — Step 1: Academic Identity
- `/onboarding/career` — Step 2: Target Role & Company Tier
- `/onboarding/skills` — Step 3: Domain Confidence Matrix
- `/onboarding/integrations` — Step 4: GitHub, LeetCode & Resume Upload
- `/onboarding/preferences` — Step 5: Daily Sprint Commitment & Mentor Persona
- `/onboarding/goals` — Step 6: Drive Season & Target CTC Bracket
- `/onboarding/analysis` — Step 7: AI Telemetry Synthesis → Baseline Score 78/100

### **Protected Application Shell** (`ProtectedRoute` → `AppLayout`)
- `/dashboard` — Candidate Executive SaaS Dashboard
- `/resume` — Resume Intelligence (ATS score, STAR bullet audit, PDF dropzone modal)
- `/github` — GitHub Intelligence (Commit velocity, AST quality grid)
- `/leetcode` — LeetCode Intelligence (Difficulty distribution, Knight rating)
- `/projects` — Project Intelligence (Architectural complexity audit, full project CRUD)
- `/placement-readiness` — Placement Readiness Audit (7-vector Recharts RadarChart, Tier-1 matrix)
- `/skill-gaps` — AI Skill Gap Analyzer (Benchmark coverage, 2x2 Impact vs Effort matrix)
- `/roadmap` — 90-Day Adaptive Placement Roadmap (Multi-phase timeline)
- `/tasks` — Today's Action Plan Tasks (Daily matrix, completion checkboxes)
- `/progress` — Progress Telemetry (5-week Recharts curve)
- `/mock-interview` — AI Mock Interview Studio (Technical/System Design/STAR drills)
- `/communication` — Communication Readiness Lab (WPM pace, verbal clarity, pitch diagnostic)
- `/ai-mentor` — AI Placement Mentor & Copilot (Socratic probing, code snippets, visual graph diagrams)
- `/achievements` — Achievements & Milestones (Level 8 XP progression, daily claim trigger)
- `/profile` — Candidate Profile (Identity banner, edit mode, UserContext sync)
- `/settings` — System & AI Settings (8-tab configuration suite, local persistence, logout)

---

## 3. Centralized State & Persistence Map

| Context / State | Primary Purpose | Storage Key |
|---|---|---|
| `AuthContext` | Token management, candidate session, login/signup/logout triggers | `placementCopilotToken`, `placementCopilotUser` |
| `UserContext` | Candidate identity, target role, academic credentials | `placementCopilotUser` |
| `OnboardingContext` | Stepper wizard state across all 7 steps | `placementCopilotOnboarding`, `placementCopilotOnboardingComplete` |
| `PlanningContext` | Single source of truth for 90-day roadmap, today's tasks, completion status | `placementor_planning_state` |
| `projectData` | Portfolio projects array with CRUD persistence | `placementor_stored_projects` |
| `interviewData` | Mock interview session history and results | `placementor_interview_history` |
| `communicationData` | Communication lab recordings and speech telemetry | `placementor_communication_history` |
| `mentorService` | AI Mentor conversation history | `placementCopilotMentorChat` |
| `profileService` | Candidate credentials & profile completion state | `placementCopilotProfile` |
| `settingsService` | Application preferences, AI reasoning density, notifications | `placementCopilotSettings` |

---

## 4. Future Backend & LLM Integration Boundaries

The application is architected with clean abstraction layers to allow swapping mock services for a real backend (e.g. FastAPI / Node.js) and real LLM providers (e.g. Gemini / OpenAI) without modifying React components:

1. **`authService`** → Connect to `/api/v1/auth/login` and `/api/v1/auth/signup`.
2. **`aiService.generateMentorResponse`** → Connect to `/api/v1/ai/mentor/chat`.
3. **`aiService.evaluateInterviewAnswer`** → Connect to `/api/v1/ai/interview/evaluate`.
4. **`aiService.evaluateCommunicationResponse`** → Connect to `/api/v1/ai/communication/evaluate`.
5. **`planningService.adaptRoadmap`** → Connect to `/api/v1/planning/adapt`.
