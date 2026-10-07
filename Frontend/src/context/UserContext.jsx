import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';
import { profileService } from '../services/profileService';

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
      college: savedUser.college || profile.college || 'CSPIT',
      degree: savedUser.degree || profile.degree || 'B.Tech IT',
      graduationYear: savedUser.graduationYear || profile.graduationYear || '2028',
      targetRole: savedUser.targetRole || career.targetRole || 'Backend SDE-1 (Tier 1)',
      secondaryRole: savedUser.secondaryRole || career.secondaryRole || 'Cybersecurity Analyst & Engineer',
      companyTier: savedUser.companyTier || career.companyTier || 'Tier-1 Product (MAANG / Unicorns)',
      githubHandle: savedUser.githubHandle || integrations.githubHandle || '',
      leetcodeHandle: savedUser.leetcodeHandle || integrations.leetcodeHandle || '',
      resumeFileName: savedUser.resumeFileName || integrations.resumeFileName || sResume || '',
      overallReadinessScore: savedUser.overallReadinessScore || 78,
      dsaLevel: savedUser.dsaLevel || skills.dsaLevel || 'Beginner',
      selectedSkills: savedUser.selectedSkills || skills.selectedSkills || ['Java', 'Spring Boot', 'Data Structures', 'SQL'],
      mentorTone: savedUser.mentorTone || preferences.mentorTone || 'Socratic Coach',
      dailyGoalMinutes: savedUser.dailyGoalMinutes || preferences.dailyGoalMinutes || '90',
      targetDrive: savedUser.targetDrive || goals.targetDrive || 'August 2026',
      targetCtc: savedUser.targetCtc || goals.targetCtc || '14 - 24 LPA (Product Tier)',
      streakDays: savedUser.streakDays !== undefined ? savedUser.streakDays : 0
    };
  });

  useEffect(() => {
    const fetchApiProfile = async () => {
      const activeUser = authService.getCurrentUser();
      if (activeUser) {
        setUser(prev => ({
          ...prev,
          ...activeUser,
          name: prev.name || activeUser.name || activeUser.full_name || 'Student Candidate'
        }));

        const apiProfile = await profileService.getProfileFromApi();
        if (apiProfile) {
          setUser(prev => ({
            ...prev,
            ...apiProfile,
            name: apiProfile.full_name || apiProfile.name || prev.name,
            targetRole: apiProfile.target_role || apiProfile.targetRole || prev.targetRole,
            college: apiProfile.college || prev.college,
            degree: apiProfile.degree || prev.degree,
            graduationYear: apiProfile.graduation_year || apiProfile.graduationYear || prev.graduationYear,
            githubHandle: apiProfile.github_username || apiProfile.githubHandle || prev.githubHandle,
            leetcodeHandle: apiProfile.leetcode_username || apiProfile.leetcodeHandle || prev.leetcodeHandle,
          }));
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
      profileService.updateProfileInApi(updated).catch(() => {});
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
