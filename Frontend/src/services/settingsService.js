// Settings Service for managing user & system configurations

const SETTINGS_STORAGE_KEY = 'placementCopilotSettings';

const defaultSettings = {
  placement: {
    targetRole: 'Backend Developer',
    companyTier: 'Tier-1 Product (MAANG / Unicorns)',
    targetCtc: '14 - 24 LPA (Product Tier)',
    targetDrive: 'August 2026 (Campus Phase 1)'
  },
  ai: {
    probingDensity: 'High (70%)',
    socraticStrictness: 'Enabled',
    telemetryWeights: 'DSA: 25%, SysDesign: 20%, Projects: 20%, Fundamentals: 15%',
    autoCommitSync: 'Enabled (Every 6 Hours)',
    maxPromptTokens: 1480
  },
  mentor: {
    defaultPersona: 'tech',
    mentorTone: 'Socratic Coach (Probing Questions)',
    codeLanguagePreference: 'C++ / Python'
  },
  notifications: {
    emailNotifications: true,
    taskReminders: true,
    achievementNotifications: true,
    mentorNotifications: true,
    weeklyProgressSummary: true
  },
  privacy: {
    localTelemetryMode: 'Strict (Local Storage Only)',
    anonymizedMetrics: false
  },
  integrations: {
    githubConnected: true,
    leetcodeConnected: true,
    googleDriveSync: true
  }
};

export const settingsService = {
  getSettings: () => {
    try {
      const saved = localStorage.getItem(SETTINGS_STORAGE_KEY);
      if (saved) {
        return { ...defaultSettings, ...JSON.parse(saved) };
      }
    } catch (e) {
      console.error('Failed to parse settings from localStorage', e);
    }
    return defaultSettings;
  },

  saveSettings: (newSettings) => {
    try {
      localStorage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(newSettings));
    } catch (e) {
      console.error('Failed to save settings to localStorage', e);
    }
  },

  resetSettings: () => {
    try {
      localStorage.removeItem(SETTINGS_STORAGE_KEY);
    } catch (e) {
      console.error('Failed to reset settings in localStorage', e);
    }
    return defaultSettings;
  }
};
