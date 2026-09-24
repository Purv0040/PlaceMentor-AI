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
      {/* Header Banner */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 bg-surface-container-low p-6 rounded-2xl border border-outline-variant/60 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <h1 className="text-2xl font-bold text-on-surface tracking-tight">Placement Readiness</h1>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-secondary-container/40 text-secondary text-xs font-mono border border-secondary/30">
              <Zap className="w-3.5 h-3.5 text-secondary" />
              TELEMETRY V4.2 · HOLISTIC SYNTHESIS ENGINE
            </span>
          </div>
          <p className="text-sm text-on-surface-variant max-w-2xl">
            Understand your current technical preparation quotient and discover high-leverage remediations synthesized across 7 diagnostic vectors.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start lg:self-center shrink-0">
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-on-primary hover:bg-primary-fixed-dim rounded-xl font-semibold text-sm transition-all shadow-md disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>{isRefreshing ? 'Synthesizing Vectors...' : 'Recalibrate Score'}</span>
          </button>
        </div>
      </div>

      {/* Metadata Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-4 rounded-xl bg-surface-container-low border border-outline-variant text-sm font-mono">
        <div className="flex items-center justify-between px-3 py-1.5 bg-surface-container rounded-lg border border-outline-variant/50">
          <span className="text-xs text-on-surface-variant">Last Synced</span>
          <span className="text-on-surface font-medium">{data.lastSynced}</span>
        </div>

        <div className="flex items-center justify-between px-3 py-1.5 bg-surface-container rounded-lg border border-outline-variant/50">
          <span className="text-xs text-on-surface-variant">Target Benchmark</span>
          <span className="text-primary font-bold">{data.targetBenchmark}</span>
        </div>

        <div className="flex items-center justify-between px-3 py-1.5 bg-surface-container rounded-lg border border-outline-variant/50">
          <span className="text-xs text-on-surface-variant">Confidence Index</span>
          <span className="text-tertiary font-bold">{data.confidenceIndex}</span>
        </div>
      </div>

      {/* Overall Readiness Gauge & 7-Vector Radar Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Overall Readiness Hero Score Card */}
        <div className="bg-surface-container-low p-6 rounded-2xl border border-outline-variant/60 space-y-6 flex flex-col justify-between shadow-sm">
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-mono uppercase tracking-wider text-on-surface-variant">Overall Readiness Score</span>
              <span className="px-3 py-1 rounded-full text-xs font-mono font-semibold bg-tertiary-container/30 text-tertiary border border-tertiary/30">
                {data.scoreStatus}
              </span>
            </div>

            {/* Circular Gauge Score Display */}
            <div className="py-6 text-center">
              <div className="inline-flex flex-col items-center justify-center w-40 h-40 rounded-full border-4 border-primary/30 bg-surface-container/60 shadow-[0_0_30px_rgba(128,131,255,0.2)]">
                <span className="text-5xl font-black text-on-surface tracking-tight">{data.overallScore}%</span>
                <span className="text-xs font-mono text-tertiary font-semibold mt-1">Readiness Index</span>
              </div>
            </div>

            <div className="text-center space-y-1">
              <p className="text-sm font-semibold text-on-surface">{data.percentileRank}</p>
              <p className="text-xs text-on-surface-variant">
                Evaluated against Tier-1 SDE screening benchmarks (Minimum threshold: 80%)
              </p>
            </div>
          </div>

          <div className="pt-4 border-t border-outline-variant/50 flex items-center justify-between text-xs font-mono">
            <span className="text-on-surface-variant">Synthesized Vectors</span>
            <span className="text-primary font-bold">7 Vectors Connected</span>
          </div>
        </div>

        {/* 7-Vector Recharts Radar Chart */}
        <div className="lg:col-span-2 bg-surface-container-low p-6 rounded-2xl border border-outline-variant/60 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-outline-variant/50">
            <div>
              <h3 className="font-semibold text-on-surface text-base">7-Vector Radar Score Breakdown</h3>
              <p className="text-xs text-on-surface-variant">Candidate Score vs Tier-1 SDE Target Benchmark</p>
            </div>
            <span className="text-xs font-mono text-secondary bg-secondary-container/20 px-2.5 py-1 rounded border border-secondary/30">
              7 Diagnostics
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="75%" data={data.radarData}>
                <PolarGrid stroke="#464554" />
                <PolarAngleAxis dataKey="vector" stroke="#dfe2f1" fontSize={11} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#908fa0" fontSize={10} />
                <Radar name="Candidate Score" dataKey="Score" stroke="#8083ff" fill="#8083ff" fillOpacity={0.4} />
                <Radar name="Tier-1 Benchmark" dataKey="Benchmark" stroke="#4edea3" fill="#4edea3" fillOpacity={0.15} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1c1f2a',
                    borderColor: '#464554',
                    borderRadius: '12px',
                    color: '#dfe2f1',
                    fontSize: '12px',
                  }}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 7-Vector Progress Bars List */}
      <div className="bg-surface-container-low p-6 rounded-2xl border border-outline-variant/60 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-outline-variant/50">
          <h3 className="font-semibold text-on-surface text-base">7-Vector Diagnostic Scores</h3>
          <span className="text-xs font-mono text-on-surface-variant">Detailed Weightage & Cutoffs</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.vectorScores.map((vector, idx) => (
            <div key={idx} className="p-4 rounded-xl bg-surface-container border border-outline-variant/40 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-on-surface">{vector.name}</span>
                <div className="flex items-center gap-2 font-mono">
                  <span className="text-on-surface font-bold">{vector.score}%</span>
                  <span className="text-on-surface-variant text-[11px]">(Target: {vector.target}%)</span>
                </div>
              </div>

              <div className="w-full bg-surface-container-high rounded-full h-2 overflow-hidden border border-outline-variant/30">
                <div
                  className={`h-full transition-all duration-500 ${
                    vector.score >= vector.target ? 'bg-tertiary' : 'bg-primary'
                  }`}
                  style={{ width: `${vector.score}%` }}
                ></div>
              </div>

              <div className="flex items-center justify-between text-[11px] font-mono text-on-surface-variant pt-0.5">
                <span>Weightage: {vector.weight}</span>
                <span
                  className={`font-semibold ${
                    vector.score >= vector.target ? 'text-tertiary' : 'text-secondary'
                  }`}
                >
                  {vector.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Phase 5 Preparation Modules Summary Cards */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-on-surface text-lg">Connected Preparation Modules</h3>
          <span className="text-xs font-mono text-on-surface-variant">Phase 5 Integration</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {data.dimensionsSummary.map((dim) => (
            <div
              key={dim.id}
              className="p-5 rounded-2xl bg-surface-container-low border border-outline-variant/60 space-y-3 hover:border-primary/40 transition-colors flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-sm text-on-surface">{dim.name}</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-tertiary-container/30 text-tertiary border border-tertiary/30">
                    {dim.score}%
                  </span>
                </div>
                <p className="text-xs text-on-surface-variant leading-relaxed">{dim.detail}</p>
              </div>

              <button
                onClick={() => navigate(dim.route)}
                className="text-xs font-semibold text-primary hover:underline inline-flex items-center gap-1 pt-2"
              >
                <span>View Module Analysis</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Tier-1 Company Benchmark Matrix */}
      <div className="bg-surface-container-low p-6 rounded-2xl border border-outline-variant/60 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-outline-variant/50">
          <h3 className="font-semibold text-on-surface text-base flex items-center gap-2">
            <Building2 className="w-5 h-5 text-primary" />
            Tier-1 Company Benchmark Matrix
          </h3>
          <span className="text-xs font-mono text-on-surface-variant">Placement Drives Season</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-outline-variant/40 text-[11px] font-mono uppercase text-on-surface-variant">
                <th className="py-2.5 px-3">Company Tier / Segment</th>
                <th className="py-2.5 px-3">Min Readiness Cutoff</th>
                <th className="py-2.5 px-3">Candidate Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/30 text-xs font-mono">
              {data.tier1Benchmarks.map((item, idx) => (
                <tr key={idx} className="hover:bg-surface-container/50 transition-colors">
                  <td className="py-3 px-3 font-semibold text-on-surface">{item.company}</td>
                  <td className="py-3 px-3 text-on-surface-variant">{item.minReadiness}% Score</td>
                  <td className="py-3 px-3">
                    <span
                      className={`px-2.5 py-1 rounded text-xs font-semibold ${
                        data.overallScore >= item.minReadiness
                          ? 'bg-tertiary-container/30 text-tertiary border border-tertiary/30'
                          : 'bg-secondary-container/30 text-secondary border border-secondary/30'
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

      {/* AI Priority Remediation Matrix */}
      <div className="p-6 rounded-2xl bg-surface-container-low border border-outline-variant/60 space-y-4">
        <h3 className="font-semibold text-on-surface text-base flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-secondary" />
          AI Priority Remediation Recommendations
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.priorityRemediations.map((rem) => (
            <div key={rem.id} className="p-4 rounded-xl bg-surface-container border border-outline-variant/50 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-semibold text-secondary uppercase tracking-wider">
                  {rem.vector}
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase bg-error/20 text-error border border-error/30">
                  {rem.priority} Priority
                </span>
              </div>
              <h4 className="font-semibold text-sm text-on-surface">{rem.title}</h4>
              <p className="text-xs text-on-surface-variant leading-relaxed">{rem.description}</p>
              <button
                onClick={() => navigate(rem.actionRoute)}
                className="text-xs font-semibold text-primary hover:underline inline-flex items-center gap-1 pt-1"
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
