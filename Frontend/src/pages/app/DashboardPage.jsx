import React, { useEffect, useState, useMemo, useCallback } from 'react';
import { NavLink } from 'react-router-dom';
import {
  ArrowRight,
  ArrowUpRight,
  Bot,
  CalendarCheck2,
  Code2,
  FileText,
  Flame,
  Github,
  LineChart,
  RefreshCw,
  Sparkles,
  Target,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { useUser } from '../../context/UserContext';
import { usePlanning } from '../../context/PlanningContext';
import { readinessService } from '../../services/readinessService';
import { skillGapService } from '../../services/skillGapService';
import { leetcodeService } from '../../services/leetcodeService';
import { githubService } from '../../services/githubService';
import { resumeService } from '../../services/resumeService';
import { planningService } from '../../services/planningService';
import { TelemetryChart, ActionPlanList } from '../../components/dashboard';

const Panel = ({ children, className = '' }) => (
  <section className={`p-5 sm:p-6 rounded-2xl bg-[#121624] border border-[#232b3e] shadow-xl ${className}`}>
    {children}
  </section>
);

const PanelTitle = ({ icon, children, action }) => (
  <div className="flex items-center justify-between gap-4 mb-5">
    <h2 className="flex items-center gap-2 text-sm sm:text-base font-bold text-white">
      {icon}
      <span>{children}</span>
    </h2>
    {action}
  </div>
);

export const DashboardPage = () => {
  const { user } = useUser();
  const { tasks, toggleTaskCompletion } = usePlanning();

  const displayName = user?.name || user?.full_name || 'Candidate';
  const targetRole = user?.targetRole || user?.career?.targetRole || user?.target_role || 'AI/ML Engineer';
  const companyTier = user?.companyTier || user?.career?.companyTier || 'Tier-1 Product (MAANG / Unicorns)';

  // Real readiness score & history
  const [readinessScore, setReadinessScore] = useState(() => user?.overallReadinessScore || 64);
  const [readinessHistory, setReadinessHistory] = useState([]);
  
  // Real progress data from backend /api/v1/progress
  const [progressData, setProgressData] = useState(null);
  const [progressLoading, setProgressLoading] = useState(true);

  // Real LeetCode profile
  const [realLcHandle, setRealLcHandle] = useState(() => {
    return user?.leetcodeHandle || user?.leetcode_username || localStorage.getItem('placementor_leetcode_handle') || '';
  });
  const [realLcSolved, setRealLcSolved] = useState(user?.leetcodeSolved || 0);

  // Real GitHub profile & sync state
  const [realGhHandle, setRealGhHandle] = useState(() => user?.githubHandle || '');
  const [isGhSyncing, setIsGhSyncing] = useState(false);
  const [ghSyncStatus, setGhSyncStatus] = useState('');

  // Real Resume details
  const [resumeName, setResumeName] = useState(() => {
    return user?.resumeFileName || localStorage.getItem('placementCopilotResumeName') || '';
  });

  // Real Skill Gaps & AI Mentor recommendations
  const [topGaps, setTopGaps] = useState([]);
  const [skillsLoading, setSkillsLoading] = useState(true);

  // Load progress metrics dynamically from /api/v1/progress
  const loadProgress = useCallback(async () => {
    try {
      const fullProgress = await planningService.getFullProgressFromApi();
      if (fullProgress) {
        setProgressData(fullProgress);
      }
    } catch (err) {
      console.warn('Failed to load progress metrics:', err);
    } finally {
      setProgressLoading(false);
    }
  }, []);

  // Initial telemetry and data hydration
  useEffect(() => {
    let isMounted = true;

    // 1. Fetch Readiness Summary & History
    readinessService.getSummary().then((summary) => {
      if (!isMounted || !summary) return;
      if (typeof summary.overall_score === 'number' && summary.overall_score > 0) {
        setReadinessScore(Math.round(summary.overall_score));
      }
    }).catch((err) => console.warn('Readiness summary load failed:', err));

    readinessService.getHistory(10).then((history) => {
      if (!isMounted || !history) return;
      setReadinessHistory(Array.isArray(history) ? history : []);
    }).catch((err) => console.warn('Readiness history load failed:', err));

    // 2. Fetch Progress Metrics
    loadProgress();

    // 3. Hydrate real LeetCode profile
    leetcodeService.getProfile().then((res) => {
      if (!isMounted || !res?.data) return;
      const profile = res.data;
      const username = profile.username || profile.handle;
      if (username) {
        setRealLcHandle(username);
        localStorage.setItem('placementor_leetcode_handle', username);
      }
      if (typeof profile.total_solved === 'number') {
        setRealLcSolved(profile.total_solved);
      } else if (typeof profile.solved_count === 'number') {
        setRealLcSolved(profile.solved_count);
      }
    }).catch((err) => console.warn('LeetCode profile load failed:', err));

    // 4. Hydrate real GitHub profile
    githubService.getProfile().then((res) => {
      if (!isMounted || !res) return;
      const data = res.data || res;
      const username = data.github_username || data.username;
      if (username) {
        setRealGhHandle(username);
      }
      if (data.sync?.status) {
        setGhSyncStatus(data.sync.status);
      }
    }).catch((err) => console.warn('GitHub profile load failed:', err));

    // 5. Hydrate real Resumes
    resumeService.getResumes().then((res) => {
      if (!isMounted || !res) return;
      const list = res.data || (Array.isArray(res) ? res : []);
      if (list && list.length > 0) {
        const active = list.find((r) => r.is_active) || list[0];
        if (active?.filename) {
          setResumeName(active.filename);
        }
      }
    }).catch((err) => console.warn('Resumes load failed:', err));

    // 6. Fetch Skill Gap Summary
    skillGapService.getSummary().then((summary) => {
      if (!isMounted || !summary) return;
      if (Array.isArray(summary.top_priority_gaps) && summary.top_priority_gaps.length > 0) {
        setTopGaps(summary.top_priority_gaps.slice(0, 3));
      }
      setSkillsLoading(false);
    }).catch((err) => {
      console.warn('Skill gaps load failed:', err);
      if (isMounted) setSkillsLoading(false);
    });

    return () => {
      isMounted = false;
    };
  }, [loadProgress]);

  // GitHub one-click sync handler
  const handleGithubSync = async (e) => {
    e.preventDefault();
    if (isGhSyncing) return;
    setIsGhSyncing(true);
    try {
      const res = await githubService.syncProfile();
      if (res?.data) {
        setGhSyncStatus(res.data.sync?.status || 'synced');
      }
    } catch (err) {
      console.warn('Manual GitHub sync failed:', err);
    } finally {
      setIsGhSyncing(false);
    }
  };

  // Re-fetch progress whenever a task is completed in ActionPlanList
  const handleTaskCompleted = useCallback(() => {
    loadProgress();
  }, [loadProgress]);

  // Next eligible pending task from user's active roadmap
  const nextPendingTask = useMemo(() => {
    if (!tasks || !Array.isArray(tasks)) return null;
    return tasks.find((t) => !t.completed && t.status !== 'completed') || null;
  }, [tasks]);

  const allTasksCompleted = useMemo(() => {
    if (!tasks || tasks.length === 0) return false;
    return tasks.every((t) => t.completed || t.status === 'completed');
  }, [tasks]);

  const startPlanRoute = useMemo(() => {
    if (nextPendingTask) {
      if (nextPendingTask.dayNumber) {
        return `/roadmap?day=${nextPendingTask.dayNumber}&taskId=${encodeURIComponent(nextPendingTask.id || nextPendingTask.taskId)}`;
      }
      return nextPendingTask.route || '/tasks';
    }
    if (allTasksCompleted) {
      return '/tasks';
    }
    return '/roadmap';
  }, [nextPendingTask, allTasksCompleted]);

  const startPlanLabel = useMemo(() => {
    if (nextPendingTask) {
      return "Start Today's Plan";
    }
    if (allTasksCompleted) {
      return "Today's Plan Completed 🎉";
    }
    return "Open 90-Day Roadmap";
  }, [nextPendingTask, allTasksCompleted]);

  // Context-aware greeting and subtext
  const greeting = useMemo(() => {
    const hour = new Date().getHours();
    let timeOfDay = 'Good morning';
    if (hour >= 12 && hour < 17) timeOfDay = 'Good afternoon';
    else if (hour >= 17) timeOfDay = 'Good evening';
    return `${timeOfDay}, ${displayName} 👋`;
  }, [displayName]);

  const activeStreak = progressData?.current_streak ?? user?.streakDays ?? 0;

  const contextSubtext = useMemo(() => {
    if (activeStreak > 0) {
      return `🔥 ${activeStreak}-day active study streak. Keep the momentum going!`;
    }
    if (readinessScore >= 80) {
      return `🎯 Outstanding readiness score. Calibrated for ${targetRole} benchmarks.`;
    }
    return `Targeting ${targetRole}. Complete today's milestone drills to boost your profile.`;
  }, [activeStreak, readinessScore, targetRole]);

  // Helper to map skill gap progress level to percentage
  const calculateGapLevelPercentage = (currentLevel) => {
    if (!currentLevel || currentLevel === 'Untested' || currentLevel === 'None') return 15;
    if (currentLevel === 'Beginner' || currentLevel === 1) return 30;
    if (currentLevel === 'Intermediate' || currentLevel === 2) return 55;
    if (currentLevel === 'Advanced' || currentLevel === 3) return 80;
    if (currentLevel === 'Expert' || currentLevel === 4) return 100;
    return 40;
  };

  return (
    <div className="dashboard-page w-full max-w-5xl mx-auto space-y-5 sm:space-y-6">
      {/* Page Header */}
      <div className="flex items-center gap-2.5 text-lg sm:text-xl font-bold text-white">
        <Code2 size={20} className="text-indigo-400" />
        <span>Dashboard</span>
      </div>

      {/* 1. Personalized Welcome Header */}
      <Panel className="flex flex-col md:flex-row md:items-center justify-between gap-4 sm:gap-6 bg-gradient-to-r from-[#121624] via-[#151b2e] to-[#121624]">
        <div>
          <h1 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight">
            {greeting}
          </h1>
          <p className="mt-1.5 text-xs sm:text-sm text-slate-300">
            Your placement readiness is <strong className="text-indigo-400 font-bold">{readinessScore}%</strong>
            <span className="mx-2 text-slate-600 hidden sm:inline">•</span>
            <span className="block sm:inline text-slate-400 text-xs mt-1 sm:mt-0">{contextSubtext}</span>
          </p>
        </div>
        <NavLink
          to={startPlanRoute}
          className={`inline-flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl text-xs font-semibold transition-all shrink-0 shadow-lg ${
            allTasksCompleted
              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/30'
              : 'bg-indigo-600 hover:bg-indigo-500 text-white hover:shadow-indigo-500/20'
          }`}
        >
          <span>{startPlanLabel}</span>
          <ArrowUpRight size={14} />
        </NavLink>
      </Panel>

      {/* 2. Four Compact Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {/* Readiness Card */}
        <NavLink
          to="/placement-readiness"
          className="p-4 rounded-2xl bg-[#121624] border border-[#232b3e] hover:border-indigo-500/50 hover:bg-[#151b2e] transition-all group shadow-sm flex flex-col justify-between"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-medium">Readiness</span>
            <Target size={14} className="text-indigo-400 opacity-70 group-hover:opacity-100 transition-opacity" />
          </div>
          <strong className="block my-2 text-center text-2xl font-bold text-indigo-400 font-mono">
            {readinessScore}%
          </strong>
          <span className="block text-center text-[11px] text-slate-500 group-hover:text-slate-400 truncate">
            Placement Readiness →
          </span>
        </NavLink>

        {/* Sprint Cadence Card */}
        <NavLink
          to="/roadmap"
          className="p-4 rounded-2xl bg-[#121624] border border-[#232b3e] hover:border-indigo-500/50 hover:bg-[#151b2e] transition-all group shadow-sm flex flex-col justify-between"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-medium">Sprint Cadence</span>
            <span
              className={`text-[10px] px-1.5 py-0.5 rounded font-mono font-medium ${
                activeStreak > 0
                  ? 'text-amber-400 bg-amber-500/10 border border-amber-500/20'
                  : 'text-slate-400 bg-slate-800'
              }`}
            >
              {activeStreak > 0 ? `${activeStreak}D Streak 🔥` : 'Target'}
            </span>
          </div>
          <strong className="block my-2 text-center text-xl font-bold text-white font-mono">
            {user?.dailyGoalMinutes || 90} <span className="text-xs font-normal text-slate-400">Min/Day</span>
          </strong>
          <span className="block text-center text-[11px] text-slate-500 group-hover:text-slate-400 truncate">
            Roadmap Activity →
          </span>
        </NavLink>

        {/* LeetCode Card */}
        <NavLink
          to="/leetcode"
          className="p-4 rounded-2xl bg-[#121624] border border-[#232b3e] hover:border-purple-500/50 hover:bg-[#151b2e] transition-all group shadow-sm flex flex-col justify-between"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-medium">LeetCode</span>
            <span
              className={`inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded font-medium ${
                realLcHandle
                  ? 'text-emerald-400 bg-emerald-500/10 border border-emerald-500/20'
                  : 'text-amber-400 bg-amber-500/10 border border-amber-500/20'
              }`}
            >
              <span className={`w-1.5 h-1.5 rounded-full ${realLcHandle ? 'bg-emerald-400' : 'bg-amber-400'}`} />
              {realLcHandle ? 'Linked' : 'Unlinked'}
            </span>
          </div>
          <strong
            className="block my-2 text-center text-base font-bold text-white truncate"
            title={realLcHandle ? `@${realLcHandle}` : 'Click to link profile'}
          >
            {realLcHandle ? `@${realLcHandle}` : 'Connect Profile'}
          </strong>
          <span className="block text-center text-[11px] text-slate-500 group-hover:text-slate-400 truncate">
            {realLcHandle ? `${realLcSolved} Problems Solved` : 'Track Code Solves →'}
          </span>
        </NavLink>

        {/* Target Role Card */}
        <NavLink
          to="/profile"
          className="p-4 rounded-2xl bg-[#121624] border border-[#232b3e] hover:border-emerald-500/50 hover:bg-[#151b2e] transition-all group shadow-sm flex flex-col justify-between"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-medium">Target Role</span>
            <Code2 size={14} className="text-emerald-400 opacity-70 group-hover:opacity-100 transition-opacity" />
          </div>
          <strong className="block my-2 text-center text-sm font-bold text-white truncate" title={targetRole}>
            {targetRole}
          </strong>
          <span className="block text-center text-[11px] text-slate-500 group-hover:text-slate-400 truncate">
            {companyTier ? companyTier.split('(')[0].trim() : 'View Configuration →'}
          </span>
        </NavLink>
      </div>

      {/* 3. Weekly Progress Chart & Today's Action Plan */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 sm:gap-6 items-stretch">
        {/* Progress Chart Panel */}
        <Panel className="lg:col-span-5 flex flex-col justify-between h-full">
          <PanelTitle
            icon={<LineChart size={16} className="text-indigo-400" />}
            action={
              <NavLink className="text-xs text-indigo-400 hover:underline flex items-center gap-0.5" to="/placement-readiness">
                <span>View Details</span>
                <ArrowRight size={12} />
              </NavLink>
            }
          >
            Your Progress
          </PanelTitle>
          <div className="flex-1">
            <TelemetryChart
              progressData={progressData}
              readinessHistory={readinessHistory}
              loading={progressLoading}
            />
          </div>
        </Panel>

        {/* Today's Action Plan Panel */}
        <Panel className="lg:col-span-7 flex flex-col justify-between h-full">
          <PanelTitle
            icon={<CalendarCheck2 size={16} className="text-indigo-400" />}
            action={
              <NavLink className="text-xs text-indigo-400 hover:underline flex items-center gap-0.5" to="/tasks">
                <span>View All</span>
                <ArrowRight size={12} />
              </NavLink>
            }
          >
            Today's Action Plan
          </PanelTitle>
          <div className="flex-1">
            <ActionPlanList maxItems={3} onTaskCompleted={handleTaskCompleted} />
          </div>
        </Panel>
      </div>

      {/* 4. Skills to Improve & AI Mentor */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 sm:gap-6 items-stretch">
        {/* Skills to Improve Panel */}
        <Panel className="flex flex-col justify-between h-full">
          <PanelTitle
            icon={<Target size={16} className="text-indigo-400" />}
            action={
              <NavLink className="text-xs text-indigo-400 hover:underline flex items-center gap-0.5" to="/skill-gaps">
                <span>View Full Analysis</span>
                <ArrowRight size={12} />
              </NavLink>
            }
          >
            Skills to Improve
          </PanelTitle>

          {skillsLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="p-3 rounded-xl bg-[#0f131d] border border-[#232b3e] animate-pulse space-y-2">
                  <div className="h-3 bg-slate-700/60 rounded w-1/2" />
                  <div className="h-2 bg-slate-800 rounded w-full" />
                </div>
              ))}
            </div>
          ) : topGaps.length > 0 ? (
            <div className="space-y-3.5">
              {topGaps.map((gap, idx) => {
                const pct = calculateGapLevelPercentage(gap.current_level);
                return (
                  <NavLink
                    key={gap.id || `gap-${idx}`}
                    to="/skill-gaps"
                    className="block p-3 rounded-xl bg-[#0f131d] border border-[#232b3e] hover:border-indigo-500/40 hover:bg-[#141926] transition-all group"
                  >
                    <div className="flex items-center justify-between gap-2 mb-1.5">
                      <div className="flex items-center gap-2 min-w-0">
                        <span className="text-xs font-semibold text-slate-200 group-hover:text-indigo-300 transition-colors truncate">
                          {gap.skill}
                        </span>
                        {gap.category && (
                          <span className="text-[10px] px-1.5 py-0.2 rounded font-mono bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 shrink-0">
                            {gap.category}
                          </span>
                        )}
                      </div>
                      <span
                        className={`text-[10px] px-1.5 py-0.5 rounded font-medium shrink-0 ${
                          gap.priority === 'High' || gap.priority === 'Critical'
                            ? 'text-rose-400 bg-rose-500/10 border border-rose-500/20'
                            : 'text-amber-400 bg-amber-500/10 border border-amber-500/20'
                        }`}
                      >
                        {gap.priority || 'High'} Priority
                      </span>
                    </div>

                    {/* Progress Bar */}
                    <div className="h-2 rounded-full bg-[#121624] overflow-hidden my-1.5 border border-[#232b3e]">
                      <div
                        className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all duration-500"
                        style={{ width: `${pct}%` }}
                      />
                    </div>

                    {/* Level Details */}
                    <div className="flex items-center justify-between text-[11px] text-slate-400 pt-0.5">
                      <span className="truncate">
                        Current: <strong className="text-slate-300">{gap.current_level_text || gap.current_level || 'Untested'}</strong>
                      </span>
                      <span className="text-slate-500 shrink-0">
                        Target: <strong className="text-indigo-400">{gap.required_level_text || gap.required_level || 'Proficient'}</strong>
                      </span>
                    </div>
                  </NavLink>
                );
              })}
            </div>
          ) : (
            <div className="p-6 rounded-xl bg-[#0f131d]/60 border border-dashed border-[#232b3e] text-center my-auto">
              <CheckCircle2 className="w-7 h-7 text-emerald-400 mx-auto mb-2" />
              <p className="text-xs font-semibold text-slate-300">No assessed skill gaps</p>
              <p className="text-[11px] text-slate-500 mt-1 max-w-xs mx-auto">
                Run a comprehensive Skill Gap Analysis to diagnose areas for technical advancement.
              </p>
              <NavLink
                to="/skill-gaps"
                className="inline-flex items-center gap-1.5 mt-3 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-colors"
              >
                Run Gap Analysis <ArrowRight size={13} />
              </NavLink>
            </div>
          )}
        </Panel>

        {/* AI Mentor Panel */}
        <Panel className="flex flex-col justify-between h-full">
          <PanelTitle
            icon={<Bot size={16} className="text-purple-400" />}
            action={
              <NavLink className="text-xs text-purple-400 hover:underline flex items-center gap-0.5" to="/mentor">
                <span>View All</span>
                <ArrowRight size={12} />
              </NavLink>
            }
          >
            AI Mentor
          </PanelTitle>

          <div className="space-y-3 flex-1">
            {topGaps.length > 0 ? (
              topGaps.slice(0, 3).map((gap, idx) => (
                <div
                  key={`mentor-rec-${idx}`}
                  className="p-3 rounded-xl bg-[#0f131d] border border-[#232b3e] hover:border-purple-500/40 transition-colors"
                >
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="text-xs font-semibold text-slate-200 truncate flex items-center gap-1.5">
                      <Sparkles size={12} className="text-purple-400 shrink-0" />
                      <span>Focus: {gap.skill}</span>
                    </span>
                    <NavLink
                      to={`/mentor?topic=${encodeURIComponent(gap.skill)}`}
                      className="text-[10px] px-2 py-0.5 rounded bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 font-medium border border-purple-500/30 transition-colors shrink-0"
                    >
                      Ask Mentor →
                    </NavLink>
                  </div>
                  <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
                    {gap.suggested_action || gap.reason || 'Practice core interview questions and architecture patterns with AI Mentor.'}
                  </p>
                </div>
              ))
            ) : (
              <div className="space-y-3">
                <div className="p-3 rounded-xl bg-[#0f131d] border border-[#232b3e]">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="text-xs font-semibold text-slate-200 truncate flex items-center gap-1.5">
                      <Sparkles size={12} className="text-purple-400" />
                      <span>{targetRole} Technical Interview Prep</span>
                    </span>
                    <NavLink
                      to="/mentor"
                      className="text-[10px] px-2 py-0.5 rounded bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 font-medium border border-purple-500/30 transition-colors"
                    >
                      Start Session →
                    </NavLink>
                  </div>
                  <p className="text-[11px] text-slate-400 line-clamp-2">
                    Review behavioral and algorithmic expectations tailored to {companyTier}.
                  </p>
                </div>
              </div>
            )}
          </div>

          <div className="pt-3 mt-3 border-t border-[#232b3e]/60 flex items-center justify-between text-xs">
            <span className="text-slate-500 text-[11px]">Real recommendations from skill gaps</span>
            <NavLink
              to="/mentor"
              className="inline-flex items-center gap-1 text-purple-400 hover:text-purple-300 hover:underline font-medium text-xs"
            >
              <span>Launch AI Mentor</span>
              <ArrowUpRight size={14} />
            </NavLink>
          </div>
        </Panel>
      </div>

      {/* 5. Compact Links for Resume Audit, GitHub Sync, and LeetCode Analytics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {/* Resume Audit Link */}
        <NavLink
          to="/resume"
          className="flex items-center justify-between gap-3 px-3.5 py-2.5 rounded-xl bg-[#121624] border border-[#232b3e] text-xs text-slate-300 hover:border-indigo-500/40 hover:bg-[#151b2e] transition-all group"
        >
          <div className="flex items-center gap-2.5 min-w-0">
            <FileText size={16} className="text-indigo-400 shrink-0" />
            <div className="min-w-0">
              <span className="font-semibold block truncate">Resume Audit</span>
              <span className="text-[10px] text-slate-500 block truncate">
                {resumeName ? `Synced: ${resumeName}` : 'Upload & Audit ATS Score'}
              </span>
            </div>
          </div>
          <ArrowRight size={14} className="text-slate-500 group-hover:text-white transition-colors shrink-0" />
        </NavLink>

        {/* GitHub Sync Link */}
        <div className="flex items-center justify-between gap-3 px-3.5 py-2.5 rounded-xl bg-[#121624] border border-[#232b3e] text-xs text-slate-300 hover:border-slate-400 hover:bg-[#151b2e] transition-all group">
          <NavLink to="/github" className="flex items-center gap-2.5 min-w-0 flex-1">
            <Github size={16} className="text-slate-200 shrink-0" />
            <div className="min-w-0">
              <span className="font-semibold block truncate">GitHub Sync</span>
              <span className="text-[10px] text-slate-500 block truncate">
                {realGhHandle ? `@${realGhHandle} (${ghSyncStatus || 'Connected'})` : 'Connect GitHub Account'}
              </span>
            </div>
          </NavLink>
          {realGhHandle ? (
            <button
              type="button"
              onClick={handleGithubSync}
              disabled={isGhSyncing}
              title="Trigger GitHub sync"
              className="p-1 rounded-md bg-[#0f131d] border border-[#232b3e] text-slate-400 hover:text-white hover:border-indigo-500 transition-colors shrink-0"
            >
              <RefreshCw size={12} className={isGhSyncing ? 'animate-spin text-indigo-400' : ''} />
            </button>
          ) : (
            <NavLink to="/github" className="text-slate-500 group-hover:text-white transition-colors shrink-0">
              <ArrowRight size={14} />
            </NavLink>
          )}
        </div>

        {/* LeetCode Analytics Link */}
        <NavLink
          to="/leetcode"
          className="flex items-center justify-between gap-3 px-3.5 py-2.5 rounded-xl bg-[#121624] border border-[#232b3e] text-xs text-slate-300 hover:border-purple-500/40 hover:bg-[#151b2e] transition-all group"
        >
          <div className="flex items-center gap-2.5 min-w-0">
            <Sparkles size={16} className="text-purple-400 shrink-0" />
            <div className="min-w-0">
              <span className="font-semibold block truncate">LeetCode Analytics</span>
              <span className="text-[10px] text-slate-500 block truncate">
                {realLcHandle ? `@${realLcHandle} • ${realLcSolved} Solved` : 'Connect LeetCode Account'}
              </span>
            </div>
          </div>
          <ArrowRight size={14} className="text-slate-500 group-hover:text-white transition-colors shrink-0" />
        </NavLink>
      </div>
    </div>
  );
};
