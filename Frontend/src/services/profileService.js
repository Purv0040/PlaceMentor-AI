import { apiRequest } from './api';

const PROFILE_STORAGE_KEY = 'placementCopilotProfile';

export const profileService = {
  getProfileFromApi: async () => {
    try {
      const res = await apiRequest('/users/me/profile');
      if (res && res.success && res.data) {
        return res.data;
      }
    } catch (e) {
      console.warn('Failed to fetch profile from API, fallback to local', e);
    }
    return null;
  },

  updateProfileInApi: async (profileData) => {
    try {
      const res = await apiRequest('/users/me/profile', {
        method: 'PUT',
        body: JSON.stringify(profileData)
      });
      if (res && res.success && res.data) {
        return res.data;
      }
    } catch (e) {
      console.warn('Failed to update profile in API', e);
    }
    return null;
  },

  formatFromApi: (apiData) => {
    if (!apiData) return null;
    const personal = apiData.personal || {};
    const career = apiData.career || {};
    const skills = apiData.skills || {};
    const integrations = apiData.integrations || {};
    const preferences = apiData.preferences || {};
    const goals = apiData.goals || {};

    return {
      name: personal.name || apiData.full_name || apiData.name || '',
      email: personal.email || apiData.email || '',
      college: personal.college || '',
      degree: personal.degree || '',
      branch: personal.branch || 'Computer Science / IT',
      graduationYear: personal.graduationYear || '2026',
      cgpa: personal.cgpa || '',
      phone: personal.phone || '',
      location: personal.location || '',
      bio: personal.bio || '',
      linkedinUrl: personal.linkedinUrl || '',
      portfolioUrl: personal.portfolioUrl || '',
      targetRole: career.targetRole || apiData.target_role || 'Full Stack Engineer',
      secondaryRole: career.secondaryRole || 'Cybersecurity Analyst & Engineer',
      companyTier: career.companyTier || 'Tier-1 Product (MAANG / Unicorns)',
      careerGoal: career.career_goal || '',
      targetCtc: goals.targetCtc || '14 - 24 LPA (Product Tier)',
      targetDrive: goals.targetDrive || 'August 2026 (Campus Phase 1)',
      primaryGoal: goals.primaryGoal || 'Master Technical Algorithms & System Architecture',
      dsaLevel: skills.dsaLevel || 'Intermediate',
      sysDesignLevel: skills.sysDesignLevel || 'Beginner',
      databaseLevel: skills.databaseLevel || 'Intermediate',
      frameworkLevel: skills.frameworkLevel || 'Advanced',
      skills: skills.selectedSkills || ['Java', 'Spring Boot', 'Data Structures', 'SQL', 'Git'],
      githubHandle: integrations.githubHandle || apiData.github_username || '',
      leetcodeHandle: integrations.leetcodeHandle || apiData.leetcode_username || '',
      resumeFileName: integrations.resumeFileName || '',
      dailyGoalMinutes: preferences.dailyGoalMinutes || '90',
      mentorTone: preferences.mentorTone || 'Socratic Coach (Probing Questions)',
      studyCadence: preferences.studyCadence || 'Daily Evening Sprint'
    };
  },

  buildApiPayload: (profile) => {
    return {
      personal: {
        name: profile.name || '',
        college: profile.college || '',
        degree: profile.degree || '',
        branch: profile.branch || 'Computer Science / IT',
        graduationYear: String(profile.graduationYear || '2026'),
        cgpa: profile.cgpa || undefined,
        email: profile.email || undefined,
        phone: profile.phone || undefined,
        location: profile.location || undefined,
        bio: profile.bio || undefined,
        linkedinUrl: profile.linkedinUrl || undefined,
        portfolioUrl: profile.portfolioUrl || undefined
      },
      career: {
        targetRole: profile.targetRole || 'Full Stack Engineer',
        secondaryRole: profile.secondaryRole || undefined,
        companyTier: profile.companyTier || undefined,
        career_goal: profile.careerGoal || undefined
      },
      skills: {
        dsaLevel: profile.dsaLevel || 'Intermediate',
        sysDesignLevel: profile.sysDesignLevel || 'Beginner',
        databaseLevel: profile.databaseLevel || 'Intermediate',
        frameworkLevel: profile.frameworkLevel || 'Advanced',
        selectedSkills: Array.isArray(profile.skills) ? profile.skills : []
      },
      integrations: {
        githubConnected: Boolean(profile.githubHandle),
        githubHandle: profile.githubHandle || null,
        leetcodeConnected: Boolean(profile.leetcodeHandle),
        leetcodeHandle: profile.leetcodeHandle || null,
        resumeUploaded: Boolean(profile.resumeFileName),
        resumeFileName: profile.resumeFileName || null
      },
      preferences: {
        dailyGoalMinutes: String(profile.dailyGoalMinutes || '90'),
        mentorTone: profile.mentorTone || 'Socratic Coach (Probing Questions)',
        studyCadence: profile.studyCadence || 'Daily Evening Sprint'
      },
      goals: {
        targetDrive: profile.targetDrive || 'August 2026 (Campus Phase 1)',
        targetCtc: profile.targetCtc || '14 - 24 LPA (Product Tier)',
        primaryGoal: profile.primaryGoal || 'Master Technical Algorithms & System Architecture'
      }
    };
  },

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
      cgpa: user.cgpa || '',
      phone: user.phone || '',
      location: user.location || '',
      bio: user.bio || '',
      linkedinUrl: user.linkedinUrl || '',
      portfolioUrl: user.portfolioUrl || '',
      targetRole: user.targetRole || onboarding.career?.targetRole || 'Full Stack Engineer',
      secondaryRole: user.secondaryRole || onboarding.career?.secondaryRole || 'Cybersecurity Analyst & Engineer',
      companyTier: user.companyTier || onboarding.career?.companyTier || 'Tier-1 Product (MAANG / Unicorns)',
      careerGoal: user.careerGoal || '',
      targetCtc: user.targetCtc || onboarding.goals?.targetCtc || '14 - 24 LPA (Product Tier)',
      targetDrive: user.targetDrive || onboarding.goals?.targetDrive || 'August 2026 (Campus Phase 1)',
      primaryGoal: user.primaryGoal || onboarding.goals?.primaryGoal || 'Master Technical Algorithms & System Architecture',
      dsaLevel: user.dsaLevel || onboarding.skills?.dsaLevel || 'Intermediate',
      sysDesignLevel: user.sysDesignLevel || onboarding.skills?.sysDesignLevel || 'Beginner',
      databaseLevel: user.databaseLevel || onboarding.skills?.databaseLevel || 'Intermediate',
      frameworkLevel: user.frameworkLevel || onboarding.skills?.frameworkLevel || 'Advanced',
      githubHandle: user.githubHandle || onboarding.integrations?.githubHandle || '',
      leetcodeHandle: user.leetcodeHandle || onboarding.integrations?.leetcodeHandle || '',
      resumeFileName: user.resumeFileName || onboarding.integrations?.resumeFileName || localStorage.getItem('placementCopilotResumeName') || '',
      dailyGoalMinutes: user.dailyGoalMinutes || onboarding.preferences?.dailyGoalMinutes || '90',
      mentorTone: user.mentorTone || onboarding.preferences?.mentorTone || 'Socratic Coach (Probing Questions)',
      studyCadence: user.studyCadence || onboarding.preferences?.studyCadence || 'Daily Evening Sprint',
      skills: user.selectedSkills || onboarding.skills?.selectedSkills || ['Java', 'Spring Boot', 'Data Structures', 'SQL', 'Git']
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
      profile.resumeFileName,
      profile.cgpa,
      profile.linkedinUrl
    ];

    const filledCount = fields.filter(f => f && String(f).trim().length > 0).length;
    return Math.round((filledCount / fields.length) * 100);
  }
};

