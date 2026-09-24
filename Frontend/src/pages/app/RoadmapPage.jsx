import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { usePlanning } from '../../context/PlanningContext';
import {
  Zap,
  RefreshCw,
  Calendar,
  CheckCircle2,
  Clock,
  Sparkles,
  ArrowUpRight,
  TrendingUp,
  SlidersHorizontal,
  ChevronRight,
  Target,
  Check,
  AlertTriangle,
  Flame,
  ArrowRight
} from 'lucide-react';

export const RoadmapPage = () => {
  const navigate = useNavigate();
  const { roadmap, tasks, toggleTaskCompletion, adaptRoadmap, toastNotification } = usePlanning();
  const [activePhaseId, setActivePhaseId] = useState('phase-2');
  const [isAdapting, setIsAdapting] = useState(false);

  const handleRecalibrate = async () => {
    setIsAdapting(true);
    await adaptRoadmap();
    setIsAdapting(false);
  };

  const activePhase = roadmap.phases.find((p) => p.id === activePhaseId) || roadmap.phases[1];
  const day34Tasks = tasks.filter((t) => t.dayNumber === 34 || t.phaseId === 'phase-2');

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Toast Notification */}
      {toastNotification && (
        <div className="fixed bottom-10 right-6 z-50 flex items-center gap-2 px-4 py-3 bg-surface-container-highest border border-primary/40 text-on-surface rounded-xl shadow-2xl font-mono text-xs animate-in slide-in-from-bottom duration-200">
          <CheckCircle2 className="w-4 h-4 text-primary shrink-0" />
          <span>{toastNotification}</span>
        </div>
      )}

      {/* Header Banner */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 bg-surface-container-low p-6 rounded-2xl border border-outline-variant/60 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <h1 className="text-2xl font-bold text-on-surface tracking-tight">90-Day Adaptive Placement Roadmap</h1>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-secondary-container/40 text-secondary text-xs font-mono border border-secondary/30">
              <Zap className="w-3.5 h-3.5 text-secondary" />
              Telemetry V4.2 · Adaptive Re-balancing Engine
            </span>
          </div>
          <p className="text-sm text-on-surface-variant max-w-2xl">
            Adaptive 90-day execution curriculum dynamically re-balanced based on your DSA accuracy, AST project audits, and ATS skill gap telemetry.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start lg:self-center shrink-0">
          <button
            onClick={handleRecalibrate}
            disabled={isAdapting}
            className="flex items-center gap-2 px-4 py-2 bg-surface-container-high hover:bg-surface-bright text-on-surface text-sm font-medium rounded-xl transition-all shadow-sm disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 text-primary ${isAdapting ? 'animate-spin' : ''}`} />
            <span>{isAdapting ? 'Re-balancing Schedule...' : 'Recalibrate Plan with AI'}</span>
          </button>
          <button
            onClick={() => navigate('/tasks')}
            className="flex items-center gap-1.5 px-4 py-2 bg-primary text-on-primary hover:bg-primary-fixed-dim text-sm font-semibold rounded-xl transition-all shadow-md"
          >
            <span>View Today's Tasks</span>
            <ArrowUpRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Overall Progress Summary Bar */}
      <div className="p-6 rounded-2xl bg-surface-container-low border border-outline-variant/60 space-y-4 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <span className="text-xs font-mono uppercase text-on-surface-variant tracking-wider block">Current Sprint & Progress</span>
            <h3 className="text-lg font-bold text-on-surface flex items-center gap-2">
              Day {roadmap.currentDay} of {roadmap.totalDays} · {roadmap.activeSprintName}
            </h3>
          </div>
          <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-tertiary-container/30 text-tertiary border border-tertiary/30 self-start sm:self-auto">
            {roadmap.overallProgressPercent}% Roadmap Completed
          </span>
        </div>

        <div className="w-full bg-surface-container rounded-full h-3 overflow-hidden border border-outline-variant/40">
          <div
            className="bg-gradient-to-r from-primary via-tertiary to-secondary h-full transition-all duration-500"
            style={{ width: `${roadmap.overallProgressPercent}%` }}
          ></div>
        </div>

        <div className="flex flex-wrap items-center justify-between text-xs font-mono text-on-surface-variant pt-1">
          <span>Completed: {roadmap.completedDaysCount} Days</span>
          <span>Last Adapted: {roadmap.lastAdapted}</span>
          <span>Remaining: {roadmap.totalDays - roadmap.completedDaysCount} Days</span>
        </div>
      </div>

      {/* Adaptive Re-balancing Alert Banner */}
      {roadmap.adaptiveRebalancingNotice && roadmap.adaptiveRebalancingNotice.isAdapted && (
        <div className="p-4 rounded-xl bg-secondary-container/15 border border-secondary/30 text-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-secondary flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-secondary" />
              Telemetry-Driven Adaptive Adjustment
            </span>
            <span className="font-mono text-[11px] text-on-surface-variant">
              Adapted {roadmap.adaptiveRebalancingNotice.adaptedAt}
            </span>
          </div>
          <p className="text-on-surface-variant font-sans">{roadmap.adaptiveRebalancingNotice.reason}</p>
          <div className="flex flex-wrap gap-2 pt-1">
            {roadmap.adaptiveRebalancingNotice.adjustments.map((adj, idx) => (
              <span key={idx} className="px-2 py-0.5 rounded bg-surface-container text-on-surface text-[11px] font-mono border border-outline-variant/40">
                • {adj}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Phase Timeline Tabs */}
      <div className="space-y-4">
        <div className="flex items-center gap-2 border-b border-outline-variant/60 pb-1 overflow-x-auto">
          {roadmap.phases.map((phase) => (
            <button
              key={phase.id}
              onClick={() => setActivePhaseId(phase.id)}
              className={`px-4 py-2.5 rounded-xl text-sm font-semibold transition-all whitespace-nowrap flex items-center gap-2 ${
                activePhaseId === phase.id
                  ? 'bg-primary text-on-primary shadow-sm'
                  : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container'
              }`}
            >
              <span>{phase.title}</span>
              <span className={`text-xs font-mono px-2 py-0.5 rounded-full ${
                phase.status === 'completed'
                  ? 'bg-tertiary-container/40 text-tertiary'
                  : phase.status === 'in-progress'
                  ? 'bg-secondary-container/40 text-secondary'
                  : 'bg-surface-container-high text-on-surface-variant'
              }`}>
                {phase.progressPercent}%
              </span>
            </button>
          ))}
        </div>

        {/* Selected Phase Details Card */}
        <div className="p-6 rounded-2xl bg-surface-container-low border border-outline-variant/60 space-y-4 shadow-sm">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-outline-variant/40">
            <div>
              <h3 className="font-bold text-on-surface text-lg">{activePhase.title}</h3>
              <p className="text-xs text-on-surface-variant font-mono">Days {activePhase.startDay} – {activePhase.endDay} ({activePhase.durationDays} Days Duration)</p>
            </div>
            <span className="px-3 py-1 rounded-full text-xs font-mono font-bold uppercase bg-surface-container text-primary border border-primary/30 self-start sm:self-auto">
              Status: {activePhase.status}
            </span>
          </div>

          <p className="text-sm text-on-surface-variant font-sans">{activePhase.subtitle}</p>

          <div className="space-y-2 pt-1">
            <span className="text-xs font-mono font-semibold uppercase tracking-wider text-primary block">
              Key Phase Milestones:
            </span>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {activePhase.milestones.map((m, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-surface-container border border-outline-variant/40 text-xs font-sans text-on-surface flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-tertiary shrink-0 mt-0.5" />
                  <span>{m}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Day 34 Execution Matrix */}
      <div className="bg-surface-container-low p-6 rounded-2xl border border-outline-variant/60 space-y-4 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-outline-variant/50">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-primary-container/20 text-primary border border-primary/30">
                ACTIVE DAY {roadmap.day34Details.dayNumber}
              </span>
              <h3 className="font-bold text-on-surface text-lg">{roadmap.day34Details.focusTitle}</h3>
            </div>
            <p className="text-xs text-on-surface-variant mt-0.5">{roadmap.day34Details.description}</p>
          </div>

          <div className="flex items-center gap-2 text-xs font-mono text-on-surface-variant self-start sm:self-auto">
            <Clock className="w-4 h-4 text-primary" />
            <span>Target: {roadmap.day34Details.recommendedHours}</span>
          </div>
        </div>

        {/* Day Tasks List */}
        <div className="space-y-3">
          <span className="text-xs font-mono uppercase font-semibold tracking-wider text-on-surface-variant block">
            Day 34 Action Items ({day34Tasks.filter((t) => t.completed).length} / {day34Tasks.length} Completed):
          </span>

          {day34Tasks.map((task) => (
            <div
              key={task.id}
              className={`p-4 rounded-xl border transition-all ${
                task.completed
                  ? 'bg-surface-container/40 border-outline-variant/40 opacity-75'
                  : 'bg-surface-container border-outline-variant hover:border-primary/40'
              } flex items-center justify-between gap-3`}
            >
              <div className="flex items-start gap-3 flex-1 min-w-0">
                <button
                  type="button"
                  onClick={() => toggleTaskCompletion(task.id)}
                  className="mt-0.5 shrink-0 text-on-surface-variant hover:text-primary transition-colors"
                >
                  <CheckCircle2
                    className={`w-5 h-5 ${
                      task.completed ? 'text-tertiary fill-tertiary/20' : 'text-outline'
                    }`}
                  />
                </button>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] font-mono uppercase font-semibold px-2 py-0.5 rounded bg-primary-container/20 text-primary border border-primary/30">
                      {task.category}
                    </span>
                    <span className="text-[10px] font-mono text-on-surface-variant flex items-center gap-1">
                      <Clock className="w-3 h-3" /> {task.duration}
                    </span>
                    <span
                      className={`text-[10px] font-mono uppercase px-1.5 py-0.5 rounded font-bold ${
                        task.priority === 'High' ? 'bg-secondary-container/30 text-secondary' : 'bg-surface-container-high text-on-surface-variant'
                      }`}
                    >
                      {task.priority}
                    </span>
                  </div>
                  <p className={`text-sm font-medium ${task.completed ? 'line-through text-on-surface-variant' : 'text-on-surface'}`}>
                    {task.title}
                  </p>
                </div>
              </div>

              <button
                onClick={() => navigate(task.route)}
                className="p-2 rounded-lg bg-surface-container-high text-on-surface-variant hover:text-on-surface hover:bg-surface-bright transition-colors shrink-0"
                title="Execute Task Module"
              >
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* AI Strategy Advice Banner */}
      <div className="p-6 rounded-2xl bg-surface-container-low border border-outline-variant/60 space-y-4 shadow-sm">
        <h3 className="font-semibold text-on-surface text-base flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-secondary" />
          Copilot Roadmap Optimization Strategy
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-surface-container border border-outline-variant/50 space-y-2">
            <h4 className="font-semibold text-sm text-on-surface">Daily Task Execution Matrix</h4>
            <p className="text-xs text-on-surface-variant leading-relaxed">
              Complete Today's 5 action items to maintain your 24-day active study streak.
            </p>
            <button
              onClick={() => navigate('/tasks')}
              className="text-xs font-semibold text-primary hover:underline inline-flex items-center gap-1 pt-1"
            >
              <span>Go to Today's Tasks</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="p-4 rounded-xl bg-surface-container border border-outline-variant/50 space-y-2">
            <h4 className="font-semibold text-sm text-on-surface">Track Completion Analytics</h4>
            <p className="text-xs text-on-surface-variant leading-relaxed">
              View your overall preparation velocity, weekly study hours, and module scores.
            </p>
            <button
              onClick={() => navigate('/progress')}
              className="text-xs font-semibold text-primary hover:underline inline-flex items-center gap-1 pt-1"
            >
              <span>View Progress Telemetry</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
