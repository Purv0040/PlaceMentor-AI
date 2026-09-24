import React, { useState } from 'react';
import { settingsService } from '../../services/settingsService';
import { SettingsHeader } from '../../components/settings/SettingsHeader';
import { SettingsSection } from '../../components/settings/SettingsSection';

export const SettingsPage = () => {
  const [settings, setSettings] = useState(() => settingsService.getSettings());
  const [isSaved, setIsSaved] = useState(false);

  const handleUpdateSettings = (updatedPartial) => {
    setSettings((prev) => {
      const nextState = {
        ...prev,
        ...updatedPartial,
        // Merge nested sections
        placement: { ...prev.placement, ...(updatedPartial.placement || {}) },
        ai: { ...prev.ai, ...(updatedPartial.ai || {}) },
        mentor: { ...prev.mentor, ...(updatedPartial.mentor || {}) },
        notifications: { ...prev.notifications, ...(updatedPartial.notifications || {}) },
        privacy: { ...prev.privacy, ...(updatedPartial.privacy || {}) },
        integrations: { ...prev.integrations, ...(updatedPartial.integrations || {}) }
      };
      settingsService.saveSettings(nextState);
      return nextState;
    });
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 2500);
  };

  const handleSaveAll = () => {
    settingsService.saveSettings(settings);
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 2500);
  };

  const handleDiscard = () => {
    const original = settingsService.getSettings();
    setSettings(original);
  };

  const handleResetAll = () => {
    const reset = settingsService.resetSettings();
    setSettings(reset);
  };

  return (
    <div className="w-full min-h-[calc(100vh-5rem)] bg-[#0f131d] text-slate-100 space-y-6 pb-12">
      {/* Header */}
      <SettingsHeader
        onSaveAll={handleSaveAll}
        onDiscard={handleDiscard}
        isSaved={isSaved}
      />

      {/* Settings Tabbed Navigation & Content Panels */}
      <SettingsSection
        settings={settings}
        onUpdateSettings={handleUpdateSettings}
        onResetAll={handleResetAll}
      />
    </div>
  );
};
