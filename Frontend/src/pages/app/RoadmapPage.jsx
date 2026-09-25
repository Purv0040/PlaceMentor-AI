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
        <div className="fixed bottom-10 right-6 z-50 flex items-center gap-2 px-4 py-3 bg-[#121624] border border-indigo-500/40 text-white rounded-xl shadow-2xl font-mono text-xs animate-in slide-in-from-bottom duration-200">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{toastNotification}</span>
        </div>
      )}

      {/* 1. HERO BANNER */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6 p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-indigo-950/60 via-purple-950/40 to-[#121624] border border-indigo-500/30 shadow-2xl">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-400 text-xs font-mono font-semibold border border-indigo-500/30">
              <Zap className="w-3.5 h-3.5 text-indigo-400" />
              Telemetry V4.2 · Adaptive Re-balancing Engine
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">90-Day Adaptive Placement Roadmap</h1>
          <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
            Adaptive 90-day execution curriculum dynamically re-balanced based on your DSA accuracy, AST project audits, and ATS skill gap telemetry.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start lg:self-center shrink-0">
          <button
            onClick={handleRecalibrate}
            disabled={isAdapting}
            className="flex items-center gap-2 px-4 py-2.5 bg-[#1a2030] hover:bg-[#232b3e] text-slate-200 hover:text-white text-xs sm:text-sm font-semibold rounded-xl border border-[#232b3e] transition-all shadow-md disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 text-indigo-400 ${isAdapting ? 'animate-spin' : ''}`} />
            <span>{isAdapting ? 'Re-balancing Schedule...' : 'Recalibrate Plan with AI'}</span>
          </button>
          <button
            onClick={() => navigate('/tasks')}
            className="flex items-center gap-1.5 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs sm:text-sm font-semibold rounded-xl transition-all shadow-lg shadow-indigo-600/30 border border-indigo-400/30"
          >
            <span>View Today's Tasks</span>
            <ArrowUpRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 2. OVERALL PROGRESS SUMMARY BAR */}
      <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <span className="text-xs font-mono uppercase text-slate-400 font-semibold tracking-wider block">Current Sprint & Progress</span>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              Day {roadmap.currentDay} of {roadmap.totalDays} · {roadmap.activeSprintName}
            </h3>
          </div>
          <span className="px-3 py-1.5 rounded-full text-xs font-mono font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 self-start sm:self-auto">
            {roadmap.overallProgressPercent}% Roadmap Completed
          </span>
        </div>

        <div className="w-full bg-[#0f131d] rounded-full h-3 overflow-hidden border border-[#232b3e]">
          <div
            className="bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-400 h-full rounded-full transition-all duration-500 shadow-sm"
            style={{ width: `${roadmap.overallProgressPercent}%` }}
          ></div>
        </div>

        <div className="flex flex-wrap items-center justify-between text-xs font-mono text-slate-400 pt-1">
          <span>Completed: {roadmap.completedDaysCount} Days</span>
          <span>Last Adapted: {roadmap.lastAdapted}</span>
          <span>Remaining: {roadmap.totalDays - roadmap.completedDaysCount} Days</span>
        </div>
      </div>

      {/* 3. ADAPTIVE RE-BALANCING ALERT BANNER */}
      {roadmap.adaptiveRebalancingNotice && roadmap.adaptiveRebalancingNotice.isAdapted && (
        <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-bold text-amber-400 flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-purple-400" />
              Telemetry-Driven Adaptive Adjustment
            </span>
            <span className="font-mono text-[11px] text-slate-400">
              Adapted {roadmap.adaptiveRebalancingNotice.adaptedAt}
            </span>
          </div>
          <p className="text-slate-300 font-sans">{roadmap.adaptiveRebalancingNotice.reason}</p>
          <div className="flex flex-wrap gap-2 pt-1">
            {roadmap.adaptiveRebalancingNotice.adjustments.map((adj, idx) => (
              <span key={idx} className="px-2.5 py-1 rounded-lg bg-[#0f131d] text-slate-200 text-[11px] font-mono border border-[#232b3e]">
                • {adj}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* 4. PHASE TIMELINE TABS */}
      <div className="space-y-4">
        <div className="flex items-center gap-2 border-b border-[#232b3e] pb-2 overflow-x-auto">
          {roadmap.phases.map((phase) => (
            <button
              key={phase.id}
              onClick={() => setActivePhaseId(phase.id)}
              className={`px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition-all whitespace-nowrap flex items-center gap-2 ${
                activePhaseId === phase.id
                  ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-600/30 border border-indigo-400/30'
                  : 'bg-[#121624] text-slate-400 hover:text-white hover:bg-[#1a2030] border border-[#232b3e]'
              }`}
            >
              <span>{phase.title}</span>
              <span className={`text-xs font-mono px-2 py-0.5 rounded-full font-bold ${
                phase.status === 'completed'
                  ? 'bg-emerald-500/20 text-emerald-400'
                  : phase.status === 'in-progress'
                  ? 'bg-amber-500/20 text-amber-400'
                  : 'bg-[#1a2030] text-slate-400'
              }`}>
                {phase.progressPercent}%
              </span>
            </button>
          ))}
        </div>

        {/* Selected Phase Details Card */}
        <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-[#232b3e]">
            <div>
              <h3 className="font-bold text-white text-lg">{activePhase.title}</h3>
              <p className="text-xs text-slate-400 font-mono">Days {activePhase.startDay} – {activePhase.endDay} ({activePhase.durationDays} Days Duration)</p>
            </div>
            <span className="px-3 py-1 rounded-full text-xs font-mono font-bold uppercase bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 self-start sm:self-auto">
              Status: {activePhase.status}
            </span>
          </div>

          <p className="text-xs sm:text-sm text-slate-300 font-sans">{activePhase.subtitle}</p>

          <div className="space-y-2 pt-1">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-indigo-400 block">
              Key Phase Milestones:
            </span>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {activePhase.milestones.map((m, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-[#0f131d] border border-[#232b3e] text-xs font-sans text-slate-200 flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <span>{m}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 5. DAY 34 EXECUTION MATRIX */}
      <div className="bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#232b3e]">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-1 rounded-full text-xs font-mono font-bold bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                ACTIVE DAY {roadmap.day34Details.dayNumber}
              </span>
              <h3 className="font-bold text-white text-lg">{roadmap.day34Details.focusTitle}</h3>
            </div>
            <p className="text-xs text-slate-400 mt-1">{roadmap.day34Details.description}</p>
          </div>

          <div className="flex items-center gap-2 text-xs font-mono text-slate-400 self-start sm:self-auto">
            <Clock className="w-4 h-4 text-indigo-400" />
            <span>Target: {roadmap.day34Details.recommendedHours}</span>
          </div>
        </div>

        {/* Day Tasks List */}
        <div className="space-y-3">
          <span className="text-xs font-mono uppercase font-bold tracking-wider text-slate-400 block">
            Day 34 Action Items ({day34Tasks.filter((t) => t.completed).length} / {day34Tasks.length} Completed):
          </span>

          {day34Tasks.map((task) => (
            <div
              key={task.id}
              className={`p-4 rounded-xl border transition-all ${
                task.completed
                  ? 'bg-[#0f131d]/60 border-[#232b3e] opacity-75'
                  : 'bg-[#0f131d] border-[#232b3e] hover:border-indigo-500/40'
              } flex items-center justify-between gap-3`}
            >
              <div className="flex items-start gap-3 flex-1 min-w-0">
                <button
                  type="button"
                  onClick={() => toggleTaskCompletion(task.id)}
                  className="mt-0.5 shrink-0 text-slate-400 hover:text-indigo-400 transition-colors"
                >
                  <CheckCircle2
                    className={`w-5 h-5 ${
                      task.completed ? 'text-emerald-400 fill-emerald-500/20' : 'text-slate-500'
                    }`}
                  />
                </button>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] font-mono uppercase font-bold px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                      {task.category}
                    </span>
                    <span className="text-[10px] font-mono text-slate-400 flex items-center gap-1">
                      <Clock className="w-3 h-3" /> {task.duration}
                    </span>
                    <span
                      className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded font-bold ${
                        task.priority === 'High' ? 'bg-amber-500/20 text-amber-400' : 'bg-[#1a2030] text-slate-400'
                      }`}
                    >
                      {task.priority}
                    </span>
                  </div>
                  <p className={`text-xs sm:text-sm font-semibold ${task.completed ? 'line-through text-slate-400' : 'text-white'}`}>
                    {task.title}
                  </p>
                </div>
              </div>

              <button
                onClick={() => navigate(task.route)}
                className="p-2 rounded-lg bg-[#1a2030] text-slate-300 hover:text-white hover:bg-[#232b3e] transition-colors shrink-0"
                title="Execute Task Module"
              >
                <ArrowRight className="w-4 h-4 text-indigo-400" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* 6. AI STRATEGY ADVICE BANNER */}
      <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-xl">
        <h3 className="font-bold text-white text-base flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-400" />
          Copilot Roadmap Optimization Strategy
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-[#0f131d] border border-[#232b3e] space-y-2 hover:border-purple-500/40 transition-colors">
            <h4 className="font-bold text-sm text-white">Daily Task Execution Matrix</h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              Complete Today's 5 action items to maintain your 24-day active study streak.
            </p>
            <button
              onClick={() => navigate('/tasks')}
              className="text-xs font-bold text-indigo-400 hover:text-indigo-300 inline-flex items-center gap-1 pt-1"
            >
              <span>Go to Today's Tasks</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="p-4 rounded-xl bg-[#0f131d] border border-[#232b3e] space-y-2 hover:border-purple-500/40 transition-colors">
            <h4 className="font-bold text-sm text-white">Track Completion Analytics</h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              View your overall preparation velocity, weekly study hours, and module scores.
            </p>
            <button
              onClick={() => navigate('/progress')}
              className="text-xs font-bold text-indigo-400 hover:text-indigo-300 inline-flex items-center gap-1 pt-1"
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
