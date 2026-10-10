import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';
import { profileService } from '../services/profileService';
import { readinessService } from '../services/readinessService';

const USER_KEY = 'placementor_user_data';

const UserContext = createContext(null);

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const activeUser = authService.getCurrentUser() || {};
    let savedUser = {};
    let savedOnboarding = {};
    try {
      const sU = localStorage.getItem(USER_KEY);
      if (sU) savedUser = JSON.parse(sU);
      const sO = localStorage.getItem('placementCopilotOnboarding');
      if (sO) savedOnboarding = JSON.parse(sO);
    } catch (e) {}

    const profile = savedOnboarding.profile || {};
    const career = savedOnboarding.career || {};
    const skills = savedOnboarding.skills || {};
    const integrations = savedOnboarding.integrations || {};
    const preferences = savedOnboarding.preferences || {};
    const goals = savedOnboarding.goals || {};

    const sResume = localStorage.getItem('placementCopilotResumeName');

    return {
      ...activeUser,
      ...savedUser,
      name: savedUser.name || profile.name || activeUser.name || activeUser.full_name || 'Student Candidate',
      email: savedUser.email || profile.email || activeUser.email || '',
      college: savedUser.college || profile.college || '',
      degree: savedUser.degree || profile.degree || '',
      graduationYear: savedUser.graduationYear || profile.graduationYear || '2026',
      targetRole: savedUser.targetRole || career.targetRole || 'Full Stack Engineer',
      secondaryRole: savedUser.secondaryRole || career.secondaryRole || 'Cybersecurity Analyst & Engineer',
      companyTier: savedUser.companyTier || career.companyTier || 'Tier-1 Product (MAANG / Unicorns)',
      githubHandle: savedUser.githubHandle || integrations.githubHandle || '',
      leetcodeHandle: savedUser.leetcodeHandle || integrations.leetcodeHandle || '',
      resumeFileName: savedUser.resumeFileName || integrations.resumeFileName || sResume || '',
      overallReadinessScore: savedUser.overallReadinessScore ?? null,
      dsaLevel: savedUser.dsaLevel || skills.dsaLevel || 'Intermediate',
      sysDesignLevel: savedUser.sysDesignLevel || skills.sysDesignLevel || 'Beginner',
      databaseLevel: savedUser.databaseLevel || skills.databaseLevel || 'Intermediate',
      frameworkLevel: savedUser.frameworkLevel || skills.frameworkLevel || 'Advanced',
      selectedSkills: savedUser.selectedSkills || skills.selectedSkills || ['Python', 'Java', 'Data Structures', 'SQL', 'Git'],
      mentorTone: savedUser.mentorTone || preferences.mentorTone || 'Socratic Coach (Probing Questions)',
      dailyGoalMinutes: savedUser.dailyGoalMinutes || preferences.dailyGoalMinutes || '90',
      studyCadence: savedUser.studyCadence || preferences.studyCadence || 'Daily Evening Sprint',
      targetDrive: savedUser.targetDrive || goals.targetDrive || 'August 2026 (Campus Phase 1)',
      targetCtc: savedUser.targetCtc || goals.targetCtc || '14 - 24 LPA (Product Tier)',
      primaryGoal: savedUser.primaryGoal || goals.primaryGoal || 'Master Technical Algorithms & System Architecture',
      streakDays: savedUser.streakDays !== undefined ? savedUser.streakDays : 0,
      applicationsCount: savedUser.applicationsCount || 0
    };
  });

  useEffect(() => {
    const fetchApiProfile = async () => {
      if (!authService.isAuthenticated()) return;
      const activeUser = authService.getCurrentUser();
      if (activeUser) {
        setUser(prev => ({
          ...prev,
          ...activeUser,
          name: prev.name || activeUser.name || activeUser.full_name || 'Student Candidate'
        }));

        try {
          const apiProfile = await profileService.getProfileFromApi();
          if (apiProfile) {
            const personal = apiProfile.personal || {};
            const career = apiProfile.career || {};
            const skills = apiProfile.skills || {};
            const integrations = apiProfile.integrations || {};
            const preferences = apiProfile.preferences || {};
            const goals = apiProfile.goals || {};

            setUser(prev => ({
              ...prev,
              ...apiProfile,
              name: personal.name || apiProfile.full_name || apiProfile.name || prev.name,
              email: personal.email || apiProfile.email || prev.email,
              college: personal.college || prev.college,
              degree: personal.degree || prev.degree,
              graduationYear: personal.graduationYear || prev.graduationYear,
              targetRole: career.targetRole || apiProfile.target_role || prev.targetRole,
              secondaryRole: career.secondaryRole || prev.secondaryRole,
              companyTier: career.companyTier || prev.companyTier,
              dsaLevel: skills.dsaLevel || prev.dsaLevel,
              sysDesignLevel: skills.sysDesignLevel || prev.sysDesignLevel,
              databaseLevel: skills.databaseLevel || prev.databaseLevel,
              frameworkLevel: skills.frameworkLevel || prev.frameworkLevel,
              selectedSkills: skills.selectedSkills?.length ? skills.selectedSkills : prev.selectedSkills,
              githubHandle: integrations.githubHandle || apiProfile.github_username || prev.githubHandle,
              leetcodeHandle: integrations.leetcodeHandle || apiProfile.leetcode_username || prev.leetcodeHandle,
              resumeFileName: integrations.resumeFileName || prev.resumeFileName,
              mentorTone: preferences.mentorTone || prev.mentorTone,
              dailyGoalMinutes: preferences.dailyGoalMinutes || prev.dailyGoalMinutes,
              studyCadence: preferences.studyCadence || prev.studyCadence,
              targetDrive: goals.targetDrive || prev.targetDrive,
              targetCtc: goals.targetCtc || prev.targetCtc,
              primaryGoal: goals.primaryGoal || prev.primaryGoal,
            }));
          }
        } catch (e) {
          console.error("Failed to fetch API profile in UserContext:", e);
        }

        try {
          const readiness = await readinessService.getLatestReadiness();
          if (readiness && typeof readiness.overall_score === 'number') {
            setUser(prev => ({
              ...prev,
              overallReadinessScore: readiness.overall_score
            }));
          }
        } catch (e) {
          // Readiness may not exist yet if student just registered
        }
      }
    };
    fetchApiProfile();
  }, []);

  const updateUserProfile = (newDetails) => {
    setUser(prev => {
      const base = prev || {};
      const updated = {
        ...base,
        ...newDetails,
        name: newDetails.name || newDetails.full_name || base.name || base.full_name,
        preferences: { ...(base.preferences || {}), ...(newDetails.preferences || {}) }
      };

      try {
        localStorage.setItem(USER_KEY, JSON.stringify(updated));
      } catch (e) {
        console.error('Failed to save user profile:', e);
      }

      // Build structured payload for backend profile update
      const structuredPayload = {
        personal: {
          name: updated.name || '',
          college: updated.college || '',
          degree: updated.degree || '',
          graduationYear: String(updated.graduationYear || '2026'),
          email: updated.email || undefined
        },
        career: {
          targetRole: updated.targetRole || 'Full Stack Engineer',
          secondaryRole: updated.secondaryRole,
          companyTier: updated.companyTier
        },
        skills: {
          dsaLevel: updated.dsaLevel || 'Intermediate',
          sysDesignLevel: updated.sysDesignLevel || 'Beginner',
          databaseLevel: updated.databaseLevel || 'Intermediate',
          frameworkLevel: updated.frameworkLevel || 'Advanced',
          selectedSkills: updated.selectedSkills || []
        },
        integrations: {
          githubConnected: !!updated.githubHandle,
          githubHandle: updated.githubHandle || null,
          leetcodeConnected: !!updated.leetcodeHandle,
          leetcodeHandle: updated.leetcodeHandle || null,
          resumeUploaded: !!updated.resumeFileName,
          resumeFileName: updated.resumeFileName || null
        },
        preferences: {
          dailyGoalMinutes: String(updated.dailyGoalMinutes || '90'),
          mentorTone: updated.mentorTone || 'Socratic Coach (Probing Questions)',
          studyCadence: updated.studyCadence || 'Daily Evening Sprint'
        },
        goals: {
          targetDrive: updated.targetDrive || 'August 2026 (Campus Phase 1)',
          targetCtc: updated.targetCtc || '14 - 24 LPA (Product Tier)',
          primaryGoal: updated.primaryGoal || 'Master Technical Algorithms & System Architecture'
        },
        overallReadinessScore: updated.overallReadinessScore || undefined
      };

      profileService.updateProfileInApi(structuredPayload).catch(() => {});
      return updated;
    });
  };

  return (
    <UserContext.Provider value={{ user, setUser, updateUserProfile }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => useContext(UserContext);
