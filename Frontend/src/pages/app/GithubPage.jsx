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
  X,
  Info,
  AlertCircle,
  Clock,
  Sparkles,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

const LANGUAGE_COLORS = {
  JavaScript: '#f1e05a',
  Python: '#3572A5',
  Java: '#b07219',
  TypeScript: '#3178c6',
  'Jupyter Notebook': '#DA5B0B',
  'C++': '#f34b7d',
  C: '#555555',
  'C#': '#178600',
  HTML: '#e34c26',
  CSS: '#563d7c',
  Go: '#00ADD8',
  Rust: '#dea584',
  PHP: '#4F5D95',
  Ruby: '#701516',
  Kotlin: '#A97BFF',
  Swift: '#F05138',
  Dart: '#00B4AB',
  Shell: '#89e051',
  Vue: '#41b883',
  SQL: '#e38c00',
  R: '#198CE7'
};

const getLanguageColor = (name) => {
  if (LANGUAGE_COLORS[name]) return LANGUAGE_COLORS[name];
  // Deterministic vibrant color generator for unlisted languages
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  const hue = Math.abs(hash % 360);
  return `hsl(${hue}, 70%, 55%)`;
};

const computeLanguageDistribution = (rawLangs) => {
  const entries = Object.entries(rawLangs).map(([name, count]) => ({ name, count: Number(count) }));
  const total = entries.reduce((acc, curr) => acc + curr.count, 0);
  if (total === 0) return [];

  // Sort all actual languages by count/bytes descending
  const sortedEntries = [...entries].sort((a, b) => b.count - a.count);

  // Largest Remainder Method for mathematically exact 100% sum across all languages
  let intSum = 0;
  const withRemainders = sortedEntries.map(entry => {
    const rawPct = (entry.count / total) * 100;
    const intPct = Math.floor(rawPct);
    intSum += intPct;
    return {
      name: entry.name,
      count: entry.count,
      percentage: intPct,
      remainder: rawPct - intPct,
      color: getLanguageColor(entry.name)
    };
  });

  const deficit = 100 - intSum;
  const sortedByRem = [...withRemainders].sort((a, b) => b.remainder - a.remainder);
  for (let i = 0; i < deficit && i < sortedByRem.length; i++) {
    sortedByRem[i].percentage += 1;
  }

  return withRemainders.map(item => ({
    name: item.name,
    count: item.count,
    percentage: item.percentage,
    color: item.color
  }));
};

