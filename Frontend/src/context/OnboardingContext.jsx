import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';
import { onboardingService } from '../services/onboardingService';

const ONBOARDING_STORAGE_KEY = 'placementCopilotOnboarding';
export const ONBOARDING_COMPLETE_KEY = 'placementCopilotOnboardingComplete';

const buildInitialState = () => {
  const activeUser = authService.getCurrentUser();
  const name = activeUser?.name || activeUser?.full_name || '';
  const email = activeUser?.email || '';

  return {
    profile: {
      name: name,
      email: email,
      college: '',
      degree: '',
      graduationYear: '2026'
    },
    career: {
      targetRole: 'Software Engineer',
      secondaryRole: 'Full Stack Developer',
      companyTier: 'Tier-1 Product (MAANG / Unicorns)'
    },
    skills: {
      dsaLevel: 'Intermediate',
      sysDesignLevel: 'Beginner',
      databaseLevel: 'Intermediate',
      frameworkLevel: 'Intermediate',
      selectedSkills: ['Python', 'Java', 'Data Structures', 'SQL', 'Git']
    },
    integrations: {
      githubConnected: false,
      githubHandle: '',
      leetcodeConnected: false,
      leetcodeHandle: '',
      resumeUploaded: false,
      resumeFileName: ''
    },
    preferences: {
      dailyGoalMinutes: '90',
      mentorTone: 'Socratic Coach (Probing Questions)',
      studyCadence: 'Daily Evening Sprint'
    },
    goals: {
      targetDrive: 'August 2026 (Campus Phase 1)',
      targetCtc: '12 - 20 LPA (Product Tier)',
      primaryGoal: 'Master Data Structures, Algorithms & System Architecture'
    },
    currentStep: 1,
    completedSteps: [1]
  };
};

const OnboardingContext = createContext(null);

export const OnboardingProvider = ({ children }) => {
  const [onboardingData, setOnboardingData] = useState(() => {
    try {
      const saved = localStorage.getItem(ONBOARDING_STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        const activeUser = authService.getCurrentUser();
        if (activeUser?.name && (!parsed.profile?.name || parsed.profile?.name === 'Alex Patel')) {
          parsed.profile = { ...parsed.profile, name: activeUser.name, email: activeUser.email };
        }
        return parsed;
      }
      return buildInitialState();
    } catch (e) {
      return buildInitialState();
    }
  });

  // Fetch initial onboarding state from backend if logged in
  useEffect(() => {
    if (!authService.isAuthenticated()) return;

    const fetchBackendState = async () => {
      try {
        const res = await onboardingService.getOnboardingState();
        if (res && res.success && res.data) {
          const apiData = res.data;
          setOnboardingData(prev => ({
            ...prev,
            profile: { ...prev.profile, ...(apiData.personal || {}) },
            career: { ...prev.career, ...(apiData.career || {}) },
            skills: { ...prev.skills, ...(apiData.skills || {}) },
            integrations: { ...prev.integrations, ...(apiData.integrations || {}) },
            preferences: { ...prev.preferences, ...(apiData.preferences || {}) },
            goals: { ...prev.goals, ...(apiData.goals || {}) },
            completedSteps: apiData.onboarding?.completed_steps?.length
              ? apiData.onboarding.completed_steps
              : prev.completedSteps,
            currentStep: apiData.onboarding?.current_step || prev.currentStep
          }));
        }
      } catch (e) {
        console.warn('Could not retrieve remote onboarding state:', e);
      }
    };
    fetchBackendState();
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem(ONBOARDING_STORAGE_KEY, JSON.stringify(onboardingData));
    } catch (e) {
      console.error('Failed to save onboarding state:', e);
    }
  }, [onboardingData]);

  const updateProfile = (profileData) => {
    setOnboardingData(prev => ({
      ...prev,
      profile: { ...prev.profile, ...profileData }
    }));
  };

  const updateCareer = (careerData) => {
    setOnboardingData(prev => ({
      ...prev,
      career: { ...prev.career, ...careerData }
    }));
  };

  const updateSkills = (skillsData) => {
    setOnboardingData(prev => ({
      ...prev,
      skills: { ...prev.skills, ...skillsData }
    }));
  };

  const updateIntegrations = (integrationsData) => {
    setOnboardingData(prev => ({
      ...prev,
      integrations: { ...prev.integrations, ...integrationsData }
    }));
  };

  const updatePreferences = (preferencesData) => {
    setOnboardingData(prev => ({
      ...prev,
      preferences: { ...prev.preferences, ...preferencesData }
    }));
  };

  const updateGoals = (goalsData) => {
    setOnboardingData(prev => ({
      ...prev,
      goals: { ...prev.goals, ...goalsData }
    }));
  };

  const completeStep = (stepNumber, stepDataPatch = {}) => {
    setOnboardingData(prev => {
      const completed = new Set(prev.completedSteps);
      completed.add(stepNumber);

      const merged = {
        ...prev,
        ...stepDataPatch,
        profile: { ...prev.profile, ...(stepDataPatch.profile || {}) },
        career: { ...prev.career, ...(stepDataPatch.career || {}) },
        skills: { ...prev.skills, ...(stepDataPatch.skills || {}) },
        integrations: { ...prev.integrations, ...(stepDataPatch.integrations || {}) },
        preferences: { ...prev.preferences, ...(stepDataPatch.preferences || {}) },
        goals: { ...prev.goals, ...(stepDataPatch.goals || {}) },
        completedSteps: Array.from(completed),
        currentStep: Math.max(stepNumber + 1, prev.currentStep)
      };

      try {
        localStorage.setItem(ONBOARDING_STORAGE_KEY, JSON.stringify(merged));
      } catch (e) {}

      // Dispatch step update payload to backend API
      const payload = {
        step_number: stepNumber,
        profile: merged.profile,
        career: merged.career,
        skills: merged.skills,
        integrations: merged.integrations,
        preferences: merged.preferences,
        goals: merged.goals
      };

      onboardingService.updateStep(stepNumber, payload).catch(err => {
        console.warn(`Step ${stepNumber} saved locally, backend notification:`, err);
      });

      return merged;
    });
  };

  const markOnboardingComplete = () => {
    localStorage.setItem(ONBOARDING_COMPLETE_KEY, 'true');
    onboardingService.completeOnboarding().catch(() => {});
  };

  const isOnboardingComplete = () => {
    return localStorage.getItem(ONBOARDING_COMPLETE_KEY) === 'true';
  };

  return (
    <OnboardingContext.Provider
      value={{
        onboardingData,
        updateProfile,
        updateCareer,
        updateSkills,
        updateIntegrations,
        updatePreferences,
        updateGoals,
        completeStep,
        markOnboardingComplete,
        isOnboardingComplete
      }}
    >
      {children}
    </OnboardingContext.Provider>
  );
};

export const useOnboarding = () => {
  const context = useContext(OnboardingContext);
  if (!context) {
    const initialState = buildInitialState();
    return {
      onboardingData: initialState,
      updateProfile: () => {},
      updateCareer: () => {},
      updateSkills: () => {},
      updateIntegrations: () => {},
      updatePreferences: () => {},
      updateGoals: () => {},
      completeStep: () => {},
      markOnboardingComplete: () => {},
      isOnboardingComplete: () => false
    };
  }
  return context;
};
