import React, { useState, useEffect } from 'react';
import { useUser } from '../../context/UserContext';
import { useOnboarding } from '../../context/OnboardingContext';
import { profileService } from '../../services/profileService';
import { ProfileHeader } from '../../components/profile/ProfileHeader';
import { ProfileForm } from '../../components/profile/ProfileForm';

export const ProfilePage = () => {
  const { user, updateUserProfile } = useUser();
  const { onboardingData } = useOnboarding();
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);
  const [toastType, setToastType] = useState('success');

  // Initialize with local fallback then hydrate with real MongoDB profile
  const [profile, setProfile] = useState(() =>
    profileService.getProfile(user, onboardingData)
  );

  useEffect(() => {
    let isMounted = true;

    const loadRealUserProfile = async () => {
      setIsLoading(true);
      try {
        const apiData = await profileService.getProfileFromApi();
        if (apiData && isMounted) {
          const formatted = profileService.formatFromApi(apiData);
          setProfile(formatted);
          profileService.saveProfile(formatted);
        } else if (isMounted) {
          // If API returns null/offline, fall back to Context
          const localData = profileService.getProfile(user, onboardingData);
          setProfile(localData);
        }
      } catch (err) {
        console.warn('Error loading real profile data from database:', err);
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };

    loadRealUserProfile();

    return () => {
      isMounted = false;
    };
  }, []);

  const completionPercent = profileService.calculateCompletion(profile);

  const showToast = (message, type = 'success') => {
    setToastMessage(message);
    setToastType(type);
    setTimeout(() => setToastMessage(null), 4000);
  };

  const handleSaveProfile = async (updatedData) => {
    setIsSaving(true);
    setProfile(updatedData);
    profileService.saveProfile(updatedData);

    try {
      // 1. Prepare structured database payload
      const payload = profileService.buildApiPayload(updatedData);

      // 2. Persist to MongoDB backend
      const res = await profileService.updateProfileInApi(payload);

      if (res) {
        showToast('Profile successfully synchronized with MongoDB database!', 'success');
      } else {
        showToast('Profile saved locally. (Backend syncing will resume when online)', 'info');
      }

      // 3. Sync with UserContext
      if (updateUserProfile) {
        updateUserProfile({
          name: updatedData.name,
          email: updatedData.email,
          targetRole: updatedData.targetRole,
          secondaryRole: updatedData.secondaryRole,
          companyTier: updatedData.companyTier,
          college: updatedData.college,
          degree: updatedData.degree,
          branch: updatedData.branch,
          graduationYear: updatedData.graduationYear,
          cgpa: updatedData.cgpa,
          phone: updatedData.phone,
          location: updatedData.location,
          bio: updatedData.bio,
          linkedinUrl: updatedData.linkedinUrl,
          portfolioUrl: updatedData.portfolioUrl,
          githubHandle: updatedData.githubHandle,
          leetcodeHandle: updatedData.leetcodeHandle,
          selectedSkills: updatedData.skills,
          dailyGoalMinutes: updatedData.dailyGoalMinutes,
          targetCtc: updatedData.targetCtc,
          targetDrive: updatedData.targetDrive
        });
      }

      setIsEditing(false);
    } catch (err) {
      console.error('Error saving profile changes:', err);
      showToast('Error saving changes to database: ' + err.message, 'error');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="profile-page w-full min-h-[calc(100vh-5rem)] bg-[#0f131d] text-slate-100 space-y-6 pb-12">
      {/* Toast Notification Banner */}
      {toastMessage && (
        <div
          className={`p-3.5 rounded-xl border text-xs font-mono flex items-center justify-between gap-2 shadow-lg transition-all animate-fade-in ${
            toastType === 'success'
              ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
              : toastType === 'error'
              ? 'bg-rose-500/10 border-rose-500/30 text-rose-400'
              : 'bg-indigo-500/10 border-indigo-500/30 text-indigo-300'
          }`}
        >
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-base">
              {toastType === 'success' ? 'check_circle' : toastType === 'error' ? 'error' : 'info'}
            </span>
            <span>{toastMessage}</span>
          </div>
          <button
            type="button"
            onClick={() => setToastMessage(null)}
            className="text-slate-400 hover:text-white"
          >
            ×
          </button>
        </div>
      )}

      {/* Loading state skeleton */}
      {isLoading ? (
        <div className="p-12 rounded-2xl bg-[#171b26] border border-[#262a35] flex flex-col items-center justify-center gap-3">
          <span className="w-8 h-8 border-3 border-indigo-500 border-t-transparent rounded-full animate-spin"></span>
          <p className="text-xs text-slate-400 font-mono">Fetching student profile from database...</p>
        </div>
      ) : (
        <>
          {/* 1. Profile Banner Header */}
          <ProfileHeader
            profile={profile}
            completionPercent={completionPercent}
            isEditing={isEditing}
            onToggleEdit={() => setIsEditing((prev) => !prev)}
          />

          {/* 2. Profile View/Edit Form */}
          <ProfileForm
            profile={profile}
            isEditing={isEditing}
            onSave={handleSaveProfile}
            onCancel={() => setIsEditing(false)}
            isSaving={isSaving}
          />
        </>
      )}
    </div>
  );
};
