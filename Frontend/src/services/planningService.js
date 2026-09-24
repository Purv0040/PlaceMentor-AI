// Service layer for Planning, Tasks, Roadmap, and Progress calculation

import { initialRoadmapData } from "../data/roadmapData";
import { initialTaskData } from "../data/taskData";
import { initialProgressData } from "../data/progressData";

const STORAGE_KEY = "placementor_planning_state";

export const planningService = {
  getInitialState: () => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        return JSON.parse(stored);
      }
    } catch (e) {
      console.error("Failed to parse stored planning state", e);
    }
    return {
      roadmap: initialRoadmapData,
      tasks: initialTaskData,
      progress: initialProgressData,
    };
  },

  saveState: (state) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
      console.error("Failed to persist planning state", e);
    }
  },

  adaptRoadmap: async (currentRoadmap, currentTasks) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          ...currentRoadmap,
          lastAdapted: "Just now (Telemetry Adapted)",
          adaptiveRebalancingNotice: {
            isAdapted: true,
            reason: "AI Copilot re-balanced Day 34-40 schedule based on active task completion velocity.",
            adaptedAt: "Just now",
            adjustments: [
              "Optimized DP practice schedule for Day 36-38.",
              "Synchronized Redis caching tasks with Project Intelligence audit."
            ]
          }
        });
      }, 700);
    });
  }
};
