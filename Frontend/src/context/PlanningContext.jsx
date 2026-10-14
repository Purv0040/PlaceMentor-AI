import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { planningService } from '../services/planningService';
import { authService } from '../services/authService';

const PlanningContext = createContext();

const mergeTaskProgress = (current, apiProgress) => apiProgress ? {
  ...current,
  overallProgressPercent: apiProgress.roadmap_completion_percentage ?? current.overallProgressPercent,
  completedTasksCount: apiProgress.completed_tasks ?? current.completedTasksCount,
  totalTasksCount: apiProgress.total_tasks ?? current.totalTasksCount,
  currentStreakDays: apiProgress.current_streak ?? current.currentStreakDays,
  longestStreakDays: apiProgress.longest_streak ?? current.longestStreakDays,
} : current;

export const PlanningProvider = ({ children }) => {
  const [planningState, setPlanningState] = useState(() => planningService.getInitialState());
  const [toastNotification, setToastNotification] = useState(null);
  const [planningLoading, setPlanningLoading] = useState(() => authService.isAuthenticated());
  const [planningError, setPlanningError] = useState(null);

  useEffect(() => {
    planningService.saveState(planningState);
  }, [planningState]);

  const showToast = (message) => {
    setToastNotification(message);
    window.setTimeout(() => setToastNotification(null), 3000);
  };

  const loadApiPlanning = useCallback(async () => {
    if (!authService.isAuthenticated()) {
      setPlanningLoading(false);
      setPlanningError('Sign in to view your roadmap.');
      return;
    }

    setPlanningLoading(true);
    setPlanningError(null);
    const apiRoadmap = await planningService.getRoadmapFromApi();
    const [apiTasks, roadmapSummary, taskProgress] = await Promise.all([
        planningService.getTasksFromApi(),
        planningService.getRoadmapSummaryFromApi(),
        planningService.getTaskProgressFromApi(),
    ]);

    const activeTasks = Array.isArray(apiTasks)
      ? apiTasks.filter((task) => !apiRoadmap?.roadmapId || task.roadmapId === apiRoadmap.roadmapId)
      : null;
    const phases = apiRoadmap?.phases || [];
    const currentDay = Number(roadmapSummary?.current_day) || null;
    const currentPhase = phases.find((phase) => currentDay && currentDay >= phase.startDay && currentDay <= phase.endDay);

    if (apiTasks && apiRoadmap && roadmapSummary) {
      const taskTotal = activeTasks ? activeTasks.length : 0;
      const taskCompleted = activeTasks ? activeTasks.filter((t) => t.completed || t.status === 'completed').length : 0;
      const computedTaskPercent = taskTotal > 0 ? Math.round((taskCompleted / taskTotal) * 100) : 0;
      const apiPercent = Number(roadmapSummary.roadmap_completion_percentage ?? roadmapSummary.progress_percentage);
      const finalPercent = (!isNaN(apiPercent) && apiPercent > 0) ? apiPercent : computedTaskPercent;

      setPlanningState((prev) => ({
        ...prev,
        tasks: activeTasks,
        roadmap: {
          ...apiRoadmap,
          currentDay,
          currentPhaseId: currentPhase?.id || null,
          currentPhaseName: roadmapSummary.current_phase_name || currentPhase?.title || null,
          overallProgressPercent: finalPercent,
        },
        progress: mergeTaskProgress(
          {
            ...prev.progress,
            totalTasksCount: taskTotal,
            completedTasksCount: taskCompleted,
            overallProgressPercent: finalPercent,
          },
          taskProgress
        ),
      }));
      setPlanningError(null);
    } else {
      setPlanningError('Your roadmap could not be loaded. Check your connection and try again.');
    }
    setPlanningLoading(false);
  }, []);

  useEffect(() => {
    loadApiPlanning();
  }, [loadApiPlanning]);

  const toggleTaskCompletion = async (taskId) => {
    const targetTask = planningState.tasks?.find((task) => task.id === taskId || task.taskId === taskId);
    if (!targetTask) return;

    const nextStatus = targetTask.completed ? 'pending' : 'completed';
    const isCompleted = nextStatus === 'completed';

    // 1. Optimistic update of tasks AND overall progress metrics immediately
    setPlanningState((prevState) => {
      const nextTasks = prevState.tasks.map((task) =>
        (task.id === targetTask.id || (targetTask.taskId && task.taskId === targetTask.taskId))
          ? {
              ...task,
              status: nextStatus,
              completed: isCompleted,
              completedAt: isCompleted ? (task.completedAt || new Date().toISOString()) : null,
            }
          : task
      );

      const totalCount = nextTasks.length;
      const completedCount = nextTasks.filter((t) => t.completed || t.status === 'completed').length;
      const computedPercent = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

      return {
        ...prevState,
        tasks: nextTasks,
        roadmap: {
          ...prevState.roadmap,
          overallProgressPercent: computedPercent,
        },
        progress: {
          ...prevState.progress,
          completedTasksCount: completedCount,
          totalTasksCount: totalCount,
          overallProgressPercent: computedPercent,
        },
      };
    });

    showToast(isCompleted ? 'Task completed.' : 'Task reopened.');

    const backendId = targetTask.taskId || targetTask.id;
    const isLocalTask = !backendId || String(backendId).startsWith('task-skill-');
    if (!isLocalTask) {
      try {
        const response = await planningService.updateTaskStatusInApi(backendId, nextStatus);
        if (response) {
          const [roadmapSummary, taskProgress] = await Promise.all([
            planningService.getRoadmapSummaryFromApi(),
            planningService.getTaskProgressFromApi(),
          ]);

          setPlanningState((prev) => {
            const total = prev.tasks?.length || 0;
            const comp = prev.tasks?.filter((t) => t.completed || t.status === 'completed').length || 0;
            const fallbackPercent = total > 0 ? Math.round((comp / total) * 100) : 0;
            const apiPercent = roadmapSummary
              ? Number(roadmapSummary.roadmap_completion_percentage ?? roadmapSummary.progress_percentage)
              : null;
            const finalPercent = (apiPercent != null && !isNaN(apiPercent)) ? apiPercent : fallbackPercent;

            return {
              ...prev,
              roadmap: roadmapSummary ? {
                ...prev.roadmap,
                currentDay: Number(roadmapSummary.current_day) || prev.roadmap.currentDay,
                currentPhaseName: roadmapSummary.current_phase_name || prev.roadmap.currentPhaseName,
                overallProgressPercent: finalPercent,
              } : {
                ...prev.roadmap,
                overallProgressPercent: fallbackPercent,
              },
              progress: mergeTaskProgress(prev.progress, taskProgress),
            };
          });
        }
      } catch (err) {
        console.warn('Background sync for task status update failed:', err);
      }
    }
  };

  /*
   * Keep existing task-add behavior available to other pages; the roadmap view
   * itself only displays tasks returned by the authenticated API.
   */
  const addSkillToRoadmap = (skillItem) => {
    const newTaskId = `task-skill-${Date.now()}`;
    const newTask = {
      id: newTaskId,
      title: `Practice & Remediate: ${skillItem.skill}`,
      description: skillItem.reason || `Remediation task added from AI Skill Gap Analyzer for ${skillItem.skill}.`,
      category: skillItem.category ? skillItem.category.split('/')[0].trim() : 'System Design',
      duration: '45 mins',
      priority: skillItem.priority || 'High',
      completed: false,
      status: 'pending',
      dayNumber: (planningState.roadmap.currentDay || 1) + 1,
      route: skillItem.actionRoute || '/roadmap'
    };

    setPlanningState((prevState) => ({ ...prevState, tasks: [newTask, ...prevState.tasks] }));
    showToast(`Added "${skillItem.skill}" to your roadmap.`);
  };

  const adaptRoadmap = async () => {
    try {
      const updatedRoadmap = await planningService.adaptRoadmap(
        planningState.roadmap,
        planningState.tasks
      );
      setPlanningState((prev) => ({ ...prev, roadmap: updatedRoadmap }));
      showToast(updatedRoadmap.adaptationReason || 'Roadmap recalibrated.');
      return true;
    } catch (error) {
      showToast(error.message || 'Roadmap recalibration failed.');
      return false;
    }
  };

  const generateCustomRoadmap = async ({ targetRole, durationDays, dailyMinutes }) => {
    try {
      setPlanningLoading(true);
      await planningService.generateCustomRoadmap({
        targetRole,
        durationDays,
        dailyMinutes,
        replaceExisting: true,
      });
      await loadApiPlanning();
      showToast(`Personalized ${durationDays || 90}-day roadmap generated successfully!`);
      return true;
    } catch (error) {
      showToast(error.message || 'Failed to generate roadmap.');
      setPlanningLoading(false);
      return false;
    }
  };

  return (
    <PlanningContext.Provider
      value={{
        roadmap: planningState.roadmap,
        tasks: planningState.tasks,
        progress: planningState.progress,
        planningLoading,
        planningError,
        reloadPlanning: loadApiPlanning,
        toggleTaskCompletion,
        addSkillToRoadmap,
        adaptRoadmap,
        generateCustomRoadmap,
        toastNotification,
      }}
    >
      {children}
    </PlanningContext.Provider>
  );
};

export const usePlanning = () => {
  const context = useContext(PlanningContext);
  if (!context) {
    throw new Error('usePlanning must be used within a PlanningProvider');
  }
  return context;
};
