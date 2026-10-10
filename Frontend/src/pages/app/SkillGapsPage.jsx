import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useUser } from '../../context/UserContext';
import { usePlanning } from '../../context/PlanningContext';
import { initialSkillGapData } from '../../data/skillGapData';
import { skillGapService } from '../../services/skillGapService';
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
  TrendingUp,
  BrainCircuit,
  SlidersHorizontal,
  ChevronRight,
  Edit3
} from 'lucide-react';

export const SkillGapsPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, updateUserProfile } = useUser();
  const { addSkillToRoadmap, toastNotification } = usePlanning();
  const [data, setData] = useState(initialSkillGapData);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [activeCategoryFilter, setActiveCategoryFilter] = useState(() => {
    return location.state?.category || 'All';
  });
  const [isEditingRole, setIsEditingRole] = useState(false);
  const [customRoleInput, setCustomRoleInput] = useState('');
  const [showCustomRoleInput, setShowCustomRoleInput] = useState(false);

  // Derive target role from navigation state or UserContext
  const displayTargetRole = location.state?.targetRole || user?.targetRole || user?.career?.targetRole || 'Backend SDE-1 (Tier 1)';

  const handleRoleChange = async (newRole) => {
    if (newRole === 'custom') {
      setShowCustomRoleInput(true);
      return;
    }
    setShowCustomRoleInput(false);
    updateUserProfile({ targetRole: newRole });
    setIsEditingRole(false);
    setIsRefreshing(true);
    const updated = await skillGapService.analyzeSkillGaps(newRole);
    if (updated) setData(updated);
    setIsRefreshing(false);
  };

  const handleCustomRoleSubmit = async (e) => {
    e.preventDefault();
    if (customRoleInput.trim()) {
      await handleRoleChange(customRoleInput.trim());
      setCustomRoleInput('');
    }
  };

  useEffect(() => {
    skillGapService.getLatestSkillGaps().then((res) => {
      if (res) setData(res);
    });
  }, []);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    const updated = await skillGapService.analyzeSkillGaps(displayTargetRole);
    if (updated) setData(updated);
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
        <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e] relative group">
          <span className="text-slate-400 shrink-0 mr-2">Target Profile</span>
          {isEditingRole ? (
            <div className="flex items-center gap-1.5 z-20">
              {showCustomRoleInput ? (
                <form onSubmit={handleCustomRoleSubmit} className="flex items-center gap-1">
                  <input
                    type="text"
                    value={customRoleInput}
                    onChange={(e) => setCustomRoleInput(e.target.value)}
                    placeholder="Enter target role..."
                    autoFocus
                    className="bg-[#121624] text-indigo-300 border border-indigo-500/50 rounded-lg px-2 py-0.5 text-xs focus:outline-none w-36"
                  />
                  <button
                    type="submit"
                    className="px-2 py-0.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold"
                  >
                    Save
                  </button>
                  <button
                    type="button"
                    onClick={() => { setShowCustomRoleInput(false); setIsEditingRole(false); }}
                    className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 hover:text-white text-xs font-bold"
                  >
                    ✕
                  </button>
                </form>
              ) : (
                <select
                  value={displayTargetRole}
                  onChange={(e) => handleRoleChange(e.target.value)}
                  onBlur={() => {
                    setTimeout(() => { if (!showCustomRoleInput) setIsEditingRole(false); }, 250);
                  }}
                  autoFocus
                  className="bg-[#121624] text-indigo-400 font-bold border border-indigo-500/60 rounded-lg px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer shadow-lg"
                >
                  <option value="Backend SDE-1 (Tier 1)">Backend SDE-1 (Tier 1)</option>
                  <option value="AI/ML Engineer">AI/ML Engineer</option>
                  <option value="Full-Stack Developer">Full-Stack Developer</option>
                  <option value="Frontend SDE-1">Frontend SDE-1</option>
                  <option value="DevOps & Cloud Engineer">DevOps & Cloud Engineer</option>
                  <option value="Data Scientist & Engineer">Data Scientist & Engineer</option>
                  <option value="Cybersecurity Engineer">Cybersecurity Engineer</option>
                  <option value="Systems Software Engineer">Systems Software Engineer</option>
                  <option value="custom">+ Custom Target Role...</option>
                </select>
              )}
            </div>
          ) : (
            <button
              onClick={() => setIsEditingRole(true)}
              title="Click to dynamically check and change target role"
              className="flex items-center gap-1.5 text-indigo-400 hover:text-indigo-300 font-bold truncate transition-colors text-right group/btn bg-indigo-500/10 hover:bg-indigo-500/20 px-2 py-0.5 rounded-lg border border-indigo-500/20"
            >
              <span className="truncate max-w-[180px]">{displayTargetRole}</span>
              <Edit3 className="w-3 h-3 text-indigo-400/80 group-hover/btn:text-indigo-300 shrink-0" />
            </button>
          )}
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

    </div>
  );
};
