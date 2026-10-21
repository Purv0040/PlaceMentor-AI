import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/UserContext';
import { leetcodeService } from '../../services/leetcodeService';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  CartesianGrid,
} from 'recharts';
import {
  Code,
  RefreshCw,
  ExternalLink,
  CheckCircle2,
  Trophy,
  Flame,
  Target,
  Plus,
  X,
  Power,
  Calendar,
  Clock,
  TrendingUp,
  AlertTriangle,
  Award,
  BookOpen,
  Check,
  ChevronRight,
  ChevronDown,
  ChevronUp,
  Filter,
  Sparkles,
  HelpCircle,
  ShieldCheck,
  Zap,
  Info,
} from 'lucide-react';

export const LeetcodePage = () => {
  const navigate = useNavigate();
  const { user, updateUserProfile } = useUser();

  // Primary State
  const [profile, setProfile] = useState(null);
  const [dailyPlan, setDailyPlan] = useState(null);
  const [activityHistory, setActivityHistory] = useState(null);
  const [focusAreas, setFocusAreas] = useState([]);
  const [readinessBreakdown, setReadinessBreakdown] = useState(null);

  // UI / Interaction State
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [selectedDays, setSelectedDays] = useState(30);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [togglingTaskId, setTogglingTaskId] = useState(null);
  const [focusFilter, setFocusFilter] = useState('All'); // 'All', 'High', 'Medium', 'Low'
  const [isSubmissionsExpanded, setIsSubmissionsExpanded] = useState(false);

  // Modals
  const [isConnectModalOpen, setIsConnectModalOpen] = useState(false);
  const [isReadinessModalOpen, setIsReadinessModalOpen] = useState(false);
  const [connectUsername, setConnectUsername] = useState('');
  const [connectError, setConnectError] = useState(null);
  const [isConnecting, setIsConnecting] = useState(false);

  // 1. Fetch initial profile data & all dynamic subsections
  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      let res = await leetcodeService.getProfile();

      // If no connected profile found, check if user context or localStorage has a candidate handle
      if (!res || !res.data) {
        const candidateHandle =
          user?.integrations?.leetcodeHandle ||
          user?.leetcodeHandle ||
          user?.integrations?.leetcodeUsername ||
          localStorage.getItem('placementor_leetcode_handle');

        if (candidateHandle) {
          const cleanUser = candidateHandle
            .trim()
            .replace(/^https?:\/\/(www\.)?leetcode\.com\/(u\/)?/, '')
            .replace(/\/.*$/, '')
            .replace(/^@/, '');

          if (cleanUser) {
            try {
              await leetcodeService.connect(cleanUser);
              res = await leetcodeService.getProfile();
            } catch (cErr) {
              console.warn('Auto-connect with candidate handle failed:', cErr);
            }
          }
        }
      }

      if (res && res.data) {
        const p = res.data;
        setProfile(p);
        setIsConnected(true);
        if (p.daily_plan) setDailyPlan(p.daily_plan);
        if (p.focus_areas) setFocusAreas(p.focus_areas);
        if (p.readiness_breakdown) setReadinessBreakdown(p.readiness_breakdown);
        if (p.activity_history) setActivityHistory(p.activity_history);

        // Fetch dedicated sub-endpoints if any is missing from root response
        if (!p.daily_plan) {
          leetcodeService.getDailyPlan().then((r) => r?.data && setDailyPlan(r.data)).catch(() => {});
        }
        if (!p.focus_areas || p.focus_areas.length === 0) {
          leetcodeService.getFocusAreas().then((r) => r?.data && setFocusAreas(r.data)).catch(() => {});
        }
        if (!p.readiness_breakdown) {
          leetcodeService.getReadinessBreakdown().then((r) => r?.data && setReadinessBreakdown(r.data)).catch(() => {});
        }
        if (!p.activity_history) {
          leetcodeService.getActivityHistory(selectedDays).then((r) => r?.data && setActivityHistory(r.data)).catch(() => {});
        }
      } else {
        setIsConnected(false);
        setProfile(null);
        setDailyPlan(null);
        setFocusAreas([]);
        setActivityHistory(null);
        setReadinessBreakdown(null);
      }
    } catch (err) {
      console.warn('Error loading LeetCode profile:', err);
      setIsConnected(false);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, [user?.integrations?.leetcodeUsername, user?.integrations?.leetcodeHandle, user?.leetcodeHandle]);

  // 2. Connect Handler
  const handleConnect = async (e) => {
    e.preventDefault();
    if (!connectUsername.trim()) return;
    setIsConnecting(true);
    setConnectError(null);
    try {
      const cleanUser = connectUsername
        .trim()
        .replace(/^https?:\/\/(www\.)?leetcode\.com\/(u\/)?/, '')
        .replace(/\/.*$/, '')
        .replace(/^@/, '');

      await leetcodeService.connect(cleanUser);
      if (updateUserProfile) {
        updateUserProfile({
          integrations: {
            ...(user?.integrations || {}),
            leetcodeUsername: cleanUser,
            leetcodeConnected: true,
          },
        });
      }
      localStorage.setItem('placementor_leetcode_handle', cleanUser);
      setIsConnectModalOpen(false);
      setConnectUsername('');
      await handleSync();
    } catch (err) {
      setConnectError(err.message || 'Failed to connect LeetCode profile');
    } finally {
      setIsConnecting(false);
    }
  };

  // 3. Sync Handler
  const handleSync = async () => {
    setIsRefreshing(true);
    try {
      await leetcodeService.syncProfile();
      await loadDashboardData();
    } catch (err) {
      console.warn('LeetCode sync failed:', err);
    } finally {
      setIsRefreshing(false);
    }
  };

  // 4. Disconnect Handler
  const handleDisconnect = async () => {
    try {
      await leetcodeService.disconnect();
      setIsConnected(false);
      setProfile(null);
      setDailyPlan(null);
      setFocusAreas([]);
      setActivityHistory(null);
      setReadinessBreakdown(null);
      if (updateUserProfile) {
        updateUserProfile({
          integrations: {
            ...(user?.integrations || {}),
            leetcodeUsername: null,
            leetcodeConnected: false,
          },
        });
      }
      localStorage.removeItem('placementor_leetcode_handle');
    } catch (err) {
      console.warn('Error disconnecting LeetCode profile:', err);
    }
  };

  // 5. Toggle Daily Practice Task
  const handleToggleTask = async (taskId) => {
    setTogglingTaskId(taskId);
    // Optimistic UI update
    setDailyPlan((prev) => {
      if (!prev) return prev;
      const updatedTasks = prev.tasks.map((t) =>
        t.task_id === taskId
          ? { ...t, status: t.status === 'completed' ? 'pending' : 'completed' }
          : t
      );
      const completedCount = updatedTasks.filter((t) => t.status === 'completed').length;
      return {
        ...prev,
        completed_count: completedCount,
        remaining_count: Math.max(0, prev.target_count - completedCount),
        tasks: updatedTasks,
      };
    });

    try {
      const res = await leetcodeService.toggleDailyTask(taskId);
      if (res?.data) {
        setDailyPlan(res.data);
      }
    } catch (err) {
      console.error('Failed to toggle daily task:', err);
      // Revert on error
      const refreshed = await leetcodeService.getDailyPlan();
      if (refreshed?.data) setDailyPlan(refreshed.data);
    } finally {
      setTogglingTaskId(null);
    }
  };

  // 6. Handle Period Selection for History Chart
  const handlePeriodChange = async (days) => {
    setSelectedDays(days);
    setIsLoadingHistory(true);
    try {
      const res = await leetcodeService.getActivityHistory(days);
      if (res?.data) {
        setActivityHistory(res.data);
      }
    } catch (err) {
      console.warn('Failed to load activity history:', err);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  // Extract strictly verified metrics from real profile data
  const stats = profile?.statistics || {};
  const contest = profile?.contest || {};
  const recentList = profile?.recent_activity || [];
  const displayedSubmissions = isSubmissionsExpanded ? recentList : recentList.slice(0, 5);
  const handleName = profile?.leetcode_username || 'Not Connected';

  const easySolved = Number(stats.easy_solved ?? 0);
  const mediumSolved = Number(stats.medium_solved ?? 0);
  const hardSolved = Number(stats.hard_solved ?? 0);
  const totalSolved = Number(stats.total_solved ?? (easySolved + mediumSolved + hardSolved));
  const configuredTarget = 500; // Standard placement preparation goal
  const targetCompletionPct = Math.min(100, Math.round((totalSolved / configuredTarget) * 100));

  const streakDays = Number(stats.current_streak ?? profile?.profile?.streak ?? 0);
  const maxStreakDays = Number(stats.longest_streak ?? Math.max(streakDays, 1));
  const readinessScore = readinessBreakdown?.readiness_score ?? (totalSolved > 0 ? Math.min(95, Math.max(30, Math.round((totalSolved / 350) * 85))) : 25);

  const difficultyChartData = [
    { name: 'Easy', Solved: easySolved, Target: 150, color: '#10b981' },
    { name: 'Medium', Solved: mediumSolved, Target: 250, color: '#6366f1' },
    { name: 'Hard', Solved: hardSolved, Target: 100, color: '#f43f5e' },
  ];

  // Topic Performance from real topic_statistics
  const topicStats = profile?.topic_statistics || [];
  const topTopics = topicStats.slice(0, 8).map((t) => {
    const solved = t.problemsSolved || 0;
    const target = 40;
    const score = Math.min(100, Math.max(0, Math.round((solved / target) * 100)));
    return {
      topic: t.tagName || 'Topic',
      solved: solved,
      target: target,
      score: score,
      status: score >= 80 ? 'Mastered' : score >= 40 ? 'Proficient' : 'Developing',
    };
  });

  // Filter Focus Areas by Priority with dynamic counts
  const highPriorityCount = focusAreas.filter((fa) => fa.priority === 'High').length;
  const mediumPriorityCount = focusAreas.filter((fa) => fa.priority === 'Medium').length;
  const lowPriorityCount = focusAreas.filter((fa) => fa.priority === 'Low').length;

  const filteredFocusAreas = focusAreas.filter((fa) => {
    if (focusFilter === 'All') return true;
    return fa.priority === focusFilter;
  });

  return (
    <div className="space-y-8 animate-in fade-in duration-300 pb-12">
      {/* ============================================================ */}
      {/* 1. PROFILE SUMMARY & HEADER                                    */}
      {/* ============================================================ */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6 p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-indigo-950/70 via-purple-950/50 to-[#121624] border border-indigo-500/30 shadow-2xl">
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <span className="p-2 rounded-xl bg-purple-500/10 border border-purple-500/30 text-purple-400">
              <Code className="w-6 h-6" />
            </span>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              LeetCode Intelligence
            </h1>
          </div>
          <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
            Data-driven DSA readiness diagnostic. Track verified submissions, conquer topic deficits, and prepare with daily recommended algorithmic challenges.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start lg:self-center shrink-0 flex-wrap">
          {isConnected ? (
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
                href={`https://leetcode.com/${handleName}`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 px-4 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs sm:text-sm font-semibold rounded-xl transition-all shadow-lg shadow-indigo-600/30 border border-indigo-400/30"
              >
                <span>LeetCode Profile</span>
                <ExternalLink className="w-4 h-4" />
              </a>
            </>
          ) : (
            <button
              onClick={() => setIsConnectModalOpen(true)}
              className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs sm:text-sm font-semibold rounded-xl transition-all shadow-lg shadow-indigo-600/30 border border-indigo-400/30"
            >
              <Plus className="w-4 h-4" />
              <span>Connect LeetCode Account</span>
            </button>
          )}
        </div>
      </div>

      {/* METADATA STATUS BAR */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 p-4 rounded-2xl bg-[#121624] border border-[#232b3e] text-xs font-mono shadow-xl">
        <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e]">
          <span className="text-slate-400">Profile Handle</span>
          <span className="text-white font-bold">@{isConnected ? handleName : 'Not Connected'}</span>
        </div>

        <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e]">
          <span className="text-slate-400">Contest Rating</span>
          <span className="text-amber-400 font-bold flex items-center gap-1">
            <Trophy className="w-3.5 h-3.5 text-amber-400" />
            {contest.rating ? `${Math.round(contest.rating)} (${contest.top_percentage ? `Top ${contest.top_percentage}%` : 'Ranked'})` : 'No Contest History'}
          </span>
        </div>

        <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e]">
          <span className="text-slate-400">Acceptance Rate</span>
          <span className="text-emerald-400 font-bold">
            {stats.acceptance_rate != null ? `${stats.acceptance_rate}%` : 'N/A'}
          </span>
        </div>

        <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e]">
          <span className="text-slate-400">Status</span>
          <div className="flex items-center gap-2">
            <span
              className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-lg text-xs font-semibold ${
                isConnected
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
              }`}
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              {isConnected ? 'LeetCode Synced' : 'Not Connected'}
            </span>
            {isConnected && (
              <button
                onClick={handleDisconnect}
                title="Disconnect LeetCode Account"
                className="p-1 rounded text-slate-400 hover:text-rose-400 hover:bg-[#1a2030] transition-colors"
              >
                <Power className="w-3.5 h-3.5 text-rose-400" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* ============================================================ */}
      {/* 2. KPI CARDS (Total Solved, Current Streak, DSA Readiness)   */}
      {/* ============================================================ */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Total Solved Card */}
        <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] hover:border-purple-500/40 transition-colors shadow-xl">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">
              Total Solved
            </span>
            <div className="p-2.5 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white font-mono">{totalSolved}</span>
            <span className="text-xs text-slate-400 font-mono">/ {configuredTarget} Target</span>
          </div>
          <div className="mt-3 flex items-center justify-between text-xs font-mono">
            <span className="text-emerald-400 font-semibold">
              Progress: {targetCompletionPct}% Complete
            </span>
            <span className="text-slate-500">
              {totalSolved >= configuredTarget ? 'Target Achieved' : `${configuredTarget - totalSolved} remaining`}
            </span>
          </div>
          {/* Progress Bar Capped at 100% */}
          <div className="w-full bg-[#0f131d] rounded-full h-1.5 mt-2 overflow-hidden border border-[#232b3e]">
            <div
              className="h-full bg-gradient-to-r from-purple-500 to-indigo-500 rounded-full transition-all duration-500"
              style={{ width: `${targetCompletionPct}%` }}
            ></div>
          </div>
        </div>

        {/* Current Streak Card */}
        <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] hover:border-amber-500/40 transition-colors shadow-xl">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">
              Current Streak
            </span>
            <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
              <Flame className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white font-mono">{streakDays}</span>
            <span className="text-xs text-slate-400 font-mono">Days</span>
          </div>
          <div className="mt-3 text-xs text-amber-400 font-medium flex items-center justify-between">
            <span>
              Best Streak: <strong className="text-white">{maxStreakDays} Days</strong>
            </span>
            <span className="text-slate-500 font-mono">
              {streakDays > 0 ? 'Active Practice' : 'Solve Today'}
            </span>
          </div>
          <div className="w-full bg-[#0f131d] rounded-full h-1.5 mt-2 overflow-hidden border border-[#232b3e]">
            <div
              className="h-full bg-amber-500 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, Math.round((streakDays / Math.max(1, maxStreakDays)) * 100))}%` }}
            ></div>
          </div>
        </div>

        {/* DSA Readiness Card */}
        <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] hover:border-indigo-500/40 transition-colors shadow-xl">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">
              DSA Readiness
            </span>
            <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <Target className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-white font-mono">{readinessScore}%</span>
              <span className="text-xs text-indigo-300 font-mono">Benchmark</span>
            </div>
            <button
              onClick={() => setIsReadinessModalOpen(true)}
              className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 underline underline-offset-4 flex items-center gap-1"
            >
              <span>View Breakdown</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
          <div className="mt-3 text-xs text-slate-400 font-medium">
            Cutoff benchmark: {readinessBreakdown?.target_tier || 'Tier-1 Technical Screening'}
          </div>
          <div className="w-full bg-[#0f131d] rounded-full h-1.5 mt-2 overflow-hidden border border-[#232b3e]">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                readinessScore >= 80 ? 'bg-emerald-500' : readinessScore >= 60 ? 'bg-indigo-500' : 'bg-amber-500'
              }`}
              style={{ width: `${readinessScore}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* ============================================================ */}
      {/* 3. DIFFICULTY BREAKDOWN & TOPIC PERFORMANCE                   */}
      {/* ============================================================ */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Difficulty Breakdown */}
        <div className="bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-xl">
          <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
            <div>
              <h3 className="font-bold text-white text-base">Difficulty Breakdown</h3>
              <p className="text-xs text-slate-400">Verified unique accepted problems</p>
            </div>
            <span className="text-xs font-mono text-indigo-400 font-semibold px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20">
              Target vs Solved
            </span>
          </div>

          <div className="h-48 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={difficultyChartData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f293d" vertical={false} />
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
                  {difficultyChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-2.5 pt-2 border-t border-[#232b3e]">
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="text-emerald-400 font-bold">Easy: {easySolved} solved</span>
              <span className="text-slate-400">Target: 150 ({Math.min(100, Math.round((easySolved / 150) * 100))}%)</span>
            </div>
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="text-indigo-400 font-bold">Medium: {mediumSolved} solved</span>
              <span className="text-slate-400">Target: 250 ({Math.min(100, Math.round((mediumSolved / 250) * 100))}%)</span>
            </div>
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="text-rose-400 font-bold">Hard: {hardSolved} solved</span>
              <span className="text-slate-400">Target: 100 ({Math.min(100, Math.round((hardSolved / 100) * 100))}%)</span>
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

          {topTopics.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {topTopics.map((topic, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-xl bg-[#0f131d] border border-[#232b3e] space-y-2.5 hover:border-indigo-500/30 transition-colors"
                >
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-white">{topic.topic}</span>
                    <span className="font-mono text-indigo-400 font-bold">{topic.score}% Mastery</span>
                  </div>

                  <div className="w-full bg-[#121624] rounded-full h-2 overflow-hidden border border-[#232b3e]">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        topic.score >= 80 ? 'bg-emerald-500' : topic.score >= 40 ? 'bg-indigo-500' : 'bg-amber-500'
                      }`}
                      style={{ width: `${topic.score}%` }}
                    ></div>
                  </div>

                  <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 pt-0.5">
                    <span>
                      {topic.solved} solved (Target: {topic.target})
                    </span>
                    <span
                      className={`font-semibold px-2 py-0.5 rounded text-[10px] ${
                        topic.status === 'Mastered'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : topic.status === 'Proficient'
                          ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      }`}
                    >
                      {topic.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center text-slate-400 text-sm border border-dashed border-[#232b3e] rounded-xl">
              Connect your LeetCode profile to view topic performance and mastery diagnostics.
            </div>
          )}
        </div>
      </div>

      {/* ============================================================ */}
      {/* 4. TODAY'S DSA PRACTICE PLAN                                  */}
      {/* ============================================================ */}
      <div className="bg-[#121624] p-6 rounded-3xl border border-indigo-500/20 shadow-2xl space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-[#232b3e]">
          <div>
            <div className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-purple-400" />
              <h2 className="text-lg font-bold text-white tracking-tight">
                Today's DSA Practice Plan
              </h2>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Personalized problem recommendations targeting your active weak areas. Persisted directly to your daily placement roadmap.
            </p>
          </div>

          {dailyPlan && (
            <div className="flex items-center gap-3 self-start sm:self-center">
              <span className="px-3 py-1 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-300 font-mono text-xs font-semibold">
                Target: {dailyPlan.target_count} Problems
              </span>
              <span className="px-3 py-1 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 font-mono text-xs font-semibold">
                Completed: {dailyPlan.completed_count} / {dailyPlan.target_count}
              </span>
              <span className="px-3 py-1 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 font-mono text-xs font-semibold">
                {dailyPlan.remaining_count} Remaining
              </span>
            </div>
          )}
        </div>

        {dailyPlan && dailyPlan.tasks && dailyPlan.tasks.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {dailyPlan.tasks.map((task) => {
              const isCompleted = task.status === 'completed';
              const isBusy = togglingTaskId === task.task_id;

              return (
                <div
                  key={task.task_id}
                  className={`p-5 rounded-2xl border transition-all duration-200 flex flex-col justify-between ${
                    isCompleted
                      ? 'bg-[#0f131d]/80 border-emerald-500/30 opacity-90'
                      : 'bg-[#0f131d] border-[#232b3e] hover:border-purple-500/40 shadow-lg'
                  }`}
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between gap-2">
                      <span
                        className={`px-2.5 py-0.5 rounded-lg text-[11px] font-mono font-semibold uppercase ${
                          task.difficulty === 'Easy'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : task.difficulty === 'Hard'
                            ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                            : 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                        }`}
                      >
                        {task.difficulty}
                      </span>
                      <span className="text-[11px] font-mono text-slate-400 bg-[#121624] px-2 py-0.5 rounded border border-[#232b3e]">
                        {task.topic}
                      </span>
                    </div>

                    <h4
                      className={`text-sm font-bold tracking-tight ${
                        isCompleted ? 'text-slate-400 line-through' : 'text-white'
                      }`}
                    >
                      {task.title}
                    </h4>

                    <div className="flex items-center gap-1.5 text-xs text-slate-400 font-mono">
                      <Clock className="w-3.5 h-3.5 text-slate-500" />
                      <span>{task.estimated_minutes || 30} mins recommended</span>
                    </div>
                  </div>

                  <div className="pt-4 mt-4 border-t border-[#232b3e] flex items-center justify-between gap-3">
                    <button
                      onClick={() => handleToggleTask(task.task_id)}
                      disabled={isBusy}
                      className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                        isCompleted
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/30'
                          : 'bg-[#1a2030] text-slate-300 border border-[#232b3e] hover:bg-[#232b3e] hover:text-white'
                      }`}
                    >
                      {isCompleted ? (
                        <>
                          <Check className="w-3.5 h-3.5 text-emerald-400" />
                          <span>Done</span>
                        </>
                      ) : (
                        <>
                          <span className="w-3.5 h-3.5 rounded-full border border-slate-500 inline-block"></span>
                          <span>Mark Done</span>
                        </>
                      )}
                    </button>

                    <a
                      href={task.resource_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs font-semibold rounded-xl shadow-md transition-all"
                    >
                      <span>Solve on LeetCode</span>
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  </div>
                </div>
              );
            })}
          </div>
        ) : !isConnected ? (
          <div className="p-8 text-center text-slate-400 text-sm border border-dashed border-[#232b3e] rounded-2xl">
            Connect your LeetCode profile to generate daily algorithmic practice recommendations targeting your active weak topics.
          </div>
        ) : (
          <div className="p-8 text-center text-slate-400 text-sm border border-dashed border-[#232b3e] rounded-2xl">
            No active DSA practice tasks configured for today. Click "Refresh Analysis" to generate recommendations based on your weak topics.
          </div>
        )}
      </div>

      {/* ============================================================ */}
      {/* 5. PROGRESS TREND CHART                                       */}
      {/* ============================================================ */}
      <div className="bg-[#121624] p-6 rounded-3xl border border-[#232b3e] shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-3 border-b border-[#232b3e]">
          <div>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-indigo-400" />
              <h3 className="font-bold text-white text-base">Progress Trend & Submission Activity</h3>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Daily submissions and coding activity from your LeetCode submission calendar. Clearly distinguishes verified zero activity from unrecorded periods.
            </p>
          </div>

          {/* Period selector */}
          <div className="flex items-center gap-1.5 bg-[#0f131d] p-1 rounded-xl border border-[#232b3e]">
            {[7, 30, 90].map((days) => (
              <button
                key={days}
                onClick={() => handlePeriodChange(days)}
                disabled={isLoadingHistory}
                className={`px-3 py-1 text-xs font-mono font-semibold rounded-lg transition-all ${
                  selectedDays === days
                    ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-white hover:bg-[#1a2030]'
                }`}
              >
                {days === 7 ? 'Last 7 Days' : days === 30 ? 'Last 30 Days' : 'Last 90 Days'}
              </button>
            ))}
          </div>
        </div>

        {/* Total in period highlight */}
        <div className="flex items-center justify-between text-xs font-mono text-slate-400 px-1">
          <span>
            Period Total:{' '}
            <strong className="text-white">
              {activityHistory?.total_submissions_in_period ?? activityHistory?.total_solved_in_period ?? 0} submissions recorded
            </strong>
          </span>
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-purple-500 inline-block"></span>
              <span>Submission Activity</span>
            </span>
            {activityHistory?.has_contest_history && (
              <span className="flex items-center gap-1.5 text-amber-400">
                <Trophy className="w-3 h-3" />
                <span>Contest History Available</span>
              </span>
            )}
          </div>
        </div>

        {/* Responsive Area Chart */}
        <div className="h-64 w-full pt-2">
          {activityHistory?.data_points && activityHistory.data_points.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={activityHistory.data_points} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                <defs>
                  <linearGradient id="activityGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f293d" vertical={false} />
                <XAxis dataKey="day" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} allowDecimals={false} />
                <Tooltip
                  content={({ active, payload, label }) => {
                    if (active && payload && payload.length) {
                      const pt = payload[0].payload;
                      return (
                        <div className="bg-[#0f172a] border border-[#232b3e] p-3 rounded-xl shadow-2xl text-xs space-y-1.5 font-mono">
                          <div className="font-bold text-white text-sm">
                            {label} ({pt.date})
                          </div>
                          <div className="text-purple-400 font-semibold flex items-center gap-1.5">
                            <span className="w-2 h-2 rounded-full bg-purple-500 inline-block"></span>
                            <span>Submissions: {pt.submissions ?? pt.problems_solved}</span>
                          </div>
                          {pt.status === 'verified_zero' && (
                            <div className="text-slate-400 text-[11px]">
                              Status: Verified 0 Submissions
                            </div>
                          )}
                          {pt.status === 'unrecorded' && (
                            <div className="text-amber-400 text-[11px]">
                              Status: Prior to recent sync window
                            </div>
                          )}
                          {pt.contest_rating && (
                            <div className="text-amber-400 text-[11px] pt-1 border-t border-slate-800">
                              Contest Rating: {pt.contest_rating}
                            </div>
                          )}
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="problems_solved"
                  stroke="#a855f7"
                  strokeWidth={2.5}
                  fillOpacity={1}
                  fill="url(#activityGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : !isConnected ? (
            <div className="h-full flex items-center justify-center text-slate-400 text-xs font-mono border border-dashed border-[#232b3e] rounded-2xl">
              Connect your LeetCode profile to visualize submission activity, cadence, and contest rating progress.
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-slate-400 text-xs font-mono border border-dashed border-[#232b3e] rounded-2xl">
              No historical activity records found for the selected {selectedDays}-day window. Click "Refresh Analysis" to synchronize your submission calendar.
            </div>
          )}
        </div>
      </div>

      {/* ============================================================ */}
      {/* 6. WEAK TOPIC RECOMMENDATIONS ("FOCUS AREAS")                 */}
      {/* ============================================================ */}
      <div className="bg-[#121624] p-6 rounded-3xl border border-[#232b3e] shadow-xl space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-[#232b3e]">
          <div>
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-indigo-400" />
              <h2 className="text-lg font-bold text-white tracking-tight">
                Focus Areas & Weak Topic Recommendations
              </h2>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Deep evaluation across 14 essential DSA patterns weighted by Tier-1 technical interview relevance.
            </p>
          </div>

          {/* Priority filter buttons with dynamic live counts */}
          <div className="flex items-center gap-1.5 bg-[#0f131d] p-1 rounded-xl border border-[#232b3e] self-start sm:self-center flex-wrap">
            {[
              { id: 'All', label: `All (${focusAreas.length})` },
              { id: 'High', label: `High (${highPriorityCount})` },
              { id: 'Medium', label: `Medium (${mediumPriorityCount})` },
              { id: 'Low', label: `Low (${lowPriorityCount})` },
            ].map(({ id, label }) => (
              <button
                key={id}
                onClick={() => setFocusFilter(id)}
                className={`px-3 py-1 text-xs font-mono font-semibold rounded-lg transition-all ${
                  focusFilter === id
                    ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-white hover:bg-[#1a2030]'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {filteredFocusAreas.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredFocusAreas.map((topicItem, index) => {
              const isHigh = topicItem.priority === 'High';
              const isMedium = topicItem.priority === 'Medium';

              return (
                <div
                  key={index}
                  className={`p-5 rounded-2xl border transition-all duration-200 bg-[#0f131d] space-y-4 hover:border-indigo-500/40 ${
                    isHigh
                      ? 'border-rose-500/30'
                      : isMedium
                      ? 'border-amber-500/20'
                      : 'border-[#232b3e]'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="text-base font-bold text-white">{topicItem.topic}</h4>
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
                            isHigh
                              ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                              : isMedium
                              ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                              : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          }`}
                        >
                          {topicItem.priority} Priority
                        </span>
                      </div>
                      <p className="text-[11px] font-mono text-slate-400 mt-0.5">
                        Interview Weight: {topicItem.interview_weight}
                      </p>
                    </div>

                    <div className="text-right font-mono">
                      <span className="text-sm font-bold text-white">
                        {topicItem.mastery_percentage}%
                      </span>
                      <p className="text-[10px] text-slate-400">Mastery</p>
                    </div>
                  </div>

                  {/* Solved vs Target count bar */}
                  <div className="space-y-1.5">
                    <div className="flex justify-between text-xs font-mono text-slate-300">
                      <span>{topicItem.problems_solved} solved</span>
                      <span className="text-slate-400">Target: {topicItem.target}</span>
                    </div>
                    <div className="w-full bg-[#121624] rounded-full h-2 overflow-hidden border border-[#232b3e]">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          topicItem.mastery_percentage >= 80
                            ? 'bg-emerald-500'
                            : topicItem.mastery_percentage >= 40
                            ? 'bg-indigo-500'
                            : 'bg-rose-500'
                        }`}
                        style={{ width: `${topicItem.mastery_percentage}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Recommended Action Advice */}
                  <div className="p-3 bg-[#121624] rounded-xl border border-[#232b3e] text-xs text-slate-300 flex items-start gap-2">
                    <Info className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                    <span>{topicItem.recommended_action}</span>
                  </div>

                  {/* Suggested Problems */}
                  {topicItem.suggested_problems && topicItem.suggested_problems.length > 0 && (
                    <div className="space-y-2 pt-2 border-t border-[#232b3e]">
                      <span className="text-[11px] font-mono uppercase text-slate-400 font-semibold block">
                        Suggested Practice:
                      </span>
                      <div className="flex flex-wrap gap-2">
                        {topicItem.suggested_problems.map((prob, pIdx) => (
                          <a
                            key={pIdx}
                            href={prob.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs bg-[#1a2030] hover:bg-[#232b3e] text-slate-200 hover:text-white border border-[#232b3e] transition-colors font-mono"
                          >
                            <span>{prob.title}</span>
                            <span
                              className={`text-[10px] font-bold ${
                                prob.difficulty === 'Easy'
                                  ? 'text-emerald-400'
                                  : prob.difficulty === 'Hard'
                                  ? 'text-rose-400'
                                  : 'text-indigo-400'
                              }`}
                            >
                              ({prob.difficulty})
                            </span>
                            <ExternalLink className="w-3 h-3 text-slate-400" />
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ) : !isConnected ? (
          <div className="p-8 text-center text-slate-400 text-sm border border-dashed border-[#232b3e] rounded-2xl">
            Connect your LeetCode account to evaluate weak topics, mastery diagnostics, and tailored problem recommendations.
          </div>
        ) : (
          <div className="p-8 text-center text-slate-400 text-sm border border-dashed border-[#232b3e] rounded-2xl">
            No focus areas found for {focusFilter === 'All' ? 'the selected filter' : `${focusFilter} Priority`}.
          </div>
        )}
      </div>

      {/* ============================================================ */}
      {/* 7. RECENT SOLVED SUBMISSIONS                                  */}
      {/* ============================================================ */}
      <div className="bg-[#121624] p-6 rounded-3xl border border-[#232b3e] shadow-xl space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
          <div>
            <h3 className="font-bold text-white text-base">Recent Solved Submissions</h3>
            <p className="text-xs text-slate-400">Accepted problem submissions retrieved directly via LeetCode GraphQL</p>
          </div>
          <span className="text-xs font-mono text-emerald-400 font-semibold px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
            {recentList.length} Recent Accepted
          </span>
        </div>

        {recentList.length > 0 ? (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-[#232b3e] text-slate-400 uppercase text-[11px]">
                    <th className="pb-3 font-semibold">Problem Title</th>
                    <th className="pb-3 font-semibold">Status</th>
                    <th className="pb-3 font-semibold">Accepted At</th>
                    <th className="pb-3 font-semibold text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#232b3e]/60">
                  {displayedSubmissions.map((sub, idx) => {
                    const submissionDate = sub.timestamp
                      ? new Date(parseInt(sub.timestamp) * 1000).toLocaleDateString([], {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric',
                        })
                      : 'Accepted';

                    const problemUrl =
                      sub.url ||
                      (sub.title_slug
                        ? `https://leetcode.com/problems/${sub.title_slug}/`
                        : `https://leetcode.com/problems/${sub.title.toLowerCase().replace(/[^a-z0-9]+/g, '-')}/`);

                    return (
                      <tr key={idx} className="hover:bg-[#0f131d] transition-colors">
                        <td className="py-3.5 text-white font-semibold flex items-center gap-2">
                          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                          <span>{sub.title}</span>
                        </td>
                        <td className="py-3.5">
                          <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                            {sub.status || 'Accepted'}
                          </span>
                        </td>
                        <td className="py-3.5 text-slate-400">{submissionDate}</td>
                        <td className="py-3.5 text-right">
                          <a
                            href={problemUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 px-3 py-1 bg-[#1a2030] hover:bg-[#232b3e] text-indigo-300 hover:text-white rounded-lg transition-colors border border-[#232b3e]"
                          >
                            <span>Open</span>
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {recentList.length > 5 && (
              <div className="flex justify-center pt-2">
                <button
                  onClick={() => setIsSubmissionsExpanded(!isSubmissionsExpanded)}
                  className="flex items-center gap-2 px-6 py-2.5 rounded-full bg-[#121624] hover:bg-[#1a2133] text-indigo-400 hover:text-indigo-300 text-xs font-semibold font-mono border border-[#232b3e] hover:border-indigo-500/40 transition-all shadow-md group cursor-pointer"
                >
                  <span>
                    {isSubmissionsExpanded
                      ? 'Show Less'
                      : `See All Submissions (${recentList.length})`}
                  </span>
                  {isSubmissionsExpanded ? (
                    <ChevronUp className="w-4 h-4 transition-transform group-hover:-translate-y-0.5" />
                  ) : (
                    <ChevronDown className="w-4 h-4 transition-transform group-hover:translate-y-0.5" />
                  )}
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="p-8 text-center text-slate-400 text-sm border border-dashed border-[#232b3e] rounded-2xl">
            No recent accepted submissions found. Solve problems on LeetCode to populate your activity feed.
          </div>
        )}
      </div>

      {/* ============================================================ */}
      {/* 8. INTERVIEW READINESS BREAKDOWN MODAL                         */}
      {/* ============================================================ */}
      {isReadinessModalOpen && readinessBreakdown && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-in fade-in duration-200">
          <div className="relative w-full max-w-2xl bg-[#121624] border border-[#232b3e] rounded-3xl shadow-2xl p-6 sm:p-8 space-y-6 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-4 border-b border-[#232b3e]">
              <div className="flex items-center gap-2.5">
                <Target className="w-6 h-6 text-indigo-400" />
                <h3 className="text-xl font-bold text-white tracking-tight">
                  DSA Interview Readiness Breakdown
                </h3>
              </div>
              <button
                onClick={() => setIsReadinessModalOpen(false)}
                className="p-1 rounded-xl text-slate-400 hover:text-white hover:bg-[#1a2133] transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Score & Tier Header */}
            <div className="p-5 rounded-2xl bg-[#0f131d] border border-indigo-500/20 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <span className="text-xs font-mono text-slate-400 uppercase tracking-wider block">
                  Overall DSA Screening Score
                </span>
                <span className="text-3xl font-extrabold text-white font-mono">
                  {readinessBreakdown.readiness_score} / 100
                </span>
              </div>
              <div className="text-right">
                <span className="text-xs font-mono text-indigo-400 font-semibold px-3 py-1 rounded-lg bg-indigo-500/10 border border-indigo-500/20">
                  {readinessBreakdown.target_tier}
                </span>
              </div>
            </div>

            {/* Mathematical Rubric Points Breakdown */}
            <div className="space-y-3">
              <h4 className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">
                Mathematical Scoring Formula & Rubric
              </h4>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
                <div className="p-3 rounded-xl bg-[#0f131d] border border-[#232b3e]">
                  <span className="text-slate-400 block text-[11px]">Easy Points</span>
                  <span className="text-emerald-400 font-bold text-base">
                    +{readinessBreakdown.easy_pts}
                  </span>
                  <span className="text-slate-500 block text-[10px] mt-0.5">Max 20 (0.15/ea)</span>
                </div>
                <div className="p-3 rounded-xl bg-[#0f131d] border border-[#232b3e]">
                  <span className="text-slate-400 block text-[11px]">Medium Points</span>
                  <span className="text-indigo-400 font-bold text-base">
                    +{readinessBreakdown.medium_pts}
                  </span>
                  <span className="text-slate-500 block text-[10px] mt-0.5">Max 45 (0.40/ea)</span>
                </div>
                <div className="p-3 rounded-xl bg-[#0f131d] border border-[#232b3e]">
                  <span className="text-slate-400 block text-[11px]">Hard Points</span>
                  <span className="text-rose-400 font-bold text-base">
                    +{readinessBreakdown.hard_pts}
                  </span>
                  <span className="text-slate-500 block text-[10px] mt-0.5">Max 35 (0.70/ea)</span>
                </div>
                <div className="p-3 rounded-xl bg-[#0f131d] border border-[#232b3e]">
                  <span className="text-slate-400 block text-[11px]">Topic Coverage</span>
                  <span className="text-purple-400 font-bold text-base">
                    +{readinessBreakdown.coverage_pts}
                  </span>
                  <span className="text-slate-500 block text-[10px] mt-0.5">Max 15 (1.5/topic)</span>
                </div>
              </div>
              {readinessBreakdown.contest_bonus > 0 && (
                <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-300 font-mono">
                  + {readinessBreakdown.contest_bonus} Points Contest Bonus for competitive rating
                </div>
              )}
            </div>

            {/* Strengths & Gaps */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="p-4 rounded-xl bg-[#0f131d] border border-emerald-500/20 space-y-2">
                <span className="font-bold text-emerald-400 flex items-center gap-1.5 font-mono">
                  <CheckCircle2 className="w-4 h-4" />
                  Key Strengths
                </span>
                <ul className="space-y-1.5 text-slate-300 list-disc list-inside">
                  {readinessBreakdown.strengths.map((s, idx) => (
                    <li key={idx}>{s}</li>
                  ))}
                </ul>
              </div>

              <div className="p-4 rounded-xl bg-[#0f131d] border border-amber-500/20 space-y-2">
                <span className="font-bold text-amber-400 flex items-center gap-1.5 font-mono">
                  <AlertTriangle className="w-4 h-4" />
                  Growth Areas
                </span>
                <ul className="space-y-1.5 text-slate-300 list-disc list-inside">
                  {readinessBreakdown.gaps.map((g, idx) => (
                    <li key={idx}>{g}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Explanation & Ethical Disclaimer */}
            <div className="space-y-2">
              <p className="text-xs text-slate-300 leading-relaxed font-mono">
                {readinessBreakdown.explanation}
              </p>
              <p className="text-[11px] text-slate-500 italic border-t border-[#232b3e] pt-3">
                Disclaimer: {readinessBreakdown.disclaimer}
              </p>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setIsReadinessModalOpen(false)}
                className="px-5 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-all shadow-md"
              >
                Close Breakdown
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ============================================================ */}
      {/* CONNECT LEETCODE MODAL                                       */}
      {/* ============================================================ */}
      {isConnectModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-in fade-in duration-200">
          <div className="relative w-full max-w-md bg-[#121624] border border-[#232b3e] rounded-2xl shadow-2xl p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
              <div className="flex items-center gap-2">
                <Code className="w-5 h-5 text-indigo-400" />
                <h3 className="font-bold text-white text-base">Connect LeetCode Profile</h3>
              </div>
              <button
                onClick={() => setIsConnectModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-[#1a2133] transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleConnect} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5 font-mono">
                  LeetCode Username or Profile URL:
                </label>
                <div className="relative">
                  <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-500 font-mono text-sm">
                    @
                  </span>
                  <input
                    type="text"
                    value={connectUsername}
                    onChange={(e) => setConnectUsername(e.target.value)}
                    placeholder="e.g. neetcode or your_handle"
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
                  disabled={isConnecting || !connectUsername.trim()}
                  className="px-5 py-2 rounded-xl text-xs font-semibold bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white transition-all shadow-md shadow-indigo-600/25 disabled:opacity-50 flex items-center gap-1.5"
                >
                  {isConnecting ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      <span>Connecting & Syncing...</span>
                    </>
                  ) : (
                    <span>Connect & Sync Stats</span>
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
