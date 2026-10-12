import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { usePlanning } from '../../context/PlanningContext';
import { useUser } from '../../context/UserContext';
import { ChevronDown, Clock3, RefreshCw, Calendar, Sparkles, Sliders } from 'lucide-react';

const TaskRow = ({ task, onToggle, isTarget }) => (
  <div
    id={`task-row-${task.id}`}
    className={`flex items-start gap-3 py-3 border-b border-slate-800/80 last:border-b-0 transition-all duration-300 ${
      isTarget ? 'bg-indigo-500/15 ring-2 ring-indigo-400 rounded-xl px-3 my-1 border border-indigo-500/40 shadow-lg shadow-indigo-500/10' : ''
    }`}
  >
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
        <details className="mt-1 text-xs text-slate-400" open={isTarget ? true : undefined}>
          <summary className="w-fit cursor-pointer select-none rounded text-slate-500 hover:text-slate-300 focus-visible:outline focus-visible:outline-2 focus-visible:outline-indigo-400">
            More details
          </summary>
          <p className="max-w-3xl pt-2 leading-5">{task.description}</p>
        </details>
      )}
    </div>
  </div>
);

const TaskGroup = ({ title, tasks, onToggle, targetTaskId }) => {
  const [showCompleted, setShowCompleted] = useState(() => {
    return Boolean(
      targetTaskId && tasks.some((t) => (t.id === targetTaskId || t.taskId === targetTaskId) && t.completed)
    );
  });

  useEffect(() => {
    if (targetTaskId && tasks.some((t) => (t.id === targetTaskId || t.taskId === targetTaskId) && t.completed)) {
      setShowCompleted(true);
    }
  }, [targetTaskId, tasks]);

  const incomplete = tasks.filter((task) => !task.completed);
  const completed = tasks.filter((task) => task.completed);

  return (
    <section aria-label={title} className="rounded-xl bg-[#111724] px-4 sm:px-5">
      <div className="flex items-center justify-between gap-3 border-b border-slate-800 py-3">
        <h3 className="text-sm font-semibold text-slate-200">{title}</h3>
        <span className="text-xs text-slate-500">{incomplete.length} remaining</span>
      </div>
      {incomplete.length > 0
        ? incomplete.map((task) => (
            <TaskRow
              key={task.id}
              task={task}
              onToggle={onToggle}
              isTarget={task.id === targetTaskId || task.taskId === targetTaskId}
            />
          ))
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
          {showCompleted && completed.map((task) => (
            <TaskRow
              key={task.id}
              task={task}
              onToggle={onToggle}
              isTarget={task.id === targetTaskId || task.taskId === targetTaskId}
            />
          ))}
        </>
      )}
    </section>
  );
};

