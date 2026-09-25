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
      {/* 1. HERO BANNER */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6 p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-indigo-950/60 via-purple-950/40 to-[#121624] border border-indigo-500/30 shadow-2xl">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-400 text-xs font-mono font-semibold border border-indigo-500/30">
              <Zap className="w-3.5 h-3.5 text-indigo-400" />
              Telemetry V4.2 • AST Engine
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">GitHub Intelligence</h1>
          <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
            Understand how your GitHub profile represents your technical skills, code complexity, and project experience against Tier-1 SDE benchmarks.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start lg:self-center shrink-0">
          <button
            onClick={handleRefresh}
            disabled={isRefreshing || !isConnected}
            className="flex items-center gap-2 px-4 py-2.5 bg-[#1a2030] hover:bg-[#232b3e] text-slate-200 hover:text-white text-xs sm:text-sm font-semibold rounded-xl border border-[#232b3e] transition-all shadow-md disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 text-indigo-400 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>{isRefreshing ? 'Syncing AST Audit...' : 'Refresh Analysis'}</span>
          </button>
          <a
            href={data.profileUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs sm:text-sm font-semibold rounded-xl transition-all shadow-lg shadow-indigo-600/30 border border-indigo-400/30"
          >
            <span>GitHub Profile</span>
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>

      {/* 2. CONNECTION & STATUS BAR */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 p-4 rounded-2xl bg-[#121624] border border-[#232b3e] text-xs font-mono shadow-xl">
        <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e]">
          <span className="text-slate-400">Profile Handle</span>
          <span className="text-white font-bold">@{data.handle}</span>
        </div>

        <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e]">
          <span className="text-slate-400">Status</span>
          <div className="flex items-center gap-2">
            <span
              className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-lg text-xs font-semibold ${
                isConnected
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
              }`}
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              {isConnected ? 'GitHub Connected' : 'Disconnected'}
            </span>
            <button
              onClick={handleToggleConnection}
              title={isConnected ? 'Disconnect GitHub' : 'Connect GitHub'}
              className="p-1 rounded text-slate-400 hover:text-white hover:bg-[#1a2030] transition-colors"
            >
              <Power className={`w-3.5 h-3.5 ${isConnected ? 'text-rose-400' : 'text-emerald-400'}`} />
            </button>
          </div>
        </div>

        <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e]">
          <span className="text-slate-400">Last Synced</span>
          <span className="text-slate-200 font-semibold">{data.lastSynced}</span>
        </div>

        <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e]">
          <span className="text-slate-400">Repositories Audited</span>
          <span className="text-indigo-400 font-bold">{data.metrics.reposAnalyzedCount} Repos</span>
        </div>
      </div>

      {/* 3. KPI CARDS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Impact Score */}
        <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] hover:border-indigo-500/40 transition-colors shadow-xl">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">GitHub Impact Score</span>
            <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <Zap className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white font-mono">{data.metrics.githubImpactScore}</span>
            <span className="text-xs text-slate-400 font-mono">/ 100</span>
          </div>
          <div className="mt-3 flex items-center gap-1.5 text-xs text-emerald-400 font-mono font-semibold">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>{data.metrics.scorePercentile}</span>
          </div>
        </div>

        {/* Card 2: Total Commits & Streak */}
        <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] hover:border-amber-500/40 transition-colors shadow-xl">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">Commits & Active Streak</span>
            <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
              <GitCommit className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white font-mono">{data.metrics.totalCommits}</span>
            <span className="text-xs text-slate-400 font-mono">Commits</span>
          </div>
          <div className="mt-3 text-xs text-slate-300 font-medium">
            Current streak: <span className="text-amber-400 font-bold">{data.metrics.activeStreakDays} Days</span> (Max: {data.metrics.longestStreakDays}d)
          </div>
        </div>

        {/* Card 3: Repository Quality Index */}
        <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] hover:border-emerald-500/40 transition-colors shadow-xl">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">Repo Quality Index</span>
            <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <ShieldCheck className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white font-mono">{data.metrics.repoQualityIndex}%</span>
          </div>
          <div className="mt-3 text-xs text-slate-400 font-medium">
            AST verified architecture patterns
          </div>
        </div>

        {/* Card 4: Language Diversity */}
        <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] hover:border-purple-500/40 transition-colors shadow-xl">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">Languages Used</span>
            <div className="p-2.5 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400">
              <Code2 className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white font-mono">{data.metrics.languageCount}</span>
            <span className="text-xs text-slate-400 font-mono">Languages</span>
          </div>
          <div className="mt-3 text-xs text-slate-400 font-medium">
            Primary: <span className="text-indigo-400 font-semibold">TypeScript & Python</span>
          </div>
        </div>
      </div>

      {/* 4. VISUALIZERS GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Language Distribution Breakdown */}
        <div className="bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-xl">
          <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
            <h3 className="font-bold text-white text-base">Language Distribution</h3>
            <span className="text-xs font-mono text-indigo-400 font-semibold px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20">AST Byte Count</span>
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
                    backgroundColor: '#121624',
                    borderColor: '#232b3e',
                    borderRadius: '12px',
                    color: '#ffffff',
                    fontSize: '12px',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-2 pt-2 border-t border-[#232b3e]">
            {data.languages.map((lang, idx) => (
              <div key={idx} className="flex items-center justify-between text-xs font-mono">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: lang.color }}></span>
                  <span className="text-slate-200 font-semibold">{lang.name}</span>
                </div>
                <span className="text-indigo-400 font-bold">{lang.percentage}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Weekly Commit Velocity Chart */}
        <div className="lg:col-span-2 bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-xl">
          <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
            <div>
              <h3 className="font-bold text-white text-base">Commit Cadence & Code Complexity</h3>
              <p className="text-xs text-slate-400">Weekly engineering commit velocity vs AST complexity score</p>
            </div>
            <span className="text-xs font-mono font-semibold text-amber-400 bg-amber-500/10 px-2.5 py-1 rounded-lg border border-amber-500/20">
              Active Streak
            </span>
          </div>

          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.weeklyCadence} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="commitGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.5} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="week" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#121624',
                    borderColor: '#232b3e',
                    borderRadius: '12px',
                    color: '#ffffff',
                    fontSize: '12px',
                  }}
                />
                <Area type="monotone" dataKey="commits" stroke="#6366f1" strokeWidth={2.5} fillOpacity={1} fill="url(#commitGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 5. REPOSITORY AUDIT GRID */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-white text-lg">Audited Repositories</h3>
          <span className="text-xs font-mono text-slate-400">Showing {data.repositories.length} Primary Repos</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.repositories.map((repo) => (
            <div
              key={repo.id}
              className="p-5 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 hover:border-indigo-500/40 transition-colors shadow-xl"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2">
                  <GitBranch className="w-5 h-5 text-indigo-400 shrink-0" />
                  <h4 className="font-bold text-white text-base hover:text-indigo-400 transition-colors cursor-pointer">
                    {repo.name}
                  </h4>
                </div>
                <span className="px-2.5 py-1 rounded-full text-xs font-mono font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 shrink-0">
                  AST {repo.astScore}%
                </span>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed line-clamp-2">
                {repo.description}
              </p>

              {/* Tech Tags */}
              <div className="flex flex-wrap gap-1.5">
                {repo.tags.map((tag, idx) => (
                  <span
                    key={idx}
                    className="px-2.5 py-1 rounded-lg bg-[#0f131d] text-slate-200 text-[11px] font-mono border border-[#232b3e]"
                  >
                    {tag}
                  </span>
                ))}
              </div>

              <div className="pt-3 border-t border-[#232b3e] flex items-center justify-between text-xs text-slate-400 font-mono">
                <div className="flex items-center gap-3">
                  <span className="flex items-center gap-1 text-slate-200 font-semibold">
                    <Star className="w-3.5 h-3.5 text-amber-400" />
                    {repo.stars}
                  </span>
                  <span className="flex items-center gap-1 text-slate-300">
                    <GitFork className="w-3.5 h-3.5 text-slate-400" />
                    {repo.forks}
                  </span>
                </div>
                <span className="text-indigo-400 font-bold">{repo.qualityTier}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 6. AI RECOMMENDATIONS BANNER */}
      <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-xl">
        <h3 className="font-bold text-white text-base flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-400" />
          Copilot GitHub Telemetry Advice
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.aiInsights.map((insight, idx) => (
            <div key={idx} className="p-4 rounded-xl bg-[#0f131d] border border-[#232b3e] space-y-2 hover:border-purple-500/40 transition-colors">
              <h4 className="font-bold text-sm text-white">{insight.title}</h4>
              <p className="text-xs text-slate-300 leading-relaxed">{insight.description}</p>
              <button
                onClick={() => navigate(insight.actionRoute)}
                className="text-xs font-bold text-indigo-400 hover:text-indigo-300 inline-flex items-center gap-1 pt-1"
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
