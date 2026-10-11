import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { usePlanning } from '../../context/PlanningContext';
import { ChevronDown, Clock3, RefreshCw } from 'lucide-react';

const TaskRow = ({ task, onToggle }) => (
  <div className="flex items-start gap-3 py-3 border-b border-slate-800/80 last:border-b-0">
    <input
      type="checkbox"
      checked={task.completed}
      onChange={() => onToggle(task.id)}
      aria-label={`${task.completed ? 'Reopen' : 'Complete'} ${task.title}`}
      className="mt-1 h-4 w-4 shrink-0 accent-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-400"
    />
    <div className="min-w-0 flex-1">
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
        <p className={`min-w-0 flex-1 text-sm leading-6 ${task.completed ? 'text-slate-400 line-through' : 'text-slate-100'}`}>
          {task.title}
        </p>
        <span className={`text-xs ${task.completed ? 'text-emerald-400' : 'text-slate-500'}`}>
          {task.completed ? 'Completed' : 'To do'}
        </span>
        {task.duration && <span className="inline-flex items-center gap-1 text-xs text-slate-400"><Clock3 size={13} />{task.duration}</span>}
      </div>
      {task.description && (
        <details className="mt-1 text-xs text-slate-400">
          <summary className="w-fit cursor-pointer select-none rounded text-slate-500 hover:text-slate-300 focus-visible:outline focus-visible:outline-2 focus-visible:outline-indigo-400">
            More details
          </summary>
          <p className="max-w-3xl pt-2 leading-5">{task.description}</p>
        </details>
      )}
    </div>
  </div>
);

const TaskGroup = ({ title, tasks, onToggle }) => {
  const [showCompleted, setShowCompleted] = useState(false);
  const incomplete = tasks.filter((task) => !task.completed);
  const completed = tasks.filter((task) => task.completed);

  return (
    <section aria-label={title} className="rounded-xl bg-[#111724] px-4 sm:px-5">
      <div className="flex items-center justify-between gap-3 border-b border-slate-800 py-3">
        <h3 className="text-sm font-semibold text-slate-200">{title}</h3>
        <span className="text-xs text-slate-500">{incomplete.length} remaining</span>
      </div>
      {incomplete.length > 0
        ? incomplete.map((task) => <TaskRow key={task.id} task={task} onToggle={onToggle} />)
        : <p className="py-4 text-sm text-slate-500">No tasks to do here.</p>}
      {completed.length > 0 && (
        <>
          <button
            type="button"
            aria-expanded={showCompleted}
            onClick={() => setShowCompleted((shown) => !shown)}
            className="flex min-h-10 w-full items-center gap-2 text-left text-xs text-slate-500 hover:text-slate-300 focus-visible:outline focus-visible:outline-2 focus-visible:outline-indigo-400"
          >
            <ChevronDown size={14} className={showCompleted ? 'rotate-180 transition-transform' : 'transition-transform'} />
            {showCompleted ? 'Hide' : 'Show'} {completed.length} completed {completed.length === 1 ? 'task' : 'tasks'}
          </button>
          {showCompleted && completed.map((task) => <TaskRow key={task.id} task={task} onToggle={onToggle} />)}
        </>
      )}
    </section>
  );
};

