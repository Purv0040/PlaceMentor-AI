import React, { useState, useMemo } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { Check, Clock, ArrowRight, Loader2, CalendarCheck2, AlertCircle } from 'lucide-react';
import { usePlanning } from '../../context/PlanningContext';

export const ActionPlanList = ({ maxItems = 3, onTaskCompleted }) => {
  const { roadmap, tasks, toggleTaskCompletion, planningLoading, planningError } = usePlanning();
  const [updatingTaskId, setUpdatingTaskId] = useState(null);
  const navigate = useNavigate();

  // Helper to extract day number from task
  const getTaskDayNumber = (t) => {
    if (!t) return 999;
    if (t.dayNumber != null && !isNaN(Number(t.dayNumber))) return Number(t.dayNumber);
    if (t.day_number != null && !isNaN(Number(t.day_number))) return Number(t.day_number);
    if (t.day != null && !isNaN(Number(t.day))) return Number(t.day);
    if (typeof t.title === 'string') {
      const match = t.title.match(/\bDay\s+(\d+)\b/i);
      if (match) return parseInt(match[1], 10);
    }
    return 999;
  };

  // Prioritize today's tasks first, then upcoming tasks chronologically, then completed tasks
  const prioritizedTasks = useMemo(() => {
    if (!tasks || !Array.isArray(tasks)) return [];

    const pending = tasks.filter((t) => !t.completed && t.status !== 'completed');
    const completed = tasks.filter((t) => t.completed || t.status === 'completed');

    const activeDay = Number(roadmap?.currentDay) || null;
    const pendingDays = pending.map(getTaskDayNumber).filter((d) => d < 999);
    const effectiveCurrentDay = activeDay || (pendingDays.length > 0 ? Math.min(...pendingDays) : 1);

    const sortedPending = [...pending].sort((a, b) => {
      const dayA = getTaskDayNumber(a);
      const dayB = getTaskDayNumber(b);

      // 1. Prioritize tasks specifically belonging to today's active day
      const isTodayA = dayA === effectiveCurrentDay;
      const isTodayB = dayB === effectiveCurrentDay;
      if (isTodayA && !isTodayB) return -1;
      if (!isTodayA && isTodayB) return 1;

      // 2. Strict chronological order (Day 21 always comes before Day 22)
      if (dayA !== dayB) {
        return dayA - dayB;
      }

      // 3. Priority tier (Critical > High > Medium > Low)
      const priorityWeight = { critical: 4, high: 3, medium: 2, low: 1 };
      const pA = priorityWeight[String(a.priority).toLowerCase()] || 2;
      const pB = priorityWeight[String(b.priority).toLowerCase()] || 2;
      if (pA !== pB) return pB - pA;

      return 0;
    });

    const sortedCompleted = [...completed].sort((a, b) => {
      const dayA = getTaskDayNumber(a);
      const dayB = getTaskDayNumber(b);
      return dayA - dayB;
    });

    return [...sortedPending, ...sortedCompleted];
  }, [tasks, roadmap?.currentDay]);

  const activeDay = Number(roadmap?.currentDay) || null;
  const pendingDays = (tasks || [])
    .filter((t) => !t.completed && t.status !== 'completed')
    .map(getTaskDayNumber)
    .filter((d) => d < 999);
  const effectiveCurrentDay = activeDay || (pendingDays.length > 0 ? Math.min(...pendingDays) : 1);

  const displayTasks = prioritizedTasks.slice(0, maxItems);

  const handleToggle = async (taskId) => {
    if (updatingTaskId) return; // Prevent duplicate requests
    setUpdatingTaskId(taskId);
    try {
      await toggleTaskCompletion(taskId);
      if (typeof onTaskCompleted === 'function') {
        onTaskCompleted(taskId);
      }
    } catch (err) {
      console.error('Failed to toggle task completion:', err);
    } finally {
      setUpdatingTaskId(null);
    }
  };

  if (planningLoading && (!tasks || tasks.length === 0)) {
    return (
      <div className="space-y-2.5">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="flex items-center gap-3 p-3 rounded-xl bg-[#0f131d] border border-[#232b3e] animate-pulse"
          >
            <div className="w-5 h-5 rounded-md bg-slate-700/60 shrink-0" />
            <div className="flex-1 space-y-1.5">
              <div className="h-3.5 bg-slate-700/60 rounded w-4/5" />
              <div className="h-2.5 bg-slate-800 rounded w-1/3" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (planningError && (!tasks || tasks.length === 0)) {
    return (
      <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-center">
        <AlertCircle className="w-5 h-5 text-red-400 mx-auto mb-1.5" />
        <p className="text-xs text-red-300 font-medium">{planningError}</p>
      </div>
    );
  }

  if (!displayTasks || displayTasks.length === 0) {
    return (
      <div className="p-6 rounded-xl bg-[#0f131d]/60 border border-dashed border-[#232b3e] text-center">
        <CalendarCheck2 className="w-7 h-7 text-slate-600 mx-auto mb-2" />
        <p className="text-xs font-semibold text-slate-300">No active roadmap tasks found</p>
        <p className="text-[11px] text-slate-500 mt-1 max-w-xs mx-auto">
          Start by generating or activating your placement roadmap to receive curated daily drills.
        </p>
        <NavLink
          to="/roadmap"
          className="inline-flex items-center gap-1.5 mt-3 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-colors"
        >
          Open Roadmap <ArrowRight className="w-3.5 h-3.5" />
        </NavLink>
      </div>
    );
  }

  return (
    <div className="space-y-2.5">
      {displayTasks.map((task) => {
        const taskId = task.id || task.taskId || task._id;
        const taskDay = getTaskDayNumber(task);
        const isMutating = updatingTaskId === taskId;
        const isDone = task.completed || task.status === 'completed';
        const isToday = taskDay === effectiveCurrentDay;
        const drillRoute = taskDay < 999
          ? `/roadmap?day=${taskDay}&taskId=${encodeURIComponent(taskId)}`
          : (task.route || '/tasks');

        return (
          <div
            key={taskId}
            onClick={() => navigate(drillRoute)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                navigate(drillRoute);
              }
            }}
            className={`group flex items-center justify-between gap-3 p-3 rounded-xl border transition-all duration-200 cursor-pointer ${
              isDone
                ? 'bg-[#0f131d]/50 border-emerald-500/20 hover:border-emerald-500/40'
                : 'bg-[#0f131d] border-[#232b3e] hover:border-indigo-500/40 hover:bg-indigo-500/5'
            }`}
          >
            {/* Completion Toggle Checkbox Button */}
            <button
              type="button"
              disabled={isMutating}
              onClick={(e) => {
                e.stopPropagation();
                handleToggle(taskId);
              }}
              aria-label={isDone ? `Mark "${task.title}" as pending` : `Mark "${task.title}" as completed`}
              className={`shrink-0 w-5 h-5 rounded-md border flex items-center justify-center transition-colors ${
                isDone
                  ? 'bg-emerald-500/20 border-emerald-500 text-emerald-400'
                  : 'border-slate-600 hover:border-indigo-400 text-transparent'
              } ${isMutating ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              {isMutating ? (
                <Loader2 className="w-3 h-3 text-indigo-400 animate-spin" />
              ) : (
                <Check className={`w-3.5 h-3.5 ${isDone ? 'opacity-100' : 'opacity-0 group-hover:opacity-30 text-indigo-400'}`} />
              )}
            </button>

            {/* Task Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1 flex-wrap">
                {isToday && !isDone && (
                  <span className="text-[10px] px-1.5 py-0.2 rounded font-medium bg-amber-500/10 text-amber-300 border border-amber-500/25">
                    Today
                  </span>
                )}
                {task.category && (
                  <span className="text-[10px] px-1.5 py-0.2 rounded font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                    {task.category}
                  </span>
                )}
                {task.duration && (
                  <span className="text-[10px] text-slate-500 flex items-center gap-1 font-mono">
                    <Clock className="w-3 h-3" /> {task.duration}
                  </span>
                )}
                {isDone && (
                  <span className="text-[10px] text-emerald-400 font-medium flex items-center gap-0.5">
                    Completed
                  </span>
                )}
              </div>
              <p
                className={`text-xs font-medium leading-snug truncate ${
                  isDone ? 'line-through text-slate-500' : 'text-slate-200'
                }`}
                title={task.title}
              >
                {task.title}
              </p>
            </div>

            {/* Action / Drill Drilldown Link */}
            <div
              className="p-1.5 rounded-lg bg-[#121624] border border-[#232b3e] text-slate-400 group-hover:text-white group-hover:border-indigo-500/40 transition-colors shrink-0"
              title="Open Task in Roadmap"
            >
              <ArrowRight className="w-3.5 h-3.5" />
            </div>
          </div>
        );
      })}

      {tasks.length > maxItems && (
        <div className="pt-1 flex items-center justify-between text-[11px] text-slate-500">
          <span>
            Showing {displayTasks.length} of {tasks.length} total tasks
          </span>
          <NavLink to="/tasks" className="text-indigo-400 hover:underline font-medium">
            View All Tasks →
          </NavLink>
        </div>
      )}
    </div>
  );
};