export const GithubPage = () => {
  const navigate = useNavigate();
  const { user, updateUserProfile } = useUser();
  const [data, setData] = useState(initialGithubData);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnectModalOpen, setIsConnectModalOpen] = useState(false);
  const [isScoreInfoOpen, setIsScoreInfoOpen] = useState(false);
  const [inputUsername, setInputUsername] = useState('');
  const [connectError, setConnectError] = useState('');
  const [isConnecting, setIsConnecting] = useState(false);
  const [refreshMessage, setRefreshMessage] = useState('');
  const [isReposExpanded, setIsReposExpanded] = useState(false);

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

        // Fetch AI analysis if available
        let analysisData = null;
        if (pData.has_analysis) {
          try {
            const analysisRes = await githubService.getAnalysis();
            if (analysisRes && analysisRes.data) {
              analysisData = analysisRes.data.analysis;
            }
          } catch (e) {
            // Analysis not yet run
          }
        }

        // Calculate dynamic language distribution from actual backend data
        const rawLangs = stats.languages || {};
        let calculatedLangs = [];

        if (Array.isArray(stats.language_distribution) && stats.language_distribution.length > 0) {
          calculatedLangs = stats.language_distribution.map(item => ({
            ...item,
            color: getLanguageColor(item.name)
          }));
        } else if (Object.keys(rawLangs).length > 0) {
          calculatedLangs = computeLanguageDistribution(rawLangs);
        } else if (repos.length > 0) {
          const counts = {};
          repos.forEach(r => {
            if (r.language && r.language !== 'Not specified') counts[r.language] = (counts[r.language] || 0) + 1;
          });
          calculatedLangs = computeLanguageDistribution(counts);
        }

        const complexityMap = {};
        (analysisData?.complexity_analyses || []).forEach(ca => {
          if (ca && ca.repo_name) complexityMap[ca.repo_name.toLowerCase()] = ca;
        });

        // Map dynamic repositories from actual backend data
        const mappedRepos = repos.map((r) => {
          const ca = complexityMap[r.name?.toLowerCase()];
          return {
            id: r.id || r.repo_id || r.name,
            name: r.name || 'Repository',
            description: r.description || 'No description provided.',
            language: r.language && r.language !== 'Not specified' ? r.language : null,
            stars: r.stars || 0,
            forks: r.forks || 0,
            qualityScore: r.quality_score || r.ast_score || 0,
            qualityTier: r.quality_tier || 'Active Project',
            complexityLevel: ca?.complexity_level || null,
            complexityConfidence: ca?.confidence || null,
            tags: Array.isArray(r.tags) && r.tags.length > 0 ? r.tags : (r.language && r.language !== 'Not specified' ? [r.language] : []),
            url: r.html_url || `https://github.com/${handle}/${r.name}`,
            pushedAt: r.pushed_at
          };
        });

        // Actual weekly commit cadence from backend events
        const weeklyCadence = Array.isArray(stats.weekly_activity) && stats.weekly_activity.length > 0
          ? stats.weekly_activity
          : [];

        // Evidence-based strengths & improvements from analysis or deterministic calculations
        const strengths = (analysisData?.strengths && analysisData.strengths.length > 0)
          ? analysisData.strengths
          : (stats.strengths || []);

        const improvements = (analysisData?.recommendations && analysisData.recommendations.length > 0)
          ? analysisData.recommendations
          : ((analysisData?.gaps && analysisData.gaps.length > 0)
            ? analysisData.gaps
            : (stats.improvements || []));

        const impactScoreVal = typeof stats.impact_score === 'number'
          ? stats.impact_score
          : (repos.length > 0 ? 50 : 0);

        const totalCommitsVal = stats.total_recent_commits ?? 0;
        const totalStarsVal = stats.total_stars ?? repos.reduce((acc, r) => acc + (r.stars || 0), 0);

        // Format last synced timestamp
        let lastSyncedText = 'Never';
        if (pData.sync?.last_successful_sync_at || pData.sync?.last_synced_at) {
          const syncDate = new Date(pData.sync.last_successful_sync_at || pData.sync.last_synced_at);
          lastSyncedText = syncDate.toLocaleString([], { dateStyle: 'short', timeStyle: 'short' });
        }

        setData({
          isConnected: true,
          handle: handle,
          profileUrl: profile.html_url || `https://github.com/${handle}`,
          lastSynced: lastSyncedText,
          languages: calculatedLangs,
          repositories: mappedRepos,
          weeklyCadence: weeklyCadence,
          strengths: strengths,
          improvements: improvements,
          evidenceSummary: analysisData?.evidence_summary || null,
          technicalCategories: (analysisData?.technical_categories || []).filter(c => c.detected),
          technicalPatterns: analysisData?.technical_patterns || [],
          hasAiAnalysis: Boolean(analysisData),
          impactBreakdown: stats.impact_breakdown || null,
          primaryLanguage: stats.primary_language || (calculatedLangs[0]?.name || 'Not specified'),
          metrics: {
            githubImpactScore: impactScoreVal,
            totalCommits: totalCommitsVal,
            activeStreakDays: stats.active_streak_days ?? 0,
            longestStreakDays: stats.longest_streak_days ?? 0,
            repoQualityIndex: stats.repo_quality_score ?? 0,
            languageCount: calculatedLangs.length,
            reposAnalyzedCount: repos.length || stats.total_repositories || 0,
            starsEarned: totalStarsVal
          }
        });
      } else {
        setIsConnected(false);
        setData(initialGithubData);
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
    setRefreshMessage('');
    try {
      await githubService.syncProfile();
      try {
        await githubService.analyzeProfile();
      } catch (aiErr) {
        console.info('AI service analysis notice:', aiErr.message);
      }
      await fetchGithubData();
      setRefreshMessage('Synchronized successfully');
      setTimeout(() => setRefreshMessage(''), 3000);
    } catch (e) {
      console.warn('GitHub sync error:', e);
      setRefreshMessage(e.message || 'Sync failed');
      setTimeout(() => setRefreshMessage(''), 4000);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleToggleConnection = async () => {
    try {
      if (isConnected) {
        await githubService.disconnect();
        setIsConnected(false);
        setData(initialGithubData);
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
      try {
        await githubService.analyzeProfile();
      } catch (aiErr) {
        console.info('Auto AI profile analysis notice:', aiErr.message);
      }
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

  const hasCommitCadence = data.weeklyCadence && data.weeklyCadence.some(w => w.commits > 0);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* 1. HERO BANNER */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6 p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-indigo-950/60 via-purple-950/40 to-[#121624] border border-indigo-500/30 shadow-2xl">
        <div className="space-y-2">
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">GitHub Intelligence</h1>
          <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
            Evidence-based analysis of your public GitHub activity, code hygiene, and project documentation benchmarked against industry standards.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start lg:self-center shrink-0">
          <button
            onClick={handleRefresh}
            disabled={isRefreshing || !isConnected}
            className="flex items-center gap-2 px-4 py-2.5 bg-[#1a2030] hover:bg-[#232b3e] text-slate-200 hover:text-white text-xs sm:text-sm font-semibold rounded-xl border border-[#232b3e] transition-all shadow-md disabled:opacity-50"
            title="Fetch latest repositories and calculate evidence metrics"
          >
            <RefreshCw className={`w-4 h-4 text-indigo-400 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>{isRefreshing ? 'Auditing GitHub...' : 'Refresh Analysis'}</span>
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

      {refreshMessage && (
        <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 rounded-xl text-xs font-mono flex items-center justify-between">
          <span>{refreshMessage}</span>
          <button onClick={() => setRefreshMessage('')} className="text-slate-400 hover:text-white">
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* 2. CONNECTION & STATUS BAR */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 p-4 rounded-2xl bg-[#121624] border border-[#232b3e] text-xs font-mono shadow-xl">
        <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e]">
          <span className="text-slate-400">Profile Handle</span>
          <span className="text-white font-bold">{data.handle ? `@${data.handle}` : 'Not Connected'}</span>
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
              {isConnected ? 'Connected' : 'Disconnected'}
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
        <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] hover:border-indigo-500/40 transition-colors shadow-xl relative">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">GitHub Impact Score</span>
            <div className="flex items-center gap-1.5">
              <button
                onClick={() => setIsScoreInfoOpen(true)}
                title="View deterministic scoring formula & breakdown"
                className="p-1 rounded text-slate-400 hover:text-indigo-300 hover:bg-indigo-500/10 transition-colors"
              >
                <Info className="w-4 h-4" />
              </button>
              <div className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
                <Zap className="w-4 h-4" />
              </div>
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white font-mono">{data.metrics.githubImpactScore}</span>
            <span className="text-xs text-slate-400 font-mono">/ 100</span>
          </div>
          <div className="mt-3 text-xs text-slate-400 font-medium flex items-center justify-between">
            <span>Deterministic multi-signal score</span>
            <button
              onClick={() => setIsScoreInfoOpen(true)}
              className="text-indigo-400 hover:text-indigo-300 underline underline-offset-2 text-[11px]"
            >
              Breakdown
            </button>
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
            Streak: <span className="text-amber-400 font-bold">{data.metrics.activeStreakDays}d</span>
            {data.metrics.longestStreakDays > 0 && ` (Max: ${data.metrics.longestStreakDays}d)`}
            <span className="block text-[11px] text-slate-400 mt-0.5">Scope: Public push events (90d)</span>
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
            README, description & hygiene average
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
            Primary: <span className="text-indigo-400 font-semibold">{data.primaryLanguage}</span>
          </div>
        </div>
      </div>

      {/* 4. VISUALIZERS GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Language Distribution Breakdown */}
        <div className="bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
              <h3 className="font-bold text-white text-base">Language Distribution</h3>
              <span className="text-xs font-mono text-indigo-400 font-semibold px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20">
                Repositories
              </span>
            </div>

            {data.languages.length > 0 ? (
              <>
                <div className="h-48 w-full mt-3">
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
                        formatter={(val) => [`${val}%`, 'Usage']}
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
              </>
            ) : (
              <div className="h-48 flex flex-col items-center justify-center text-center p-4">
                <Code2 className="w-8 h-8 text-slate-500 mb-2 opacity-50" />
                <p className="text-xs text-slate-400 font-mono">No language statistics detected.</p>
                <p className="text-[11px] text-slate-500 mt-1">Connect a profile with public repositories to view distribution.</p>
              </div>
            )}
          </div>
        </div>

        {/* Weekly Commit Activity Chart */}
        <div className="lg:col-span-2 bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
              <div>
                <h3 className="font-bold text-white text-base">Weekly Push Activity</h3>
                <p className="text-xs text-slate-400">Weekly public push activity over the last 6 weeks</p>
              </div>
              <span className="text-xs font-mono font-semibold text-indigo-400 bg-indigo-500/10 px-2.5 py-1 rounded-lg border border-indigo-500/20">
                Public Push Events
              </span>
            </div>

            {!isConnected ? (
              <div className="h-56 flex flex-col items-center justify-center text-center p-6 space-y-2">
                <Clock className="w-8 h-8 text-slate-500 opacity-50" />
                <p className="text-xs text-slate-300 font-mono font-semibold">GitHub History Unavailable</p>
                <p className="text-[11px] text-slate-400 max-w-md">
                  Connect your GitHub account to load real public push activity over the last 6 weeks.
                </p>
              </div>
            ) : data.weeklyCadence.length === 0 ? (
              <div className="h-56 flex flex-col items-center justify-center text-center p-6 space-y-2">
                <Clock className="w-8 h-8 text-slate-500 opacity-50" />
                <p className="text-xs text-slate-300 font-mono font-semibold">Push History Unavailable</p>
                <p className="text-[11px] text-slate-400 max-w-md">
                  No public push activity was retrieved from the GitHub Events API. Click "Refresh Analysis" to query public events.
                </p>
              </div>
            ) : hasCommitCadence ? (
              <div className="space-y-3 mt-3">
                <div className="h-48 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data.weeklyCadence} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <defs>
                        <linearGradient id="commitGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#6366f1" stopOpacity={0.5} />
                          <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <XAxis dataKey="week" stroke="#64748b" fontSize={11} tickLine={false} />
                      <YAxis stroke="#64748b" fontSize={11} tickLine={false} allowDecimals={false} tickFormatter={(val) => Math.round(val)} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#121624',
                          borderColor: '#232b3e',
                          borderRadius: '12px',
                          color: '#ffffff',
                          fontSize: '12px',
                        }}
                        formatter={(val, name, item) => {
                          const w = item?.payload || {};
                          const count = parseInt(val, 10);
                          if (w.status === 'incomplete_history') {
                            return ['Unverified (Before oldest event)', 'Coverage'];
                          }
                          const pushLabel = count === 1 ? 'push event' : 'push events';
                          return [`${count} ${pushLabel} (${w.status === 'verified_zero' ? 'Verified 0' : 'Recorded'})`, 'Activity'];
                        }}
                        labelFormatter={(label, items) => {
                          const w = items?.[0]?.payload;
                          if (w && w.start_date && w.end_date) {
                            return `${label}: ${w.start_date} to ${w.end_date}`;
                          }
                          return `${label} (7-day window)`;
                        }}
                      />
                      <Area
                        type="monotone"
                        dataKey="commits"
                        stroke="#6366f1"
                        strokeWidth={2.5}
                        fillOpacity={1}
                        fill="url(#commitGrad)"
                        dot={{ r: 3, fill: '#6366f1' }}
                        activeDot={{ r: 5 }}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
                {/* Integer counts badges per week with date range tooltips and status */}
                <div>
                  <div className="flex items-center justify-between pt-2 border-t border-[#232b3e]/60 text-[11px] font-mono text-slate-400">
                    {data.weeklyCadence.map((w, idx) => (
                      <span
                        key={idx}
                        className="flex items-center gap-1 cursor-help"
                        title={w.start_date && w.end_date ? `${w.week}: ${w.start_date} to ${w.end_date} (${w.status})` : ''}
                      >
                        <span className="text-slate-500">{w.week}:</span>
                        {w.status === 'incomplete_history' ? (
                          <span className="text-amber-400 font-semibold text-[10px]" title="History prior to oldest recorded event is unverified by GitHub Events API">Unverified*</span>
                        ) : (
                          <span className={w.commits > 0 ? "text-indigo-400 font-bold" : "text-slate-500"}>
                            {parseInt(w.commits, 10)}
                          </span>
                        )}
                      </span>
                    ))}
                  </div>
                  {data.weeklyCadence.some(w => w.status === 'incomplete_history') && (
                    <p className="text-[10px] text-slate-500 font-mono mt-1.5 text-right">
                      * Weeks prior to oldest recorded event are marked Unverified due to GitHub event horizon.
                    </p>
                  )}
                </div>
              </div>
            ) : (
              <div className="h-56 flex flex-col items-center justify-center text-center p-6 space-y-2">
                <Clock className="w-8 h-8 text-slate-500 opacity-50" />
                <p className="text-xs text-slate-300 font-mono font-semibold">No public push events recorded in the last 6 weeks.</p>
                <p className="text-[11px] text-slate-400 max-w-md">
                  Zero push events were detected across the 42-day window in Asia/Kolkata timezone. Push code to your repositories to see weekly trends.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 5. REPOSITORY AUDIT GRID */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <h3 className="font-bold text-white text-lg">Audited Repositories</h3>
            {data.repositories.length > 2 && (
              <button
                onClick={() => setIsReposExpanded(!isReposExpanded)}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-400 hover:text-indigo-300 text-xs font-semibold font-mono border border-indigo-500/20 transition-all cursor-pointer"
                title={isReposExpanded ? "Collapse to 2 repositories" : `Expand to see all ${data.repositories.length} repositories`}
              >
                <span>{isReposExpanded ? 'Show Less' : `See All (${data.repositories.length})`}</span>
                {isReposExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </button>
            )}
          </div>
          <span className="text-xs font-mono text-slate-400">
            {data.repositories.length > 0
              ? (isReposExpanded
                  ? `Showing all ${data.repositories.length} Repositories`
                  : `Showing 2 of ${data.repositories.length} Repositories`)
              : 'No Repositories'}
          </span>
        </div>

        {data.repositories.length > 0 ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {(isReposExpanded ? data.repositories : data.repositories.slice(0, 2)).map((repo) => (
                <div
                  key={repo.id}
                  className="p-5 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 hover:border-indigo-500/40 transition-colors shadow-xl"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2">
                      <GitBranch className="w-5 h-5 text-indigo-400 shrink-0" />
                      <a
                        href={repo.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-bold text-white text-base hover:text-indigo-400 transition-colors cursor-pointer"
                      >
                        {repo.name}
                      </a>
                    </div>
                    <div className="flex items-center gap-1.5 shrink-0">
                      {repo.complexityLevel && (
                        <span
                          className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded uppercase tracking-wider border ${
                            repo.complexityLevel.toLowerCase() === 'advanced'
                              ? 'bg-purple-500/10 text-purple-400 border-purple-500/20'
                              : repo.complexityLevel.toLowerCase() === 'intermediate'
                              ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'
                              : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                          }`}
                          title={repo.complexityConfidence ? `Complexity: ${repo.complexityLevel} (${Math.round(repo.complexityConfidence * 100)}% confidence)` : `Complexity: ${repo.complexityLevel}`}
                        >
                          {repo.complexityLevel}
                        </span>
                      )}
                      <span className="text-xs font-mono text-indigo-400 font-semibold px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20">
                        {repo.qualityScore}/100
                      </span>
                    </div>
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed line-clamp-2">
                    {repo.description}
                  </p>

                  {/* Tech Tags */}
                  {repo.tags && repo.tags.length > 0 && (
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
                  )}

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
                      {repo.language && repo.language !== 'Not specified' && (
                        <span className="text-slate-400">{repo.language}</span>
                      )}
                    </div>
                    <span className="text-indigo-400 font-bold">{repo.qualityTier}</span>
                  </div>
                </div>
              ))}
            </div>

            {data.repositories.length > 2 && (
              <div className="flex justify-center pt-2">
                <button
                  onClick={() => setIsReposExpanded(!isReposExpanded)}
                  className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-[#121624] hover:bg-[#1a2133] text-indigo-400 hover:text-indigo-300 text-xs font-semibold font-mono border border-[#232b3e] hover:border-indigo-500/40 transition-all shadow-md group cursor-pointer"
                >
                  <span>
                    {isReposExpanded
                      ? 'Show Less'
                      : `See All Repositories (${data.repositories.length})`}
                  </span>
                  {isReposExpanded ? (
                    <ChevronUp className="w-4 h-4 transition-transform group-hover:-translate-y-0.5" />
                  ) : (
                    <ChevronDown className="w-4 h-4 transition-transform group-hover:translate-y-0.5" />
                  )}
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="p-8 rounded-2xl bg-[#121624] border border-[#232b3e] text-center space-y-2">
            <GitBranch className="w-8 h-8 text-slate-500 mx-auto opacity-50" />
            <p className="text-sm font-semibold text-slate-300">No public repositories found</p>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">
              Please connect your GitHub account with public repositories or click Refresh Analysis to fetch data.
            </p>
          </div>
        )}
      </div>

      {/* 6. GITHUB STRENGTHS & IMPROVEMENTS (PHASE 5) */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-indigo-400" />
            <h3 className="font-bold text-white text-lg">Evidence-Based GitHub Insights</h3>
          </div>
          <span className="text-xs font-mono text-slate-400">
            {data.hasAiAnalysis ? 'Deterministic & AI Verified' : 'Deterministic Audit'}
          </span>
        </div>

        {/* AI Evidence Narrative if present */}
        {data.evidenceSummary && (
          <div className="p-5 rounded-2xl bg-[#121624] border border-indigo-500/30 shadow-xl space-y-2">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              <h4 className="font-bold text-white text-sm">Portfolio Evidence Narrative</h4>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              {data.evidenceSummary}
            </p>
          </div>
        )}

        {/* Verified Technical Domains */}
        {data.technicalCategories && data.technicalCategories.length > 0 && (
          <div className="p-4 rounded-xl bg-[#0f131d] border border-[#232b3e] flex flex-wrap items-center gap-2">
            <span className="text-xs font-mono text-slate-400 mr-1">Verified Technical Domains:</span>
            {data.technicalCategories.map((cat, idx) => (
              <span
                key={idx}
                className="px-2.5 py-1 rounded-lg bg-indigo-500/10 text-indigo-300 text-xs font-mono border border-indigo-500/20 flex items-center gap-1.5"
                title={`Verified in: ${(cat.evidence_repos || []).join(', ') || 'repositories'}`}
              >
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
                <span>{cat.category}</span>
                {cat.evidence_repos && cat.evidence_repos.length > 0 && (
                  <span className="text-[10px] text-indigo-400/80 font-bold">({cat.evidence_repos.length})</span>
                )}
              </span>
            ))}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Strengths */}
          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-xl">
            <div className="flex items-center gap-2 pb-3 border-b border-[#232b3e]">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <h4 className="font-bold text-white text-sm">Portfolio Strengths</h4>
            </div>

            {data.strengths && data.strengths.length > 0 ? (
              <ul className="space-y-2.5">
                {data.strengths.map((str, idx) => (
                  <li key={idx} className="flex items-start gap-2.5 text-xs text-slate-200">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0" />
                    <span>{str}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-xs text-slate-400 italic">No strengths evaluated yet. Run an audit to generate findings.</p>
            )}
          </div>

          {/* Actionable Improvements */}
          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-xl">
            <div className="flex items-center gap-2 pb-3 border-b border-[#232b3e]">
              <TrendingUp className="w-4 h-4 text-amber-400" />
              <h4 className="font-bold text-white text-sm">Actionable Improvements</h4>
            </div>

            {data.improvements && data.improvements.length > 0 ? (
              <ul className="space-y-2.5">
                {data.improvements.map((imp, idx) => (
                  <li key={idx} className="flex items-start gap-2.5 text-xs text-slate-200">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 shrink-0" />
                    <span>{imp}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-xs text-slate-400 italic">No recommendations identified. Maintain current repository standards.</p>
            )}
          </div>
        </div>
      </div>

      {/* SCORE BREAKDOWN MODAL */}
      {isScoreInfoOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-in fade-in duration-200">
          <div className="relative w-full max-w-lg bg-[#121624] border border-[#232b3e] rounded-2xl shadow-2xl p-6 space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
              <div className="flex items-center gap-2">
                <Zap className="w-5 h-5 text-indigo-400" />
                <h3 className="font-bold text-white text-base">GitHub Impact Score Calculation</h3>
              </div>
              <button
                onClick={() => setIsScoreInfoOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-[#1a2133] transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="text-xs text-slate-300 space-y-3">
              <p>
                The Impact Score (0–100) is deterministically calculated across 4 verified dimensions with explicit weights:
              </p>

              <div className="space-y-2.5 pt-2">
                <div className="p-3 rounded-xl bg-[#0f131d] border border-[#232b3e] space-y-1">
                  <div className="flex justify-between font-semibold text-slate-200">
                    <span>1. Repository Quality (35% weight)</span>
                    <span className="text-indigo-400 font-mono">
                      {data.impactBreakdown?.repository_quality?.score ?? '—'}/100
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400">
                    {data.impactBreakdown?.repository_quality?.evidence || 'Evaluates README documentation and project descriptions across original repositories.'}
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-[#0f131d] border border-[#232b3e] space-y-1">
                  <div className="flex justify-between font-semibold text-slate-200">
                    <span>2. Activity & Freshness (25% weight)</span>
                    <span className="text-indigo-400 font-mono">
                      {data.impactBreakdown?.activity_freshness?.score ?? '—'}/100
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400">
                    {data.impactBreakdown?.activity_freshness?.evidence || 'Measures recency of code pushes and commits.'}
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-[#0f131d] border border-[#232b3e] space-y-1">
                  <div className="flex justify-between font-semibold text-slate-200">
                    <span>3. Language Breadth (20% weight)</span>
                    <span className="text-indigo-400 font-mono">
                      {data.impactBreakdown?.language_breadth?.score ?? '—'}/100
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400">
                    {data.impactBreakdown?.language_breadth?.evidence || 'Evaluates programming language versatility across public repositories.'}
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-[#0f131d] border border-[#232b3e] space-y-1">
                  <div className="flex justify-between font-semibold text-slate-200">
                    <span>4. Community Engagement (20% weight)</span>
                    <span className="text-indigo-400 font-mono">
                      {data.impactBreakdown?.community_engagement?.score ?? '—'}/100
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400">
                    {data.impactBreakdown?.community_engagement?.evidence || 'Measures public stars, forks, and project visibility.'}
                  </p>
                </div>
              </div>

              <p className="text-[11px] text-slate-400 pt-1">
                Total Score = (0.35 × Quality) + (0.25 × Freshness) + (0.20 × Languages) + (0.20 × Engagement).
              </p>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setIsScoreInfoOpen(false)}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-all shadow-md"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

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
                    <span>Connect GitHub Account</span>
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