export const RoadmapPage = () => {
  const navigate = useNavigate();
  const {
    roadmap,
    tasks,
    toggleTaskCompletion,
    adaptRoadmap,
    toastNotification,
    planningLoading,
    planningError,
    reloadPlanning,
  } = usePlanning();
  const [activePhaseId, setActivePhaseId] = useState(null);
  const [isAdapting, setIsAdapting] = useState(false);

  const phases = Array.isArray(roadmap?.phases) ? roadmap.phases : [];
  const activePhase = phases.find((phase) => phase.id === activePhaseId)
    || phases.find((phase) => phase.id === roadmap?.currentPhaseId)
    || phases[0];

  useEffect(() => {
    if (!activePhaseId && phases.length) {
      setActivePhaseId(roadmap?.currentPhaseId || phases[0].id);
    }
  }, [activePhaseId, phases, roadmap?.currentPhaseId]);

  const currentDay = Number(roadmap?.currentDay) || 0;
  const totalDays = Number(roadmap?.totalDays) || null;
  const progressPercent = Math.min(100, Math.max(0, Number(roadmap?.overallProgressPercent) || 0));
  const currentPhase = phases.find((phase) => currentDay >= phase.startDay && currentDay <= phase.endDay);
  const phaseTasks = useMemo(() => {
    if (!activePhase || !Array.isArray(tasks)) return [];
    return tasks
      .filter((task) => task.taskId && task.dayNumber >= activePhase.startDay && task.dayNumber <= activePhase.endDay)
      .sort((a, b) => a.dayNumber - b.dayNumber || a.title.localeCompare(b.title));
  }, [activePhase, tasks]);

  const todayTasks = phaseTasks.filter((task) => task.dayNumber === currentDay);
  const laterTasks = phaseTasks.filter((task) => task.dayNumber !== currentDay);
  const weekGroups = [...new Set(laterTasks.map((task) => Math.ceil(task.dayNumber / 7)))];

  const handleRecalibrate = async () => {
    setIsAdapting(true);
    try {
      if (await adaptRoadmap()) await reloadPlanning();
    } finally {
      setIsAdapting(false);
    }
  };

  if (planningLoading) {
    return <div role="status" className="rounded-2xl border border-slate-800 bg-[#121624] p-6 text-sm text-slate-400">Loading your roadmap…</div>;
  }

  if (planningError) {
    return (
      <section className="rounded-2xl border border-slate-800 bg-[#121624] p-6 sm:p-8" aria-labelledby="roadmap-error-title">
        <h1 id="roadmap-error-title" className="text-xl font-semibold text-white">90-Day Adaptive Placement Roadmap</h1>
        <p role="alert" className="mt-2 text-sm text-slate-400">{planningError}</p>
        <button type="button" onClick={reloadPlanning} className="mt-5 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-300">Try again</button>
      </section>
    );
  }

  return (
    <main className="mx-auto max-w-5xl space-y-5 pb-8 text-slate-100">
      {toastNotification && <div role="status" className="fixed bottom-6 right-6 z-50 rounded-lg border border-slate-700 bg-[#121624] px-4 py-3 text-sm text-slate-100 shadow-xl">{toastNotification}</div>}

      <header className="flex flex-col gap-4 rounded-2xl border border-slate-800 bg-[#121624] p-5 sm:flex-row sm:items-center sm:justify-between sm:p-6">
        <div>
          <h1 className="text-xl font-semibold tracking-tight text-white sm:text-2xl">90-Day Adaptive Placement Roadmap</h1>
          {roadmap?.targetRole && <p className="mt-1 text-sm text-slate-400">Preparing for {roadmap.targetRole}</p>}
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <button type="button" onClick={handleRecalibrate} disabled={isAdapting} className="inline-flex min-h-10 items-center gap-2 rounded-lg px-3 text-sm text-slate-400 hover:bg-slate-800 hover:text-white disabled:opacity-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-indigo-400">
            <RefreshCw size={15} className={isAdapting ? 'animate-spin' : ''} />
            {isAdapting ? 'Updating…' : 'Recalibrate'}
          </button>
          <button type="button" onClick={() => navigate('/tasks')} className="min-h-10 rounded-lg bg-indigo-600 px-4 text-sm font-medium text-white hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-300">View today’s tasks</button>
        </div>
      </header>

      <section aria-label="Roadmap progress" className="rounded-2xl border border-slate-800 bg-[#121624] p-5 sm:p-6">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <p className="text-sm text-slate-400">Overall completion</p>
            <p className="mt-1 text-3xl font-semibold tabular-nums text-white">{progressPercent}%</p>
          </div>
          <p className="text-sm text-slate-400">Day {currentDay || '—'} of {totalDays || '—'}</p>
        </div>
        <div
          className="mt-4 h-2 overflow-hidden rounded-full bg-slate-800"
          role="progressbar"
          aria-label="Overall roadmap completion"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={progressPercent}
        >
          <div className="h-full rounded-full bg-indigo-500 transition-[width]" style={{ width: `${progressPercent}%` }} />
        </div>
        <div className="mt-4 flex flex-wrap gap-x-6 gap-y-2 text-sm text-slate-400">
          <span>Week {currentDay ? Math.ceil(currentDay / 7) : '—'}</span>
          <span>Current phase: {currentPhase?.title || roadmap?.currentPhaseName || '—'}</span>
        </div>
      </section>

      {phases.length > 0 ? (
        <section aria-label="Roadmap phases" className="space-y-4">
          <div role="tablist" aria-label="Roadmap phase" className="flex gap-2 overflow-x-auto border-b border-slate-800 pb-2">
            {phases.map((phase, index) => (
              <button
                key={phase.id}
                id={`${phase.id}-tab`}
                type="button"
                role="tab"
                aria-selected={activePhase?.id === phase.id}
                aria-controls="roadmap-phase-panel"
                onClick={() => setActivePhaseId(phase.id)}
                onKeyDown={(event) => {
                  if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return;
                  event.preventDefault();
                  const direction = event.key === 'ArrowRight' ? 1 : -1;
                  const nextIndex = (index + direction + phases.length) % phases.length;
                  setActivePhaseId(phases[nextIndex].id);
                  event.currentTarget.parentElement.querySelectorAll('[role="tab"]')[nextIndex]?.focus();
                }}
                className={`min-h-10 shrink-0 rounded-lg px-4 text-sm font-medium transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-indigo-400 ${activePhase?.id === phase.id ? 'bg-indigo-500/15 text-indigo-200 ring-1 ring-indigo-400/40' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
              >
                {phase.title}
              </button>
            ))}
          </div>

          {activePhase && (
            <div role="tabpanel" id="roadmap-phase-panel" aria-labelledby={`${activePhase.id}-tab`} className="space-y-4">
              <div className="flex flex-wrap items-baseline justify-between gap-2 px-1">
                <h2 className="text-lg font-semibold text-white">{activePhase.title}</h2>
                <p className="text-sm text-slate-500">Days {activePhase.startDay}–{activePhase.endDay}</p>
              </div>

              {phaseTasks.length === 0 ? (
                <p className="rounded-xl border border-slate-800 bg-[#121624] p-5 text-sm text-slate-400">No scheduled tasks are available for this phase yet.</p>
              ) : (
                <div className="space-y-4">
                  {todayTasks.length > 0 && <TaskGroup title={`Today · Day ${currentDay}`} tasks={todayTasks} onToggle={toggleTaskCompletion} />}
                  {weekGroups.map((week) => (
                    <TaskGroup key={week} title={`Week ${week}`} tasks={laterTasks.filter((task) => Math.ceil(task.dayNumber / 7) === week)} onToggle={toggleTaskCompletion} />
                  ))}
                </div>
              )}
            </div>
          )}
        </section>
      ) : (
        <p className="rounded-xl border border-slate-800 bg-[#121624] p-5 text-sm text-slate-400">Your roadmap does not have any phases yet.</p>
      )}
    </main>
  );
};
