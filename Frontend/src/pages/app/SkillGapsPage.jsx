import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/UserContext';
import { usePlanning } from '../../context/PlanningContext';
import { initialSkillGapData } from '../../data/skillGapData';
import { aiService } from '../../services/aiService';
import {
  Zap,
  RefreshCw,
  Target,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  ArrowUpRight,
  Layers,
  Award,
  Grid,
  TrendingUp,
  BrainCircuit,
  SlidersHorizontal,
  ChevronRight
} from 'lucide-react';

export const SkillGapsPage = () => {
  const navigate = useNavigate();
  const { user } = useUser();
  const { addSkillToRoadmap, toastNotification } = usePlanning();
  const [data, setData] = useState(initialSkillGapData);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [activeCategoryFilter, setActiveCategoryFilter] = useState('All');

  // Derive target role from UserContext if available
  const displayTargetRole = user?.targetRole || user?.career?.targetRole || 'Backend SDE-1 (Tier-1 Parity)';

  const handleRefresh = async () => {
    setIsRefreshing(true);
    const updated = await aiService.analyzeSkillGaps(displayTargetRole);
    setData((prev) => ({
      ...prev,
      lastCalibrated: 'Just now (Automated)',
    }));
    setIsRefreshing(false);
  };

  const filteredGaps = activeCategoryFilter === 'All'
    ? data.gaps
    : data.gaps.filter((g) => g.category.includes(activeCategoryFilter));

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* 1. HERO BANNER */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6 p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-indigo-950/60 via-purple-950/40 to-[#121624] border border-indigo-500/30 shadow-2xl">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-400 text-xs font-mono font-semibold border border-indigo-500/30">
              <Zap className="w-3.5 h-3.5 text-indigo-400" />
              TELEMETRY V4.2 · ROLE BENCHMARK ENGINE
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">AI Skill Gap Analyzer</h1>
          <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
            Discover which skills you already have, which skills you need, and what to learn next for your target role.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start lg:self-center shrink-0">
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="flex items-center gap-2 px-4 py-2.5 bg-[#1a2030] hover:bg-[#232b3e] text-slate-200 hover:text-white text-xs sm:text-sm font-semibold rounded-xl border border-[#232b3e] transition-all shadow-md disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 text-indigo-400 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>{isRefreshing ? 'Recalibrating Role Gaps...' : 'Refresh Analysis'}</span>
          </button>
          <button
            onClick={() => navigate('/roadmap')}
            className="flex items-center gap-1.5 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs sm:text-sm font-semibold rounded-xl transition-all shadow-lg shadow-indigo-600/30 border border-indigo-400/30"
          >
            <span>View 90-Day Roadmap</span>
            <ArrowUpRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 2. TARGET PROFILE & CALIBRATION BAR */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-4 rounded-2xl bg-[#121624] border border-[#232b3e] text-xs font-mono shadow-xl">
        <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e]">
          <span className="text-slate-400">Target Profile</span>
          <span className="text-indigo-400 font-bold truncate max-w-[180px]">{displayTargetRole}</span>
        </div>

        <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e]">
          <span className="text-slate-400">Last Calibrated</span>
          <span className="text-slate-200 font-semibold">{data.lastCalibrated}</span>
        </div>

        <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e]">
          <span className="text-slate-400">Confidence Index</span>
          <span className="text-emerald-400 font-bold">{data.confidenceIndex}</span>
        </div>
      </div>

      {/* 3. OVERALL SKILL COVERAGE KPI BANNER */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Coverage Score */}
        <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] hover:border-emerald-500/40 transition-colors shadow-xl">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">Overall Skill Coverage</span>
            <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white font-mono">{data.overallCoverage}%</span>
          </div>
          <div className="mt-3 text-xs text-slate-400 font-medium">
            Target cutoff: Tier-1 Readiness Threshold
          </div>
        </div>

        {/* Audited Skills Count */}
        <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] hover:border-indigo-500/40 transition-colors shadow-xl">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">Skills Audited</span>
            <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <Layers className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white font-mono">{data.totalAudited}</span>
            <span className="text-xs text-slate-400 font-mono">Skills</span>
          </div>
          <div className="mt-3 text-xs text-slate-400 font-medium">
            Evaluated across 4 engineering domains
          </div>
        </div>

        {/* Gaps Identified Count */}
        <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] hover:border-amber-500/40 transition-colors shadow-xl">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">Critical/High Gaps</span>
            <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white font-mono">{data.gapsIdentifiedCount}</span>
            <span className="text-xs text-slate-400 font-mono">Gaps</span>
          </div>
          <div className="mt-3 text-xs text-amber-400 font-semibold">
            Requires active roadmap remediation
          </div>
        </div>
      </div>

      {/* 4. CATEGORY COVERAGE PROGRESS BREAKDOWN */}
      <div className="bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-xl">
        <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
          <h3 className="font-bold text-white text-base">Category Coverage Breakdown</h3>
          <span className="text-xs font-mono text-indigo-400 font-semibold px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20">Target Role Benchmarks</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {data.categoryCoverage.map((cat, idx) => (
            <div key={idx} className="p-4 rounded-xl bg-[#0f131d] border border-[#232b3e] space-y-2.5 hover:border-indigo-500/30 transition-colors">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-white">{cat.category}</span>
                <span className="font-mono text-indigo-400 font-bold">{cat.coverage}% Coverage</span>
              </div>
              <div className="w-full bg-[#121624] rounded-full h-2 overflow-hidden border border-[#232b3e]">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{ width: `${cat.coverage}%`, backgroundColor: cat.color }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 5. CURRENT VS REQUIRED BENCHMARK MATRIX (SKILL GAPS GRID) */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="font-bold text-white text-lg">Multi-Vector Skill Gap Audit</h3>
            <p className="text-xs text-slate-400">Current skill level vs target role benchmark</p>
          </div>

          {/* Category Filter Pills */}
          <div className="flex flex-wrap items-center gap-1.5 text-xs font-mono">
            {['All', 'Backend', 'DSA', 'Cloud', 'DBMS'].map((filter) => (
              <button
                key={filter}
                onClick={() => setActiveCategoryFilter(filter)}
                className={`px-3 py-1.5 rounded-lg border transition-all ${
                  activeCategoryFilter === filter
                    ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white border-indigo-400/30 shadow-md font-bold'
                    : 'bg-[#121624] text-slate-400 border-[#232b3e] hover:text-white hover:bg-[#1a2030]'
                }`}
              >
                {filter}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4">
          {filteredGaps.map((gap) => (
            <div
              key={gap.id}
              className="p-5 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 hover:border-indigo-500/40 transition-colors shadow-xl"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-[#232b3e]">
                <div className="flex items-center gap-2">
                  <h4 className="font-bold text-white text-base">{gap.skill}</h4>
                  <span className="px-2.5 py-0.5 rounded-lg text-[10px] font-mono font-semibold uppercase bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                    {gap.category}
                  </span>
                </div>

                <span
                  className={`px-2.5 py-1 rounded-full text-xs font-mono font-bold uppercase self-start sm:self-auto ${
                    gap.priority === 'Critical'
                      ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                      : gap.priority === 'High'
                      ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                      : 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30'
                  }`}
                >
                  {gap.priority} Priority
                </span>
              </div>

              {/* Level Comparison Bar */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 p-3.5 rounded-xl bg-[#0f131d] border border-[#232b3e] text-xs font-mono">
                <div>
                  <span className="text-[11px] text-slate-400 block mb-0.5">CURRENT LEVEL</span>
                  <span className="text-white font-bold">{gap.currentLevelText}</span>
                  <span className="text-[11px] text-slate-400 ml-2">(Level {gap.currentLevel}/5)</span>
                </div>

                <div>
                  <span className="text-[11px] text-indigo-400 block mb-0.5">TARGET REQUIRED LEVEL</span>
                  <span className="text-indigo-400 font-bold">{gap.requiredLevelText}</span>
                  <span className="text-[11px] text-indigo-400/80 ml-2">(Level {gap.requiredLevel}/5)</span>
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed">
                <strong className="text-white font-bold">Tier-1 Rationale:</strong> {gap.reason}
              </p>

              <div className="pt-2 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <span className="text-xs text-emerald-400 font-medium">Suggested Action: {gap.suggestedAction}</span>
                <button
                  onClick={() => {
                    if (gap.actionLabel.includes('Roadmap') || gap.actionLabel.includes('Tasks')) {
                      addSkillToRoadmap(gap);
                    }
                    navigate(gap.actionRoute);
                  }}
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white transition-all shadow-lg shadow-indigo-600/30 border border-indigo-400/30 flex items-center justify-center gap-1.5 self-start sm:self-auto"
                >
                  <span>{gap.actionLabel}</span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 6. 2X2 SKILL PRIORITY MATRIX: IMPACT VS EFFORT */}
      <div className="bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-xl">
        <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
          <div>
            <h3 className="font-bold text-white text-base flex items-center gap-2">
              <Grid className="w-5 h-5 text-purple-400" />
              2x2 Skill Priority Matrix: Impact vs. Effort
            </h3>
            <p className="text-xs text-slate-400">Prioritize skills based on hiring ROI vs study effort</p>
          </div>
          <span className="text-xs font-mono font-semibold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-lg border border-emerald-500/20">
            Strategic Grid
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
          {/* Quick Wins */}
          <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 space-y-2">
            <div className="flex items-center justify-between text-emerald-400 font-bold">
              <span>QUICK WINS (High Impact, Low Effort)</span>
              <span className="text-[10px] bg-emerald-500/20 px-2 py-0.5 rounded">Priority 1</span>
            </div>
            <div className="space-y-1.5 pt-1">
              {data.matrix2x2.quickWins.map((item, idx) => (
                <div key={idx} className="p-2 rounded-lg bg-[#0f131d] border border-[#232b3e] flex items-center justify-between text-white font-semibold">
                  <span>{item.skill}</span>
                  <span className="text-[10px] text-emerald-400 font-mono">{item.category}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Major Projects */}
          <div className="p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/30 space-y-2">
            <div className="flex items-center justify-between text-indigo-400 font-bold">
              <span>MAJOR PROJECTS (High Impact, High Effort)</span>
              <span className="text-[10px] bg-indigo-500/20 px-2 py-0.5 rounded">Priority 2</span>
            </div>
            <div className="space-y-1.5 pt-1">
              {data.matrix2x2.majorProjects.map((item, idx) => (
                <div key={idx} className="p-2 rounded-lg bg-[#0f131d] border border-[#232b3e] flex items-center justify-between text-white font-semibold">
                  <span>{item.skill}</span>
                  <span className="text-[10px] text-indigo-400 font-mono">{item.category}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Fill-ins */}
          <div className="p-4 rounded-xl bg-[#0f131d] border border-[#232b3e] space-y-2">
            <div className="flex items-center justify-between text-slate-300 font-bold">
              <span>FILL-INS (Low Impact, Low Effort)</span>
              <span className="text-[10px] text-slate-400">Priority 3</span>
            </div>
            <div className="space-y-1.5 pt-1">
              {data.matrix2x2.fillIns.map((item, idx) => (
                <div key={idx} className="p-2 rounded-lg bg-[#121624] border border-[#232b3e] flex items-center justify-between text-slate-300">
                  <span>{item.skill}</span>
                  <span className="text-[10px] font-mono">{item.category}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Hard Long-term */}
          <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 space-y-2">
            <div className="flex items-center justify-between text-amber-400 font-bold">
              <span>LONG TERM (Low Impact, High Effort)</span>
              <span className="text-[10px] text-amber-400">Priority 4</span>
            </div>
            <div className="space-y-1.5 pt-1">
              {data.matrix2x2.hardLongTerm.map((item, idx) => (
                <div key={idx} className="p-2 rounded-lg bg-[#0f131d] border border-[#232b3e] flex items-center justify-between text-slate-300">
                  <span>{item.skill}</span>
                  <span className="text-[10px] text-amber-400 font-mono">{item.category}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 7. AI LEARNING RECOMMENDATIONS BANNER */}
      <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-xl">
        <h3 className="font-bold text-white text-base flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-400" />
          Copilot Skill Gap Roadmap Strategy
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-[#0f131d] border border-[#232b3e] space-y-2 hover:border-purple-500/40 transition-colors">
            <h4 className="font-bold text-sm text-white">Target 90-Day Adaptive Roadmap</h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              Incorporate Redis Caching and 2D DP problem sets into your active 90-day placement sprint schedule.
            </p>
            <button
              onClick={() => navigate('/roadmap')}
              className="text-xs font-bold text-indigo-400 hover:text-indigo-300 inline-flex items-center gap-1 pt-1"
            >
              <span>View 90-Day Roadmap</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="p-4 rounded-xl bg-[#0f131d] border border-[#232b3e] space-y-2 hover:border-purple-500/40 transition-colors">
            <h4 className="font-bold text-sm text-white">Execute Daily Practice Tasks</h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              Start with Today's Action Plan tasks focusing on Course Schedule II and Course Schedule III.
            </p>
            <button
              onClick={() => navigate('/tasks')}
              className="text-xs font-bold text-indigo-400 hover:text-indigo-300 inline-flex items-center gap-1 pt-1"
            >
              <span>View Today's Tasks</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
