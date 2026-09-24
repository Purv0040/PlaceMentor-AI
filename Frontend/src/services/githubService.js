// Mock service for GitHub Intelligence

import { initialGithubData } from "../data/githubData";

export const githubService = {
  getProfile: async () => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(initialGithubData);
      }, 300);
    });
  },

  syncProfile: async (handle) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          ...initialGithubData,
          handle: handle || initialGithubData.handle,
          lastSynced: "Just now",
          metrics: {
            ...initialGithubData.metrics,
            totalCommits: initialGithubData.metrics.totalCommits + 5,
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
