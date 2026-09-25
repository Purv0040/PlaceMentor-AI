import React from 'react';
import { useNavigate } from 'react-router-dom';
import { usePlanning } from '../../context/PlanningContext';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, BarChart, Bar, Cell } from 'recharts';
import {
  Zap,
  TrendingUp,
  CheckCircle2,
  Flame,
  Calendar,
  Sparkles,
  ArrowUpRight,
  Clock,
  Target,
  BarChart3,
  Award
} from 'lucide-react';

export const ProgressPage = () => {
  const navigate = useNavigate();
  const { progress, tasks, roadmap } = usePlanning();

  const completedCount = tasks.filter((t) => t.completed).length;
  const totalCount = tasks.length;
  const completionPercent = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 bg-gradient-to-r from-indigo-950/60 via-purple-950/40 to-[#121624] p-6 rounded-2xl border border-indigo-500/30 shadow-xl backdrop-blur-md">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">Progress Telemetry & Analytics</h1>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 text-xs font-mono border border-cyan-500/30">
              <Zap className="w-3.5 h-3.5 text-cyan-400" />
              TELEMETRY V4.2 · PREPARATION ANALYTICS
            </span>
          </div>
          <p className="text-sm text-slate-300 max-w-2xl">
            Real-time preparation analytics tracking task completion velocity, daily study streak consistency, and 90-day adaptive roadmap milestones.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start lg:self-center shrink-0">
          <button
            onClick={() => navigate('/roadmap')}
            className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-sm font-semibold rounded-xl transition-all shadow-md shadow-indigo-600/25"
          >
            <span>View 90-Day Roadmap</span>
            <ArrowUpRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Key Metrics KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Overall Preparation Progress */}
        <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] shadow-lg">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400">Overall Preparation</span>
            <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <TrendingUp className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white">{progress.overallProgressPercent}%</span>
          </div>
          <div className="mt-3 text-xs text-emerald-400 font-medium flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Target: Tier-1 SDE Screening Cutoff</span>
          </div>
        </div>

        {/* Card 2: Tasks Completion Ratio */}
        <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] shadow-lg">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400">Completed Tasks</span>
            <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white">{completedCount}</span>
            <span className="text-xs text-slate-400 font-mono">/ {totalCount} Active Tasks</span>
          </div>
          <div className="mt-3 text-xs text-slate-400">
            Today's completion: <span className="text-emerald-400 font-semibold">{completionPercent}%</span>
          </div>
        </div>

        {/* Card 3: Active Streak */}
        <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] shadow-lg">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400">Active Streak</span>
            <div className="p-2 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <Flame className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white">{progress.currentStreakDays}</span>
            <span className="text-xs text-slate-400 font-mono">Days</span>
          </div>
          <div className="mt-3 text-xs text-slate-400">
            Longest streak: <span className="text-amber-400 font-semibold">{progress.longestStreakDays} Days</span>
          </div>
        </div>

        {/* Card 4: Roadmap Completion */}
        <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] shadow-lg">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400">Roadmap Sprint</span>
            <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <Calendar className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-white">{roadmap.overallProgressPercent}%</span>
          </div>
          <div className="mt-3 text-xs text-slate-400">
            Day {roadmap.currentDay} of {roadmap.totalDays} · Sprint 5
          </div>
        </div>
      </div>

      {/* Weekly Velocity Recharts Graph */}
      <div className="bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-lg">
        <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
          <div>
            <h3 className="font-semibold text-white text-base flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-indigo-400" />
              Weekly Task Completion Velocity
            </h3>
            <p className="text-xs text-slate-400">Completed tasks vs target velocity across 5 preparation weeks</p>
          </div>
          <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded border border-emerald-500/30">
            Velocity Tracked
          </span>
        </div>

        <div className="h-60 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={progress.weeklyCompletionVelocity} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="velocityGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#818cf8" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#818cf8" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="week" stroke="#64748b" fontSize={11} tickLine={false} />
              <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  borderColor: '#334155',
                  borderRadius: '12px',
                  color: '#f8fafc',
                  fontSize: '12px',
                }}
              />
              <Area type="monotone" dataKey="completed" stroke="#818cf8" strokeWidth={2.5} fillOpacity={1} fill="url(#velocityGrad)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Module-by-Module Progress Breakdown */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-white text-lg">Preparation Module Telemetry Scores</h3>
          <span className="text-xs font-mono text-slate-400">Showing 6 Module Scores</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {progress.moduleProgressBreakdown.map((item, idx) => (
            <div
              key={idx}
              className="p-5 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-3 hover:border-indigo-500/40 transition-all shadow-lg flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-sm text-white">{item.module}</span>
                  <span className="px-2.5 py-0.5 rounded text-xs font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                    {item.score}%
                  </span>
                </div>
                <p className="text-xs text-slate-400 font-mono">{item.status}</p>
              </div>

              <button
                onClick={() => navigate(item.route)}
                className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 hover:underline inline-flex items-center gap-1 pt-2"
              >
                <span>View Module Details</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* AI Advice Banner */}
      <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-lg">
        <h3 className="font-semibold text-white text-base flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-400" />
          Copilot Progress Insights
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-2">
            <h4 className="font-semibold text-sm text-white">Maintain Daily Action Plan Tasks</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Completing 2 more tasks today will bring your daily execution to 100%.
            </p>
            <button
              onClick={() => navigate('/tasks')}
              className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 hover:underline inline-flex items-center gap-1 pt-1"
            >
              <span>Execute Today's Tasks</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-2">
            <h4 className="font-semibold text-sm text-white">Review 90-Day Roadmap Sprint</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Sprint 5 is 35% complete. Check Day 35-40 Graph & Caching milestones.
            </p>
            <button
              onClick={() => navigate('/roadmap')}
              className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 hover:underline inline-flex items-center gap-1 pt-1"
            >
              <span>Go to 90-Day Roadmap</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
