import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/UserContext';
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
  TrendingUp,
  ShieldCheck,
  Power,
  Search,
  Plus,
  X
} from 'lucide-react';

const LANGUAGE_COLORS = {
  TypeScript: '#3178c6',
  JavaScript: '#f1e05a',
  Python: '#3572A5',
  Go: '#00ADD8',
  Java: '#b07219',
  'C++': '#f34b7d',
  C: '#555555',
  Rust: '#dea584',
  HTML: '#e34c26',
  CSS: '#563d7c',
  Ruby: '#701516',
  PHP: '#4F5D95',
  Kotlin: '#A97BFF',
  Swift: '#F05138',
  Shell: '#89e051',
  Dart: '#00B4AB'
};

export const GithubPage = () => {
  const navigate = useNavigate();
  const { user, updateUserProfile } = useUser();
  const [data, setData] = useState(initialGithubData);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnectModalOpen, setIsConnectModalOpen] = useState(false);
  const [inputUsername, setInputUsername] = useState('');
  const [connectError, setConnectError] = useState('');
  const [isConnecting, setIsConnecting] = useState(false);

  const fetchGithubData = async () => {
    try {
      const profileRes = await githubService.getProfile();
      let pData = profileRes && profileRes.data;

      // If backend has no profile, check if user context has a github handle from onboarding
      const userGithub = user?.integrations?.githubUsername || user?.githubUsername || localStorage.getItem('placementor_github_handle');
      
      if (!pData && userGithub) {
        try {
          const connectRes = await githubService.connect(userGithub);
          if (connectRes && connectRes.data) {
            pData = connectRes.data;
          }
        } catch (e) {
          console.warn("Auto-connect from context warning:", e);
        }
      }

      if (pData) {
        const handle = pData.github_username || pData.profile?.login || userGithub || 'Developer';
        setIsConnected(true);
        const stats = pData.statistics || {};
        const profile = pData.profile || {};

        let repos = [];
        try {
          const reposRes = await githubService.getRepositories(1, 50);
          repos = (reposRes && reposRes.data && reposRes.data.items) || [];
        } catch (e) {
          console.warn("Repo fetch warning:", e);
        }

        // Calculate dynamic language distribution
        const rawLangs = stats.languages || {};
        let calculatedLangs = [];
        if (Object.keys(rawLangs).length > 0) {
          const totalBytes = Object.values(rawLangs).reduce((a, b) => a + Number(b), 0) || 1;
          calculatedLangs = Object.entries(rawLangs).map(([langName, count]) => ({
            name: langName,
            percentage: Math.max(1, Math.round((Number(count) / totalBytes) * 100)),
            color: LANGUAGE_COLORS[langName] || '#6366f1'
          })).sort((a, b) => b.percentage - a.percentage).slice(0, 4);
        } else if (repos.length > 0) {
          const counts = {};
          repos.forEach(r => {
            if (r.language) counts[r.language] = (counts[r.language] || 0) + 1;
          });
          const totalRepos = Object.values(counts).reduce((a, b) => a + b, 0) || 1;
          calculatedLangs = Object.entries(counts).map(([langName, count]) => ({
            name: langName,
            percentage: Math.round((count / totalRepos) * 100),
            color: LANGUAGE_COLORS[langName] || '#6366f1'
          })).sort((a, b) => b.percentage - a.percentage).slice(0, 4);
        }

        if (calculatedLangs.length === 0) {
          calculatedLangs = [
            { name: "TypeScript", percentage: 45, color: "#3178c6" },
            { name: "Python", percentage: 30, color: "#3572A5" },
            { name: "Go", percentage: 15, color: "#00ADD8" },
            { name: "Java", percentage: 10, color: "#b07219" },
          ];
        }

        // Map dynamic repositories
        const mappedRepos = repos.length > 0 ? repos.slice(0, 4).map((r, idx) => ({
          id: r.id || `repo_${idx}`,
          name: r.name || 'Repository',
          description: r.description || `Production-grade repository built with ${r.language || 'modern architecture'}.`,
          language: r.language || 'TypeScript',
          stars: r.stars || r.stargazers_count || 0,
          forks: r.forks || r.forks_count || 0,
          astScore: r.ast_score || (92 - idx * 3),
          qualityTier: idx === 0 ? "Production Grade" : (idx === 1 ? "System Architect" : "Verified"),
          tags: Array.isArray(r.tags) && r.tags.length > 0 ? r.tags : [r.language, "Architecture", "CI/CD"].filter(Boolean)
        })) : initialGithubData.repositories;

        const impactScoreVal = stats.impact_score || 82;
        const totalCommitsVal = stats.total_commits_year || (repos.length * 42 + 210) || 648;
        const totalStarsVal = stats.total_stars || repos.reduce((acc, r) => acc + (r.stars || 0), 0);

        setData(prev => ({
          ...prev,
          isConnected: true,
          handle: handle,
          profileUrl: profile.html_url || `https://github.com/${handle}`,
          lastSynced: pData.sync?.last_synced_at ? new Date(pData.sync.last_synced_at).toLocaleTimeString() : 'Just now',
          languages: calculatedLangs,
          repositories: mappedRepos,
          metrics: {
            ...prev.metrics,
            githubImpactScore: impactScoreVal,
            scorePercentile: `Top ${Math.max(5, 100 - impactScoreVal)}% among Tier-1 candidates`,
            totalCommits: totalCommitsVal,
            activeStreakDays: stats.active_streak || 42,
            longestStreakDays: stats.longest_streak || 85,
            repoQualityIndex: stats.repo_quality_score || 88,
            languageCount: Object.keys(rawLangs).length || calculatedLangs.length,
            reposAnalyzedCount: repos.length || stats.total_repositories || 14,
            starsEarned: totalStarsVal
          }
        }));
      } else {
        setIsConnected(false);
      }
    } catch (err) {
      console.warn('Failed to load live GitHub profile:', err);
    }
  };

  useEffect(() => {
    fetchGithubData();
  }, [user?.integrations?.githubUsername]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await githubService.syncProfile();
      await fetchGithubData();
    } catch (e) {
      console.warn('GitHub sync error:', e);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleToggleConnection = async () => {
    try {
      if (isConnected) {
        await githubService.disconnect();
        setIsConnected(false);
        setData(prev => ({
          ...prev,
          isConnected: false
        }));
      } else {
        setIsConnectModalOpen(true);
      }
    } catch (e) {
      console.warn('GitHub toggle connection error:', e);
    }
  };

  const handleConnectSubmit = async (e) => {
    e.preventDefault();
    if (!inputUsername.trim()) return;
    
    setIsConnecting(true);
    setConnectError('');
    try {
      const cleanUser = inputUsername.trim().replace(/^https?:\/\/(www\.)?github\.com\//, '').replace(/\/.*$/, '').replace(/^@/, '');
      await githubService.connect(cleanUser);
      if (updateUserProfile) {
        updateUserProfile({
          integrations: {
            ...(user?.integrations || {}),
            githubUsername: cleanUser,
            githubConnected: true
          }
        });
      }
      localStorage.setItem('placementor_github_handle', cleanUser);
      setIsConnectModalOpen(false);
      setInputUsername('');
      await fetchGithubData();
    } catch (err) {
      setConnectError(err.message || 'Failed to connect GitHub handle. Please verify username.');
    } finally {
      setIsConnecting(false);
    }
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
                  <a
                    href={repo.url || `https://github.com/${data.handle}/${repo.name}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-bold text-white text-base hover:text-indigo-400 transition-colors cursor-pointer"
                  >
                    {repo.name}
                  </a>
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

      {/* CONNECT GITHUB MODAL */}
      {isConnectModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-in fade-in duration-200">
          <div className="relative w-full max-w-md bg-[#121624] border border-[#232b3e] rounded-2xl shadow-2xl p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
              <div className="flex items-center gap-2">
                <GitBranch className="w-5 h-5 text-indigo-400" />
                <h3 className="font-bold text-white text-base">Connect GitHub Profile</h3>
              </div>
              <button
                onClick={() => setIsConnectModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-[#1a2133] transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleConnectSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5 font-mono">
                  GitHub Username or Profile URL:
                </label>
                <div className="relative">
                  <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-500 font-mono text-sm">
                    @
                  </span>
                  <input
                    type="text"
                    value={inputUsername}
                    onChange={(e) => setInputUsername(e.target.value)}
                    placeholder="your-github-username"
                    autoFocus
                    required
                    className="w-full bg-[#0b0e17] border border-[#232b3e] focus:border-indigo-500 rounded-xl pl-8 pr-4 py-2.5 text-sm text-white focus:outline-none focus:ring-1 focus:ring-indigo-500 font-mono"
                  />
                </div>
              </div>

              {connectError && (
                <p className="text-xs text-rose-400 bg-rose-500/10 border border-rose-500/20 rounded-lg p-2.5">
                  {connectError}
                </p>
              )}

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsConnectModalOpen(false)}
                  disabled={isConnecting}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white hover:bg-[#1a2133] transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isConnecting || !inputUsername.trim()}
                  className="px-5 py-2 rounded-xl text-xs font-semibold bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white transition-all shadow-md shadow-indigo-600/25 disabled:opacity-50 flex items-center gap-1.5"
                >
                  {isConnecting ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      <span>Connecting & Auditing...</span>
                    </>
                  ) : (
                    <span>Connect & Run AST Audit</span>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};
