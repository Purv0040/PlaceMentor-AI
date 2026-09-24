# PlaceMentor AI — Reusable Component Inventory (Component Map)

This catalog defines the reusable UI primitives, layout structures, and domain-specific modules identified across the 20 Stitch HTML pages to ensure zero code duplication during migration.

---

## 1. Layout & Shell Components (`src/components/layout/`)
- `AppLayout`: Standard application shell with responsive desktop Sidebar, sticky Header, Outlet area, and Mobile navigation bar.
- `PublicLayout`: Marketing and authentication shell with brand header and footer matching `19.html`.
- `OnboardingLayout`: Stepped wizard wrapper with `OnboardingProvider` & `StepIndicator`.
- `Sidebar`: Categorized navigation sidebar (Main, Preparation, Intelligence, Planning, Practice, AI Copilot, Personal) with active route indicators and Lucide icons.
- `Header`: Global sticky header with search bar, readiness score badge, notification bell, and `UserMenuDropdown`.
- `MobileNavigation`: Mobile drawer & bottom tab bar navigation.

---

## 2. Common UI Primitives (`src/components/common/`)
- `UserMenuDropdown`: Profile dropdown menu with Profile link, Settings link, and `AuthContext.logout()` trigger.
- `FileUploadModal`: Drag & drop PDF resume upload modal with format validation, progress bar, file size display, and reset/remove.
- `ProjectModal`: Modal form for adding or editing projects (title, description, category, tech stack, architecture tags, URLs).
- `StepIndicator`: 7-step horizontal progress bar matching Stitch obsidian design.
- `Button`: Standard styled button variants (Primary Indigo, AI Purple, Secondary, Ghost, Outline, Danger) with loading spinner support.
- `Input`: Standard obsidian-styled input with icon prefix, label, and error message.
- `PasswordInput`: Password input field with toggleable show/hide eye icon.
- `FormError`: Inline alert banner for form submission error feedback.
- `Card`: Dark surface container with customizable padding, subtle border, and obsidian backdrop.
- `Badge`: Status and tag indicators (Success Emerald, Warning Amber, Critical Rose, AI Purple, Mono Pill).

---

## 3. Preparation & Dashboard Domain Components
- `TelemetryChart`: Recharts AreaChart visualizing 5-week readiness, DSA accuracy, and System Design telemetry curve.
- `ActionPlanList`: Interactive daily task checklist with completion checkboxes and route shortcuts.

---

## 4. Context & Data Layer Modules
- `AuthContext`: Manages user token, authentication state, login, signup, and logout.
- `OnboardingContext`: Manages state across all 7 onboarding steps with `localStorage` sync.
- `UserContext`: Stores candidate profile details and provides `updateUserProfile()`.
- `PlanningContext`: Unified single source of truth managing tasks, 90-day roadmap, progress telemetry, and `localStorage` persistence (`placementor_planning_state`).
- `resumeData`: Centralized mock data for ATS scores, bullet point audits, detected/missing skills.
- `githubData` & `githubService`: Mock contribution stats, language breakdown, repo quality scores, sync methods.
- `leetcodeData` & `leetcodeService`: Mock solved counts, contest rating (Knight), topic performance, submissions.
- `projectData`: Portfolio projects array with `localStorage` initialization and persistence.
- `readinessData` & `readinessService`: 7-vector score objects, overall readiness gauge, Tier-1 benchmark comparisons.
- `skillGapData`: Current vs required skill gaps array, 2x2 Impact vs Effort matrix, category coverage breakdown.
- `roadmapData`, `taskData`, `progressData`, `planningService`: Centralized planning datasets & calculation services.
- `interviewData` & `communicationData`: Question bank, prompt bank, and `localStorage` session history handlers.
- `mentorService`: Aggregates student application state, manages `placementCopilotMentorChat` in `localStorage`, and handles deterministic contextual mock responses.
- `achievementService`: Derives XP, level progression, active streaks, and badge unlock states dynamically from application context.
- `profileService`: Manages candidate credentials and calculates centralized profile completion percentage.
- `settingsService`: Manages system, AI reasoning, notification, and privacy settings in `placementCopilotSettings`.

---

## 5. Domain Components (`src/components/`)
### AI Mentor (`src/components/mentor/`)
- `MentorHeader`: Top header with page title, live SDE engine status indicator, and active student pipeline context banner chip.
- `MentorPersonaTabs`: Interactive tab selector for switching between Technical Interviewer, Socratic DSA Tutor, STAR Coach, and Placement Strategist personas.
- `MentorMessage`: Message bubble component rendering AI and candidate messages with syntax-highlighted code snippets, visual graph diagrams, checkpoint quiz cards, and route action buttons.
- `MentorQuickPrompts`: Clickable prompt recommendation chips for quick user message triggers.
- `MentorInputDock`: Textarea dock with keyboard handlers (Enter to send, Shift+Enter newline), file attachments, voice toggle simulation, clear chat action, and send trigger.
- `MentorContextPanel`: Diagnostic sidebar displaying active problem context, real-time code reviewer telemetry scores, and preparation navigation shortcuts.

### Achievements (`src/components/achievements/`)
- `AchievementHeader`: Level 8 "Consistent Builder" XP progression banner, active streak indicator, and Daily XP claim trigger (+50 XP toast).
- `AchievementFilterTabs`: Category filter tabs (All, Consistency, DSA & Code, System Design, Milestones, Interview & STAR) and real-time search bar.
- `AchievementCard`: Card rendering unlocked/locked status badges, requirement progress bars, XP rewards, unlock timestamps, and SPA route navigation shortcuts.

### Profile (`src/components/profile/`)
- `ProfileHeader`: Profile avatar banner with candidate name, target role badge, degree details, and completion percentage gauge.
- `ProfileForm`: View mode and edit mode forms for candidate profile attributes with UserContext sync and localStorage persistence.

### Settings (`src/components/settings/`)
- `SettingsHeader`: Header strip displaying kernel version badge, Discard action, and Save All Changes trigger.
- `SettingsSection`: 8-tab configuration suite covering placement targets, AI personalization parameters, mentor persona tuning, notification toggles, privacy mode, connected accounts, frontend-safe password change form with AuthContext logout, and Danger Zone reset confirmation dialog.

---

## 6. App Pages & Sub-Components
- `DashboardPage`: Complete candidate SaaS Dashboard matching `20.html`.
- `ResumePage`: Resume Intelligence page matching `7.html`.
- `GithubPage`: GitHub Intelligence page matching `8.html`.
- `LeetcodePage`: LeetCode Intelligence page matching `9.html`.
- `ProjectsPage`: Project Intelligence page matching `10.html`.
- `PlacementReadinessPage`: Placement Readiness page matching `11.html` & `4.html`.
- `SkillGapsPage`: AI Skill Gap Analyzer page matching `12.html`.
- `RoadmapPage`: 90-Day Adaptive Placement Roadmap page matching `1.html`, `2.html`, `13.html`.
- `TasksPage`: Today's Action Plan Tasks page matching `13.html` & `20.html`.
- `ProgressPage`: Progress Telemetry page matching `3.html`, `13.html`, `17.html`.
- `MockInterviewPage`: AI Mock Interview Studio matching `14.html` (with `InterviewSetupModal`).
- `CommunicationPage`: Communication Readiness Lab matching `15.html`.
- `AIMentorPage`: AI Placement Mentor & Copilot matching `5.html` & `16.html`.
- `AchievementsPage`: Achievements & Milestones page matching `17.html`.
- `ProfilePage`: Student Profile page matching Stitch candidate profile specifications.
- `SettingsPage`: System & AI Settings page matching `18.html`.


