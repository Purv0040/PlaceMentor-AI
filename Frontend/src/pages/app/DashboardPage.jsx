import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import {
  Sparkles,
  TrendingUp,
  Zap,
  Target,
  ArrowRight,
  Flame,
  Award,
  AlertCircle,
  FileText,
  Github,
  Code2,
  FolderKanban,
  Mic,
  Activity,
  CheckCircle2,
  Bot
} from 'lucide-react';
import { useUser } from '../../context/UserContext';
import { dashboardData } from '../../data/dashboardData';
import { readinessService } from '../../services/readinessService';
import { skillGapService } from '../../services/skillGapService';
import { TelemetryChart } from '../../components/dashboard/TelemetryChart';
import { ActionPlanList } from '../../components/dashboard/ActionPlanList';

export const DashboardPage = () => {
  const { user } = useUser();
  const [readinessScore, setReadinessScore] = useState(user?.overallReadinessScore || dashboardData.readinessScore);
  const [readinessLabel, setReadinessLabel] = useState(dashboardData.readinessTrend);
  const [aiInsights, setAiInsights] = useState(dashboardData.aiInsights);

  useEffect(() => {
    if (user?.overallReadinessScore) {
      setReadinessScore(user.overallReadinessScore);
    }
    readinessService.getSummary().then((summary) => {
      if (summary && typeof summary.overall_score === 'number' && !user?.overallReadinessScore) {
        setReadinessScore(Math.round(summary.overall_score));
        if (summary.readiness_label) {
          setReadinessLabel(summary.readiness_label);
        }
      }
    });

    skillGapService.getSummary().then((gapSummary) => {
      if (gapSummary && gapSummary.top_priority_gaps && gapSummary.top_priority_gaps.length > 0) {
        const dynamicInsights = gapSummary.top_priority_gaps.map((g, idx) => ({
          id: `dyn-gap-${idx}`,
          title: `Prioritize ${g.skill} (${g.category})`,
          description: g.reason || g.suggested_action,
          priority: g.priority || 'High',
          route: '/skill-gaps'
        }));
        setAiInsights(dynamicInsights);
      }
    });
  }, [user]);

  return (
    <div className="space-y-6">
      {/* 1. WELCOME HERO BANNER */}
      <div className="p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-indigo-950/60 via-purple-950/40 to-[#121624] border border-indigo-500/30 flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-2xl">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 border border-indigo-500/30 text-indigo-400 text-xs font-mono font-semibold">
            <Sparkles className="w-3.5 h-3.5" /> Day {dashboardData.sprintDay} of {dashboardData.totalSprintDays}-Day Placement Sprint
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
            Good Morning, {user?.name || user?.full_name || 'Candidate'} 👋
          </h1>
          <p className="text-xs sm:text-sm text-slate-300">
            Target: <span className="text-white font-semibold">{user?.targetRole || 'Software Engineer'}</span> • Readiness Baseline:{' '}
            <span className="text-indigo-400 font-mono font-bold">{readinessScore}%</span> ({readinessLabel})
          </p>
        </div>

        <NavLink
          to="/tasks"
          className="px-5 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs sm:text-sm shadow-lg shadow-indigo-600/30 flex items-center gap-2 transition-all shrink-0 self-start md:self-auto border border-indigo-400/30"
        >
          <Zap className="w-4 h-4" /> Start Today's Action Plan <ArrowRight className="w-4 h-4" />
        </NavLink>
      </div>

      {/* 2. TOP METRICS STAT CARDS */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-2.5 hover:border-indigo-500/40 transition-colors">
          <div className="flex items-center justify-between">
            <p className="text-xs text-slate-400 font-medium">Overall Readiness</p>
            <Sparkles className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-bold text-white font-mono">{readinessScore}%</span>
            <span className="text-xs text-emerald-400 font-mono font-semibold">{readinessLabel}</span>
          </div>
          <div className="w-full h-1.5 rounded-full bg-[#0f131d] overflow-hidden">
            <div className="h-full rounded-full bg-indigo-500" style={{ width: `${readinessScore}%` }} />
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-2.5 hover:border-amber-500/40 transition-colors">
          <div className="flex items-center justify-between">
            <p className="text-xs text-slate-400 font-medium">Preparation Streak</p>
            <Flame className="w-4 h-4 text-amber-400" />
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-bold text-white font-mono">
              {(user?.streakDays !== undefined && user?.streakDays !== null) ? user.streakDays : 0} Days
            </span>
            <span className="text-xs text-amber-400 font-mono font-semibold">
              {(user?.streakDays || 0) > 0 ? '🔥 Active Sprint' : '⚡ Day 1 Sprint'}
            </span>
          </div>
          <div className="w-full h-1.5 rounded-full bg-[#0f131d] overflow-hidden">
            <div
              className="h-full rounded-full bg-amber-500"
              style={{ width: `${Math.min(100, Math.max(5, (((user?.streakDays || 0)) / 30) * 100))}%` }}
            />
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-2.5 hover:border-purple-500/40 transition-colors">
          <div className="flex items-center justify-between">
            <p className="text-xs text-slate-400 font-medium">LeetCode Solved</p>
            <Code2 className="w-4 h-4 text-purple-400" />
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-bold text-white font-mono">
              {user?.leetcodeHandle ? (user?.leetcodeSolved || 248) : 0}
            </span>
            <span className="text-xs text-purple-400 font-mono">
              {user?.leetcodeHandle ? (user?.leetcodeBreakdown || '148 Med / 32 Hard') : 'Not Connected'}
            </span>
          </div>
          <div className="w-full h-1.5 rounded-full bg-[#0f131d] overflow-hidden">
            <div
              className="h-full rounded-full bg-purple-500"
              style={{ width: user?.leetcodeHandle ? `${Math.min(100, ((user?.leetcodeSolved || 248) / 400) * 100)}%` : '0%' }}
            />
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-2.5 hover:border-emerald-500/40 transition-colors">
          <div className="flex items-center justify-between">
            <p className="text-xs text-slate-400 font-medium">Target Company Benchmark</p>
            <Target className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-xl font-bold text-white truncate">{user?.targetRole || 'Full Stack Engineer'}</span>
            <span className="text-xs text-emerald-400 font-mono font-semibold">{user?.companyTier ? user.companyTier.split('(')[0].trim() : 'Tier-1 Target'}</span>
          </div>
          <div className="w-full h-1.5 rounded-full bg-[#0f131d] overflow-hidden">
            <div className="h-full rounded-full bg-emerald-500" style={{ width: `${readinessScore}%` }} />
          </div>
        </div>
      </div>

      {/* 3. MAIN DASHBOARD CONTENT GRID */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left Column (2 Cols): Telemetry Chart & 7-Vector Progress */}
        <div className="lg:col-span-2 space-y-6">
          {/* Recharts Telemetry Curve Chart Card */}
          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-xl">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-bold text-base text-white flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-indigo-400" /> 5-Week Telemetry Curve
                </h3>
                <p className="text-xs text-slate-400">Longitudinal tracking of candidate readiness & DSA accuracy</p>
              </div>
              <span className="text-xs text-emerald-400 font-mono font-semibold px-2 py-1 rounded bg-emerald-500/10 border border-emerald-500/20">
                +18% Progress
              </span>
            </div>

            <TelemetryChart />
          </div>

          {/* 7-Vector Readiness Breakdown */}
          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-xl">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-bold text-base text-white flex items-center gap-2">
                  <Award className="w-4 h-4 text-purple-400" /> 7-Vector Readiness Breakdown
                </h3>
                <p className="text-xs text-slate-400">Baseline score evaluation vs SDE-1 target requirements</p>
              </div>
              <NavLink to="/placement-readiness" className="text-xs text-indigo-400 hover:underline font-semibold flex items-center gap-1">
                View Full Audit →
              </NavLink>
            </div>

            <div className="space-y-3.5">
              {dashboardData.vectorScores.map((v) => (
                <div key={v.id} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-200 font-semibold">{v.vector}</span>
                    <span className="text-indigo-400 font-mono font-bold">
                      {v.score}% <span className="text-slate-500 font-normal">/ {v.target}% Target</span>
                    </span>
                  </div>
                  <div className="w-full h-2 rounded-full bg-[#0f131d] overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{ width: `${v.score}%`, backgroundColor: v.color }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column (1 Col): Today's Tasks, AI Insights, Recent Activity */}
        <div className="space-y-6">
          {/* Today's Tasks */}
          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-xl">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-base text-white">Today's Action Plan</h3>
              <NavLink to="/tasks" className="text-xs text-indigo-400 hover:underline font-semibold">
                View All →
              </NavLink>
            </div>
            <ActionPlanList />
          </div>

          {/* AI Insights Card */}
          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-xl">
            <h3 className="font-bold text-base text-white flex items-center gap-2">
              <Bot className="w-4.5 h-4.5 text-purple-400" /> AI Mentor Recommendations
            </h3>

            <div className="space-y-3">
              {aiInsights.map((ins) => (
                <NavLink
                  key={ins.id}
                  to={ins.route}
                  className="p-3.5 rounded-xl bg-[#0f131d] border border-[#232b3e] hover:border-purple-500/40 block space-y-1 transition-all"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white">{ins.title}</span>
                    <span className={`text-[10px] font-mono font-semibold px-2 py-0.5 rounded ${
                      ins.priority === 'High' ? 'bg-rose-500/20 text-rose-400' :
                      ins.priority === 'Success' ? 'bg-emerald-500/20 text-emerald-400' :
                      'bg-indigo-500/20 text-indigo-400'
                    }`}>
                      {ins.priority}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 leading-snug">{ins.description}</p>
                </NavLink>
              ))}
            </div>
          </div>

          {/* Recent Activity Timeline */}
          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-xl">
            <h3 className="font-bold text-base text-white flex items-center gap-2">
              <Activity className="w-4 h-4 text-amber-400" /> Recent Telemetry Activity
            </h3>

            <div className="space-y-3">
              {dashboardData.recentActivity.map((act) => (
                <div key={act.id} className="flex items-start gap-3 text-xs p-2.5 rounded-xl bg-[#0f131d] border border-[#232b3e]">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-slate-200 truncate">{act.title}</p>
                    <p className="text-[11px] text-slate-400 truncate">{act.desc}</p>
                  </div>
                  <span className="text-[10px] text-slate-500 font-mono shrink-0">{act.time}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 4. QUICK ACTIONS GRID */}
      <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-xl">
        <h3 className="font-bold text-base text-white">Preparation Shortcuts & Quick Tools</h3>

        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          <NavLink
            to="/resume"
            className="p-4 rounded-xl bg-[#0f131d] border border-[#232b3e] hover:border-indigo-500/40 text-center space-y-2 transition-all hover:-translate-y-0.5"
          >
            <FileText className="w-5 h-5 text-indigo-400 mx-auto" />
            <p className="text-xs font-bold text-white">Resume Audit</p>
          </NavLink>

          <NavLink
            to="/github"
            className="p-4 rounded-xl bg-[#0f131d] border border-[#232b3e] hover:border-slate-400 text-center space-y-2 transition-all hover:-translate-y-0.5"
          >
            <Github className="w-5 h-5 text-white mx-auto" />
            <p className="text-xs font-bold text-white">GitHub Sync</p>
          </NavLink>

          <NavLink
            to="/leetcode"
            className="p-4 rounded-xl bg-[#0f131d] border border-[#232b3e] hover:border-amber-500/40 text-center space-y-2 transition-all hover:-translate-y-0.5"
          >
            <Code2 className="w-5 h-5 text-amber-400 mx-auto" />
            <p className="text-xs font-bold text-white">LeetCode Solves</p>
          </NavLink>

          <NavLink
            to="/projects"
            className="p-4 rounded-xl bg-[#0f131d] border border-[#232b3e] hover:border-indigo-500/40 text-center space-y-2 transition-all hover:-translate-y-0.5"
          >
            <FolderKanban className="w-5 h-5 text-indigo-400 mx-auto" />
            <p className="text-xs font-bold text-white">Projects Audit</p>
          </NavLink>

          <NavLink
            to="/mock-interview"
            className="p-4 rounded-xl bg-[#0f131d] border border-[#232b3e] hover:border-purple-500/40 text-center space-y-2 transition-all hover:-translate-y-0.5 col-span-2 sm:col-span-1"
          >
            <Mic className="w-5 h-5 text-purple-400 mx-auto" />
            <p className="text-xs font-bold text-white">Launch AI Mock</p>
          </NavLink>
        </div>
      </div>
    </div>
  );
};