export const RoadmapPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useUser();
  const {
    roadmap,
    tasks,
    toggleTaskCompletion,
    adaptRoadmap,
    generateCustomRoadmap,
    toastNotification,
    planningLoading,
    planningError,
    reloadPlanning,
  } = usePlanning();

  const searchParams = useMemo(() => new URLSearchParams(location.search), [location.search]);
  const targetTaskId = searchParams.get('taskId') || location.state?.taskId;
  const targetDay = Number(searchParams.get('day') || location.state?.day);

  const registeredRole = user?.targetRole || roadmap?.targetRole || 'Full Stack Engineer';

  // State for dynamic duration & daily study time
  const [selectedDuration, setSelectedDuration] = useState(roadmap?.totalDays || 90);
  const [isCustomDuration, setIsCustomDuration] = useState(false);
  const [customDurationInput, setCustomDurationInput] = useState('');

  const [selectedDailyMinutes, setSelectedDailyMinutes] = useState(
    Number(user?.dailyGoalMinutes) || roadmap?.availableMinutesPerDay || 60
  );
  const [isCustomDaily, setIsCustomDaily] = useState(false);
  const [customDailyInput, setCustomDailyInput] = useState('');

  const [activePhaseId, setActivePhaseId] = useState(null);
  const [isAdapting, setIsAdapting] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  // Sync initial inputs with loaded roadmap state
  useEffect(() => {
    if (roadmap?.totalDays) {
      if ([15, 30, 45, 60, 90].includes(roadmap.totalDays)) {
        setSelectedDuration(roadmap.totalDays);
        setIsCustomDuration(false);
      } else {
        setSelectedDuration(roadmap.totalDays);
        setIsCustomDuration(true);
        setCustomDurationInput(String(roadmap.totalDays));
      }
    }
  }, [roadmap?.totalDays]);

  useEffect(() => {
    if (roadmap?.availableMinutesPerDay) {
      if ([30, 45, 60, 120].includes(roadmap.availableMinutesPerDay)) {
        setSelectedDailyMinutes(roadmap.availableMinutesPerDay);
        setIsCustomDaily(false);
      } else {
        setSelectedDailyMinutes(roadmap.availableMinutesPerDay);
        setIsCustomDaily(true);
        setCustomDailyInput(String(roadmap.availableMinutesPerDay));
      }
    }
  }, [roadmap?.availableMinutesPerDay]);

  const phases = Array.isArray(roadmap?.phases) ? roadmap.phases : [];
  const activePhase = phases.find((phase) => phase.id === activePhaseId)
    || phases.find((phase) => phase.id === roadmap?.currentPhaseId)
    || phases[0];

  useEffect(() => {
    if (!activePhaseId && phases.length) {
      setActivePhaseId(roadmap?.currentPhaseId || phases[0].id);
    }
  }, [activePhaseId, phases, roadmap?.currentPhaseId]);

  // If navigated with a target task or day, ensure active phase contains that day
  useEffect(() => {
    if ((targetTaskId || targetDay) && phases.length) {
      const allList = Array.isArray(tasks) ? tasks : [];
      const foundTask = allList.find((t) => t.id === targetTaskId || t.taskId === targetTaskId);
      const dayNum = foundTask?.dayNumber || targetDay;
      if (dayNum) {
        const matchingPhase = phases.find((p) => dayNum >= p.startDay && dayNum <= p.endDay);
        if (matchingPhase && matchingPhase.id !== activePhaseId) {
          setActivePhaseId(matchingPhase.id);
        }
      }
    }
  }, [targetTaskId, targetDay, tasks, phases, activePhaseId]);

  // Smooth scroll into target task row when active phase is rendered
  useEffect(() => {
    if (targetTaskId) {
      const timer = setTimeout(() => {
        const el = document.getElementById(`task-row-${targetTaskId}`);
        if (el) {
          el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }, 250);
      return () => clearTimeout(timer);
    }
  }, [targetTaskId, activePhaseId]);

  const currentDay = Number(roadmap?.currentDay) || 0;
  const totalDays = Number(roadmap?.totalDays) || selectedDuration || 90;
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

  const handleDurationPreset = (days) => {
    setIsCustomDuration(false);
    setSelectedDuration(days);
  };

  const handleCustomDurationChange = (e) => {
    const val = e.target.value;
    setCustomDurationInput(val);
    const num = parseInt(val, 10);
    if (!isNaN(num) && num >= 1 && num <= 365) {
      setSelectedDuration(num);
    }
  };

  const handleDailyPreset = (mins) => {
    setIsCustomDaily(false);
    setSelectedDailyMinutes(mins);
  };

  const handleCustomDailyChange = (e) => {
    const val = e.target.value;
    setCustomDailyInput(val);
    const num = parseInt(val, 10);
    if (!isNaN(num) && num >= 15 && num <= 480) {
      setSelectedDailyMinutes(num);
    }
  };

  const handleGenerateCustomRoadmap = async () => {
    const finalDays = isCustomDuration ? parseInt(customDurationInput, 10) || selectedDuration : selectedDuration;
    const finalMins = isCustomDaily ? parseInt(customDailyInput, 10) || selectedDailyMinutes : selectedDailyMinutes;

    if (!finalDays || finalDays < 1 || finalDays > 365) return;
    if (!finalMins || finalMins < 15 || finalMins > 480) return;

    setIsGenerating(true);
    try {
      await generateCustomRoadmap({
        targetRole: registeredRole,
        durationDays: finalDays,
        dailyMinutes: finalMins,
      });
    } finally {
      setIsGenerating(false);
    }
  };

  if (planningLoading) {
    return <div role="status" className="rounded-2xl border border-slate-800 bg-[#121624] p-6 text-sm text-slate-400">Loading your roadmap…</div>;
  }

  if (planningError) {
    return (
      <section className="rounded-2xl border border-slate-800 bg-[#121624] p-6 sm:p-8" aria-labelledby="roadmap-error-title">
        <h1 id="roadmap-error-title" className="text-xl font-semibold text-white">{totalDays}-Day Adaptive Placement Roadmap</h1>
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
          <h1 className="text-xl font-semibold tracking-tight text-white sm:text-2xl">{totalDays}-Day Adaptive Placement Roadmap</h1>
          <p className="mt-1 text-sm text-slate-400">Preparing for <span className="font-medium text-indigo-300">{registeredRole}</span></p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <button type="button" onClick={handleRecalibrate} disabled={isAdapting} className="inline-flex min-h-10 items-center gap-2 rounded-lg px-3 text-sm text-slate-400 hover:bg-slate-800 hover:text-white disabled:opacity-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-indigo-400">
            <RefreshCw size={15} className={isAdapting ? 'animate-spin' : ''} />
            {isAdapting ? 'Updating…' : 'Recalibrate'}
          </button>
          <button type="button" onClick={() => navigate('/tasks')} className="min-h-10 rounded-lg bg-indigo-600 px-4 text-sm font-medium text-white hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-300">View today’s tasks</button>
        </div>
      </header>

      {/* Dynamic Roadmap Preferences & Generation Controls */}
      <section aria-label="Roadmap Preparation Plan Configuration" className="rounded-2xl border border-slate-800 bg-[#121624] p-5 sm:p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
          <div>
            <h2 className="text-base font-semibold text-white flex items-center gap-2">
              <Sliders size={18} className="text-indigo-400" />
              Personalized Plan Settings
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Customize your study cadence and preparation runway. Existing completed tasks are preserved.
            </p>
          </div>
          {/* Target Role Sync Badge */}
          <div className="flex items-center gap-2 self-start sm:self-auto rounded-lg bg-indigo-500/10 border border-indigo-500/20 px-3 py-1.5 text-xs">
            <span className="text-slate-400">Target Role:</span>
            <span className="font-semibold text-indigo-300">{registeredRole}</span>
            <span className="inline-flex items-center text-[10px] text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded font-medium">
              Profile Synced
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 pt-1">
          {/* Preparation Duration */}
          <div className="space-y-2">
            <label className="text-xs font-medium text-slate-300 flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Calendar size={14} className="text-indigo-400" />
                Study Duration
              </span>
              <span className="text-indigo-300 font-semibold">{selectedDuration} Days</span>
            </label>
            <div className="flex flex-wrap gap-2">
              {[15, 30, 45, 60, 90].map((days) => (
                <button
                  key={days}
                  type="button"
                  onClick={() => handleDurationPreset(days)}
                  className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-all ${
                    !isCustomDuration && selectedDuration === days
                      ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-600/30'
                      : 'bg-[#111724] text-slate-400 hover:text-white hover:bg-slate-800 border border-slate-800'
                  }`}
                >
                  {days} Days
                </button>
              ))}
              <button
                type="button"
                onClick={() => {
                  setIsCustomDuration(true);
                  if (!customDurationInput) setCustomDurationInput(String(selectedDuration));
                }}
                className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-all ${
                  isCustomDuration
                    ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-600/30'
                    : 'bg-[#111724] text-slate-400 hover:text-white hover:bg-slate-800 border border-slate-800'
                }`}
              >
                Custom
              </button>
            </div>
            {isCustomDuration && (
              <div className="flex items-center gap-2 pt-1">
                <input
                  type="number"
                  min="1"
                  max="365"
                  value={customDurationInput}
                  onChange={handleCustomDurationChange}
                  placeholder="Days (1-365)"
                  className="w-32 rounded-lg bg-[#111724] border border-slate-700 px-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                />
                <span className="text-xs text-slate-400">days (1–365)</span>
              </div>
            )}
          </div>

          {/* Daily Study Time */}
          <div className="space-y-2">
            <label className="text-xs font-medium text-slate-300 flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Clock3 size={14} className="text-indigo-400" />
                Daily Study Time
              </span>
              <span className="text-indigo-300 font-semibold">
                {selectedDailyMinutes >= 60 && selectedDailyMinutes % 60 === 0
                  ? `${selectedDailyMinutes / 60} Hour${selectedDailyMinutes > 60 ? 's' : ''}`
                  : `${selectedDailyMinutes} Mins`}/day
              </span>
            </label>
            <div className="flex flex-wrap gap-2">
              {[
                { label: '30 Mins', value: 30 },
                { label: '45 Mins', value: 45 },
                { label: '1 Hour', value: 60 },
                { label: '2 Hours', value: 120 },
              ].map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => handleDailyPreset(opt.value)}
                  className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-all ${
                    !isCustomDaily && selectedDailyMinutes === opt.value
                      ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-600/30'
                      : 'bg-[#111724] text-slate-400 hover:text-white hover:bg-slate-800 border border-slate-800'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
              <button
                type="button"
                onClick={() => {
                  setIsCustomDaily(true);
                  if (!customDailyInput) setCustomDailyInput(String(selectedDailyMinutes));
                }}
                className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-all ${
                  isCustomDaily
                    ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-600/30'
                    : 'bg-[#111724] text-slate-400 hover:text-white hover:bg-slate-800 border border-slate-800'
                }`}
              >
                Custom
              </button>
            </div>
            {isCustomDaily && (
              <div className="flex items-center gap-2 pt-1">
                <input
                  type="number"
                  min="15"
                  max="480"
                  value={customDailyInput}
                  onChange={handleCustomDailyChange}
                  placeholder="Mins (15-480)"
                  className="w-32 rounded-lg bg-[#111724] border border-slate-700 px-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                />
                <span className="text-xs text-slate-400">minutes/day (15–480)</span>
              </div>
            )}
          </div>
        </div>

        <div className="pt-2 flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-t border-slate-800/80">
          <p className="text-xs text-slate-400">
            Estimated runway: <span className="text-slate-200 font-medium">~{Math.round((selectedDuration * selectedDailyMinutes) / 60)} study hours</span> across <span className="text-slate-200 font-medium">{selectedDuration} days</span>
          </p>
          <button
            type="button"
            onClick={handleGenerateCustomRoadmap}
            disabled={isGenerating || planningLoading}
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-500 disabled:opacity-50 transition-colors shadow-sm shadow-indigo-600/25"
          >
            {isGenerating ? (
              <>
                <RefreshCw size={13} className="animate-spin" />
                Generating Adaptive Roadmap…
              </>
            ) : (
              <>
                <Sparkles size={13} />
                Generate {selectedDuration}-Day Roadmap
              </>
            )}
          </button>
        </div>
      </section>

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
                  {todayTasks.length > 0 && (
                    <TaskGroup
                      title={`Today · Day ${currentDay}`}
                      tasks={todayTasks}
                      onToggle={toggleTaskCompletion}
                      targetTaskId={targetTaskId}
                    />
                  )}
                  {weekGroups.map((week) => (
                    <TaskGroup
                      key={week}
                      title={`Week ${week}`}
                      tasks={laterTasks.filter((task) => Math.ceil(task.dayNumber / 7) === week)}
                      onToggle={toggleTaskCompletion}
                      targetTaskId={targetTaskId}
                    />
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
