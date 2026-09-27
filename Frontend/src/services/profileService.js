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
      name: user.name || user.full_name || onboarding.profile?.name || 'Student Candidate',
      email: user.email || onboarding.profile?.email || '',
      college: user.college || onboarding.profile?.college || 'University Student',
      degree: user.degree || onboarding.profile?.degree || 'B.Tech / B.E.',
      branch: user.branch || 'Computer Engineering',
      graduationYear: user.graduationYear || onboarding.profile?.graduationYear || '2026',
      targetRole: user.targetRole || onboarding.career?.targetRole || 'Full Stack Engineer',
      secondaryRole: user.secondaryRole || onboarding.career?.secondaryRole || 'Cybersecurity Analyst & Engineer',
      companyTier: user.companyTier || onboarding.career?.companyTier || 'Tier-1 Product (MAANG / Unicorns)',
      targetCtc: user.targetCtc || onboarding.goals?.targetCtc || '12 - 20 LPA (Product Tier)',
      targetDrive: user.targetDrive || onboarding.goals?.targetDrive || 'August 2026 (Campus Phase 1)',
      dsaLevel: user.dsaLevel || onboarding.skills?.dsaLevel || 'Intermediate',
      sysDesignLevel: user.sysDesignLevel || onboarding.skills?.sysDesignLevel || 'Beginner',
      githubHandle: user.githubHandle || onboarding.integrations?.githubHandle || '',
      leetcodeHandle: user.leetcodeHandle || onboarding.integrations?.leetcodeHandle || '',
      resumeFileName: user.resumeFileName || onboarding.integrations?.resumeFileName || '',
      dailyGoalMinutes: user.preferences?.dailyGoalMinutes || onboarding.preferences?.dailyGoalMinutes || '90',
      mentorTone: user.preferences?.mentorTone || onboarding.preferences?.mentorTone || 'Socratic Coach (Probing Questions)',
      skills: onboarding.skills?.selectedSkills || ['Data Structures', 'Python', 'Git', 'SQL']
    };
  },

  saveProfile: (profileData) => {
    try {
      localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(profileData));
    } catch (e) {
      console.error('Failed to save profile to localStorage', e);
    }
  },

  calculateCompletion: (profile) => {
    if (!profile) return 0;
    const fields = [
      profile.name,
      profile.email,
      profile.college,
      profile.degree,
      profile.targetRole,
      profile.githubHandle,
      profile.leetcodeHandle,
      profile.resumeFileName
    ];

    const filledCount = fields.filter(f => f && String(f).trim().length > 0).length;
    return Math.round((filledCount / fields.length) * 100);
  }
};
