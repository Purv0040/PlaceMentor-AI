// Mock service for LeetCode Intelligence

import { initialLeetcodeData } from "../data/leetcodeData";

export const leetcodeService = {
  getProfile: async () => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(initialLeetcodeData);
      }, 300);
    });
  },

  syncProfile: async (handle) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          ...initialLeetcodeData,
          handle: handle || initialLeetcodeData.handle,
          lastSynced: "Just now",
          metrics: {
            ...initialLeetcodeData.metrics,
            totalSolved: initialLeetcodeData.metrics.totalSolved + 1,
            currentStreakDays: initialLeetcodeData.metrics.currentStreakDays + 1
          }
        });
      }, 900);
    });
  },

  toggleConnection: async (currentState) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(!currentState);
      }, 400);
    });
  }
};
