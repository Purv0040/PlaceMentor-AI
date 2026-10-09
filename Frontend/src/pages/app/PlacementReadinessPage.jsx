import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { readinessService } from '../../services/readinessService';
import { initialReadinessData } from '../../data/readinessData';
import { useApp } from '../../context/AppContext';
import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Tooltip } from 'recharts';
import {
  Zap,
  RefreshCw,
  Target,
  CheckCircle2,
  TrendingUp,
  TrendingDown,
  ShieldCheck,
  FileText,
  GitBranch,
  Code,
  FolderGit2,
  Building2,
  AlertTriangle,
  HelpCircle,
  Clock,
  ArrowRight,
  Info,
  Check
} from 'lucide-react';

export const PlacementReadinessPage = () => {
  const navigate = useNavigate();
  const { theme } = useApp();
  const [data, setData] = useState(initialReadinessData);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const chartColors = theme === 'light'
    ? {
        grid: '#cbd5e1',
        axis: '#334155',
        radius: '#64748b',
        tooltipBackground: '#ffffff',
        tooltipBorder: '#cbd5e1',
        tooltipText: '#172033'
      }
    : {
        grid: '#232b3e',
        axis: '#cbd5e1',
        radius: '#64748b',
        tooltipBackground: '#121624',
        tooltipBorder: '#232b3e',
        tooltipText: '#ffffff'
      };

  useEffect(() => {
    setIsLoading(true);
    readinessService.getLatestReadiness().then((res) => {
      if (res) setData(res);
      setIsLoading(false);
    }).catch(() => {
      setIsLoading(false);
    });
  }, []);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    const updated = await readinessService.calculateReadiness();
    if (updated) setData(updated);
    setIsRefreshing(false);
  };

  const getStatusBadge = (status) => {
    switch (status?.toLowerCase()) {
      case 'strong':
      case 'assessed':
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
      case 'provisional':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
      case 'stale evidence':
      case 'stale':
        return 'bg-rose-500/20 text-rose-400 border-rose-500/30';
      default:
        return 'bg-slate-800 text-slate-400 border-slate-700';
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
              EVIDENCE-BASED SCORING ENGINE V2.0 · DETERMINISTIC TELEMETRY
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">Placement Readiness</h1>
          <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
            Evidence-based technical placement quotient synthesized across 7 diagnostic categories, with verifiable telemetry and target-role skill gap analysis.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start lg:self-center shrink-0">
          <button
            onClick={handleRefresh}
            disabled={isRefreshing || isLoading}
            className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white rounded-xl font-semibold text-xs sm:text-sm transition-all shadow-lg shadow-indigo-600/30 border border-indigo-400/30 disabled:opacity-50 cursor-pointer"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>{isRefreshing ? 'Recalculating Evidence...' : 'Recalibrate Score'}</span>
          </button>
        </div>
      </div>

      {/* STALE DATA WARNING BANNER IF PRESENT */}
      {data.staleData && data.staleData.length > 0 && (
        <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-start gap-3 text-xs text-amber-200">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold text-amber-300">Stale Telemetry Detected:</span>
            {data.staleData.map((s, idx) => (
              <p key={idx} className="text-slate-300">{s.message}</p>
            ))}
          </div>
        </div>
      )}

      {/* 2. METADATA BAR */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 p-4 rounded-2xl bg-[#121624] border border-[#232b3e] text-xs font-mono shadow-xl">
        <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e]">
          <span className="text-slate-400">Last Synced</span>
          <span className="text-slate-200 font-semibold">{data.lastSynced}</span>
        </div>

        <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e]">
          <span className="text-slate-400">Target Role</span>
          <span className="text-indigo-400 font-bold truncate max-w-[140px]">{data.targetBenchmark}</span>
        </div>

        <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e]">
          <span className="text-slate-400">Evidence Coverage</span>
          <span className="text-purple-400 font-bold">{data.coveragePercentage}%</span>
        </div>

        <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e]">
          <span className="text-slate-400">Confidence Index</span>
          <span className="text-emerald-400 font-bold">{data.confidenceIndex}</span>
        </div>
      </div>

      {/* 3. OVERALL READINESS GAUGE & 7-VECTOR RADAR GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Overall Readiness Hero Score Card */}
        <div className="bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-6 flex flex-col justify-between shadow-xl">
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">Overall Readiness Score</span>
              <span className={`px-3 py-1 rounded-full text-xs font-mono font-semibold border ${getStatusBadge(data.scoreStatus)}`}>
                {data.scoreStatus}
              </span>
            </div>

            {/* Circular Gauge Score Display */}
            <div className="py-6 text-center">
              <div className="inline-flex flex-col items-center justify-center w-40 h-40 rounded-full border-4 border-indigo-500/40 bg-gradient-to-b from-indigo-950/60 to-[#0f131d] shadow-[0_0_30px_rgba(99,102,241,0.25)] relative">
                <span className="text-5xl font-black text-white tracking-tight font-mono">{data.overallScore}%</span>
                <span className="text-xs font-mono text-indigo-400 font-semibold mt-1">Readiness Index</span>
                
                {/* Score Delta Pill */}
                {data.scoreDelta !== null && data.scoreDelta !== undefined && (
                  <div className={`absolute -bottom-3 px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold flex items-center gap-1 border shadow-md ${
                    data.scoreDelta >= 0 ? 'bg-emerald-950/80 text-emerald-400 border-emerald-500/40' : 'bg-rose-950/80 text-rose-400 border-rose-500/40'
                  }`}>
                    {data.scoreDelta >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                    <span>{data.scoreDelta >= 0 ? `+${data.scoreDelta}%` : `${data.scoreDelta}%`}</span>
                  </div>
                )}
              </div>
            </div>

            <div className="text-center space-y-1">
              <p className="text-xs sm:text-sm font-bold text-white">{data.percentileRank}</p>
              <p className="text-xs text-slate-400">
                Evidence-weighted average of all assessed diagnostic vectors
              </p>
            </div>
          </div>

          <div className="pt-4 border-t border-[#232b3e] flex items-center justify-between text-xs font-mono">
            <span className="text-slate-400">Scored Categories</span>
            <span className="text-indigo-400 font-bold">
              {data.vectorScores.filter(v => v.hasScore).length} of 7 Assessed
            </span>
          </div>
        </div>

        {/* 7-Vector Recharts Radar Chart */}
        <div className="lg:col-span-2 bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-xl">
          <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
            <div>
              <h3 className="font-bold text-white text-base">7-Vector Radar Score Breakdown</h3>
              <p className="text-xs text-slate-400">Candidate Score vs Target Competency Benchmark</p>
            </div>
            <span className="text-xs font-mono text-purple-400 font-semibold bg-purple-500/10 px-2.5 py-1 rounded-lg border border-purple-500/20">
              7 Diagnostics
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="75%" data={data.radarData}>
                <PolarGrid stroke={chartColors.grid} />
                <PolarAngleAxis dataKey="vector" stroke={chartColors.axis} fontSize={11} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} stroke={chartColors.radius} fontSize={10} />
                <Radar name="Candidate Score" dataKey="Score" stroke="#6366f1" fill="#6366f1" fillOpacity={0.4} />
                <Radar name="Benchmark" dataKey="Benchmark" stroke="#10b981" fill="#10b981" fillOpacity={0.15} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: chartColors.tooltipBackground,
                    borderColor: chartColors.tooltipBorder,
                    borderRadius: '12px',
                    color: chartColors.tooltipText,
                    fontSize: '12px',
                  }}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 4. 7-VECTOR PROGRESS & RUBRICS LIST */}
      <div className="bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-xl">
        <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
          <h3 className="font-bold text-white text-base">7-Vector Diagnostic Scores & Rubrics</h3>
          <span className="text-xs font-mono text-slate-400">Normalized Weightage & Verification Status</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.vectorScores.map((vector, idx) => (
            <div key={idx} className="p-4 rounded-xl bg-[#0f131d] border border-[#232b3e] space-y-2.5 hover:border-indigo-500/30 transition-colors">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-white">{vector.name}</span>
                <div className="flex items-center gap-2 font-mono">
                  <span className={`font-bold ${vector.hasScore ? 'text-indigo-400' : 'text-slate-500'}`}>
                    {vector.hasScore ? `${vector.score}%` : 'N/A'}
                  </span>
                  <span className="text-slate-400 text-[11px]">(Target: {vector.target}%)</span>
                </div>
              </div>

              <div className="w-full bg-[#121624] rounded-full h-2 overflow-hidden border border-[#232b3e]">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    !vector.hasScore ? 'bg-slate-700' : vector.score >= vector.target ? 'bg-emerald-500' : 'bg-indigo-500'
                  }`}
                  style={{ width: `${vector.hasScore ? vector.score : 0}%` }}
                ></div>
              </div>

              <div className="space-y-1">
                <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 pt-0.5">
                  <span>Weight: {vector.weight}</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${getStatusBadge(vector.status)}`}>
                    {vector.status}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 leading-snug">{vector.reason}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 5. TARGET-ROLE FIT & SPECIFIC COMPETENCY GAPS */}
      {data.roleAlignment && (
        <div className="bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-xl">
          <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
            <div>
              <h3 className="font-bold text-white text-base flex items-center gap-2">
                <Target className="w-5 h-5 text-indigo-400" />
                Target-Role Fit: {data.targetBenchmark}
              </h3>
              <p className="text-xs text-slate-400">Role competency alignment evaluated separately from general readiness</p>
            </div>
            <div className="text-right font-mono">
              <span className="text-xl font-bold text-indigo-400">{data.roleAlignment.role_alignment_score ?? 0}%</span>
              <p className="text-[10px] text-slate-400">Competency Match</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div className="p-4 rounded-xl bg-[#0f131d] border border-emerald-500/20 space-y-2">
              <span className="font-bold text-emerald-400 flex items-center gap-1.5">
                <Check className="w-4 h-4" /> Aligned Competencies ({data.roleAlignment.aligned_skills?.length || 0})
              </span>
              <div className="flex flex-wrap gap-1.5 pt-1">
                {data.roleAlignment.aligned_skills?.map((sk, i) => (
                  <span key={i} className="px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 text-[11px] font-mono">
                    {sk}
                  </span>
                ))}
              </div>
            </div>

            <div className="p-4 rounded-xl bg-[#0f131d] border border-amber-500/20 space-y-2">
              <span className="font-bold text-amber-400 flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4" /> Missing Role Skills ({data.roleAlignment.missing_skills?.length || 0})
              </span>
              <div className="flex flex-wrap gap-1.5 pt-1">
                {data.roleAlignment.missing_skills?.map((sk, i) => (
                  <span key={i} className="px-2.5 py-1 rounded-lg bg-amber-500/10 text-amber-300 border border-amber-500/20 text-[11px] font-mono">
                    {sk}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Role specific gaps */}
          {data.roleAlignment.role_specific_gaps && data.roleAlignment.role_specific_gaps.length > 0 && (
            <div className="pt-2 space-y-2">
              <span className="text-xs font-bold text-slate-300 font-mono uppercase">Key Role Engineering Gaps</span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {data.roleAlignment.role_specific_gaps.map((gap, i) => (
                  <div key={i} className="p-3 rounded-xl bg-[#0f131d] border border-[#232b3e] text-xs space-y-1">
                    <span className="font-bold text-indigo-300">{gap.area}</span>
                    <p className="text-slate-400 text-[11px]">{gap.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 6. HIGH-LEVERAGE PLACEMENT REMEDIATIONS */}
      <div className="bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-xl">
        <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
          <div>
            <h3 className="font-bold text-white text-base flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-indigo-400" />
              High-Leverage AI Remediations
            </h3>
            <p className="text-xs text-slate-400">Actionable steps to elevate candidate readiness quotient</p>
          </div>
        </div>

        <div className="space-y-3">
          {data.priorityRemediations.map((rem, i) => (
            <div key={i} className="p-4 rounded-xl bg-[#0f131d] border border-[#232b3e] flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:border-indigo-500/30 transition-colors">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 font-mono text-[10px] font-bold">
                    {rem.vector}
                  </span>
                  <span className="text-xs text-slate-400">Priority: {rem.priority}</span>
                </div>
                <p className="text-xs font-semibold text-white">{rem.title}</p>
              </div>

              <button
                onClick={() => navigate(rem.actionRoute)}
                className="self-start sm:self-center px-4 py-2 bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer shrink-0"
              >
                <span>{rem.actionLabel}</span>
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
