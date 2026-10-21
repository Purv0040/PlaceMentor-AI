import React, { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { usePlanning } from '../../context/PlanningContext';
import {
  Zap,
  CheckCircle2,
  Clock,
  ArrowRight,
  Sparkles,
  ArrowUpRight,
  ListTodo,
  History,
  ChevronDown,
  CalendarCheck2,
  AlertCircle,
  RefreshCw,
} from 'lucide-react';

const formatCompletionDate = (dateVal) => {
  if (!dateVal) return null;
  try {
    const d = new Date(dateVal);
    if (isNaN(d.getTime())) return null;
    return d.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  } catch {
    return null;
  }
};

export const TasksPage = () => {
  const navigate = useNavigate();
  const {
    tasks,
    toggleTaskCompletion,
    roadmap,
    toastNotification,
    planningLoading,
    planningError,
    reloadPlanning,
  } = usePlanning();

  const [activeCategory, setActiveCategory] = useState('All');
  const [expandedDays, setExpandedDays] = useState({});

  const toggleDayExpansion = (dayNum) => {
    setExpandedDays((prev) => ({
      ...prev,
      [dayNum]: !prev[dayNum],
    }));
  };

  // Derive active roadmap day from existing roadmap state (matching RoadmapPage)
  const currentDay = Number(roadmap?.currentDay) || 1;
  const currentSprint = Math.ceil(currentDay / 7);
  const currentPhase = Array.isArray(roadmap?.phases)
    ? roadmap.phases.find((p) => currentDay >= p.startDay && currentDay <= p.endDay)
    : null;
  const phaseName = currentPhase?.title || roadmap?.currentPhaseName || 'Foundation';

  // 1. All valid tasks belonging to active roadmap, strictly deduplicated by dayNumber and title
  const allTasks = useMemo(() => {
    if (!Array.isArray(tasks)) return [];
    const valid = tasks.filter((t) => (t.id || t.taskId) && t.dayNumber != null);

    // Deduplicate by dayNumber + title (case-insensitive)
    const dedupMap = new Map();
    for (const t of valid) {
      const key = `${t.dayNumber}_${(t.title || '').trim().toLowerCase()}`;
      if (!dedupMap.has(key)) {
        dedupMap.set(key, t);
      } else {
        const existing = dedupMap.get(key);
        const currCompleted = t.completed || t.status === 'completed';
        const existCompleted = existing.completed || existing.status === 'completed';
        if (currCompleted && !existCompleted) {
          dedupMap.set(key, t);
        } else if (currCompleted && existCompleted) {
          const tTime = new Date(t.completedAt || 0).getTime();
          const exTime = new Date(existing.completedAt || 0).getTime();
          if (tTime > exTime) dedupMap.set(key, t);
        }
      }
    }
    return Array.from(dedupMap.values());
  }, [tasks]);

  // 2. Today's Tasks: Strictly matching currentDay
  const todayTasks = useMemo(() => {
    return allTasks
      .filter((t) => t.dayNumber === currentDay)
      .sort((a, b) => a.title.localeCompare(b.title));
  }, [allTasks, currentDay]);

  // 3. Completed Days: Previous days (dayNumber < currentDay) where ALL tasks are completed
  const completedDays = useMemo(() => {
    const daysMap = new Map();
    for (const t of allTasks) {
      if (t.dayNumber < currentDay && t.dayNumber >= 1) {
        if (!daysMap.has(t.dayNumber)) {
          daysMap.set(t.dayNumber, []);
        }
        daysMap.get(t.dayNumber).push(t);
      }
    }

    const completedList = [];
    const sortedDays = Array.from(daysMap.keys()).sort((a, b) => b - a); // Most recent first
    for (const dayNum of sortedDays) {
      const dayTasks = daysMap.get(dayNum);
      const isFullyCompleted = dayTasks.length > 0 && dayTasks.every((t) => t.completed);
      if (isFullyCompleted) {
        const completedDates = dayTasks
          .map((t) => t.completedAt)
          .filter(Boolean);
        const latestCompletedDate = completedDates.length > 0 ? completedDates[0] : null;

        completedList.push({
          dayNumber: dayNum,
          tasks: dayTasks,
          taskCount: dayTasks.length,
          completedAt: latestCompletedDate,
        });
      }
    }
    return completedList;
  }, [allTasks, currentDay]);

  // Dynamic category pills for today's tasks
  const todayCategories = useMemo(() => {
    const cats = new Set(todayTasks.map((t) => t.category).filter(Boolean));
    return ['All', ...Array.from(cats)];
  }, [todayTasks]);

  // Filter today's tasks by selected category
  const filteredTodayTasks = useMemo(() => {
    if (activeCategory === 'All') return todayTasks;
    return todayTasks.filter((t) => t.category === activeCategory);
  }, [todayTasks, activeCategory]);

  // Progress metrics calculated strictly for Today's tasks
  const completedTodayCount = todayTasks.filter((t) => t.completed).length;
  const totalTodayCount = todayTasks.length;
  const pendingTodayCount = totalTodayCount - completedTodayCount;
  const todayCompletionPercent = totalTodayCount > 0
    ? Math.round((completedTodayCount / totalTodayCount) * 100)
    : 0;

  const todayMinutes = todayTasks.reduce(
    (sum, t) => sum + (Number(t.estimatedMinutes) || 60),
    0
  );
  const todayDurationText = todayMinutes >= 60
    ? `${(todayMinutes / 60).toFixed(1)} Hours`
    : `${todayMinutes} Mins`;

  if (planningLoading) {
    return (
      <div role="status" className="rounded-2xl border border-slate-800 bg-[#121624] p-8 text-sm text-slate-400 flex items-center gap-3">
        <RefreshCw size={18} className="animate-spin text-indigo-400" />
        <span>Loading Today’s tasks…</span>
      </div>
    );
  }

  if (planningError) {
    return (
      <section className="rounded-2xl border border-slate-800 bg-[#121624] p-6 sm:p-8" aria-labelledby="tasks-error-title">
        <div className="flex items-center gap-2 text-rose-400">
          <AlertCircle size={20} />
          <h1 id="tasks-error-title" className="text-xl font-semibold text-white">Today's Tasks</h1>
        </div>
        <p role="alert" className="mt-2 text-sm text-slate-400">{planningError}</p>
        <button
          type="button"
          onClick={reloadPlanning}
          className="mt-5 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-300"
        >
          Try again
        </button>
      </section>
    );
  }

  return (
    <div className="tasks-page space-y-6 animate-in fade-in duration-300">
      {/* Toast Notification */}
      {toastNotification && (
        <div className="fixed bottom-10 right-6 z-50 flex items-center gap-2 px-4 py-3 bg-[#121624] border border-indigo-500/40 text-white rounded-xl shadow-2xl font-mono text-xs animate-in slide-in-from-bottom duration-200">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{toastNotification}</span>
        </div>
      )}

      {/* 1. HERO BANNER */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6 p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-indigo-950/60 via-purple-950/40 to-[#121624] border border-indigo-500/30 shadow-2xl">
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-400 text-xs font-mono font-semibold border border-indigo-500/30">
              <Zap className="w-3.5 h-3.5 text-indigo-400" />
              Day {currentDay} Execution Matrix
            </span>
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-purple-500/15 text-purple-300 text-[11px] font-mono border border-purple-500/25">
              Sprint {currentSprint} · {phaseName}
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">Today's Tasks</h1>
          <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
            Prioritized engineering drills assigned exclusively to Day {currentDay} of your personalized roadmap.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start lg:self-center shrink-0">
          <button
            onClick={() => navigate('/roadmap')}
            className="flex items-center gap-1.5 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs sm:text-sm font-semibold rounded-xl transition-all shadow-lg shadow-indigo-600/30 border border-indigo-400/30"
          >
            <span>View Roadmap</span>
            <ArrowUpRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 2. DAILY COMPLETION SUMMARY BAR */}
      <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <span className="text-xs font-mono uppercase text-slate-400 font-semibold tracking-wider block">Today's Progress</span>
            <h3 className="text-lg font-bold text-white">
              {completedTodayCount} of {totalTodayCount} Tasks Completed ({todayCompletionPercent}%)
            </h3>
          </div>
          <div className="flex flex-wrap items-center gap-2 self-start sm:self-auto">
            <span className="px-3 py-1.5 rounded-full text-xs font-mono font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              Sprint {currentSprint} · Day {currentDay}
            </span>
            {completedDays.length > 0 && (
              <span className="px-3 py-1.5 rounded-full text-xs font-mono font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                {completedDays.length} {completedDays.length === 1 ? 'Day' : 'Days'} Completed
              </span>
            )}
          </div>
        </div>

        <div className="progress-track w-full bg-[#0f131d] rounded-full h-3 overflow-hidden border border-[#232b3e]">
          <div
            className="bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-400 h-full rounded-full transition-all duration-500 shadow-sm"
            style={{ width: `${todayCompletionPercent}%` }}
          ></div>
        </div>

        <div className="flex flex-wrap items-center justify-between text-xs font-mono text-slate-400 pt-1 gap-2">
          <span>Active Tasks: {pendingTodayCount}</span>
          <span>Target Duration: ~{todayDurationText} Total</span>
          <span className={todayCompletionPercent === 100 ? 'text-emerald-400 font-semibold' : 'text-indigo-400 font-semibold'}>
            Status: {todayCompletionPercent === 100 ? 'All Tasks Completed 🎉' : 'In Progress'}
          </span>
        </div>
      </div>

      {/* 3. TODAY'S TASKS LIST */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="font-bold text-white text-lg flex items-center gap-2">
              <ListTodo className="w-5 h-5 text-indigo-400" />
              Day {currentDay} Tasks
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Only tasks scheduled for today are displayed here.
            </p>
          </div>

          {/* Dynamic Category Filter Pills */}
          {todayCategories.length > 1 && (
            <div className="flex flex-wrap items-center gap-1.5 text-xs font-mono">
              {todayCategories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setActiveCategory(cat)}
                  className={`px-3 py-1 rounded-xl border transition-all ${
                    activeCategory === cat
                      ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white border-indigo-400/30 font-bold shadow-md'
                      : 'bg-[#121624] text-slate-400 border-[#232b3e] hover:text-white hover:bg-[#1a2030]'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Task Cards List */}
        <div className="grid grid-cols-1 gap-3">
          {todayTasks.length === 0 ? (
            <div className="p-8 text-center rounded-2xl bg-[#121624] border border-dashed border-[#232b3e] text-slate-400 text-xs space-y-3">
              <p>No tasks scheduled for Day {currentDay}.</p>
              <button
                type="button"
                onClick={() => navigate('/roadmap')}
                className="inline-flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg transition-colors"
              >
                <span>View Full Roadmap</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : filteredTodayTasks.length === 0 ? (
            <div className="p-8 text-center rounded-2xl bg-[#121624] border border-dashed border-[#232b3e] text-slate-400 text-xs">
              No tasks found for category "{activeCategory}" today.
            </div>
          ) : (
            filteredTodayTasks.map((task) => (
              <div
                key={task.id}
                className={`tasks-page-task p-4 rounded-2xl border transition-all ${
                  task.completed
                    ? 'tasks-page-task-completed bg-[#0f131d]/60 border-[#232b3e] opacity-80'
                    : 'bg-[#121624] border-[#232b3e] hover:border-indigo-500/40'
                } flex items-start justify-between gap-4 shadow-xl`}
              >
                <div className="flex items-start gap-3.5 flex-1 min-w-0">
                  <button
                    type="button"
                    onClick={() => toggleTaskCompletion(task.id)}
                    aria-label={`${task.completed ? 'Reopen' : 'Complete'} ${task.title}`}
                    className="mt-0.5 shrink-0 text-slate-400 hover:text-indigo-400 transition-colors"
                  >
                    <CheckCircle2
                      className={`w-5 h-5 ${
                        task.completed ? 'text-emerald-400 fill-emerald-500/20' : 'text-slate-500 hover:text-slate-300'
                      }`}
                    />
                  </button>

                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                      <span className="text-[10px] font-mono uppercase font-bold px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                        {task.category}
                      </span>
                      {task.duration && (
                        <span className="text-[10px] font-mono text-slate-400 flex items-center gap-1">
                          <Clock className="w-3.5 h-3.5" /> {task.duration}
                        </span>
                      )}
                      <span
                        className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded font-bold ${
                          task.priority === 'High' || task.priority === 'HIGH'
                            ? 'bg-amber-500/20 text-amber-400'
                            : 'bg-[#1a2030] text-slate-400'
                        }`}
                      >
                        {task.priority} Priority
                      </span>
                      {task.completed && (
                        <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded font-medium">
                          Completed {task.completedAt ? `· ${formatCompletionDate(task.completedAt)}` : ''}
                        </span>
                      )}
                    </div>

                    <p className={`text-xs sm:text-sm font-semibold leading-relaxed ${task.completed ? 'line-through text-slate-400' : 'text-white'}`}>
                      {task.title}
                    </p>

                    {task.description && (
                      <details className="mt-1 text-xs text-slate-400">
                        <summary className="w-fit cursor-pointer select-none rounded text-slate-500 hover:text-slate-300 focus-visible:outline focus-visible:outline-2 focus-visible:outline-indigo-400">
                          More details
                        </summary>
                        <p className="max-w-3xl pt-2 leading-relaxed text-slate-300">{task.description}</p>
                      </details>
                    )}
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => {
                    navigate(`/roadmap?taskId=${encodeURIComponent(task.id)}&day=${task.dayNumber || currentDay}`, {
                      state: { taskId: task.id, day: task.dayNumber || currentDay }
                    });
                  }}
                  className="p-2.5 rounded-xl bg-[#1a2030] text-slate-300 hover:text-white hover:bg-[#232b3e] border border-[#232b3e] transition-colors shrink-0"
                  title="Open task in Roadmap"
                  aria-label={`Open ${task.title} in Roadmap`}
                >
                  <ArrowRight className="w-4 h-4 text-indigo-400" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* 4. COMPLETED DAYS HISTORY */}
      <div className="space-y-4 pt-2">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
          <div>
            <h3 className="font-bold text-white text-lg flex items-center gap-2">
              <History className="w-5 h-5 text-emerald-400" />
              Completed Days History
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Previous roadmap days where all required tasks have been fully completed.
            </p>
          </div>
          <span className="text-xs font-mono text-slate-400">
            {completedDays.length} {completedDays.length === 1 ? 'day' : 'days'} archived
          </span>
        </div>

        {completedDays.length === 0 ? (
          <div className="p-8 text-center rounded-2xl bg-[#121624] border border-dashed border-[#232b3e] text-slate-400 text-xs space-y-2">
            <CalendarCheck2 className="w-8 h-8 text-slate-500 mx-auto opacity-60" />
            <p className="text-slate-300 font-medium">No fully completed previous days yet.</p>
            <p className="text-slate-500 max-w-md mx-auto">
              Days where all tasks are completed will automatically appear in this archive as you progress through your roadmap.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {completedDays.map((dayItem) => {
              const isExpanded = !!expandedDays[dayItem.dayNumber];
              return (
                <div
                  key={dayItem.dayNumber}
                  className="rounded-2xl border border-slate-800 bg-[#121624] overflow-hidden transition-all shadow-md"
                >
                  <button
                    type="button"
                    onClick={() => toggleDayExpansion(dayItem.dayNumber)}
                    aria-expanded={isExpanded}
                    className="w-full p-4 flex items-center justify-between gap-3 text-left hover:bg-slate-800/40 transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-indigo-400"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="h-8 w-8 rounded-lg bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center shrink-0">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      </div>
                      <div className="min-w-0">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="font-bold text-sm text-white">Day {dayItem.dayNumber}</span>
                          <span className="text-xs text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded font-mono font-medium">
                            All {dayItem.taskCount} {dayItem.taskCount === 1 ? 'task' : 'tasks'} completed
                          </span>
                        </div>
                        {dayItem.completedAt && (
                          <p className="text-[11px] text-slate-400 font-mono mt-0.5">
                            Completed on {formatCompletionDate(dayItem.completedAt)}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-2 text-xs text-slate-400 shrink-0">
                      <span className="hidden sm:inline">{isExpanded ? 'Hide tasks' : 'View tasks'}</span>
                      <ChevronDown
                        size={16}
                        className={`transition-transform duration-200 ${isExpanded ? 'rotate-180 text-white' : ''}`}
                      />
                    </div>
                  </button>

                  {isExpanded && (
                    <div className="border-t border-slate-800/80 px-4 py-3 bg-[#0f131d]/70 space-y-2.5">
                      {dayItem.tasks.map((task) => (
                        <div
                          key={task.id}
                          className="flex items-start justify-between gap-3 py-2 border-b border-slate-800/50 last:border-b-0 text-xs"
                        >
                          <div className="flex items-start gap-2.5 min-w-0 flex-1">
                            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                            <div className="min-w-0 flex-1">
                              <p className="font-medium text-slate-200 leading-snug">{task.title}</p>
                              {task.description && (
                                <p className="text-slate-400 text-[11px] mt-0.5 leading-relaxed">{task.description}</p>
                              )}
                              <div className="flex flex-wrap items-center gap-2 mt-1.5 text-[10px] font-mono text-slate-400">
                                <span className="px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                                  {task.category}
                                </span>
                                {task.duration && <span>{task.duration}</span>}
                                {task.completedAt && (
                                  <span className="text-emerald-400/90">
                                    {formatCompletionDate(task.completedAt)}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>

                          <button
                            type="button"
                            onClick={() => {
                              navigate(`/roadmap?taskId=${encodeURIComponent(task.id)}&day=${task.dayNumber || dayItem.dayNumber}`, {
                                state: { taskId: task.id, day: task.dayNumber || dayItem.dayNumber }
                              });
                            }}
                            className="p-1.5 rounded-lg bg-[#1a2030] text-slate-400 hover:text-white hover:bg-[#232b3e] border border-[#232b3e] transition-colors shrink-0"
                            title="Open task in Roadmap"
                            aria-label={`Open ${task.title} in Roadmap`}
                          >
                            <ArrowRight className="w-3.5 h-3.5 text-indigo-400" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* 5. ROADMAP SYNC FOOTER CARD */}
      <div className="p-5 rounded-2xl bg-[#121624] border border-[#232b3e] flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-xl">
        <div className="space-y-1">
          <h4 className="font-bold text-sm text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-purple-400" />
            Curriculum Synchronization
          </h4>
          <p className="text-xs text-slate-300 leading-relaxed">
            Task completion is persistently synchronized with MongoDB and reflected across your Roadmap and Progress telemetry.
          </p>
        </div>

        <button
          onClick={() => navigate('/roadmap')}
          className="inline-flex items-center justify-center gap-1.5 px-4 py-2 bg-[#1a2030] hover:bg-[#232b3e] text-indigo-300 hover:text-white border border-[#232b3e] text-xs font-semibold rounded-xl transition-colors shrink-0"
        >
          <span>Open Roadmap</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
