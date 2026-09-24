# PlaceMentor AI — Migration Map (Stitch HTML → React)

This document provides the complete, authoritative mapping between the original Google Stitch HTML prototypes located in `Frontend/stich/` and their target React modular components and routes.

---

## 1. Complete HTML File Migration Matrix

| Stitch File | Section/View | Target React Page | Route | Category | Status | Primary Purpose / Features |
|---|---|---|---|---|---|---|
| `20.html` | Modern Placement SaaS Dashboard | `DashboardPage.jsx` | `/dashboard` | App | **Migrated** | Candidate greeting, 7-vector score baseline, 5-week Recharts telemetry curve, action plan checklist, AI insights feed, quick action shortcuts. |
| `19.html` (`#view-landing`) | Landing Page | `LandingPage.jsx` | `/` | Public | **Migrated** | Hero, Telemetry Engine, Complete Platform Suite, Onboarding Flow preview, FAQ, Bottom CTA. |
| `19.html` (`#view-login`) | Welcome Back | `LoginPage.jsx` | `/login` | Public | **Migrated** | Email/password form, Show/hide password, Remember me, Social buttons, `authService.login()` integration. |
| `19.html` (`#view-signup`) | Create Your Account | `SignupPage.jsx` | `/signup` | Public | **Migrated** | Name, email, password, terms checkbox, `authService.signup()` integration -> `/onboarding`. |
| `19.html` (`#view-forgot`) | Reset Your Password | `ForgotPasswordPage.jsx` | `/forgot-password` | Public | **Migrated** | Email input, reset password mock trigger, inline success message with resend link. |
| `19.html` (`#view-onboarding`) | Onboarding Intro | `OnboardingIntroPage.jsx` | `/onboarding` | Onboarding | **Migrated** | Welcome overview and 7-step onboarding process preview. |
| `19.html` (`#onboarding-step-1`) | Profile Step | `ProfileStep.jsx` | `/onboarding/profile` | Onboarding | **Migrated** | Step 1: Name, College, Degree & Branch, Graduation Year. |
| `19.html` (`#onboarding-step-2`) | Career Target | `CareerStep.jsx` | `/onboarding/career` | Onboarding | **Migrated** | Step 2: Role selection cards (Backend, Full Stack, AI/ML, Frontend), Secondary Role, Company Tier. |
| `19.html` (`#onboarding-step-3`) | Skills Assessment | `SkillsStep.jsx` | `/onboarding/skills` | Onboarding | **Migrated** | Step 3: Domain confidence selectors (DSA, SysDesign, DBMS, Frameworks) & skill chips. |
| `19.html` (`#onboarding-step-4`) | Integrations Sync | `IntegrationsStep.jsx` | `/onboarding/integrations` | Onboarding | **Migrated** | Step 4: GitHub handle sync, LeetCode profile handle, Resume PDF dropzone upload. |
| `19.html` (`#onboarding-step-5`) | Prep Preferences | `PreferencesStep.jsx` | `/onboarding/preferences` | Onboarding | **Migrated** | Step 5: Daily commitment (45m/90m/3h), AI Mentor Tone (Socratic vs Senior Engineer). |
| `19.html` (`#onboarding-step-6`) | Placement Goals | `GoalsStep.jsx` | `/onboarding/goals` | Onboarding | **Migrated** | Step 6: Target Placement Drive season, CTC Bracket (6-12 LPA, 14-24 LPA, 25+ LPA). |
| `19.html` (`#view-analysis`) | AI Analysis Synthesis | `AnalysisStep.jsx` | `/onboarding/analysis` | Onboarding | **Migrated** | Step 7: Animated AI synthesis progress steps → Baseline score 78/100 → Dashboard handoff. |
| `1.html` | 90-Day Adaptive Placement Roadmap | `RoadmapPage.jsx` | `/roadmap` | App | **Migrated** | Interactive 90-day multi-phase roadmap timeline, phase milestones, daily study matrix. |
| `2.html` | 90-Day Adaptive Roadmap (Detail View) | `RoadmapPage.jsx` | `/roadmap` | App | **Migrated** | Detailed topic curriculum with graph algorithms, pub-sub microservices, and DBMS tuning. |
| `3.html` | Executive SDE Readiness Dashboard | `DashboardPage.jsx` | `/dashboard` | App | Foundation Ready | High-level executive dashboard showing candidate vs Google SDE-1 baseline comparison. |
| `4.html` | Placement Readiness Intelligence | `PlacementReadinessPage.jsx` | `/placement-readiness` | App | Foundation Ready | Multi-vector readiness breakdown, Tier-1 benchmark matrix, competency gaps. |
| `5.html` | AI Placement Mentor & Copilot | `AIMentorPage.jsx` | `/ai-mentor` | App | **Migrated** | Interactive chat copilot with socratic probing, student context integration, code snippets, visual topology diagram, checkpoints, and route actions. |
| `6.html` | Student Placement Dashboard (Candidate View) | `DashboardPage.jsx` | `/dashboard` | App | Foundation Ready | Personalized student dashboard, daily goals, readiness trend graph, telemetry badges. |
| `7.html` | Resume Intelligence | `ResumePage.jsx` | `/resume` | App | **Migrated** | ATS score gauge, STAR bullet point audit with AI optimizer, keyword gap analysis, PDF dropzone upload modal. |
| `8.html` | GitHub Intelligence | `GithubPage.jsx` | `/github` | App | **Migrated** | Commit cadence velocity, language distribution PieChart, repository AST quality grid, profile sync toggle. |
| `9.html` | LeetCode Intelligence | `LeetcodePage.jsx` | `/leetcode` | App | **Migrated** | Solved count by difficulty BarChart, topic performance mastery matrix, recent submissions log, Knight rating. |
| `10.html` | Project Intelligence | `ProjectsPage.jsx` | `/projects` | App | **Migrated** | Architectural complexity audit cards, full project CRUD modal with localStorage, STAR bullet generator. |
| `11.html` | Placement Readiness (7-Vector Audit) | `PlacementReadinessPage.jsx` | `/placement-readiness` | App | **Migrated** | Overall readiness score gauge (82%), 7-vector Recharts RadarChart, preparation modules summary grid, Tier-1 benchmark matrix. |
| `12.html` | AI Skill Gap Analyzer | `SkillGapsPage.jsx` | `/skill-gaps` | App | **Migrated** | Target role benchmark coverage (UserContext integration), multi-vector skill gap audit, 2x2 Impact vs Effort matrix, category coverage. |
| `13.html` | 90-Day AI Roadmap & Today's Tasks Matrix | `RoadmapPage.jsx` & `TasksPage.jsx` | `/roadmap`, `/tasks` | App | **Migrated** | Telemetry-driven rebalancing, missed task recovery, day-by-day execution matrix, single source of truth planning context. |
| `14.html` | AI Mock Interview Studio | `MockInterviewPage.jsx` | `/mock-interview` | App | **Migrated** | Multi-stage technical/system design/behavioral drills, setup modal, live session timer, AI evaluation & score breakdown. |
| `15.html` | Communication Readiness Lab | `CommunicationPage.jsx` | `/communication` | App | **Migrated** | Speech & articulation diagnostic matrix, verbal clarity (82%), WPM pace (145), pitch stability, filler words analysis, interactive prompt studio. |
| `16.html` | AI Placement Mentor (Chat Workspace) | `AIMentorPage.jsx` | `/ai-mentor` | App | **Migrated** | Full conversational workspace with code snippet box, persona selector tabs, quick prompt suggestions, localStorage persistence, and active diagnostic panel. |
| `17.html` | Achievements & Milestones | `AchievementsPage.jsx` | `/achievements` | App | **Migrated** | Level 8 Consistent Builder XP progression banner, active streak, category tabs filter, search filter, Daily XP claim trigger (+50 XP toast), earned/locked achievement grids. |
| `18.html` | System & AI Settings | `SettingsPage.jsx` | `/settings` | App | **Migrated** | 8-tab configuration suite covering placement targets, AI personalization, mentor persona tuning, notifications, privacy, connected accounts, security (password change UI & logout), and danger zone reset dialog. |

