import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { initialLeetcodeData } from '../../data/leetcodeData';
import { leetcodeService } from '../../services/leetcodeService';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';
import {
  Code,
  Zap,
  RefreshCw,
  ExternalLink,
  CheckCircle2,
  Trophy,
  Flame,
  Target,
  Sparkles,
  ArrowUpRight,
  Clock,
  Activity,
  Award
} from 'lucide-react';

export const LeetcodePage = () => {
  const navigate = useNavigate();
  const [data, setData] = useState(initialLeetcodeData);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isConnected, setIsConnected] = useState(true);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    const updated = await leetcodeService.syncProfile(data.handle);
    setData(updated);
    setIsRefreshing(false);
  };

  const handleToggleConnection = async () => {
    const nextState = await leetcodeService.toggleConnection(isConnected);
    setIsConnected(nextState);
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 bg-surface-container-low p-6 rounded-2xl border border-outline-variant/60 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <h1 className="text-2xl font-bold text-on-surface tracking-tight">LeetCode Intelligence</h1>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-secondary-container/40 text-secondary text-xs font-mono border border-secondary/30">
              <Zap className="w-3.5 h-3.5 text-secondary" />
              Telemetry V4.2 • DSA Diagnostic Engine
            </span>
          </div>
          <p className="text-sm text-on-surface-variant max-w-2xl">
            Analyze your DSA preparation, identify weak topics, and build a stronger problem-solving profile for Tier-1 coding screening cutoffs.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start lg:self-center shrink-0">
          <button
            onClick={handleRefresh}
            disabled={isRefreshing || !isConnected}
            className="flex items-center gap-2 px-4 py-2 bg-surface-container-high hover:bg-surface-bright text-on-surface text-sm font-medium rounded-xl transition-all shadow-sm disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 text-primary ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>{isRefreshing ? 'Syncing Stats...' : 'Refresh Analysis'}</span>
          </button>
          <a
            href={data.profileUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-4 py-2 bg-primary text-on-primary hover:bg-primary-fixed-dim text-sm font-semibold rounded-xl transition-all shadow-md"
          >
            <span>LeetCode Profile</span>
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>

      {/* Connection & Rank Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 p-4 rounded-xl bg-surface-container-low border border-outline-variant text-sm font-mono">
        <div className="flex items-center justify-between px-3 py-1.5 bg-surface-container rounded-lg border border-outline-variant/50">
          <span className="text-xs text-on-surface-variant">Profile Handle</span>
          <span className="text-on-surface font-semibold">@{data.handle}</span>
        </div>

        <div className="flex items-center justify-between px-3 py-1.5 bg-surface-container rounded-lg border border-outline-variant/50">
          <span className="text-xs text-on-surface-variant">Contest Rating</span>
          <span className="text-secondary font-bold flex items-center gap-1">
            <Trophy className="w-3.5 h-3.5 text-secondary" />
            {data.metrics.contestRating} ({data.metrics.rankTitle})
          </span>
        </div>

        <div className="flex items-center justify-between px-3 py-1.5 bg-surface-container rounded-lg border border-outline-variant/50">
          <span className="text-xs text-on-surface-variant">Global Rank</span>
          <span className="text-tertiary font-semibold">{data.metrics.globalRank}</span>
        </div>

        <div className="flex items-center justify-between px-3 py-1.5 bg-surface-container rounded-lg border border-outline-variant/50">
          <span className="text-xs text-on-surface-variant">Status</span>
          <span
            onClick={handleToggleConnection}
            className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-semibold cursor-pointer ${
              isConnected
                ? 'bg-tertiary-container/30 text-tertiary border border-tertiary/30'
                : 'bg-error-container/30 text-error border border-error/30'
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            {isConnected ? 'LeetCode Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      {/* Key Metrics KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Solved */}
        <div className="p-5 bg-surface-container-low rounded-2xl border border-outline-variant/60 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-on-surface-variant">Total Solved</span>
            <div className="p-2 rounded-xl bg-tertiary-container/20 text-tertiary">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-on-surface">{data.metrics.totalSolved}</span>
            <span className="text-xs text-on-surface-variant font-mono">/ {data.metrics.targetSolved} Target</span>
          </div>
          <div className="mt-3 text-xs text-on-surface-variant">
            Target progress: <span className="text-tertiary font-semibold">85% Complete</span>
          </div>
        </div>

        {/* Active Streak */}
        <div className="p-5 bg-surface-container-low rounded-2xl border border-outline-variant/60 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-on-surface-variant">Current Streak</span>
            <div className="p-2 rounded-xl bg-secondary-container/20 text-secondary">
              <Flame className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-on-surface">{data.metrics.currentStreakDays}</span>
            <span className="text-xs text-on-surface-variant font-mono">Days</span>
          </div>
          <div className="mt-3 text-xs text-on-surface-variant">
            Max Streak: <span className="text-secondary font-semibold">{data.metrics.longestStreakDays} Days</span>
          </div>
        </div>

        {/* Screening Readiness */}
        <div className="p-5 bg-surface-container-low rounded-2xl border border-outline-variant/60 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-on-surface-variant">DSA Readiness</span>
            <div className="p-2 rounded-xl bg-primary-container/20 text-primary">
              <Target className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-on-surface">{data.metrics.readinessScore}%</span>
          </div>
          <div className="mt-3 text-xs text-on-surface-variant">
            Cutoff benchmark: Tier-1 Screening Ready
          </div>
        </div>

        {/* Solved Active Days */}
        <div className="p-5 bg-surface-container-low rounded-2xl border border-outline-variant/60 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-on-surface-variant">Active Practice Days</span>
            <div className="p-2 rounded-xl bg-surface-bright text-on-surface">
              <Activity className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-on-surface">{data.metrics.activeDaysCount}</span>
            <span className="text-xs text-on-surface-variant font-mono">Days</span>
          </div>
          <div className="mt-3 text-xs text-on-surface-variant">
            Total submission activity
          </div>
        </div>
      </div>

      {/* Visualizers Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Difficulty Breakdown */}
        <div className="bg-surface-container-low p-6 rounded-2xl border border-outline-variant/60 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-outline-variant/50">
            <h3 className="font-semibold text-on-surface text-base">Difficulty Breakdown</h3>
            <span className="text-xs font-mono text-on-surface-variant">Solved vs Target</span>
          </div>

          <div className="h-48 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.difficultyChartData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                <XAxis dataKey="name" stroke="#908fa0" fontSize={11} tickLine={false} />
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
                <Bar dataKey="Solved" radius={[6, 6, 0, 0]}>
                  {data.difficultyChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-3 pt-2 border-t border-outline-variant/40">
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="text-tertiary font-medium">Easy ({data.difficultyBreakdown.easy.solved})</span>
              <span className="text-on-surface-variant">Target: {data.difficultyBreakdown.easy.target}</span>
            </div>
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="text-primary font-medium">Medium ({data.difficultyBreakdown.medium.solved})</span>
              <span className="text-on-surface-variant">Target: {data.difficultyBreakdown.medium.target}</span>
            </div>
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="text-error font-medium">Hard ({data.difficultyBreakdown.hard.solved})</span>
              <span className="text-on-surface-variant">Target: {data.difficultyBreakdown.hard.target}</span>
            </div>
          </div>
        </div>

        {/* Topic Mastery Matrix */}
        <div className="lg:col-span-2 bg-surface-container-low p-6 rounded-2xl border border-outline-variant/60 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-outline-variant/50">
            <div>
              <h3 className="font-semibold text-on-surface text-base">Topic Performance & Mastery</h3>
              <p className="text-xs text-on-surface-variant">Evaluated topic confidence against Tier-1 SDE cutoffs</p>
            </div>
            <span className="text-xs font-mono text-secondary bg-secondary-container/20 px-2.5 py-1 rounded border border-secondary/30">
              DSA Diagnostic
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {data.topicPerformance.map((topic, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-surface-container border border-outline-variant/40 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-on-surface">{topic.topic}</span>
                  <span className="font-mono text-secondary">{topic.score}%</span>
                </div>

                <div className="w-full bg-surface-container-high rounded-full h-2 overflow-hidden border border-outline-variant/30">
                  <div
                    className={`h-full transition-all duration-500 ${
                      topic.score >= 80 ? 'bg-tertiary' : topic.score >= 70 ? 'bg-primary' : 'bg-secondary'
                    }`}
                    style={{ width: `${topic.score}%` }}
                  ></div>
                </div>

                <div className="flex items-center justify-between text-[11px] font-mono text-on-surface-variant pt-1">
                  <span>Solved: {topic.solved} / {topic.target}</span>
                  <span className="font-semibold text-on-surface">{topic.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Activity Table */}
      <div className="bg-surface-container-low p-6 rounded-2xl border border-outline-variant/60 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-outline-variant/50">
          <h3 className="font-semibold text-on-surface text-base">Recent Solved Submissions</h3>
          <span className="text-xs font-mono text-on-surface-variant">Last 4 Submissions</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-outline-variant/40 text-[11px] font-mono uppercase text-on-surface-variant">
                <th className="py-2.5 px-3">Problem Title</th>
                <th className="py-2.5 px-3">Difficulty</th>
                <th className="py-2.5 px-3">Topic</th>
                <th className="py-2.5 px-3">Runtime</th>
                <th className="py-2.5 px-3">AI Rating</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/30 text-xs">
              {data.recentSubmissions.map((sub) => (
                <tr key={sub.id} className="hover:bg-surface-container/50 transition-colors">
                  <td className="py-3 px-3 font-semibold text-on-surface">{sub.title}</td>
                  <td className="py-3 px-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
                        sub.difficulty === 'Hard'
                          ? 'bg-error/20 text-error'
                          : sub.difficulty === 'Medium'
                          ? 'bg-primary-container/20 text-primary'
                          : 'bg-tertiary-container/20 text-tertiary'
                      }`}
                    >
                      {sub.difficulty}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-on-surface-variant font-mono">{sub.topic}</td>
                  <td className="py-3 px-3 text-on-surface-variant font-mono">{sub.runtime}</td>
                  <td className="py-3 px-3 font-semibold text-tertiary font-mono">{sub.aiRating}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* AI Recommendations Banner */}
      <div className="p-6 rounded-2xl bg-surface-container-low border border-outline-variant/60 space-y-4">
        <h3 className="font-semibold text-on-surface text-base flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-secondary" />
          Copilot LeetCode Diagnostic Advice
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.aiInsights.map((insight, idx) => (
            <div key={idx} className="p-4 rounded-xl bg-surface-container border border-outline-variant/50 space-y-2">
              <h4 className="font-semibold text-sm text-on-surface">{insight.title}</h4>
              <p className="text-xs text-on-surface-variant leading-relaxed">{insight.description}</p>
              <button
                onClick={() => navigate(insight.actionRoute)}
                className="text-xs font-semibold text-primary hover:underline inline-flex items-center gap-1 pt-1"
              >
                <span>{insight.actionLabel}</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
