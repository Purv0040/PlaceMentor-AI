// Service layer for Planning, Tasks, Roadmap, and Progress calculation

import { apiRequest } from "./api";
import { initialRoadmapData } from "../data/roadmapData";
import { getDynamicTasks, initialTaskData } from "../data/taskData";
import { initialProgressData } from "../data/progressData";

const STORAGE_KEY = "placementor_planning_state";

export const planningService = {
  getTasksFromApi: async () => {
    try {
      const res = await apiRequest("/tasks");
      if (Array.isArray(res)) {
        return res.map((t) => ({
          id: t.id || t.task_id,
          taskId: t.task_id || t.id,
          roadmapId: t.roadmap_id || null,
          title: t.title,
          description: t.description || "",
          category: t.category || "General",
          duration: t.estimated_minutes != null ? `${t.estimated_minutes} min` : null,
          priority: t.priority || "Medium",
          difficulty: t.difficulty || "Intermediate",
          skill: t.skill || "",
          estimatedMinutes: t.estimated_minutes != null ? t.estimated_minutes : 60,
          status: t.status || "pending",
          completed: t.status === "completed",
          completedAt: t.completed_at || null,
          dayNumber: t.day_number ?? null,
          phaseNumber: t.phase_number ?? null,
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
              const startDay = phase.start_day ?? phase.startDay ?? null;
              const endDay = phase.end_day ?? phase.endDay ?? null;
              return {
                ...phase,
                id: `phase-${phase.phase_number || index + 1}`,
                phaseNumber: phase.phase_number || index + 1,
                title: ["Foundation", "Skill Development", "Placement Preparation"][index] || phase.name,
                sourceTitle: phase.name || phase.title || "",
                subtitle: phase.subtitle || phase.goal || "",
                startDay,
                endDay,
                durationDays: startDay != null && endDay != null ? endDay - startDay + 1 : null,
                status: phase.status || "upcoming",
                tasks,
              };
            })
          : [];

        return {
          id: res.id,
          roadmapId: res.roadmap_id,
          title: res.title,
          targetRole: res.target_role,
          description: res.description,
          currentDay: null,
          totalDays: res.duration_days ?? res.total_days ?? 90,
          availableMinutesPerDay: res.available_minutes_per_day ?? 120,
          currentPhaseId: null,
          currentPhaseName: null,
          overallProgressPercent: null,
          lastAdapted: res.updated_at || null,
          phases,
          allTasks: Array.isArray(res.all_tasks) ? res.all_tasks : [],
          startDate: res.start_date,
        };
      }
    } catch (e) {
      console.warn("Failed to fetch roadmap from API, using fallback", e);
    }
    return null;
  },

  generateCustomRoadmap: async ({
    targetRole,
    durationDays = 90,
    dailyMinutes = 60,
    replaceExisting = true,
  } = {}) => {
    try {
      const payload = {
        force_regenerate: true,
        replace_existing: replaceExisting,
      };
      if (targetRole) payload.target_role = targetRole;
      if (durationDays) payload.duration_days = Number(durationDays);
      if (dailyMinutes) payload.available_minutes_per_day = Number(dailyMinutes);

      const res = await apiRequest("/roadmap/generate", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      return res;
    } catch (e) {
      console.error("Failed to generate custom roadmap", e);
      throw e;
    }
  },

  getRoadmapSummaryFromApi: async () => {
    try {
      return await apiRequest("/roadmap/summary");
    } catch (e) {
      console.warn("Failed to fetch roadmap summary", e);
      return null;
    }
  },

  updateTaskStatusInApi: async (taskId, status) => {
    try {
      return await apiRequest(`/tasks/${encodeURIComponent(taskId)}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      });
    } catch (e) {
      console.warn("Failed to update task status in API", e);
      return null;
    }
  },

  getTaskProgressFromApi: async () => {
    try {
      return await apiRequest("/tasks/progress");
    } catch (e) {
      console.warn("Failed to refresh task progress", e);
      return null;
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
    const res = await apiRequest("/adaptive/recalculate", {
      method: "POST",
      body: JSON.stringify({ roadmap_id: currentRoadmap?.roadmapId }),
    });
    if (!res?.id) throw new Error("Roadmap recalibration failed.");
    return {
      ...currentRoadmap,
      lastAdapted: res.created_at || new Date().toISOString(),
      adaptationReason: res.reason,
    };
  },
};

