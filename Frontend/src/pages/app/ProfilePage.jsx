import React, { useState } from 'react';
import { useUser } from '../../context/UserContext';
import { useOnboarding } from '../../context/OnboardingContext';
import { profileService } from '../../services/profileService';
import { ProfileHeader } from '../../components/profile/ProfileHeader';
import { ProfileForm } from '../../components/profile/ProfileForm';

export const ProfilePage = () => {
  const { user, updateUserProfile } = useUser();
  const { onboardingData } = useOnboarding();
  const [isEditing, setIsEditing] = useState(false);

  const [profile, setProfile] = useState(() =>
    profileService.getProfile(user, onboardingData)
  );

  const completionPercent = profileService.calculateProfileCompletion(profile);

  const handleSaveProfile = (updatedData) => {
    setProfile(updatedData);
    profileService.saveProfile(updatedData);

    // Sync with UserContext
    if (updateUserProfile) {
      updateUserProfile({
        name: updatedData.name,
        targetRole: updatedData.targetRole,
        college: updatedData.college,
        degree: updatedData.degree,
        graduationYear: updatedData.graduationYear,
        githubHandle: updatedData.githubHandle,
        leetcodeHandle: updatedData.leetcodeHandle
      });
    }

    setIsEditing(false);
  };

  return (
    <div className="w-full min-h-[calc(100vh-5rem)] bg-[#0f131d] text-slate-100 space-y-6 pb-12">
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
      />
    </div>
  );
};
