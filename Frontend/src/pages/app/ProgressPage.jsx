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
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 bg-surface-container-low p-6 rounded-2xl border border-outline-variant/60 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <h1 className="text-2xl font-bold text-on-surface tracking-tight">Progress Telemetry & Analytics</h1>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-secondary-container/40 text-secondary text-xs font-mono border border-secondary/30">
              <Zap className="w-3.5 h-3.5 text-secondary" />
              TELEMETRY V4.2 · PREPARATION ANALYTICS
            </span>
          </div>
          <p className="text-sm text-on-surface-variant max-w-2xl">
            Real-time preparation analytics tracking task completion velocity, daily study streak consistency, and 90-day adaptive roadmap milestones.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start lg:self-center shrink-0">
          <button
            onClick={() => navigate('/roadmap')}
            className="flex items-center gap-1.5 px-4 py-2 bg-primary text-on-primary hover:bg-primary-fixed-dim text-sm font-semibold rounded-xl transition-all shadow-md"
          >
            <span>View 90-Day Roadmap</span>
            <ArrowUpRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Key Metrics KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Overall Preparation Progress */}
        <div className="p-5 bg-surface-container-low rounded-2xl border border-outline-variant/60 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-on-surface-variant">Overall Preparation</span>
            <div className="p-2 rounded-xl bg-primary-container/20 text-primary">
              <TrendingUp className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-on-surface">{progress.overallProgressPercent}%</span>
          </div>
          <div className="mt-3 text-xs text-tertiary font-medium flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Target: Tier-1 SDE Screening Cutoff</span>
          </div>
        </div>

        {/* Card 2: Tasks Completion Ratio */}
        <div className="p-5 bg-surface-container-low rounded-2xl border border-outline-variant/60 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-on-surface-variant">Completed Tasks</span>
            <div className="p-2 rounded-xl bg-tertiary-container/20 text-tertiary">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-on-surface">{completedCount}</span>
            <span className="text-xs text-on-surface-variant font-mono">/ {totalCount} Active Tasks</span>
          </div>
          <div className="mt-3 text-xs text-on-surface-variant">
            Today's completion: <span className="text-tertiary font-semibold">{completionPercent}%</span>
          </div>
        </div>

        {/* Card 3: Active Streak */}
        <div className="p-5 bg-surface-container-low rounded-2xl border border-outline-variant/60 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-on-surface-variant">Active Streak</span>
            <div className="p-2 rounded-xl bg-secondary-container/20 text-secondary">
              <Flame className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-on-surface">{progress.currentStreakDays}</span>
            <span className="text-xs text-on-surface-variant font-mono">Days</span>
          </div>
          <div className="mt-3 text-xs text-on-surface-variant">
            Longest streak: <span className="text-secondary font-semibold">{progress.longestStreakDays} Days</span>
          </div>
        </div>

        {/* Card 4: Roadmap Completion */}
        <div className="p-5 bg-surface-container-low rounded-2xl border border-outline-variant/60 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-on-surface-variant">Roadmap Sprint</span>
            <div className="p-2 rounded-xl bg-surface-bright text-on-surface">
              <Calendar className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-on-surface">{roadmap.overallProgressPercent}%</span>
          </div>
          <div className="mt-3 text-xs text-on-surface-variant">
            Day {roadmap.currentDay} of {roadmap.totalDays} · Sprint 5
          </div>
        </div>
      </div>

      {/* Weekly Velocity Recharts Graph */}
      <div className="bg-surface-container-low p-6 rounded-2xl border border-outline-variant/60 space-y-4 shadow-sm">
        <div className="flex items-center justify-between pb-3 border-b border-outline-variant/50">
          <div>
            <h3 className="font-semibold text-on-surface text-base flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-primary" />
              Weekly Task Completion Velocity
            </h3>
            <p className="text-xs text-on-surface-variant">Completed tasks vs target velocity across 5 preparation weeks</p>
          </div>
          <span className="text-xs font-mono text-tertiary bg-tertiary-container/20 px-2.5 py-1 rounded border border-tertiary/30">
            Velocity Tracked
          </span>
        </div>

        <div className="h-60 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={progress.weeklyCompletionVelocity} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="velocityGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#4edea3" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#4edea3" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="week" stroke="#908fa0" fontSize={11} tickLine={false} />
              <YAxis stroke="#908fa0" fontSize={11} tickLine={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1c1f2a',
                  borderColor: '#464554',
                  borderRadius: '12px',
                  color: '#dfe2f1',
                  fontSize: '12px',
                }}
              />
              <Area type="monotone" dataKey="completed" stroke="#4edea3" strokeWidth={2.5} fillOpacity={1} fill="url(#velocityGrad)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Module-by-Module Progress Breakdown */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-on-surface text-lg">Preparation Module Telemetry Scores</h3>
          <span className="text-xs font-mono text-on-surface-variant">Showing 6 Module Scores</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {progress.moduleProgressBreakdown.map((item, idx) => (
            <div
              key={idx}
              className="p-5 rounded-2xl bg-surface-container-low border border-outline-variant/60 space-y-3 hover:border-primary/40 transition-colors shadow-sm flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-sm text-on-surface">{item.module}</span>
                  <span className="px-2.5 py-0.5 rounded text-xs font-mono font-bold bg-tertiary-container/30 text-tertiary border border-tertiary/30">
                    {item.score}%
                  </span>
                </div>
                <p className="text-xs text-on-surface-variant font-mono">{item.status}</p>
              </div>

              <button
                onClick={() => navigate(item.route)}
                className="text-xs font-semibold text-primary hover:underline inline-flex items-center gap-1 pt-2"
              >
                <span>View Module Details</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* AI Advice Banner */}
      <div className="p-6 rounded-2xl bg-surface-container-low border border-outline-variant/60 space-y-4 shadow-sm">
        <h3 className="font-semibold text-on-surface text-base flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-secondary" />
          Copilot Progress Insights
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-surface-container border border-outline-variant/50 space-y-2">
            <h4 className="font-semibold text-sm text-on-surface">Maintain Daily Action Plan Tasks</h4>
            <p className="text-xs text-on-surface-variant leading-relaxed">
              Completing 2 more tasks today will bring your daily execution to 100%.
            </p>
            <button
              onClick={() => navigate('/tasks')}
              className="text-xs font-semibold text-primary hover:underline inline-flex items-center gap-1 pt-1"
            >
              <span>Execute Today's Tasks</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="p-4 rounded-xl bg-surface-container border border-outline-variant/50 space-y-2">
            <h4 className="font-semibold text-sm text-on-surface">Review 90-Day Roadmap Sprint</h4>
            <p className="text-xs text-on-surface-variant leading-relaxed">
              Sprint 5 is 35% complete. Check Day 35-40 Graph & Caching milestones.
            </p>
            <button
              onClick={() => navigate('/roadmap')}
              className="text-xs font-semibold text-primary hover:underline inline-flex items-center gap-1 pt-1"
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
