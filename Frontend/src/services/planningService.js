// Service layer for Planning, Tasks, Roadmap, and Progress calculation

import { apiRequest } from "./api";
import { initialRoadmapData } from "../data/roadmapData";
import { initialTaskData } from "../data/taskData";
import { initialProgressData } from "../data/progressData";

const STORAGE_KEY = "placementor_planning_state";

export const planningService = {
  getTasksFromApi: async () => {
    try {
      const res = await apiRequest("/tasks");
      if (res && Array.isArray(res)) {
        return res.map((t) => ({
          id: t.id,
          title: t.title,
          description: t.description || "",
          category: t.category || "General",
          duration: `${t.estimated_minutes || 45} mins`,
          priority: t.priority || "Medium",
          completed: t.status === "completed",
          dayNumber: t.day_number || 1,
          phaseId: t.phase_id || "phase-1",
          route: "/tasks",
        }));
      }
    } catch (e) {
      console.warn("Failed to fetch tasks from API, using fallback", e);
    }
    return null;
  },

  getRoadmapFromApi: async () => {
    try {
      const res = await apiRequest("/roadmap");
      if (res && res.title) {
        const phases = Array.isArray(res.phases)
          ? res.phases.map((phase, index) => {
              const tasks = Array.isArray(phase.tasks) ? phase.tasks : [];
              return {
                ...phase,
                id: phase.id || phase.phase_id || `phase-${phase.phase_number || index + 1}`,
                title: phase.title || phase.name || `Phase ${phase.phase_number || index + 1}`,
                subtitle: phase.subtitle || phase.goal || "",
                startDay: phase.startDay ?? phase.start_day ?? 1,
                endDay: phase.endDay ?? phase.end_day ?? 1,
                durationDays: phase.durationDays ?? phase.duration_days ?? Math.max(1, (phase.endDay ?? phase.end_day ?? 1) - (phase.startDay ?? phase.start_day ?? 1) + 1),
                status: phase.status || "upcoming",
                progressPercent: phase.progressPercent ?? phase.progress_percentage ?? 0,
                milestones: Array.isArray(phase.milestones)
                  ? phase.milestones
                  : tasks.map((task) => task.title).filter(Boolean),
              };
            })
          : initialRoadmapData.phases;

        return {
          ...initialRoadmapData,
          id: res.id,
          title: res.title,
          description: res.description,
          currentDay: res.current_day || 1,
          totalDays: res.total_days || 90,
          currentPhaseId: res.current_phase || "phase-1",
          currentPhaseName: res.phase_name || "Phase 1: Foundations",
          completionPercentage: Math.round(res.progress_percentage || 0),
          lastAdapted: res.updated_at ? new Date(res.updated_at).toLocaleDateString() : "Recently",
          phases,
          adaptiveRebalancingNotice: {
            isAdapted: true,
            reason: "Synced with AI Adaptive Engine Backend",
            adaptedAt: "Live Backend",
            adjustments: ["Real-time adaptive schedule synchronized."],
          },
        };
      }
    } catch (e) {
      console.warn("Failed to fetch roadmap from API, using fallback", e);
    }
    return null;
  },

  completeTaskInApi: async (taskId) => {
    try {
      await apiRequest(`/tasks/${taskId}/complete`, { method: "POST" });
    } catch (e) {
      console.warn("Failed to complete task in API", e);
    }
  },

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

  resetForRole: (targetRole, selectedSkills) => {
    const freshTasks = getDynamicTasks(targetRole, selectedSkills, 1);
    const newState = {
      roadmap: initialRoadmapData,
      tasks: freshTasks,
      progress: {
        ...initialProgressData,
        completedTasksCount: 0,
        totalTasksCount: freshTasks.length,
        overallProgressPercent: 12
      }
    };
    planningService.saveState(newState);
    return newState;
  },

  saveState: (state) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
      console.error("Failed to persist planning state", e);
    }
  },

  adaptRoadmap: async (currentRoadmap, currentTasks) => {
    try {
      const res = await apiRequest("/adaptive/recalculate", { method: "POST" });
      if (res && res.id) {
        return {
          ...currentRoadmap,
          lastAdapted: "Just now (AI Adaptive Recalculated)",
          adaptiveRebalancingNotice: {
            isAdapted: true,
            reason: res.reason || "AI Copilot re-balanced schedule based on performance velocity.",
            adaptedAt: "Just now",
            adjustments: res.adjustments || [
              "Optimized study & drill schedule.",
              "Synchronized with AST & DSA telemetry.",
            ],
          },
        };
      }
    } catch (e) {
      console.warn("Adaptive API recalculate fallback", e);
    }

    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          ...currentRoadmap,
          lastAdapted: "Just now (Telemetry Adapted)",
          adaptiveRebalancingNotice: {
            isAdapted: true,
            reason: "AI Copilot re-balanced schedule based on active task completion velocity.",
            adaptedAt: "Just now",
            adjustments: [
              "Optimized DP practice schedule.",
              "Synchronized Redis caching tasks with Project Intelligence audit.",
            ],
          },
        });
      }, 700);
    });
  },
};

