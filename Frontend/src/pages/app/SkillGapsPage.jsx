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
      {/* Header Banner */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 bg-surface-container-low p-6 rounded-2xl border border-outline-variant/60 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <h1 className="text-2xl font-bold text-on-surface tracking-tight">AI Skill Gap Analyzer</h1>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-secondary-container/40 text-secondary text-xs font-mono border border-secondary/30">
              <Zap className="w-3.5 h-3.5 text-secondary" />
              TELEMETRY V4.2 · ROLE BENCHMARK ENGINE
            </span>
          </div>
          <p className="text-sm text-on-surface-variant max-w-2xl">
            Discover which skills you already have, which skills you need, and what to learn next for your target role.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start lg:self-center shrink-0">
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="flex items-center gap-2 px-4 py-2 bg-surface-container-high hover:bg-surface-bright text-on-surface text-sm font-medium rounded-xl transition-all shadow-sm disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 text-primary ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>{isRefreshing ? 'Recalibrating Role Gaps...' : 'Refresh Analysis'}</span>
          </button>
          <button
            onClick={() => navigate('/roadmap')}
            className="flex items-center gap-1.5 px-4 py-2 bg-primary text-on-primary hover:bg-primary-fixed-dim text-sm font-semibold rounded-xl transition-all shadow-md"
          >
            <span>View 90-Day Roadmap</span>
            <ArrowUpRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Target Profile & Calibration Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-4 rounded-xl bg-surface-container-low border border-outline-variant text-sm font-mono">
        <div className="flex items-center justify-between px-3 py-1.5 bg-surface-container rounded-lg border border-outline-variant/50">
          <span className="text-xs text-on-surface-variant">Target Profile</span>
          <span className="text-primary font-bold truncate max-w-[180px]">{displayTargetRole}</span>
        </div>

        <div className="flex items-center justify-between px-3 py-1.5 bg-surface-container rounded-lg border border-outline-variant/50">
          <span className="text-xs text-on-surface-variant">Last Calibrated</span>
          <span className="text-on-surface font-medium">{data.lastCalibrated}</span>
        </div>

        <div className="flex items-center justify-between px-3 py-1.5 bg-surface-container rounded-lg border border-outline-variant/50">
          <span className="text-xs text-on-surface-variant">Confidence Index</span>
          <span className="text-tertiary font-bold">{data.confidenceIndex}</span>
        </div>
      </div>

      {/* Overall Skill Coverage KPI Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Coverage Score */}
        <div className="p-5 bg-surface-container-low rounded-2xl border border-outline-variant/60 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-on-surface-variant">Overall Skill Coverage</span>
            <div className="p-2 rounded-xl bg-tertiary-container/20 text-tertiary">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-on-surface">{data.overallCoverage}%</span>
          </div>
          <div className="mt-3 text-xs text-on-surface-variant">
            Target cutoff: Tier-1 Readiness Threshold
          </div>
        </div>

        {/* Audited Skills Count */}
        <div className="p-5 bg-surface-container-low rounded-2xl border border-outline-variant/60 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-on-surface-variant">Skills Audited</span>
            <div className="p-2 rounded-xl bg-primary-container/20 text-primary">
              <Layers className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-on-surface">{data.totalAudited}</span>
            <span className="text-xs text-on-surface-variant font-mono">Skills</span>
          </div>
          <div className="mt-3 text-xs text-on-surface-variant">
            Evaluated across 4 engineering domains
          </div>
        </div>

        {/* Gaps Identified Count */}
        <div className="p-5 bg-surface-container-low rounded-2xl border border-outline-variant/60 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-on-surface-variant">Critical/High Gaps</span>
            <div className="p-2 rounded-xl bg-secondary-container/20 text-secondary">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-on-surface">{data.gapsIdentifiedCount}</span>
            <span className="text-xs text-on-surface-variant font-mono">Gaps</span>
          </div>
          <div className="mt-3 text-xs text-secondary font-medium">
            Requires active roadmap remediation
          </div>
        </div>
      </div>

      {/* Category Coverage Progress Breakdown */}
      <div className="bg-surface-container-low p-6 rounded-2xl border border-outline-variant/60 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-outline-variant/50">
          <h3 className="font-semibold text-on-surface text-base">Category Coverage Breakdown</h3>
          <span className="text-xs font-mono text-on-surface-variant">Target Role Benchmarks</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {data.categoryCoverage.map((cat, idx) => (
            <div key={idx} className="p-4 rounded-xl bg-surface-container border border-outline-variant/40 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-on-surface">{cat.category}</span>
                <span className="font-mono text-on-surface font-bold">{cat.coverage}% Coverage</span>
              </div>
              <div className="w-full bg-surface-container-high rounded-full h-2 overflow-hidden border border-outline-variant/30">
                <div
                  className="h-full transition-all duration-500"
                  style={{ width: `${cat.coverage}%`, backgroundColor: cat.color }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Current vs Required Benchmark Matrix (Skill Gaps Grid) */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="font-semibold text-on-surface text-lg">Multi-Vector Skill Gap Audit</h3>
            <p className="text-xs text-on-surface-variant">Current skill level vs target role benchmark</p>
          </div>

          {/* Category Filter Pills */}
          <div className="flex flex-wrap items-center gap-1.5 text-xs font-mono">
            {['All', 'Backend', 'DSA', 'Cloud', 'DBMS'].map((filter) => (
              <button
                key={filter}
                onClick={() => setActiveCategoryFilter(filter)}
                className={`px-3 py-1 rounded-lg border transition-all ${
                  activeCategoryFilter === filter
                    ? 'bg-primary text-on-primary border-primary shadow-sm font-semibold'
                    : 'bg-surface-container text-on-surface-variant border-outline-variant/60 hover:text-on-surface'
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
              className="p-5 rounded-2xl bg-surface-container-low border border-outline-variant/60 space-y-4 hover:border-primary/40 transition-colors shadow-sm"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-outline-variant/40">
                <div className="flex items-center gap-2">
                  <h4 className="font-bold text-on-surface text-base">{gap.skill}</h4>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-surface-container text-on-surface-variant border border-outline-variant/50">
                    {gap.category}
                  </span>
                </div>

                <span
                  className={`px-2.5 py-0.5 rounded-full text-xs font-mono font-bold uppercase self-start sm:self-auto ${
                    gap.priority === 'Critical'
                      ? 'bg-error/20 text-error border border-error/30'
                      : gap.priority === 'High'
                      ? 'bg-secondary-container/30 text-secondary border border-secondary/30'
                      : 'bg-primary-container/20 text-primary border border-primary/30'
                  }`}
                >
                  {gap.priority} Priority
                </span>
              </div>

              {/* Level Comparison Bar */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 p-3.5 rounded-xl bg-surface-container/60 border border-outline-variant/30 text-xs font-mono">
                <div>
                  <span className="text-[11px] text-outline block mb-0.5">CURRENT LEVEL</span>
                  <span className="text-on-surface font-semibold">{gap.currentLevelText}</span>
                  <span className="text-[11px] text-on-surface-variant ml-2">(Level {gap.currentLevel}/5)</span>
                </div>

                <div>
                  <span className="text-[11px] text-primary block mb-0.5">TARGET REQUIRED LEVEL</span>
                  <span className="text-primary font-bold">{gap.requiredLevelText}</span>
                  <span className="text-[11px] text-primary/80 ml-2">(Level {gap.requiredLevel}/5)</span>
                </div>
              </div>

              <p className="text-xs text-on-surface-variant leading-relaxed">
                <strong className="text-on-surface font-semibold">Tier-1 Rationale:</strong> {gap.reason}
              </p>

              <div className="pt-2 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <span className="text-xs text-tertiary font-medium">Suggested Action: {gap.suggestedAction}</span>
                <button
                  onClick={() => {
                    if (gap.actionLabel.includes('Roadmap') || gap.actionLabel.includes('Tasks')) {
                      addSkillToRoadmap(gap);
                    }
                    navigate(gap.actionRoute);
                  }}
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-primary text-on-primary hover:bg-primary-fixed-dim transition-all shadow-sm flex items-center justify-center gap-1.5 self-start sm:self-auto"
                >
                  <span>{gap.actionLabel}</span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 2x2 Skill Priority Matrix: Impact vs Effort */}
      <div className="bg-surface-container-low p-6 rounded-2xl border border-outline-variant/60 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-outline-variant/50">
          <div>
            <h3 className="font-semibold text-on-surface text-base flex items-center gap-2">
              <Grid className="w-5 h-5 text-secondary" />
              2x2 Skill Priority Matrix: Impact vs. Effort
            </h3>
            <p className="text-xs text-on-surface-variant">Prioritize skills based on hiring ROI vs study effort</p>
          </div>
          <span className="text-xs font-mono text-tertiary bg-tertiary-container/20 px-2.5 py-1 rounded border border-tertiary/30">
            Strategic Grid
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
          {/* Quick Wins */}
          <div className="p-4 rounded-xl bg-tertiary-container/10 border border-tertiary/30 space-y-2">
            <div className="flex items-center justify-between text-tertiary font-bold">
              <span>QUICK WINS (High Impact, Low Effort)</span>
              <span className="text-[10px] bg-tertiary-container/30 px-2 py-0.5 rounded">Priority 1</span>
            </div>
            <div className="space-y-1.5 pt-1">
              {data.matrix2x2.quickWins.map((item, idx) => (
                <div key={idx} className="p-2 rounded bg-surface-container border border-outline-variant/30 flex items-center justify-between text-on-surface">
                  <span>{item.skill}</span>
                  <span className="text-[10px] text-tertiary">{item.category}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Major Projects */}
          <div className="p-4 rounded-xl bg-primary-container/10 border border-primary/30 space-y-2">
            <div className="flex items-center justify-between text-primary font-bold">
              <span>MAJOR PROJECTS (High Impact, High Effort)</span>
              <span className="text-[10px] bg-primary-container/30 px-2 py-0.5 rounded">Priority 2</span>
            </div>
            <div className="space-y-1.5 pt-1">
              {data.matrix2x2.majorProjects.map((item, idx) => (
                <div key={idx} className="p-2 rounded bg-surface-container border border-outline-variant/30 flex items-center justify-between text-on-surface">
                  <span>{item.skill}</span>
                  <span className="text-[10px] text-primary">{item.category}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Fill-ins */}
          <div className="p-4 rounded-xl bg-surface-container border border-outline-variant/50 space-y-2">
            <div className="flex items-center justify-between text-on-surface font-bold">
              <span>FILL-INS (Low Impact, Low Effort)</span>
              <span className="text-[10px] text-on-surface-variant">Priority 3</span>
            </div>
            <div className="space-y-1.5 pt-1">
              {data.matrix2x2.fillIns.map((item, idx) => (
                <div key={idx} className="p-2 rounded bg-surface-container-low border border-outline-variant/30 flex items-center justify-between text-on-surface-variant">
                  <span>{item.skill}</span>
                  <span className="text-[10px]">{item.category}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Hard Long-term */}
          <div className="p-4 rounded-xl bg-secondary-container/10 border border-secondary/30 space-y-2">
            <div className="flex items-center justify-between text-secondary font-bold">
              <span>LONG TERM (Low Impact, High Effort)</span>
              <span className="text-[10px] text-secondary">Priority 4</span>
            </div>
            <div className="space-y-1.5 pt-1">
              {data.matrix2x2.hardLongTerm.map((item, idx) => (
                <div key={idx} className="p-2 rounded bg-surface-container border border-outline-variant/30 flex items-center justify-between text-on-surface-variant">
                  <span>{item.skill}</span>
                  <span className="text-[10px] text-secondary">{item.category}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* AI Learning Recommendations Banner */}
      <div className="p-6 rounded-2xl bg-surface-container-low border border-outline-variant/60 space-y-4">
        <h3 className="font-semibold text-on-surface text-base flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-secondary" />
          Copilot Skill Gap Roadmap Strategy
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-surface-container border border-outline-variant/50 space-y-2">
            <h4 className="font-semibold text-sm text-on-surface">Target 90-Day Adaptive Roadmap</h4>
            <p className="text-xs text-on-surface-variant leading-relaxed">
              Incorporate Redis Caching and 2D DP problem sets into your active 90-day placement sprint schedule.
            </p>
            <button
              onClick={() => navigate('/roadmap')}
              className="text-xs font-semibold text-primary hover:underline inline-flex items-center gap-1 pt-1"
            >
              <span>View 90-Day Roadmap</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="p-4 rounded-xl bg-surface-container border border-outline-variant/50 space-y-2">
            <h4 className="font-semibold text-sm text-on-surface">Execute Daily Practice Tasks</h4>
            <p className="text-xs text-on-surface-variant leading-relaxed">
              Start with Today's Action Plan tasks focusing on Course Schedule II and Course Schedule III.
            </p>
            <button
              onClick={() => navigate('/tasks')}
              className="text-xs font-semibold text-primary hover:underline inline-flex items-center gap-1 pt-1"
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
