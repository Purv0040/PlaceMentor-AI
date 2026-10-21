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
import { getRoleSkillGapData } from '../../data/skillGapData';

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
  const { roadmap, tasks, toggleTaskCompletion } = usePlanning();

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
  const [topGaps, setTopGaps] = useState(() => {
    const calibrated = getRoleSkillGapData(targetRole, user);
    return Array.isArray(calibrated?.gaps) && calibrated.gaps.length > 0
      ? calibrated.gaps.slice(0, 3)
      : [];
  });
  const [skillsLoading, setSkillsLoading] = useState(false);

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

    // 1. Fetch Readiness dynamically calibrated for profile telemetry & History
    readinessService.getLatestReadiness(user).then((readiness) => {
      if (!isMounted || !readiness) return;
      if (typeof readiness.overallScore === 'number' && readiness.overallScore > 0) {
        setReadinessScore(Math.round(readiness.overallScore));
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

    // 6. Fetch Skill Gap Summary calibrated for role
    skillGapService.getLatestSkillGaps(targetRole, user).then((analysis) => {
      if (!isMounted) return;
      if (analysis && Array.isArray(analysis.gaps) && analysis.gaps.length > 0) {
        setTopGaps(analysis.gaps.slice(0, 3));
      } else {
        const fallback = getRoleSkillGapData(targetRole, user);
        if (Array.isArray(fallback?.gaps) && fallback.gaps.length > 0) {
          setTopGaps(fallback.gaps.slice(0, 3));
        }
      }
      setSkillsLoading(false);
    }).catch((err) => {
      console.warn('Skill gaps load failed, falling back to role benchmarks:', err);
      if (isMounted) {
        const fallback = getRoleSkillGapData(targetRole, user);
        if (Array.isArray(fallback?.gaps) && fallback.gaps.length > 0) {
          setTopGaps(fallback.gaps.slice(0, 3));
        }
        setSkillsLoading(false);
      }
    });

    return () => {
      isMounted = false;
    };
  }, [loadProgress, targetRole, user]);

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
    if (typeof currentLevel === 'number') {
      if (currentLevel <= 1) return 25;
      if (currentLevel === 2) return 50;
      if (currentLevel === 3) return 75;
      if (currentLevel >= 4) return 100;
    }
    const str = String(currentLevel).toLowerCase();
    if (str.includes('1/4') || str.includes('beginner')) return 30;
    if (str.includes('2/4') || str.includes('intermediate')) return 55;
    if (str.includes('3/4') || str.includes('advanced')) return 80;
    if (str.includes('4/4') || str.includes('expert')) return 100;
    return 45;
  };

  return (
    <div className="dashboard-page w-full max-w-5xl mx-auto space-y-5 sm:space-y-6">
      {/* 1. Personalized Welcome Header */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-[#151a2d] via-[#121624] to-[#101422] border border-[#232b3e] shadow-lg flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold mb-2">
            <Sparkles size={13} />
            <span>AI Placement Dashboard</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight">
            {greeting}
          </h1>
          <p className="mt-1.5 text-xs sm:text-sm text-slate-300">
            Your placement readiness is <strong className="text-indigo-400 font-bold">{readinessScore}%</strong>
            <span className="mx-2 text-slate-600 hidden sm:inline">•</span>
            <span className="block sm:inline text-slate-400 text-xs mt-1 sm:mt-0">{contextSubtext}</span>
          </p>
        </div>

        <div className="flex items-center gap-2.5 self-start md:self-center shrink-0">
          <NavLink
            to={startPlanRoute}
            className="inline-flex items-center gap-1.5 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 active:scale-95 text-white text-xs sm:text-sm font-semibold rounded-xl transition-all shadow-md shadow-indigo-600/25 cursor-pointer"
          >
            <span>{startPlanLabel}</span>
            <ArrowRight size={14} />
          </NavLink>
        </div>
      </div>

      {/* 2. Sleek Metrics Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Readiness Card */}
        <NavLink
          to="/placement-readiness"
          className="relative overflow-hidden p-5 rounded-2xl bg-gradient-to-b from-[#151a2c] to-[#101422] border border-[#232b3e] hover:border-indigo-500/50 hover:shadow-lg hover:shadow-indigo-500/10 hover:-translate-y-0.5 transition-all duration-200 group flex flex-col justify-between"
        >
          <div className="absolute top-0 right-0 w-28 h-28 bg-indigo-500/5 rounded-full blur-2xl group-hover:bg-indigo-500/10 transition-colors pointer-events-none" />

          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Readiness Score
              </span>
              <div className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 group-hover:scale-105 transition-transform">
                <Target size={16} />
              </div>
            </div>

            <div className="flex items-baseline gap-2">
              <span className="text-3xl sm:text-4xl font-extrabold text-white font-mono tracking-tight">
                {readinessScore}%
              </span>
              <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${
                readinessScore >= 75
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                  : readinessScore >= 50
                  ? 'bg-indigo-500/10 text-indigo-300 border-indigo-500/20'
                  : 'bg-amber-500/10 text-amber-300 border-amber-500/20'
              }`}>
                {readinessScore >= 75 ? 'Ready' : readinessScore >= 50 ? 'Moderate' : 'Developing'}
              </span>
            </div>

            {/* Mini Progress Bar */}
            <div className="w-full bg-[#1e2538] rounded-full h-1.5 mt-3.5 overflow-hidden border border-[#2a344d]/40">
              <div
                className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-500"
                style={{ width: `${Math.min(100, Math.max(0, readinessScore))}%` }}
              />
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-[#232b3e]/60 flex items-center justify-between text-xs text-slate-400 group-hover:text-indigo-300 transition-colors">
            <span>Diagnostic Breakdown</span>
            <ArrowUpRight size={14} className="group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
          </div>
        </NavLink>

        {/* Sprint Cadence Card */}
        <NavLink
          to="/roadmap"
          className="relative overflow-hidden p-5 rounded-2xl bg-gradient-to-b from-[#151a2c] to-[#101422] border border-[#232b3e] hover:border-amber-500/50 hover:shadow-lg hover:shadow-amber-500/10 hover:-translate-y-0.5 transition-all duration-200 group flex flex-col justify-between"
        >
          <div className="absolute top-0 right-0 w-28 h-28 bg-amber-500/5 rounded-full blur-2xl group-hover:bg-amber-500/10 transition-colors pointer-events-none" />

          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Sprint Cadence
              </span>
              <div className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 group-hover:scale-105 transition-transform">
                <Flame size={16} />
              </div>
            </div>

            <div className="flex items-baseline gap-1.5">
              <span className="text-3xl sm:text-4xl font-extrabold text-white font-mono tracking-tight">
                {user?.dailyGoalMinutes || 90}
              </span>
              <span className="text-xs font-medium text-slate-400 font-mono">min / day</span>
              {activeStreak > 0 && (
                <span className="ml-auto text-[11px] font-semibold px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/20">
                  {activeStreak}d Streak 🔥
                </span>
              )}
            </div>

            <p className="mt-3.5 text-xs text-slate-400 truncate">
              {user?.studyCadence || 'Daily Evening Sprints'} · Roadmap pace
            </p>
          </div>

          <div className="mt-4 pt-3 border-t border-[#232b3e]/60 flex items-center justify-between text-xs text-slate-400 group-hover:text-amber-300 transition-colors">
            <span>View Roadmap Schedule</span>
            <ArrowUpRight size={14} className="group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
          </div>
        </NavLink>

        {/* Target Role Card */}
        <NavLink
          to="/profile"
          className="relative overflow-hidden p-5 rounded-2xl bg-gradient-to-b from-[#151a2c] to-[#101422] border border-[#232b3e] hover:border-emerald-500/50 hover:shadow-lg hover:shadow-emerald-500/10 hover:-translate-y-0.5 transition-all duration-200 group flex flex-col justify-between"
        >
          <div className="absolute top-0 right-0 w-28 h-28 bg-emerald-500/5 rounded-full blur-2xl group-hover:bg-emerald-500/10 transition-colors pointer-events-none" />

          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Target Role
              </span>
              <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 group-hover:scale-105 transition-transform">
                <Code2 size={16} />
              </div>
            </div>

            <h3 className="text-lg sm:text-xl font-bold text-white tracking-tight truncate" title={targetRole}>
              {targetRole}
            </h3>

            <div className="mt-2.5 flex items-center gap-1.5">
              <span className="text-[11px] font-semibold text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-md border border-emerald-500/20 truncate">
                {companyTier ? companyTier.split('(')[0].trim() : 'Tier-1 Target'}
              </span>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-[#232b3e]/60 flex items-center justify-between text-xs text-slate-400 group-hover:text-emerald-300 transition-colors">
            <span>Configure Role & Goals</span>
            <ArrowUpRight size={14} className="group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
          </div>
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
              readinessScore={readinessScore}
              tasks={tasks}
              roadmap={roadmap}
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
                        Current: <strong className="text-slate-300">{gap.current_level_text || gap.currentLevelText || gap.current_level || 'Untested'}</strong>
                      </span>
                      <span className="text-slate-500 shrink-0">
                        Target: <strong className="text-indigo-400">{gap.required_level_text || gap.requiredLevelText || gap.required_level || 'Proficient'}</strong>
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
                    {gap.suggestedAction || gap.suggested_action || gap.reason || 'Practice core interview questions and architecture patterns with AI Mentor.'}
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

      {/* 5. Compact Links for Resume Audit and GitHub Sync */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
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
      </div>
    </div>
  );
};
