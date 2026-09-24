import React, { createContext, useContext, useState, useEffect } from 'react';

const ONBOARDING_STORAGE_KEY = 'placementCopilotOnboarding';
export const ONBOARDING_COMPLETE_KEY = 'placementCopilotOnboardingComplete';

const defaultState = {
  profile: {
    name: 'Alex Patel',
    college: 'CSPIT',
    degree: 'B.Tech IT',
    graduationYear: '2027'
  },
  career: {
    targetRole: 'Backend Developer',
    secondaryRole: 'AI/ML Engineer',
    companyTier: 'Tier-1 Product (MAANG / Unicorns)'
  },
  skills: {
    dsaLevel: 'Intermediate',
    sysDesignLevel: 'Beginner',
    databaseLevel: 'Intermediate',
    frameworkLevel: 'Advanced',
    selectedSkills: ['Java', 'Spring Boot', 'Data Structures', 'SQL', 'Git']
  },
  integrations: {
    githubConnected: true,
    githubHandle: 'alexpatel-dev',
    leetcodeConnected: true,
    leetcodeHandle: 'alex_patel99',
    resumeUploaded: true,
    resumeFileName: 'Alex_Patel_Backend_Resume.pdf'
  },
  preferences: {
    dailyGoalMinutes: '90',
    mentorTone: 'Socratic Coach (Probing Questions)',
    studyCadence: 'Daily Evening Sprint'
  },
  goals: {
    targetDrive: 'August 2026 (Campus Phase 1)',
    targetCtc: '14 - 24 LPA (Product Tier)',
    primaryGoal: 'Master Graph Algorithms & System Microservices'
  },
  currentStep: 1,
  completedSteps: [1]
};

const OnboardingContext = createContext(null);

export const OnboardingProvider = ({ children }) => {
  const [onboardingData, setOnboardingData] = useState(() => {
    try {
      const saved = localStorage.getItem(ONBOARDING_STORAGE_KEY);
      return saved ? JSON.parse(saved) : defaultState;
    } catch (e) {
      return defaultState;
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

export const useOnboarding = () => useContext(OnboardingContext);
