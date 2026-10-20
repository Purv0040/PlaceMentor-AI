import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { readinessService } from '../../services/readinessService';
import { useApp } from '../../context/AppContext';
import { useUser } from '../../context/UserContext';
import {
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Tooltip
} from 'recharts';
import {
  RefreshCw,
  Target,
  CheckCircle2,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  ArrowRight,
  Check,
  ChevronDown,
  ChevronUp,
  Sparkles,
  MessageSquare,
  ArrowUpRight,
  FileText,
  Code2,
  GitBranch,
  Video,
  ShieldCheck,
  Clock
} from 'lucide-react';

export const PlacementReadinessPage = () => {
  const navigate = useNavigate();
  const { theme } = useApp();
  const { user } = useUser();
  const [data, setData] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedVectors, setExpandedVectors] = useState({});
  const [errorMessage, setErrorMessage] = useState(null);

  const userRole = user?.targetRole || data?.targetBenchmark || 'Full Stack Engineer';

  const chartColors = theme === 'light'
    ? {
        grid: '#e2e8f0',
        axis: '#475569',
        radius: '#94a3b8',
        tooltipBackground: '#ffffff',
        tooltipBorder: '#cbd5e1',
        tooltipText: '#0f172a'
      }
    : {
        grid: '#232b3e',
        axis: '#cbd5e1',
        radius: '#475569',
        tooltipBackground: '#121624',
        tooltipBorder: '#232b3e',
        tooltipText: '#f8fafc'
      };

  const loadReadinessData = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const res = await readinessService.getLatestReadiness(user);
      if (res) {
        setData(res);
      }
    } catch (err) {
      console.error('Error fetching readiness data:', err);
      setErrorMessage('Unable to load telemetry data. Please verify your connection.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadReadinessData();
  }, [user?.targetRole, user?.companyTier, user?.resumeFileName, user?.leetcodeHandle, user?.githubHandle]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    setErrorMessage(null);
    try {
      const updated = await readinessService.calculateReadiness(userRole, user);
      if (updated) {
        setData(updated);
      }
    } catch (err) {
      console.error('Failed to recalibrate readiness:', err);
      setErrorMessage('Recalibration encountered a temporary error. Please try again.');
    } finally {
      setIsRefreshing(false);
    }
  };

  const toggleVectorExpand = (key) => {
    setExpandedVectors((prev) => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const getModuleIcon = (name = '') => {
    const lower = name.toLowerCase();
    if (lower.includes('resume')) return <FileText className="w-4 h-4 text-indigo-400 shrink-0" />;
    if (lower.includes('leetcode') || lower.includes('problem') || lower.includes('dsa')) return <Code2 className="w-4 h-4 text-emerald-400 shrink-0" />;
    if (lower.includes('github') || lower.includes('portfolio') || lower.includes('code')) return <GitBranch className="w-4 h-4 text-purple-400 shrink-0" />;
    if (lower.includes('interview') || lower.includes('mock')) return <Video className="w-4 h-4 text-amber-400 shrink-0" />;
    return <Target className="w-4 h-4 text-indigo-400 shrink-0" />;
  };

  const getStatusBadge = (status) => {
    const s = status?.toLowerCase() || '';
    if (s.includes('provisional')) {
      return {
        label: status || 'Provisional',
        type: 'provisional',
        className: 'bg-amber-500/15 text-amber-300 border-amber-500/30'
      };
    }
    if (s.includes('strong') || s.includes('assessed') || s.includes('qualified') || s.includes('synced') || s.includes('ready') || s.includes('on track')) {
      return {
        label: status || 'Assessed',
        type: 'assessed',
        className: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
      };
    }
    if (s.includes('stale') || s.includes('review') || s.includes('work') || s.includes('pending') || s.includes('attention') || s.includes('needs')) {
      return {
        label: status || 'Needs Attention',
        type: 'attention',
        className: 'bg-rose-500/15 text-rose-300 border-rose-500/30'
      };
    }
    return {
      label: status || 'Active',
      type: 'default',
      className: 'bg-indigo-500/15 text-indigo-300 border-indigo-500/30'
    };
  };

  // Map gap descriptions to relevant module routes
  const getGapAction = (gapText) => {
    const lower = (gapText || '').toLowerCase();
    if (lower.includes('dsa') || lower.includes('leetcode') || lower.includes('algorithm') || lower.includes('problem')) {
      return { label: 'Practice DSA', route: '/leetcode' };
    }
    if (lower.includes('resume') || lower.includes('ats') || lower.includes('bullet') || lower.includes('star')) {
      return { label: 'Audit Resume', route: '/resume' };
    }
    if (lower.includes('github') || lower.includes('repo') || lower.includes('commit') || lower.includes('code')) {
      return { label: 'Sync GitHub', route: '/github' };
    }
    if (lower.includes('interview') || lower.includes('mock') || lower.includes('behavioral')) {
      return { label: 'Mock Screen', route: '/interviews' };
    }
    return { label: 'View Tasks', route: '/tasks' };
  };

  // Skeleton shimmer while loading
  if (isLoading && !data) {
    return (
      <div className="space-y-5 animate-pulse max-w-6xl mx-auto">
        <div className="h-28 rounded-2xl bg-[#121624] border border-[#232b3e]" />
        <div className="h-16 rounded-xl bg-[#121624] border border-[#232b3e]" />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <div className="h-72 rounded-2xl bg-[#121624] border border-[#232b3e]" />
          <div className="lg:col-span-2 h-72 rounded-2xl bg-[#121624] border border-[#232b3e]" />
        </div>
        <div className="h-44 rounded-2xl bg-[#121624] border border-[#232b3e]" />
      </div>
    );
  }

  if (!data) return null;

  const targetTierName = user?.companyTier?.split('(')[0]?.trim() || 'Tier-1 Tech';
  const targetDriveName = user?.targetDrive?.split('(')[0]?.trim() || `Class of ${user?.graduationYear || '2026'}`;

  return (
    <div className="space-y-6 max-w-6xl mx-auto animate-in fade-in duration-300">
      {/* ERROR BANNER */}
      {errorMessage && (
        <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-between text-xs text-rose-200">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{errorMessage}</span>
          </div>
          <button
            type="button"
            onClick={handleRefresh}
            className="px-3 py-1 bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/30 rounded-lg text-rose-300 font-semibold cursor-pointer transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* 1. HEADER */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 p-5 sm:p-6 rounded-2xl bg-gradient-to-r from-[#181d33] via-[#121624] to-[#121624] border border-[#232b3e] shadow-lg">
        <div className="space-y-1">
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">Placement Readiness</h1>
          <p className="text-xs sm:text-sm text-slate-300">
            Real-time hiring bar evaluation calibrated across 4 core preparation vectors.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Target Role Pill */}
          <div className="inline-flex items-center gap-2 px-3.5 py-2 bg-[#0f131d] border border-indigo-500/30 rounded-xl text-xs sm:text-sm text-slate-200 font-medium shadow-sm">
            <Target className="w-4 h-4 text-indigo-400 shrink-0" />
            <span className="text-slate-400">Target Role:</span>
            <span className="text-indigo-300 font-semibold">{userRole}</span>
          </div>

          {/* Recalibrate Score Button */}
          <button
            type="button"
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="inline-flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 active:scale-95 text-white rounded-xl font-semibold text-xs sm:text-sm transition-all shadow-md shadow-indigo-600/20 disabled:opacity-50 cursor-pointer focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>{isRefreshing ? 'Recalculating...' : 'Recalibrate Score'}</span>
          </button>
        </div>
      </div>

      {/* 2. REFINED METRICS BAR */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-3.5 rounded-xl bg-[#121624] border border-[#232b3e] shadow-md flex flex-col justify-between">
          <span className="text-[11px] text-slate-400 font-medium">Target Tier</span>
          <span className="text-sm font-semibold text-white truncate mt-1" title={targetTierName}>
            {targetTierName}
          </span>
        </div>
        <div className="p-3.5 rounded-xl bg-[#121624] border border-[#232b3e] shadow-md flex flex-col justify-between">
          <span className="text-[11px] text-slate-400 font-medium">Placement Drive</span>
          <span className="text-sm font-semibold text-white truncate mt-1" title={targetDriveName}>
            {targetDriveName}
          </span>
        </div>
        <div className="p-3.5 rounded-xl bg-[#121624] border border-[#232b3e] shadow-md flex flex-col justify-between">
          <span className="text-[11px] text-slate-400 font-medium">Telemetry Coverage</span>
          <div className="flex items-center gap-1.5 mt-1">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span className="text-sm font-semibold font-mono text-emerald-400">
              {Math.round(data.coveragePercentage || 0)}%
            </span>
          </div>
        </div>
        <div className="p-3.5 rounded-xl bg-[#121624] border border-[#232b3e] shadow-md flex flex-col justify-between">
          <span className="text-[11px] text-slate-400 font-medium">Confidence Index</span>
          <span className="text-sm font-semibold font-mono text-indigo-300 mt-1">
            {data.confidenceIndex?.replace('(', '· ').replace(')', '') || '94% Connected'}
          </span>
        </div>
      </div>

      {/* 3. READINESS OVERVIEW (HERO GAUGE + RADAR CHART) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Overall Readiness Visual Focus */}
        <div className="bg-[#121624] p-6 rounded-2xl border border-[#232b3e] flex flex-col justify-between shadow-lg">
          <div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Overall Readiness
              </span>
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${getStatusBadge(data.scoreStatus).className}`}>
                {data.scoreStatus}
              </span>
            </div>

            {/* Circular Progress Gauge */}
            <div className="py-6 flex flex-col items-center justify-center">
              <div className="relative inline-flex items-center justify-center w-36 h-36">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
                  <circle
                    cx="60"
                    cy="60"
                    r="48"
                    className="text-[#1a2234]"
                    strokeWidth="10"
                    stroke="currentColor"
                    fill="transparent"
                  />
                  <circle
                    cx="60"
                    cy="60"
                    r="48"
                    className="text-indigo-500 transition-all duration-1000 ease-out"
                    strokeWidth="10"
                    strokeDasharray={2 * Math.PI * 48}
                    strokeDashoffset={2 * Math.PI * 48 * (1 - (data.overallScore || 0) / 100)}
                    strokeLinecap="round"
                    stroke="currentColor"
                    fill="transparent"
                  />
                </svg>
                <div className="absolute flex flex-col items-center justify-center text-center">
                  <span className="text-4xl font-black text-white font-mono tracking-tight">
                    {data.overallScore}%
                  </span>
                  <span className="text-[11px] font-medium text-indigo-300">
                    Readiness
                  </span>
                </div>

                {/* Score Delta Pill - Only displayed when supported by historical data */}
                {data.scoreDelta !== null && data.scoreDelta !== undefined && (
                  <div
                    className={`absolute -bottom-2.5 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold flex items-center gap-1 border shadow ${
                      data.scoreDelta >= 0
                        ? 'bg-emerald-950/90 text-emerald-300 border-emerald-500/40'
                        : 'bg-rose-950/90 text-rose-300 border-rose-500/40'
                    }`}
                  >
                    {data.scoreDelta >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                    <span>{data.scoreDelta >= 0 ? `+${data.scoreDelta}%` : `${data.scoreDelta}%`}</span>
                  </div>
                )}
              </div>

              <p className="mt-5 text-xs font-semibold text-white text-center">
                {data.percentileRank}
              </p>
              <p className="text-[11px] text-slate-400 text-center mt-0.5">
                Calculated across {data.vectorScores?.length || 4} diagnostic vectors
              </p>
            </div>
          </div>

          <div className="pt-3 border-t border-[#232b3e] flex items-center justify-between text-xs text-slate-400">
            <span>Diagnostic Verification</span>
            <span className="text-indigo-400 font-semibold font-mono flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              {data.vectorScores.filter(v => v.hasScore).length} / {data.vectorScores.length} Assessed
            </span>
          </div>
        </div>

        {/* Competency Radar Chart */}
        <div className="lg:col-span-2 bg-[#121624] p-6 rounded-2xl border border-[#232b3e] shadow-lg flex flex-col justify-between">
          <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
            <div>
              <h3 className="font-bold text-white text-base">4-Vector Competency Breakdown</h3>
              <p className="text-xs text-slate-400">Candidate Score vs Target Hiring Benchmark</p>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <span className="inline-flex items-center gap-1.5 text-indigo-400 font-medium">
                <span className="w-2.5 h-2.5 rounded-full bg-indigo-500" /> Candidate
              </span>
              <span className="inline-flex items-center gap-1.5 text-emerald-400 font-medium">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> Benchmark
              </span>
            </div>
          </div>

          <div className="h-64 sm:h-72 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="72%" data={data.radarData} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
                <PolarGrid stroke={chartColors.grid} />
                <PolarAngleAxis
                  dataKey="vector"
                  stroke={chartColors.axis}
                  fontSize={12}
                  tickLine={false}
                  tick={{ fill: chartColors.axis, fontWeight: 500 }}
                />
                <PolarRadiusAxis
                  angle={30}
                  domain={[0, 100]}
                  stroke={chartColors.radius}
                  fontSize={10}
                  tick={{ fill: chartColors.radius }}
                />
                <Radar
                  name="Candidate Score"
                  dataKey="Score"
                  stroke="#6366f1"
                  fill="#6366f1"
                  fillOpacity={0.35}
                  strokeWidth={2}
                />
                <Radar
                  name="Target Benchmark"
                  dataKey="Benchmark"
                  stroke="#10b981"
                  fill="#10b981"
                  fillOpacity={0.12}
                  strokeWidth={2}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const item = payload[0].payload;
                      const score = item.Score;
                      const benchmark = item.Benchmark;
                      const diff = score - benchmark;
                      return (
                        <div className="p-3 bg-[#121624]/95 backdrop-blur-md border border-[#232b3e] rounded-xl shadow-2xl text-xs space-y-1.5 min-w-[170px]">
                          <p className="font-bold text-white text-sm pb-1 border-b border-[#232b3e]">
                            {item.fullName || item.vector}
                          </p>
                          <div className="flex items-center justify-between text-slate-300">
                            <span className="flex items-center gap-1.5">
                              <span className="w-2 h-2 rounded-full bg-indigo-500" />
                              Your Score:
                            </span>
                            <span className="font-mono font-bold text-indigo-300">{score}%</span>
                          </div>
                          <div className="flex items-center justify-between text-slate-300">
                            <span className="flex items-center gap-1.5">
                              <span className="w-2 h-2 rounded-full bg-emerald-500" />
                              Benchmark:
                            </span>
                            <span className="font-mono font-bold text-emerald-400">{benchmark}%</span>
                          </div>
                          <div className="pt-1.5 border-t border-[#232b3e] flex items-center justify-between font-mono text-[11px]">
                            <span className="text-slate-400">Difference:</span>
                            <span className={`font-semibold px-1.5 py-0.5 rounded text-[10px] ${diff >= 0 ? 'bg-emerald-500/15 text-emerald-300' : 'bg-amber-500/15 text-amber-300'}`}>
                              {diff >= 0 ? `+${diff}% Qualified` : `-${Math.abs(diff)}% Gap`}
                            </span>
                          </div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 4. PREPARATION MODULES (CONSISTENT, CLEAN CARDS) */}
      {data.dimensionsSummary && data.dimensionsSummary.length > 0 && (
        <div className="bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-lg">
          <div className="flex items-center justify-between pb-2 border-b border-[#232b3e]">
            <div>
              <h3 className="font-bold text-white text-base">Preparation Modules</h3>
              <p className="text-xs text-slate-400">Connected modules contributing to placement readiness</p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
            {data.dimensionsSummary.map((dim) => {
              const badge = getStatusBadge(dim.status);
              const vector = data.vectorScores?.find(v => v.route === dim.route);
              const target = vector?.target || 80;
              return (
                <div
                  key={dim.id}
                  onClick={() => navigate(dim.route)}
                  className="group p-4 rounded-xl bg-[#0f131d] border border-[#232b3e] hover:border-indigo-500/50 flex flex-col justify-between space-y-3 cursor-pointer transition-all duration-200"
                >
                  <div className="space-y-2.5">
                    <div className="flex items-start justify-between gap-1">
                      <div className="flex items-center gap-2">
                        {getModuleIcon(dim.name)}
                        <span className="font-semibold text-xs text-white group-hover:text-indigo-300 transition-colors">
                          {dim.name}
                        </span>
                      </div>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono border shrink-0 ${badge.className}`}>
                        {badge.label}
                      </span>
                    </div>

                    <div className="flex items-baseline justify-between pt-1">
                      <span className="text-2xl font-bold font-mono text-indigo-400">
                        {dim.score !== null ? `${dim.score}%` : 'N/A'}
                      </span>
                      <span className="text-[11px] text-slate-400 font-mono">
                        Target: {target}%
                      </span>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-[#121624] rounded-full h-1.5 overflow-hidden border border-[#232b3e]">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${dim.score >= target ? 'bg-emerald-500' : 'bg-indigo-500'}`}
                        style={{ width: `${Math.min(100, dim.score || 0)}%` }}
                      />
                    </div>

                    <p className="text-[11px] text-slate-400 leading-snug line-clamp-2">
                      {dim.detail}
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(dim.route);
                    }}
                    className="w-full py-1.5 bg-indigo-600/10 group-hover:bg-indigo-600 text-indigo-300 group-hover:text-white border border-indigo-500/20 group-hover:border-transparent rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-all cursor-pointer"
                  >
                    <span>Audit Module</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* 5. DIAGNOSTIC SCORES & EXPANDABLE RUBRICS */}
      <div className="bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-lg">
        <div className="flex items-center justify-between pb-2 border-b border-[#232b3e]">
          <div>
            <h3 className="font-bold text-white text-base">Diagnostic Scores & Rubrics</h3>
            <p className="text-xs text-slate-400">Expand any category to inspect scoring evidence, rubrics, and next steps</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
          {data.vectorScores.map((vector) => {
            const isExpanded = !!expandedVectors[vector.key];
            const badge = getStatusBadge(vector.status);
            const isProvisional = badge.type === 'provisional';
            return (
              <div
                key={vector.key}
                className="p-4 rounded-xl bg-[#0f131d] border border-[#232b3e] hover:border-indigo-500/30 transition-all space-y-3"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <span className="font-bold text-sm text-white">{vector.name}</span>
                    <span className="block text-[11px] text-slate-400">Weight: {vector.weight}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-base font-bold font-mono text-indigo-400">
                      {vector.hasScore ? `${vector.score}%` : 'N/A'}
                    </span>
                    <span className="block text-[10px] text-slate-400 font-mono">
                      Target: {vector.target}%
                    </span>
                  </div>
                </div>

                {/* Progress bar */}
                <div className="w-full bg-[#121624] rounded-full h-1.5 overflow-hidden border border-[#232b3e]">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      vector.score >= vector.target ? 'bg-emerald-500' : 'bg-indigo-500'
                    }`}
                    style={{ width: `${Math.min(100, vector.score || 0)}%` }}
                  />
                </div>

                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-1.5">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-medium border flex items-center gap-1 ${badge.className}`}>
                      {isProvisional ? <Clock className="w-3 h-3" /> : <CheckCircle2 className="w-3 h-3" />}
                      <span>{badge.label}</span>
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={() => toggleVectorExpand(vector.key)}
                    className="inline-flex items-center gap-1 text-[11px] text-indigo-300 hover:text-indigo-200 cursor-pointer focus:outline-none"
                  >
                    <span>{isExpanded ? 'Hide Details' : 'View Details'}</span>
                    {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </button>
                </div>

                {/* Expandable Details */}
                {isExpanded && (
                  <div className="pt-3 border-t border-[#232b3e] space-y-3 text-xs animate-in fade-in duration-200">
                    <p className="text-slate-300 text-xs leading-relaxed">{vector.reason}</p>

                    {vector.evidence && vector.evidence.length > 0 && (
                      <div className="space-y-1">
                        <span className="text-[10px] font-semibold uppercase text-emerald-400 tracking-wider">
                          Verified Evidence:
                        </span>
                        <ul className="space-y-1">
                          {vector.evidence.map((ev, i) => (
                            <li key={i} className="text-[11px] text-slate-300 flex items-start gap-1.5">
                              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                              <span>{ev}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {vector.rubricDetail && (
                      <div className="p-2.5 rounded-lg bg-[#121624] border border-[#232b3e] text-[11px] text-indigo-300 font-mono">
                        <span className="text-[10px] uppercase text-slate-400 block font-bold">Rubric Formula:</span>
                        {vector.rubricDetail}
                      </div>
                    )}

                    <button
                      type="button"
                      onClick={() => navigate(vector.route)}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 rounded-lg text-xs font-semibold border border-indigo-500/30 transition-colors cursor-pointer"
                    >
                      <span>Audit {vector.name}</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* 6. VERIFIED STRENGTHS & ACTIONABLE READINESS GAPS */}
      {(() => {
        const visibleStrengths = (data.strengths || []).filter(
          (str) => typeof str === 'string' && !str.toLowerCase().includes('cs fundamental') && !str.toLowerCase().includes('fundamental')
        );
        const visiblePriorityGaps = (data.priorityGaps || []).filter(
          (gap) => typeof gap === 'string' && !gap.toLowerCase().includes('cs fundamental') && !gap.toLowerCase().includes('fundamental')
        );

        return (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {/* Verified Strengths */}
            <div className="bg-[#121624] p-6 rounded-2xl border border-emerald-500/20 space-y-3 shadow-lg flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between pb-2 border-b border-[#232b3e]">
                  <h3 className="font-bold text-white text-base flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    Verified Telemetry Strengths
                  </h3>
                  <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono font-medium">
                    {visibleStrengths.length} Assets
                  </span>
                </div>

                <div className="space-y-2 mt-3">
                  {visibleStrengths.length > 0 ? (
                    visibleStrengths.map((str, i) => (
                      <div key={i} className="p-3 rounded-xl bg-[#0f131d] border border-emerald-500/15 flex items-start gap-2.5 text-xs text-slate-200">
                        <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                        <span>{str}</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-xs text-slate-400 italic">Complete module assessments to register verified telemetry strengths.</p>
                  )}
                </div>
              </div>
            </div>

            {/* Actionable Critical Readiness Gaps */}
            <div className="bg-[#121624] p-6 rounded-2xl border border-amber-500/20 space-y-3 shadow-lg flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between pb-2 border-b border-[#232b3e]">
                  <h3 className="font-bold text-white text-base flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-amber-400" />
                    Critical Readiness Gaps
                  </h3>
                  <span className="px-2 py-0.5 rounded text-[10px] bg-amber-500/10 text-amber-400 border border-amber-500/20 font-mono font-medium">
                    {visiblePriorityGaps.length} Blockers
                  </span>
                </div>

                <div className="space-y-2 mt-3">
                  {visiblePriorityGaps.length > 0 ? (
                    visiblePriorityGaps.map((gap, i) => {
                      const action = getGapAction(gap);
                      return (
                        <div
                          key={i}
                          className="p-3 rounded-xl bg-[#0f131d] border border-amber-500/15 flex items-start justify-between gap-3 text-xs text-slate-200"
                        >
                          <div className="flex items-start gap-2.5">
                            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                            <span>{gap}</span>
                          </div>
                          <button
                            type="button"
                            onClick={() => navigate(action.route)}
                            className="shrink-0 px-2.5 py-1 bg-amber-500/15 hover:bg-amber-500/25 text-amber-300 border border-amber-500/30 rounded-lg text-[10px] font-semibold transition-colors flex items-center gap-1 cursor-pointer"
                          >
                            <span>{action.label}</span>
                            <ArrowRight className="w-3 h-3" />
                          </button>
                        </div>
                      );
                    })
                  ) : (
                    <p className="text-xs text-slate-400 italic">No critical blockers detected across current telemetry.</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        );
      })()}

      {/* 7. TARGET-ROLE ALIGNMENT */}
      {data.roleAlignment && (
        <div className="bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-lg">
          <div className="flex items-center justify-between pb-2 border-b border-[#232b3e]">
            <div>
              <h3 className="font-bold text-white text-base flex items-center gap-2">
                <Target className="w-4 h-4 text-indigo-400" />
                Target Role Alignment: {userRole}
              </h3>
              <p className="text-xs text-slate-400">Competencies evaluated against standard hiring bars</p>
            </div>
            <div className="text-right">
              <span className="text-2xl font-bold font-mono text-indigo-400">
                {data.roleAlignment.role_alignment_score ?? 0}%
              </span>
              <p className="text-[10px] text-slate-400">Competency Match</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            {/* Aligned Skills */}
            <div className="p-4 rounded-xl bg-[#0f131d] border border-emerald-500/20 space-y-2">
              <span className="font-bold text-emerald-400 flex items-center gap-1.5">
                <Check className="w-3.5 h-3.5" />
                Aligned Skills ({data.roleAlignment.aligned_skills?.length || 0})
              </span>
              <div className="flex flex-wrap gap-1.5 pt-1">
                {data.roleAlignment.aligned_skills && data.roleAlignment.aligned_skills.length > 0 ? (
                  data.roleAlignment.aligned_skills.map((sk, i) => (
                    <span key={i} className="px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 text-[11px] font-mono">
                      {sk}
                    </span>
                  ))
                ) : (
                  <span className="text-slate-400 italic text-[11px]">No aligned competencies detected yet.</span>
                )}
              </div>
            </div>

            {/* Missing Skills */}
            <div className="p-4 rounded-xl bg-[#0f131d] border border-amber-500/20 space-y-2">
              <span className="font-bold text-amber-400 flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5" />
                Missing Role Skills ({data.roleAlignment.missing_skills?.length || 0})
              </span>
              <div className="flex flex-wrap gap-1.5 pt-1">
                {data.roleAlignment.missing_skills && data.roleAlignment.missing_skills.length > 0 ? (
                  data.roleAlignment.missing_skills.map((sk, i) => (
                    <span key={i} className="px-2.5 py-1 rounded-lg bg-amber-500/10 text-amber-300 border border-amber-500/20 text-[11px] font-mono">
                      {sk}
                    </span>
                  ))
                ) : (
                  <span className="text-emerald-400 text-[11px]">All required primary competencies met.</span>
                )}
              </div>
            </div>
          </div>

          {/* Role-Specific Gaps */}
          {data.roleAlignment.role_specific_gaps && data.roleAlignment.role_specific_gaps.length > 0 && (
            <div className="pt-2 space-y-2">
              <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Key Role Technical Gaps
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {data.roleAlignment.role_specific_gaps.map((gap, i) => (
                  <div key={i} className="p-3 rounded-xl bg-[#0f131d] border border-[#232b3e] text-xs space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-indigo-300">{gap.area}</span>
                      {gap.severity && (
                        <span className={`px-1.5 py-0.5 rounded text-[10px] font-mono ${
                          gap.severity.toLowerCase().includes('high')
                            ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                            : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                        }`}>
                          {gap.severity}
                        </span>
                      )}
                    </div>
                    <p className="text-slate-400 text-[11px] leading-snug">{gap.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 8. ACTIONABLE RECOMMENDATIONS */}
      {data.priorityRemediations && data.priorityRemediations.length > 0 && (
        <div className="bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-lg">
          <div className="flex items-center justify-between pb-2 border-b border-[#232b3e]">
            <div>
              <h3 className="font-bold text-white text-base flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-indigo-400" />
                Recommended Next Steps
              </h3>
              <p className="text-xs text-slate-400">Targeted priority actions to elevate placement readiness</p>
            </div>
            <span className="text-xs text-indigo-400 font-mono font-medium">
              {data.priorityRemediations.length} Recommendations
            </span>
          </div>

          <div className="space-y-2.5">
            {data.priorityRemediations.map((rem, i) => (
              <div
                key={rem.id || i}
                className="p-3.5 rounded-xl bg-[#0f131d] border border-[#232b3e] hover:border-indigo-500/30 flex flex-col sm:flex-row sm:items-center justify-between gap-3 transition-colors"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded bg-indigo-500/15 text-indigo-400 border border-indigo-500/25 font-mono text-[10px] font-bold">
                      {rem.vector}
                    </span>
                    <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                      rem.priority === 'Critical' ? 'bg-rose-500/15 text-rose-300' : 'bg-amber-500/15 text-amber-300'
                    }`}>
                      {rem.priority} Priority
                    </span>
                  </div>
                  <p className="text-xs font-semibold text-white">{rem.title}</p>
                </div>

                <button
                  type="button"
                  onClick={() => navigate(rem.actionRoute)}
                  className="self-start sm:self-center px-3.5 py-1.5 bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer shrink-0"
                >
                  <span>{rem.actionLabel}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 9. BOTTOM AI MENTOR ENTRY */}
      <div className="p-5 sm:p-6 rounded-2xl bg-gradient-to-r from-purple-950/30 via-indigo-950/25 to-[#121624] border border-[#232b3e] shadow-md flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-indigo-400 font-bold text-sm">
            <MessageSquare className="w-4 h-4" />
            <span>Have questions about your diagnostic breakdown?</span>
          </div>
          <p className="text-xs text-slate-300 max-w-xl">
            Ask our AI Mentor to explain your hiring gap analysis for <span className="text-indigo-300 font-semibold">{userRole}</span> and formulate a tactical roadmap.
          </p>
        </div>

        <button
          type="button"
          onClick={() => navigate('/mentor')}
          className="self-start sm:self-center px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 active:scale-95 text-white rounded-xl text-xs font-bold transition-all shadow-md flex items-center gap-2 cursor-pointer shrink-0 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Ask AI Mentor About My Score</span>
          <ArrowUpRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