---

## 2. Phase Implementation Status Summary

- **Phase 1 (Foundation)**: Completed — TailwindCSS theme tokens, Google Fonts, Lucide & Material Symbols icons.
- **Phase 2 (Landing & Auth)**: Completed — `LandingPage`, `LoginPage`, `SignupPage`, `ForgotPasswordPage`, `AuthContext`.
- **Phase 3 (Onboarding)**: Completed — 7-step onboarding wizard, `OnboardingContext`, `AnalysisStep`.
- **Phase 4 (App Shell & Dashboard)**: Completed — `AppLayout`, `Sidebar`, `Header`, `DashboardPage`, `TelemetryChart`, `ActionPlanList`.
- **Phase 5 (Preparation Modules)**: Completed — `ResumePage`, `GithubPage`, `LeetcodePage`, `ProjectsPage`.
- **Phase 6 (Intelligence Modules)**: Completed — `PlacementReadinessPage`, `SkillGapsPage`.
- **Phase 7 (Planning & Roadmap)**: Completed — `RoadmapPage`, `TasksPage`, `ProgressPage`, `PlanningContext`.
- **Phase 8 (Practice Modules)**: Completed — `MockInterviewPage`, `CommunicationPage`.
- **Phase 9 (AI Mentor Migration)**: Completed — `AIMentorPage`, `mentorService`, persona tabs, code snippets, visual graph diagrams, SPA route actions.
- **Phase 10 (Achievements, Profile, Settings)**: Completed — `AchievementsPage`, `ProfilePage`, `SettingsPage`, `achievementService`, `profileService`, `settingsService`.
- **Phase 11 (Final Integration & Production Readiness)**: Completed — Complete 29-route audit, `ErrorBoundary` integration, zero console errors, responsive polish across desktop/tablet/mobile, production build validated, `ARCHITECTURE.md` documented.

**FRONTEND MIGRATION STATUS: COMPLETE**
