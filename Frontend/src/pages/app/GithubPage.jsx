import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { githubService } from '../../services/githubService';
import { initialGithubData } from '../../data/githubData';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, AreaChart, Area, XAxis, YAxis } from 'recharts';
import {
  GitBranch,
  GitCommit,
  RefreshCw,
  ExternalLink,
  Zap,
  CheckCircle2,
  Star,
  GitFork,
  Code2,
  Sparkles,
  ArrowUpRight,
  TrendingUp,
  ShieldCheck,
  Power
} from 'lucide-react';

export const GithubPage = () => {
  const navigate = useNavigate();
  const [data, setData] = useState(initialGithubData);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isConnected, setIsConnected] = useState(true);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    const updated = await githubService.syncProfile(data.handle);
    setData(updated);
    setIsRefreshing(false);
  };

  const handleToggleConnection = async () => {
    const nextState = await githubService.toggleConnection(isConnected);
    setIsConnected(nextState);
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 bg-surface-container-low p-6 rounded-2xl border border-outline-variant/60 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <h1 className="text-2xl font-bold text-on-surface tracking-tight">GitHub Intelligence</h1>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-secondary-container/40 text-secondary text-xs font-mono border border-secondary/30">
              <Zap className="w-3.5 h-3.5 text-secondary" />
              Telemetry V4.2 • AST Engine
            </span>
          </div>
          <p className="text-sm text-on-surface-variant max-w-2xl">
            Understand how your GitHub profile represents your technical skills, code complexity, and project experience against Tier-1 SDE benchmarks.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start lg:self-center shrink-0">
          <button
            onClick={handleRefresh}
            disabled={isRefreshing || !isConnected}
            className="flex items-center gap-2 px-4 py-2 bg-surface-container-high hover:bg-surface-bright text-on-surface text-sm font-medium rounded-xl transition-all shadow-sm disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 text-primary ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>{isRefreshing ? 'Syncing AST Audit...' : 'Refresh Analysis'}</span>
          </button>
          <a
            href={data.profileUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-4 py-2 bg-primary text-on-primary hover:bg-primary-fixed-dim text-sm font-semibold rounded-xl transition-all shadow-md"
          >
            <span>GitHub Profile</span>
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>

      {/* Connection & Status Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 p-4 rounded-xl bg-surface-container-low border border-outline-variant text-sm font-mono">
        <div className="flex items-center justify-between px-3 py-1.5 bg-surface-container rounded-lg border border-outline-variant/50">
          <span className="text-xs text-on-surface-variant">Profile Handle</span>
          <span className="text-on-surface font-semibold">@{data.handle}</span>
        </div>

        <div className="flex items-center justify-between px-3 py-1.5 bg-surface-container rounded-lg border border-outline-variant/50">
          <span className="text-xs text-on-surface-variant">Status</span>
          <div className="flex items-center gap-2">
            <span
              className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-semibold ${
                isConnected
                  ? 'bg-tertiary-container/30 text-tertiary border border-tertiary/30'
                  : 'bg-error-container/30 text-error border border-error/30'
              }`}
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              {isConnected ? 'GitHub Connected' : 'Disconnected'}
            </span>
            <button
              onClick={handleToggleConnection}
              title={isConnected ? 'Disconnect GitHub' : 'Connect GitHub'}
              className="p-1 rounded text-on-surface-variant hover:text-on-surface hover:bg-surface-bright transition-colors"
            >
              <Power className={`w-3.5 h-3.5 ${isConnected ? 'text-error' : 'text-tertiary'}`} />
            </button>
          </div>
        </div>

        <div className="flex items-center justify-between px-3 py-1.5 bg-surface-container rounded-lg border border-outline-variant/50">
          <span className="text-xs text-on-surface-variant">Last Synced</span>
          <span className="text-on-surface">{data.lastSynced}</span>
        </div>

        <div className="flex items-center justify-between px-3 py-1.5 bg-surface-container rounded-lg border border-outline-variant/50">
          <span className="text-xs text-on-surface-variant">Repositories Audited</span>
          <span className="text-primary font-bold">{data.metrics.reposAnalyzedCount} Repos</span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Impact Score */}
        <div className="p-5 bg-surface-container-low rounded-2xl border border-outline-variant/60 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-on-surface-variant">GitHub Impact Score</span>
            <div className="p-2 rounded-xl bg-primary-container/20 text-primary">
              <Zap className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-on-surface">{data.metrics.githubImpactScore}</span>
            <span className="text-xs text-on-surface-variant font-mono">/ 100</span>
          </div>
          <div className="mt-3 flex items-center gap-1 text-xs text-tertiary font-medium">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>{data.metrics.scorePercentile}</span>
          </div>
        </div>

        {/* Card 2: Total Commits & Streak */}
        <div className="p-5 bg-surface-container-low rounded-2xl border border-outline-variant/60 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-on-surface-variant">Commits & Active Streak</span>
            <div className="p-2 rounded-xl bg-tertiary-container/20 text-tertiary">
              <GitCommit className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-on-surface">{data.metrics.totalCommits}</span>
            <span className="text-xs text-on-surface-variant font-mono">Commits</span>
          </div>
          <div className="mt-3 text-xs text-on-surface-variant">
            Current streak: <span className="text-tertiary font-semibold">{data.metrics.activeStreakDays} Days</span> (Max: {data.metrics.longestStreakDays}d)
          </div>
        </div>

        {/* Card 3: Repository Quality Index */}
        <div className="p-5 bg-surface-container-low rounded-2xl border border-outline-variant/60 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-on-surface-variant">Repo Quality Index</span>
            <div className="p-2 rounded-xl bg-secondary-container/20 text-secondary">
              <ShieldCheck className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-on-surface">{data.metrics.repoQualityIndex}%</span>
          </div>
          <div className="mt-3 text-xs text-on-surface-variant">
            AST verified architecture patterns
          </div>
        </div>

        {/* Card 4: Language Diversity */}
        <div className="p-5 bg-surface-container-low rounded-2xl border border-outline-variant/60 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-on-surface-variant">Languages Used</span>
            <div className="p-2 rounded-xl bg-surface-bright text-on-surface">
              <Code2 className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-on-surface">{data.metrics.languageCount}</span>
            <span className="text-xs text-on-surface-variant font-mono">Languages</span>
          </div>
          <div className="mt-3 text-xs text-on-surface-variant">
            Primary: <span className="text-primary font-semibold">TypeScript & Python</span>
          </div>
        </div>
      </div>

      {/* Visualizers Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Language Distribution Breakdown */}
        <div className="bg-surface-container-low p-6 rounded-2xl border border-outline-variant/60 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-outline-variant/50">
            <h3 className="font-semibold text-on-surface text-base">Language Distribution</h3>
            <span className="text-xs font-mono text-on-surface-variant">AST Byte Count</span>
          </div>

          <div className="h-48 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.languages}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={4}
                  dataKey="percentage"
                >
                  {data.languages.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1c1f2a',
                    borderColor: '#464554',
                    borderRadius: '12px',
                    color: '#dfe2f1',
                    fontSize: '12px',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-2 pt-2 border-t border-outline-variant/40">
            {data.languages.map((lang, idx) => (
              <div key={idx} className="flex items-center justify-between text-xs font-mono">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: lang.color }}></span>
                  <span className="text-on-surface font-medium">{lang.name}</span>
                </div>
                <span className="text-on-surface-variant font-semibold">{lang.percentage}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Weekly Commit Velocity Chart */}
        <div className="lg:col-span-2 bg-surface-container-low p-6 rounded-2xl border border-outline-variant/60 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-outline-variant/50">
            <div>
              <h3 className="font-semibold text-on-surface text-base">Commit Cadence & Code Complexity</h3>
              <p className="text-xs text-on-surface-variant">Weekly engineering commit velocity vs AST complexity score</p>
            </div>
            <span className="text-xs font-mono text-tertiary bg-tertiary-container/20 px-2.5 py-1 rounded border border-tertiary/30">
              Active Streak
            </span>
          </div>

          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.weeklyCadence} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="commitGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8083ff" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#8083ff" stopOpacity={0} />
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
                <Area type="monotone" dataKey="commits" stroke="#8083ff" strokeWidth={2} fillOpacity={1} fill="url(#commitGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Repository Audit Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-on-surface text-lg">Audited Repositories</h3>
          <span className="text-xs font-mono text-on-surface-variant">Showing {data.repositories.length} Primary Repos</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.repositories.map((repo) => (
            <div
              key={repo.id}
              className="p-5 rounded-2xl bg-surface-container-low border border-outline-variant/60 space-y-4 hover:border-primary/40 transition-colors"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2">
                  <GitBranch className="w-5 h-5 text-primary shrink-0" />
                  <h4 className="font-semibold text-on-surface text-base hover:text-primary transition-colors cursor-pointer">
                    {repo.name}
                  </h4>
                </div>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-semibold bg-tertiary-container/30 text-tertiary border border-tertiary/30 shrink-0">
                  AST {repo.astScore}%
                </span>
              </div>

              <p className="text-xs text-on-surface-variant leading-relaxed line-clamp-2">
                {repo.description}
              </p>

              {/* Tech Tags */}
              <div className="flex flex-wrap gap-1.5">
                {repo.tags.map((tag, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-0.5 rounded bg-surface-container text-on-surface text-[11px] font-mono border border-outline-variant/40"
                  >
                    {tag}
                  </span>
                ))}
              </div>

              <div className="pt-3 border-t border-outline-variant/40 flex items-center justify-between text-xs text-on-surface-variant font-mono">
                <div className="flex items-center gap-3">
                  <span className="flex items-center gap-1 text-on-surface">
                    <Star className="w-3.5 h-3.5 text-secondary" />
                    {repo.stars}
                  </span>
                  <span className="flex items-center gap-1">
                    <GitFork className="w-3.5 h-3.5" />
                    {repo.forks}
                  </span>
                </div>
                <span className="text-primary font-medium">{repo.qualityTier}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* AI Recommendations Banner */}
      <div className="p-6 rounded-2xl bg-surface-container-low border border-outline-variant/60 space-y-4">
        <h3 className="font-semibold text-on-surface text-base flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-secondary" />
          Copilot GitHub Telemetry Advice
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
