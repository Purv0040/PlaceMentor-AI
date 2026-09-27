import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';

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

  const completeStep = (stepNumber) => {
    setOnboardingData(prev => {
      const completed = new Set(prev.completedSteps);
      completed.add(stepNumber);
      return {
        ...prev,
        completedSteps: Array.from(completed)
      };
    });
  };

  const markOnboardingComplete = () => {
    localStorage.setItem(ONBOARDING_COMPLETE_KEY, 'true');
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
