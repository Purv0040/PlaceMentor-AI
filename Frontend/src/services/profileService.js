// Profile Service for candidate details and consistent profile completion calculation

const PROFILE_STORAGE_KEY = 'placementCopilotProfile';

export const profileService = {
  getProfile: (userContext = null, onboardingData = null) => {
    try {
      const saved = localStorage.getItem(PROFILE_STORAGE_KEY);
      if (saved) {
        return JSON.parse(saved);
      }
    } catch (e) {
      console.error('Failed to parse profile from localStorage', e);
    }

    const user = userContext?.user || {};
    const onboarding = onboardingData || {};

    return {
      name: user.name || onboarding.profile?.name || 'Alex Patel',
      email: user.email || 'alex.patel@cspit.ac.in',
      college: user.college || onboarding.profile?.college || 'CSPIT',
      degree: user.degree || onboarding.profile?.degree || 'B.Tech IT',
      branch: user.branch || 'Information Technology',
      graduationYear: user.graduationYear || onboarding.profile?.graduationYear || '2027',
      targetRole: user.targetRole || onboarding.career?.targetRole || 'Backend Developer',
      secondaryRole: user.secondaryRole || onboarding.career?.secondaryRole || 'AI/ML Engineer',
      companyTier: user.companyTier || onboarding.career?.companyTier || 'Tier-1 Product (MAANG / Unicorns)',
      targetCtc: user.targetCtc || onboarding.goals?.targetCtc || '14 - 24 LPA (Product Tier)',
      targetDrive: user.targetDrive || onboarding.goals?.targetDrive || 'August 2026 (Campus Phase 1)',
      dsaLevel: user.dsaLevel || onboarding.skills?.dsaLevel || 'Intermediate',
      sysDesignLevel: user.sysDesignLevel || onboarding.skills?.sysDesignLevel || 'Beginner',
      githubHandle: user.githubHandle || onboarding.integrations?.githubHandle || 'alexpatel-dev',
      leetcodeHandle: user.leetcodeHandle || onboarding.integrations?.leetcodeHandle || 'alex_patel99',
      resumeFileName: user.resumeFileName || onboarding.integrations?.resumeFileName || 'Alex_Patel_Backend_Resume.pdf',
      dailyGoalMinutes: user.preferences?.dailyGoalMinutes || onboarding.preferences?.dailyGoalMinutes || '90',
      mentorTone: user.preferences?.mentorTone || onboarding.preferences?.mentorTone || 'Socratic Coach (Probing Questions)',
      skills: onboarding.skills?.selectedSkills || ['Java', 'Spring Boot', 'Data Structures', 'SQL', 'Git', 'Docker']
    };
  },

  saveProfile: (profileData) => {
    try {
      localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(profileData));
    } catch (e) {
      console.error('Failed to save profile to localStorage', e);
    }
  },

  calculateProfileCompletion: (profile) => {
    if (!profile) return 80;

    let score = 0;
    if (profile.name && profile.email) score += 15;
    if (profile.college && profile.degree) score += 15;
    if (profile.targetRole) score += 15;
    if (profile.githubHandle) score += 15;
    if (profile.leetcodeHandle) score += 15;
    if (profile.resumeFileName) score += 15;
    if (profile.dailyGoalMinutes) score += 10;

    return Math.min(score, 100);
  }
};
