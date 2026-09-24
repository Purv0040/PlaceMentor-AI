import React from 'react';
import { Routes, Route } from 'react-router-dom';

// Layouts & Protection
import { PublicLayout } from '../components/layout/PublicLayout';
import { OnboardingLayout } from '../components/layout/OnboardingLayout';
import { AppLayout } from '../components/layout/AppLayout';
import { ProtectedRoute } from '../components/routes/ProtectedRoute';

// Public Pages
import { LandingPage } from '../pages/public/LandingPage';
import { LoginPage } from '../pages/public/LoginPage';
import { SignupPage } from '../pages/public/SignupPage';
import { ForgotPasswordPage } from '../pages/public/ForgotPasswordPage';

// Onboarding Pages
import { OnboardingIntroPage } from '../pages/onboarding/OnboardingIntroPage';
import { ProfileStep } from '../pages/onboarding/ProfileStep';
import { CareerStep } from '../pages/onboarding/CareerStep';
import { SkillsStep } from '../pages/onboarding/SkillsStep';
import { IntegrationsStep } from '../pages/onboarding/IntegrationsStep';
import { PreferencesStep } from '../pages/onboarding/PreferencesStep';
import { GoalsStep } from '../pages/onboarding/GoalsStep';
import { AnalysisStep } from '../pages/onboarding/AnalysisStep';

// Application Pages (Phase 4 Dashboard Migrated + App Shell Placeholders)
import { DashboardPage } from '../pages/app/DashboardPage';
import { ResumePage } from '../pages/app/ResumePage';
import { GithubPage } from '../pages/app/GithubPage';
import { LeetcodePage } from '../pages/app/LeetcodePage';
import { ProjectsPage } from '../pages/app/ProjectsPage';
import { PlacementReadinessPage } from '../pages/app/PlacementReadinessPage';
import { SkillGapsPage } from '../pages/app/SkillGapsPage';
import { RoadmapPage } from '../pages/app/RoadmapPage';
import { TasksPage } from '../pages/app/TasksPage';
import { ProgressPage } from '../pages/app/ProgressPage';
import { MockInterviewPage } from '../pages/app/MockInterviewPage';
import { CommunicationPage } from '../pages/app/CommunicationPage';
import { AIMentorPage } from '../pages/app/AIMentorPage';
import { AchievementsPage } from '../pages/app/AchievementsPage';
import { ProfilePage } from '../pages/app/ProfilePage';
import { SettingsPage } from '../pages/app/SettingsPage';
import { NotFoundPage } from '../pages/app/NotFoundPage';

export const AppRoutes = () => {
  return (
    <Routes>
      {/* Public Landing & Auth Routes */}
      <Route element={<PublicLayout />}>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      </Route>

      {/* Onboarding Stepper Routes */}
      <Route path="/onboarding" element={<OnboardingLayout />}>
        <Route index element={<OnboardingIntroPage />} />
        <Route path="profile" element={<ProfileStep />} />
        <Route path="career" element={<CareerStep />} />
        <Route path="skills" element={<SkillsStep />} />
        <Route path="integrations" element={<IntegrationsStep />} />
        <Route path="preferences" element={<PreferencesStep />} />
        <Route path="goals" element={<GoalsStep />} />
        <Route path="analysis" element={<AnalysisStep />} />
      </Route>

      {/* Protected Authenticated Application Shell (Phase 4) */}
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/resume" element={<ResumePage />} />
          <Route path="/github" element={<GithubPage />} />
          <Route path="/leetcode" element={<LeetcodePage />} />
          <Route path="/projects" element={<ProjectsPage />} />
          <Route path="/placement-readiness" element={<PlacementReadinessPage />} />
          <Route path="/skill-gaps" element={<SkillGapsPage />} />
          <Route path="/roadmap" element={<RoadmapPage />} />
          <Route path="/tasks" element={<TasksPage />} />
          <Route path="/progress" element={<ProgressPage />} />
          <Route path="/mock-interview" element={<MockInterviewPage />} />
          <Route path="/communication" element={<CommunicationPage />} />
          <Route path="/ai-mentor" element={<AIMentorPage />} />
          <Route path="/achievements" element={<AchievementsPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>
      </Route>

      {/* 404 Fallback */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
};
