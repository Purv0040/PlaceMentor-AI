import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { readinessService } from '../../services/readinessService';
import { initialReadinessData } from '../../data/readinessData';
import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Tooltip } from 'recharts';
import {
  Zap,
  RefreshCw,
  Target,
  CheckCircle2,
  TrendingUp,
  ShieldCheck,
  Sparkles,
  ArrowUpRight,
  FileText,
  GitBranch,
  Code,
  FolderGit2,
  Building2,
  AlertTriangle
} from 'lucide-react';

export const PlacementReadinessPage = () => {
  const navigate = useNavigate();
  const [data, setData] = useState(initialReadinessData);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    readinessService.calculateReadiness().then((res) => setData(res));
  }, []);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    const updated = await readinessService.calculateReadiness();
    setData(updated);
    setIsRefreshing(false);
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* 1. HERO BANNER */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6 p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-indigo-950/60 via-purple-950/40 to-[#121624] border border-indigo-500/30 shadow-2xl">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-400 text-xs font-mono font-semibold border border-indigo-500/30">
              <Zap className="w-3.5 h-3.5 text-indigo-400" />
              TELEMETRY V4.2 · HOLISTIC SYNTHESIS ENGINE
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">Placement Readiness</h1>
          <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
            Understand your current technical preparation quotient and discover high-leverage remediations synthesized across 7 diagnostic vectors.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start lg:self-center shrink-0">
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white rounded-xl font-semibold text-xs sm:text-sm transition-all shadow-lg shadow-indigo-600/30 border border-indigo-400/30 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>{isRefreshing ? 'Synthesizing Vectors...' : 'Recalibrate Score'}</span>
          </button>
        </div>
      </div>

      {/* 2. METADATA BAR */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-4 rounded-2xl bg-[#121624] border border-[#232b3e] text-xs font-mono shadow-xl">
        <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e]">
          <span className="text-slate-400">Last Synced</span>
          <span className="text-slate-200 font-semibold">{data.lastSynced}</span>
        </div>

        <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e]">
          <span className="text-slate-400">Target Benchmark</span>
          <span className="text-indigo-400 font-bold">{data.targetBenchmark}</span>
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
              <span className="px-3 py-1 rounded-full text-xs font-mono font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                {data.scoreStatus}
              </span>
            </div>

            {/* Circular Gauge Score Display */}
            <div className="py-6 text-center">
              <div className="inline-flex flex-col items-center justify-center w-40 h-40 rounded-full border-4 border-indigo-500/40 bg-gradient-to-b from-indigo-950/60 to-[#0f131d] shadow-[0_0_30px_rgba(99,102,241,0.25)]">
                <span className="text-5xl font-black text-white tracking-tight font-mono">{data.overallScore}%</span>
                <span className="text-xs font-mono text-indigo-400 font-semibold mt-1">Readiness Index</span>
              </div>
            </div>

            <div className="text-center space-y-1">
              <p className="text-xs sm:text-sm font-bold text-white">{data.percentileRank}</p>
              <p className="text-xs text-slate-400">
                Evaluated against Tier-1 SDE screening benchmarks (Minimum threshold: 80%)
              </p>
            </div>
          </div>

          <div className="pt-4 border-t border-[#232b3e] flex items-center justify-between text-xs font-mono">
            <span className="text-slate-400">Synthesized Vectors</span>
            <span className="text-indigo-400 font-bold">7 Vectors Connected</span>
          </div>
        </div>

        {/* 7-Vector Recharts Radar Chart */}
        <div className="lg:col-span-2 bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-xl">
          <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
            <div>
              <h3 className="font-bold text-white text-base">7-Vector Radar Score Breakdown</h3>
              <p className="text-xs text-slate-400">Candidate Score vs Tier-1 SDE Target Benchmark</p>
            </div>
            <span className="text-xs font-mono text-purple-400 font-semibold bg-purple-500/10 px-2.5 py-1 rounded-lg border border-purple-500/20">
              7 Diagnostics
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="75%" data={data.radarData}>
                <PolarGrid stroke="#232b3e" />
                <PolarAngleAxis dataKey="vector" stroke="#cbd5e1" fontSize={11} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#64748b" fontSize={10} />
                <Radar name="Candidate Score" dataKey="Score" stroke="#6366f1" fill="#6366f1" fillOpacity={0.4} />
                <Radar name="Tier-1 Benchmark" dataKey="Benchmark" stroke="#10b981" fill="#10b981" fillOpacity={0.15} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#121624',
                    borderColor: '#232b3e',
                    borderRadius: '12px',
                    color: '#ffffff',
                    fontSize: '12px',
                  }}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 4. 7-VECTOR PROGRESS BARS LIST */}
      <div className="bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-xl">
        <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
          <h3 className="font-bold text-white text-base">7-Vector Diagnostic Scores</h3>
          <span className="text-xs font-mono text-slate-400">Detailed Weightage & Cutoffs</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.vectorScores.map((vector, idx) => (
            <div key={idx} className="p-4 rounded-xl bg-[#0f131d] border border-[#232b3e] space-y-2.5 hover:border-indigo-500/30 transition-colors">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-white">{vector.name}</span>
                <div className="flex items-center gap-2 font-mono">
                  <span className="text-indigo-400 font-bold">{vector.score}%</span>
                  <span className="text-slate-400 text-[11px]">(Target: {vector.target}%)</span>
                </div>
              </div>

              <div className="w-full bg-[#121624] rounded-full h-2 overflow-hidden border border-[#232b3e]">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    vector.score >= vector.target ? 'bg-emerald-500' : 'bg-indigo-500'
                  }`}
                  style={{ width: `${vector.score}%` }}
                ></div>
              </div>

              <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 pt-0.5">
                <span>Weightage: {vector.weight}</span>
                <span
                  className={`font-bold ${
                    vector.score >= vector.target ? 'text-emerald-400' : 'text-amber-400'
                  }`}
                >
                  {vector.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 5. PREPARATION MODULES SUMMARY CARDS */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-white text-lg">Connected Preparation Modules</h3>
          <span className="text-xs font-mono text-slate-400">Phase 5 Integration</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {data.dimensionsSummary.map((dim) => (
            <div
              key={dim.id}
              className="p-5 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-3 hover:border-indigo-500/40 transition-colors flex flex-col justify-between shadow-xl"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-sm text-white">{dim.name}</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                    {dim.score}%
                  </span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">{dim.detail}</p>
              </div>

              <button
                onClick={() => navigate(dim.route)}
                className="text-xs font-bold text-indigo-400 hover:text-indigo-300 inline-flex items-center gap-1 pt-2"
              >
                <span>View Module Analysis</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* 6. TIER-1 COMPANY BENCHMARK MATRIX */}
      <div className="bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-xl">
        <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
          <h3 className="font-bold text-white text-base flex items-center gap-2">
            <Building2 className="w-5 h-5 text-indigo-400" />
            Tier-1 Company Benchmark Matrix
          </h3>
          <span className="text-xs font-mono text-slate-400">Placement Drives Season</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-[#232b3e] text-[11px] font-mono uppercase text-slate-400">
                <th className="py-3 px-4">Company Tier / Segment</th>
                <th className="py-3 px-4">Min Readiness Cutoff</th>
                <th className="py-3 px-4">Candidate Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#232b3e] text-xs font-mono">
              {data.tier1Benchmarks.map((item, idx) => (
                <tr key={idx} className="hover:bg-[#0f131d] transition-colors">
                  <td className="py-3.5 px-4 font-bold text-white">{item.company}</td>
                  <td className="py-3.5 px-4 text-slate-300">{item.minReadiness}% Score</td>
                  <td className="py-3.5 px-4">
                    <span
                      className={`px-2.5 py-1 rounded-lg text-xs font-semibold ${
                        data.overallScore >= item.minReadiness
                          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                          : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                      }`}
                    >
                      {item.currentMatch}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 7. AI PRIORITY REMEDIATION MATRIX */}
      <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-xl">
        <h3 className="font-bold text-white text-base flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-400" />
          AI Priority Remediation Recommendations
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.priorityRemediations.map((rem) => (
            <div key={rem.id} className="p-4 rounded-xl bg-[#0f131d] border border-[#232b3e] space-y-2 hover:border-purple-500/40 transition-colors">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-indigo-400 uppercase tracking-wider">
                  {rem.vector}
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase bg-rose-500/20 text-rose-400 border border-rose-500/30">
                  {rem.priority} Priority
                </span>
              </div>
              <h4 className="font-bold text-sm text-white">{rem.title}</h4>
              <p className="text-xs text-slate-300 leading-relaxed">{rem.description}</p>
              <button
                onClick={() => navigate(rem.actionRoute)}
                className="text-xs font-bold text-indigo-400 hover:text-indigo-300 inline-flex items-center gap-1 pt-1"
              >
                <span>{rem.actionLabel}</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
