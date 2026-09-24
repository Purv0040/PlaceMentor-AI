import React, { createContext, useContext, useState, useEffect } from 'react';
import { planningService } from '../services/planningService';

const PlanningContext = createContext();

export const PlanningProvider = ({ children }) => {
  const [planningState, setPlanningState] = useState(() => planningService.getInitialState());
  const [toastNotification, setToastNotification] = useState(null);

  useEffect(() => {
    planningService.saveState(planningState);
  }, [planningState]);

  const showToast = (message) => {
    setToastNotification(message);
    setTimeout(() => setToastNotification(null), 3000);
  };

  const toggleTaskCompletion = (taskId) => {
    setPlanningState((prevState) => {
      const updatedTasks = prevState.tasks.map((t) =>
        t.id === taskId ? { ...t, completed: !t.completed } : t
      );

      const completedCount = updatedTasks.filter((t) => t.completed).length;
      const totalCount = updatedTasks.length;
      const completionPercent = Math.round((completedCount / totalCount) * 100);

      const updatedProgress = {
        ...prevState.progress,
        completedTasksCount: completedCount,
        totalTasksCount: totalCount,
        overallProgressPercent: Math.round(60 + (completedCount * 2)),
      };

      const targetTask = prevState.tasks.find((t) => t.id === taskId);
      const isCompleted = targetTask ? !targetTask.completed : false;
      showToast(isCompleted ? `Task completed! (+1 task)` : `Task marked in-complete`);

      return {
        ...prevState,
        tasks: updatedTasks,
        progress: updatedProgress,
      };
    });
  };

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
      dayNumber: 35,
      phaseId: 'phase-2',
      route: skillItem.actionRoute || '/roadmap'
    };

    setPlanningState((prevState) => {
      const updatedTasks = [newTask, ...prevState.tasks];
      const updatedRoadmap = {
        ...prevState.roadmap,
        lastAdapted: 'Just now (Skill Gap Added)',
        adaptiveRebalancingNotice: {
          isAdapted: true,
          reason: `Added "${skillItem.skill}" to Day 35 active execution matrix.`,
          adaptedAt: 'Just now',
          adjustments: [
            `Inserted task "${newTask.title}" into Sprint 5 schedule.`,
            `Prioritized ${skillItem.priority || 'High'} level remediation for target role readiness.`
          ]
        }
      };

      return {
        ...prevState,
        tasks: updatedTasks,
        roadmap: updatedRoadmap,
      };
    });

    showToast(`Added "${skillItem.skill}" to 90-Day Roadmap (Day 35)!`);
  };

  const adaptRoadmap = async () => {
    const updatedRoadmap = await planningService.adaptRoadmap(
      planningState.roadmap,
      planningState.tasks
    );
    setPlanningState((prev) => ({
      ...prev,
      roadmap: updatedRoadmap,
    }));
    showToast('Roadmap schedule re-balanced with AI Copilot!');
  };

  return (
    <PlanningContext.Provider
      value={{
        roadmap: planningState.roadmap,
        tasks: planningState.tasks,
        progress: planningState.progress,
        toggleTaskCompletion,
        addSkillToRoadmap,
        adaptRoadmap,
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
