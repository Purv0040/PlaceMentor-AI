import React, { useState, useEffect } from 'react';
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
  Award,
  Link,
  Unlink,
  AlertCircle
} from 'lucide-react';

export const LeetcodePage = () => {
  const navigate = useNavigate();
  const [data, setData] = useState(initialLeetcodeData);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [connectUsername, setConnectUsername] = useState('');
  const [connectError, setConnectError] = useState(null);
  const [isConnecting, setIsConnecting] = useState(false);

  useEffect(() => {
    fetchProfileData();
  }, []);

  const mapBackendToFrontendData = (res, analysisRes) => {
    if (!res || !res.data) {
      return {
        handle: 'Not Connected',
        profileUrl: 'https://leetcode.com',
        metrics: {
          totalSolved: 0,
          targetSolved: 500,
          currentStreakDays: 0,
          longestStreakDays: 0,
          contestRating: 0,
          rankTitle: 'Unranked',
          globalRank: 'N/A',
          readinessScore: 0,
          activeDaysCount: 0
        },
        difficultyChartData: [
          { name: 'Easy', Solved: 0, color: '#10b981' },
          { name: 'Medium', Solved: 0, color: '#f59e0b' },
          { name: 'Hard', Solved: 0, color: '#ef4444' }
        ],
        difficultyBreakdown: {
          easy: { solved: 0, target: 150 },
          medium: { solved: 0, target: 250 },
          hard: { solved: 0, target: 100 }
        },
        topicPerformance: [],
        recentSubmissions: [],
        aiInsights: [
          {
            title: 'Connect LeetCode Account',
            description: 'Link your LeetCode handle to sync solved problem metrics and automated contest rating telemetry.',
            actionLabel: 'Connect Profile',
            actionRoute: '/onboarding/integrations'
          }
        ]
      };
    }
    const p = res.data;
    const stats = p.statistics || {};
    const contest = p.contest || {};
    const topics = p.topic_statistics || [];
    const recent = p.recent_activity || [];
    const ai = (analysisRes && analysisRes.data && analysisRes.data.analysis) || p.analysis || {};

    const easySolved = stats.easy_solved || 0;
    const mediumSolved = stats.medium_solved || 0;
    const hardSolved = stats.hard_solved || 0;
    const totalSolved = stats.total_solved || (easySolved + mediumSolved + hardSolved);

    const difficultyChartData = [
      { name: 'Easy', Solved: easySolved, color: '#10b981' },
      { name: 'Medium', Solved: mediumSolved, color: '#f59e0b' },
      { name: 'Hard', Solved: hardSolved, color: '#ef4444' },
    ];

    const mappedTopics = topics.length > 0
      ? topics.slice(0, 6).map((t) => ({
          topic: t.tagName || 'DSA Topic',
          solved: t.problemsSolved || 0,
          target: 50,
          score: Math.min(100, Math.round(((t.problemsSolved || 0) / 40) * 100)),
          status: (t.problemsSolved || 0) >= 30 ? 'Mastered' : (t.problemsSolved || 0) >= 15 ? 'Developing' : 'Needs Practice'
        }))
      : [];

    const mappedRecent = recent.length > 0
      ? recent.slice(0, 5).map((r, idx) => ({
          id: idx + 1,
          title: r.title || 'Problem Title',
          difficulty: r.difficulty || (idx % 2 === 0 ? 'Medium' : 'Easy'),
          topic: r.topic || 'Algorithms',
          runtime: r.timestamp ? new Date(parseInt(r.timestamp) * 1000).toLocaleDateString() : 'Accepted',
          aiRating: 'Optimal'
        }))
      : [];

    const mappedAiInsights = ai.recommendations
      ? ai.recommendations.map((rec, i) => ({
          title: `Recommendation ${i + 1}`,
          description: rec,
          actionLabel: 'Solve Targeted Problems',
          actionRoute: '/leetcode'
        }))
      : [];

    return {
      handle: p.leetcode_username || 'leetcode_user',
      profileUrl: `https://leetcode.com/${p.leetcode_username || ''}`,
      metrics: {
        totalSolved: totalSolved,
        targetSolved: stats.total_questions || 500,
        currentStreakDays: stats.current_streak || 0,
        longestStreakDays: stats.longest_streak || 0,
        contestRating: contest.rating ? Math.round(contest.rating) : 0,
        rankTitle: contest.top_percentage ? `Top ${contest.top_percentage}%` : 'Unranked',
        globalRank: contest.global_ranking ? `#${contest.global_ranking.toLocaleString()}` : 'N/A',
        readinessScore: Math.min(98, Math.round((totalSolved / 300) * 85)) || 0,
        activeDaysCount: stats.active_days || 0,
      },
      difficultyChartData,
      difficultyBreakdown: {
        easy: { solved: easySolved, target: stats.easy_total || 150 },
        medium: { solved: mediumSolved, target: stats.medium_total || 250 },
        hard: { solved: hardSolved, target: stats.hard_total || 100 },
      },
      topicPerformance: mappedTopics,
      recentSubmissions: mappedRecent,
      aiInsights: mappedAiInsights,
    };
  };

  const fetchProfileData = async () => {
    setIsLoading(true);
    try {
      const res = await leetcodeService.getProfile();
      if (res && res.data && res.data.leetcode_username) {
        setIsConnected(true);
        const analysisRes = await leetcodeService.getAnalysis().catch(() => null);
        setData(mapBackendToFrontendData(res, analysisRes));
      } else {
        setIsConnected(false);
        setData(mapBackendToFrontendData(null, null));
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleConnect = async (e) => {
    e.preventDefault();
    if (!connectUsername.trim()) return;
    setIsConnecting(true);
    setConnectError(null);
    try {
      const res = await leetcodeService.connect(connectUsername.trim());
      setIsConnected(true);
      setConnectUsername('');
      // Auto-sync after connection
      await handleSync();
    } catch (err) {
      setConnectError(err.message || 'Failed to connect LeetCode profile');
    } finally {
      setIsConnecting(false);
    }
  };

  const handleSync = async () => {
    setIsRefreshing(true);
    try {
      await leetcodeService.syncProfile();
      const updatedProfile = await leetcodeService.getProfile();
      let analysisRes = null;
      try {
        analysisRes = await leetcodeService.analyzeProfile();
      } catch (e) {
        analysisRes = await leetcodeService.getAnalysis().catch(() => null);
      }
      setData(mapBackendToFrontendData(updatedProfile, analysisRes));
    } catch (err) {
      console.error('LeetCode sync failed:', err);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleDisconnect = async () => {
    if (!window.confirm('Are you sure you want to disconnect your LeetCode account?')) return;
    try {
      await leetcodeService.disconnect();
      setIsConnected(false);
      setData(initialLeetcodeData);
    } catch (err) {
      console.error('Error disconnecting LeetCode account:', err);
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <RefreshCw className="w-8 h-8 text-indigo-400 animate-spin" />
        <p className="text-slate-400 text-sm font-mono">Loading LeetCode Intelligence Telemetry...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* 1. HERO BANNER */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6 p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-indigo-950/60 via-purple-950/40 to-[#121624] border border-indigo-500/30 shadow-2xl">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-400 text-xs font-mono font-semibold border border-indigo-500/30">
              <Zap className="w-3.5 h-3.5 text-indigo-400" />
              Telemetry V4.2 • DSA Diagnostic Engine
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">LeetCode Intelligence</h1>
          <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
            Analyze your DSA preparation, identify weak topics, and build a stronger problem-solving profile for Tier-1 coding screening cutoffs.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start lg:self-center shrink-0">
          {isConnected && (
            <>
              <button
                onClick={handleSync}
                disabled={isRefreshing}
                className="flex items-center gap-2 px-4 py-2.5 bg-[#1a2030] hover:bg-[#232b3e] text-slate-200 hover:text-white text-xs sm:text-sm font-semibold rounded-xl border border-[#232b3e] transition-all shadow-md disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 text-indigo-400 ${isRefreshing ? 'animate-spin' : ''}`} />
                <span>{isRefreshing ? 'Syncing Stats...' : 'Refresh Analysis'}</span>
              </button>
              <a
                href={data.profileUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs sm:text-sm font-semibold rounded-xl transition-all shadow-lg shadow-indigo-600/30 border border-indigo-400/30"
              >
                <span>LeetCode Profile</span>
                <ExternalLink className="w-4 h-4" />
              </a>
            </>
          )}
        </div>
      </div>

      {/* CONNECT CARD (IF NOT CONNECTED) */}
      {!isConnected && (
        <div className="p-8 rounded-3xl bg-[#121624] border border-indigo-500/30 shadow-2xl space-y-6">
          <div className="max-w-xl space-y-3">
            <div className="flex items-center gap-2 text-indigo-400 font-mono text-xs uppercase tracking-wider font-semibold">
              <Link className="w-4 h-4" /> Connect LeetCode Profile
            </div>
            <h2 className="text-xl font-bold text-white">Integrate your LeetCode problem-solving activity</h2>
            <p className="text-sm text-slate-400 leading-relaxed">
              Enter your public LeetCode username to sync your solved statistics, topic performance matrix, and contest ratings for AI placement analysis.
            </p>
          </div>

          <form onSubmit={handleConnect} className="flex flex-col sm:flex-row gap-3 max-w-lg">
            <input
              type="text"
              value={connectUsername}
              onChange={(e) => setConnectUsername(e.target.value)}
              placeholder="e.g. neetcode or tourist"
              className="flex-1 px-4 py-3 bg-[#0f131d] border border-[#232b3e] focus:border-indigo-500/60 rounded-xl text-white text-sm outline-none transition-colors"
            />
            <button
              type="submit"
              disabled={isConnecting || !connectUsername.trim()}
              className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-sm rounded-xl transition-all shadow-lg shadow-indigo-600/20 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isConnecting ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Connecting...
                </>
              ) : (
                'Connect Profile'
              )}
            </button>
          </form>

          {connectError && (
            <div className="flex items-center gap-2 text-rose-400 text-xs bg-rose-500/10 border border-rose-500/20 px-4 py-3 rounded-xl max-w-lg">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{connectError}</span>
            </div>
          )}
        </div>
      )}

      {/* 2. CONNECTION & RANK BAR */}
      {isConnected && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 p-4 rounded-2xl bg-[#121624] border border-[#232b3e] text-xs font-mono shadow-xl">
          <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e]">
            <span className="text-slate-400">Profile Handle</span>
            <span className="text-white font-bold">@{data.handle}</span>
          </div>

          <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e]">
            <span className="text-slate-400">Contest Rating</span>
            <span className="text-amber-400 font-bold flex items-center gap-1">
              <Trophy className="w-3.5 h-3.5 text-amber-400" />
              {data.metrics.contestRating} ({data.metrics.rankTitle})
            </span>
          </div>

          <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e]">
            <span className="text-slate-400">Global Rank</span>
            <span className="text-emerald-400 font-bold">{data.metrics.globalRank}</span>
          </div>

          <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e]">
            <span className="text-slate-400">Status</span>
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <CheckCircle2 className="w-3.5 h-3.5" />
                LeetCode Connected
              </span>
              <button
                onClick={handleDisconnect}
                title="Disconnect account"
                className="p-1 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 transition-colors"
              >
                <Unlink className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 3. KEY METRICS KPI CARDS */}
      {isConnected && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Total Solved */}
          <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] hover:border-purple-500/40 transition-colors shadow-xl">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">Total Solved</span>
              <div className="p-2.5 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400">
                <CheckCircle2 className="w-5 h-5" />
              </div>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-white font-mono">{data.metrics.totalSolved}</span>
              <span className="text-xs text-slate-400 font-mono">/ {data.metrics.targetSolved} Target</span>
            </div>
            <div className="mt-3 text-xs text-emerald-400 font-mono font-semibold">
              Target progress: {Math.min(100, Math.round((data.metrics.totalSolved / data.metrics.targetSolved) * 100))}% Complete
            </div>
          </div>

          {/* Active Streak */}
          <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] hover:border-amber-500/40 transition-colors shadow-xl">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">Current Streak</span>
              <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
                <Flame className="w-5 h-5" />
              </div>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-white font-mono">{data.metrics.currentStreakDays}</span>
              <span className="text-xs text-slate-400 font-mono">Days</span>
            </div>
            <div className="mt-3 text-xs text-amber-400 font-medium">
              Max Streak: <span className="font-bold">{data.metrics.longestStreakDays} Days</span>
            </div>
          </div>

          {/* Screening Readiness */}
          <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] hover:border-indigo-500/40 transition-colors shadow-xl">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">DSA Readiness</span>
              <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
                <Target className="w-5 h-5" />
              </div>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-white font-mono">{data.metrics.readinessScore}%</span>
            </div>
            <div className="mt-3 text-xs text-slate-400 font-medium">
              Cutoff benchmark: Tier-1 Screening Ready
            </div>
          </div>

          {/* Solved Active Days */}
          <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] hover:border-emerald-500/40 transition-colors shadow-xl">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">Active Practice Days</span>
              <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                <Activity className="w-5 h-5" />
              </div>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-white font-mono">{data.metrics.activeDaysCount}</span>
              <span className="text-xs text-slate-400 font-mono">Days</span>
            </div>
            <div className="mt-3 text-xs text-slate-400 font-medium">
              Total submission activity
            </div>
          </div>
        </div>
      )}

      {/* 4. VISUALIZERS GRID */}
      {isConnected && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Difficulty Breakdown */}
          <div className="bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-xl">
            <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
              <h3 className="font-bold text-white text-base">Difficulty Breakdown</h3>
              <span className="text-xs font-mono text-indigo-400 font-semibold px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20">Solved vs Target</span>
            </div>

            <div className="h-48 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.difficultyChartData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                  <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} />
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
                  <Bar dataKey="Solved" radius={[6, 6, 0, 0]}>
                    {data.difficultyChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="space-y-2.5 pt-2 border-t border-[#232b3e]">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-emerald-400 font-bold">Easy ({data.difficultyBreakdown.easy.solved})</span>
                <span className="text-slate-400">Total: {data.difficultyBreakdown.easy.target}</span>
              </div>
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-amber-400 font-bold">Medium ({data.difficultyBreakdown.medium.solved})</span>
                <span className="text-slate-400">Total: {data.difficultyBreakdown.medium.target}</span>
              </div>
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-rose-400 font-bold">Hard ({data.difficultyBreakdown.hard.solved})</span>
                <span className="text-slate-400">Total: {data.difficultyBreakdown.hard.target}</span>
              </div>
            </div>
          </div>

          {/* Topic Mastery Matrix */}
          <div className="lg:col-span-2 bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-xl">
            <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
              <div>
                <h3 className="font-bold text-white text-base">Topic Performance & Mastery</h3>
                <p className="text-xs text-slate-400">Evaluated topic confidence against Tier-1 SDE cutoffs</p>
              </div>
              <span className="text-xs font-mono text-purple-400 font-semibold bg-purple-500/10 px-2.5 py-1 rounded-lg border border-purple-500/20">
                DSA Diagnostic
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {data.topicPerformance.map((topic, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-[#0f131d] border border-[#232b3e] space-y-2.5 hover:border-indigo-500/30 transition-colors">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-white">{topic.topic}</span>
                    <span className="font-mono text-indigo-400 font-bold">{topic.score}%</span>
                  </div>

                  <div className="w-full bg-[#121624] rounded-full h-2 overflow-hidden border border-[#232b3e]">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        topic.score >= 80 ? 'bg-emerald-500' : topic.score >= 50 ? 'bg-indigo-500' : 'bg-amber-500'
                      }`}
                      style={{ width: `${topic.score}%` }}
                    ></div>
                  </div>

                  <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 pt-0.5">
                    <span>Solved: {topic.solved} / {topic.target}</span>
                    <span className="font-semibold text-slate-200">{topic.status}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 5. RECENT ACTIVITY TABLE */}
      {isConnected && (
        <div className="bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-xl">
          <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
            <h3 className="font-bold text-white text-base">Recent Solved Submissions</h3>
            <span className="text-xs font-mono text-slate-400">Latest Activity</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-[#232b3e] text-[11px] font-mono uppercase text-slate-400">
                  <th className="py-3 px-4">Problem Title</th>
                  <th className="py-3 px-4">Difficulty</th>
                  <th className="py-3 px-4">Topic</th>
                  <th className="py-3 px-4">Date / Runtime</th>
                  <th className="py-3 px-4">AI Rating</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#232b3e] text-xs">
                {data.recentSubmissions.map((sub) => (
                  <tr key={sub.id} className="hover:bg-[#0f131d] transition-colors">
                    <td className="py-3.5 px-4 font-bold text-white">{sub.title}</td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`px-2.5 py-1 rounded-lg text-[10px] font-mono font-bold uppercase ${
                          sub.difficulty === 'Hard'
                            ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                            : sub.difficulty === 'Medium'
                            ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                            : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        }`}
                      >
                        {sub.difficulty}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-300 font-mono">{sub.topic}</td>
                    <td className="py-3.5 px-4 text-slate-400 font-mono">{sub.runtime}</td>
                    <td className="py-3.5 px-4 font-bold text-emerald-400 font-mono">{sub.aiRating}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 6. AI RECOMMENDATIONS BANNER */}
      {isConnected && (
        <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-xl">
          <h3 className="font-bold text-white text-base flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-400" />
            Copilot LeetCode Diagnostic Advice
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.aiInsights.map((insight, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-[#0f131d] border border-[#232b3e] space-y-2 hover:border-purple-500/40 transition-colors">
                <h4 className="font-bold text-sm text-white">{insight.title}</h4>
                <p className="text-xs text-slate-300 leading-relaxed">{insight.description}</p>
                <button
                  onClick={() => navigate(insight.actionRoute || '/app/leetcode')}
                  className="text-xs font-bold text-indigo-400 hover:text-indigo-300 inline-flex items-center gap-1 pt-1"
                >
                  <span>{insight.actionLabel}</span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
