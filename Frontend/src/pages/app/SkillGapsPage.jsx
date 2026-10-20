import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useUser } from '../../context/UserContext';
import { usePlanning } from '../../context/PlanningContext';
import { initialSkillGapData } from '../../data/skillGapData';
import { skillGapService } from '../../services/skillGapService';
import {
  RefreshCw,
  Target,
  CheckCircle2,
  AlertTriangle,
  ArrowUpRight,
  Layers,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Filter,
  Check,
  Info,
  ArrowRight,
  BookOpen
} from 'lucide-react';

export const SkillGapsPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useUser();
  const { addSkillToRoadmap } = usePlanning();
  const [data, setData] = useState(initialSkillGapData);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [activeCategoryFilter, setActiveCategoryFilter] = useState(() => {
    return location.state?.category || 'All';
  });
  const [expandedGapIds, setExpandedGapIds] = useState(new Set());
  const [expandedCategoryIdx, setExpandedCategoryIdx] = useState(null);

  // Derive target role strictly from active UserContext
  const displayTargetRole = user?.targetRole || user?.career?.targetRole || location.state?.targetRole || 'Full Stack Engineer';

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

  const toggleGapExpand = (id) => {
    setExpandedGapIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const toggleAllGaps = () => {
    if (expandedGapIds.size === filteredGaps.length && filteredGaps.length > 0) {
      setExpandedGapIds(new Set());
    } else {
      setExpandedGapIds(new Set(filteredGaps.map((g) => g.id)));
    }
  };

  // Helper to extract skills relevant to a specific category
  const getSkillsForCategory = (catName) => {
    const cLower = (catName || '').toLowerCase();
    return (data.gaps || []).filter((g) => {
      const gCat = (g.category || '').toLowerCase();
      const gSkill = (g.skill || '').toLowerCase();
      if (cLower.includes('data structure') || cLower.includes('algo')) {
        return gCat.includes('dsa') || gCat.includes('algo') || gSkill.includes('dp') || gSkill.includes('programming');
      }
      if (cLower.includes('backend') || cLower.includes('microservice')) {
        return gCat.includes('backend') || gCat.includes('systems') || gSkill.includes('redis') || gSkill.includes('kafka');
      }
      if (cLower.includes('system design') || cLower.includes('architecture')) {
        return gCat.includes('design') || gCat.includes('architecture') || gCat.includes('communication') || gSkill.includes('system design');
      }
      if (cLower.includes('cloud') || cLower.includes('devops')) {
        return gCat.includes('cloud') || gCat.includes('devops') || gSkill.includes('kubernetes') || gSkill.includes('docker');
      }
      return gCat.includes(cLower) || cLower.includes(gCat);
    });
  };

  // Dynamic category pills list for filtering
  const categoryFilters = ['All', ...new Set((data.categoryCoverage || []).map((c) => c.category))];

  const filteredGaps = (data.gaps || []).filter((g) => {
    if (activeCategoryFilter === 'All') return true;
    const cLower = activeCategoryFilter.toLowerCase();
    const gCat = (g.category || '').toLowerCase();
    const gSkill = (g.skill || '').toLowerCase();
    if (cLower.includes('data structure') || cLower.includes('algo')) {
      return gCat.includes('dsa') || gCat.includes('algo') || gSkill.includes('dp');
    }
    if (cLower.includes('backend') || cLower.includes('microservice')) {
      return gCat.includes('backend') || gCat.includes('systems') || gSkill.includes('redis') || gSkill.includes('kafka');
    }
    if (cLower.includes('system design') || cLower.includes('architecture')) {
      return gCat.includes('design') || gCat.includes('architecture') || gCat.includes('communication');
    }
    if (cLower.includes('cloud') || cLower.includes('devops')) {
      return gCat.includes('cloud') || gCat.includes('devops') || gSkill.includes('kubernetes');
    }
    return gCat.includes(cLower) || cLower.includes(gCat);
  });

  const getPriorityBadge = (priority) => {
    switch (priority) {
      case 'Critical':
        return {
          label: 'Critical Gap',
          className: 'bg-rose-500/10 text-rose-300 border-rose-500/30'
        };
      case 'High':
        return {
          label: 'High Priority',
          className: 'bg-amber-500/10 text-amber-300 border-amber-500/30'
        };
      case 'Medium':
        return {
          label: 'Medium Priority',
          className: 'bg-indigo-500/10 text-indigo-300 border-indigo-500/30'
        };
      default:
        return {
          label: `${priority || 'Standard'} Priority`,
          className: 'bg-slate-500/10 text-slate-300 border-slate-500/30'
        };
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto animate-in fade-in duration-300">
      {/* 1. SIMPLIFIED HEADER */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-[#181d33] via-[#121624] to-[#121624] border border-[#232b3e] shadow-lg">
        <div className="space-y-1.5">
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">AI Skill Gap Analyzer</h1>
          <p className="text-xs sm:text-sm text-slate-300 max-w-2xl">
            Identify priority skill gaps, compare proficiency levels against target role benchmarks, and accelerate your preparation.
          </p>
        </div>

        <div className="flex items-center gap-2.5 self-start md:self-center shrink-0">
          <button
            type="button"
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="inline-flex items-center gap-2 px-3.5 py-2 bg-[#1a2030] hover:bg-[#232b3e] active:scale-95 text-slate-200 hover:text-white text-xs sm:text-sm font-semibold rounded-xl border border-[#232b3e] transition-all shadow-sm disabled:opacity-50 cursor-pointer focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-indigo-400 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>{isRefreshing ? 'Recalibrating...' : 'Refresh Analysis'}</span>
          </button>
          <button
            type="button"
            onClick={() => navigate('/roadmap')}
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 active:scale-95 text-white text-xs sm:text-sm font-semibold rounded-xl transition-all shadow-md shadow-indigo-600/20 cursor-pointer focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
          >
            <span>View 90-Day Roadmap</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* 2. TARGET PROFILE & CALIBRATION BAR */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-3.5 rounded-xl bg-[#121624] border border-[#232b3e] text-xs shadow-md">
        {/* Target Profile - Fixed User Role */}
        <div className="flex items-center justify-between px-3 py-1.5 rounded-lg bg-[#0f131d] border border-[#232b3e]/60">
          <span className="text-[11px] text-slate-400">Target Role</span>
          <span className="text-indigo-300 font-semibold truncate ml-2 max-w-[190px]">
            {displayTargetRole}
          </span>
        </div>

        {/* Last Calibrated */}
        <div className="flex items-center justify-between px-3 py-1.5 rounded-lg bg-[#0f131d] border border-[#232b3e]/60">
          <span className="text-[11px] text-slate-400">Last Calibrated</span>
          <span className="text-slate-200 font-medium truncate ml-2">{data.lastCalibrated}</span>
        </div>

        {/* Confidence Index */}
        <div className="flex items-center justify-between px-3 py-1.5 rounded-lg bg-[#0f131d] border border-[#232b3e]/60">
          <span className="text-[11px] text-slate-400">Confidence Index</span>
          <span className="text-emerald-400 font-semibold font-mono">{data.confidenceIndex}</span>
        </div>
      </div>

      {/* 3. CLEAN SUMMARY CARDS */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Overall Skill Coverage */}
        <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] shadow-md flex flex-col justify-between hover:border-indigo-500/30 transition-colors">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Overall Skill Coverage
            </span>
            <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4">
            <div className="flex items-baseline gap-1.5">
              <span className="text-3xl sm:text-4xl font-extrabold text-white font-mono">{data.overallCoverage}%</span>
            </div>
            <p className="mt-1 text-xs text-slate-400">
              Calibrated against Tier-1 hiring benchmarks
            </p>
          </div>
        </div>

        {/* Skills Audited */}
        <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] shadow-md flex flex-col justify-between hover:border-indigo-500/30 transition-colors">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Skills Audited
            </span>
            <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <Layers className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4">
            <div className="flex items-baseline gap-1.5">
              <span className="text-3xl sm:text-4xl font-extrabold text-white font-mono">{data.totalAudited}</span>
              <span className="text-xs font-medium text-slate-400">Total Skills</span>
            </div>
            <p className="mt-1 text-xs text-slate-400">
              Evaluated across core engineering domains
            </p>
          </div>
        </div>

        {/* Critical/High Gaps */}
        <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] shadow-md flex flex-col justify-between hover:border-amber-500/30 transition-colors">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Critical/High Gaps
            </span>
            <div className="p-2 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4">
            <div className="flex items-baseline gap-1.5">
              <span className="text-3xl sm:text-4xl font-extrabold text-amber-300 font-mono">{data.gapsIdentifiedCount}</span>
              <span className="text-xs font-medium text-slate-400">Key Gaps</span>
            </div>
            <p className="mt-1 text-xs text-amber-400/90 font-medium">
              Requires active roadmap remediation
            </p>
          </div>
        </div>
      </div>

      {/* 4. CATEGORY COVERAGE BREAKDOWN */}
      <div className="bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-lg">
        <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
          <div>
            <h3 className="font-bold text-white text-base">Category Coverage Breakdown</h3>
            <p className="text-xs text-slate-400">Competency distribution calibrated for your target role</p>
          </div>
          <span className="text-xs font-semibold text-indigo-300 px-2.5 py-1 rounded-lg bg-indigo-500/10 border border-indigo-500/20 font-mono">
            Target Role Benchmarks
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
          {(data.categoryCoverage || []).map((cat, idx) => {
            const isExpanded = expandedCategoryIdx === idx;
            const relevantSkills = getSkillsForCategory(cat.category);

            return (
              <div
                key={idx}
                className="p-4 rounded-xl bg-[#0f131d] border border-[#232b3e] hover:border-indigo-500/40 transition-colors space-y-2.5"
              >
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-white">{cat.category}</span>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-indigo-300 font-bold">{cat.coverage}%</span>
                    <button
                      type="button"
                      onClick={() => setExpandedCategoryIdx(isExpanded ? null : idx)}
                      className="text-slate-400 hover:text-indigo-300 transition-colors cursor-pointer"
                      title={isExpanded ? 'Hide tracked skills' : 'View tracked skills in this category'}
                    >
                      {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                </div>

                {/* Consistent Progress Bar */}
                <div className="w-full bg-[#121624] rounded-full h-2 overflow-hidden border border-[#232b3e]">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${Math.min(100, cat.coverage || 0)}%`,
                      backgroundColor: cat.color || '#6366f1'
                    }}
                  />
                </div>

                {/* Category Skill Pills / Expandable Details */}
                {isExpanded && (
                  <div className="pt-2 border-t border-[#232b3e]/60 space-y-2 animate-in fade-in duration-200">
                    <span className="text-[10px] uppercase font-semibold text-slate-400 tracking-wider block">
                      Tracked Skills in {cat.category}:
                    </span>
                    {relevantSkills.length > 0 ? (
                      <div className="flex flex-wrap gap-1.5">
                        {relevantSkills.map((sk) => (
                          <span
                            key={sk.id}
                            className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 text-[11px] font-medium"
                          >
                            {sk.skill} ({sk.currentLevel}/{sk.requiredLevel})
                          </span>
                        ))}
                      </div>
                    ) : (
                      <p className="text-[11px] text-slate-400 italic">No critical priority gaps detected in this domain.</p>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* 5. MULTI-VECTOR SKILL GAP AUDIT */}
      <div className="bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-lg">
        {/* Section Header with Category Filters & Expand All */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3 border-b border-[#232b3e]">
          <div>
            <h3 className="font-bold text-white text-base">Multi-Vector Skill Gap Audit</h3>
            <p className="text-xs text-slate-400">Current proficiency level vs target role benchmark</p>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={toggleAllGaps}
              className="text-xs text-indigo-300 hover:text-indigo-200 font-medium px-2.5 py-1 rounded-lg bg-[#0f131d] border border-[#232b3e] hover:border-indigo-500/40 transition-colors cursor-pointer"
            >
              {expandedGapIds.size === filteredGaps.length && filteredGaps.length > 0
                ? 'Collapse All Details'
                : 'Expand All Details'}
            </button>
          </div>
        </div>

        {/* Category Filter Pills */}
        <div className="flex flex-wrap items-center gap-1.5 text-xs">
          <span className="text-slate-400 text-xs font-medium mr-1 flex items-center gap-1">
            <Filter className="w-3.5 h-3.5" />
            Filter:
          </span>
          {categoryFilters.map((catName) => {
            const isActive = activeCategoryFilter === catName;
            return (
              <button
                key={catName}
                type="button"
                onClick={() => setActiveCategoryFilter(catName)}
                className={`px-3 py-1 rounded-lg font-medium text-xs transition-all cursor-pointer ${
                  isActive
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'bg-[#0f131d] text-slate-300 hover:text-white border border-[#232b3e] hover:border-indigo-500/30'
                }`}
              >
                {catName}
              </button>
            );
          })}
        </div>

        {/* Skill Gap Cards Grid */}
        <div className="grid grid-cols-1 gap-3.5 pt-2">
          {filteredGaps.length > 0 ? (
            filteredGaps.map((gap) => {
              const isExpanded = expandedGapIds.has(gap.id);
              const badge = getPriorityBadge(gap.priority);
              const currentLvl = Math.max(1, Math.min(5, gap.currentLevel || 1));
              const requiredLvl = Math.max(1, Math.min(5, gap.requiredLevel || 3));
              const levelDelta = Math.max(0, requiredLvl - currentLvl);

              return (
                <div
                  key={gap.id}
                  onClick={() => toggleGapExpand(gap.id)}
                  className={`p-4 sm:p-5 rounded-xl bg-[#0f131d] border transition-all duration-200 cursor-pointer ${
                    isExpanded ? 'border-indigo-500/50 shadow-md' : 'border-[#232b3e] hover:border-indigo-500/30'
                  }`}
                >
                  {/* Top Bar: Skill Name, Category, Priority, and Expand Toggle */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
                    <div className="flex flex-wrap items-center gap-2">
                      <h4 className="font-bold text-white text-sm sm:text-base">{gap.skill}</h4>
                      <span className="px-2.5 py-0.5 rounded-md text-[10px] font-mono font-semibold uppercase bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                        {gap.category}
                      </span>
                    </div>

                    <div className="flex items-center gap-2.5 self-start sm:self-auto">
                      <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${badge.className}`}>
                        {badge.label}
                      </span>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleGapExpand(gap.id);
                        }}
                        className="p-1 rounded-md text-slate-400 hover:text-white hover:bg-slate-800/60 transition-colors"
                        title={isExpanded ? 'Collapse' : 'Expand details'}
                      >
                        {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  {/* Proficiency Comparison Bar */}
                  <div className="mt-3.5 p-3 rounded-lg bg-[#121624] border border-[#232b3e] space-y-2">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-xs">
                      <div className="flex items-center gap-2">
                        <span className="text-[11px] text-slate-400">Current:</span>
                        <span className="text-white font-semibold">{gap.currentLevelText || `Level ${currentLvl}/5`}</span>
                      </div>

                      <div className="flex items-center gap-2">
                        <span className="text-[11px] text-indigo-300">Target Required:</span>
                        <span className="text-indigo-300 font-semibold">{gap.requiredLevelText || `Level ${requiredLvl}/5`}</span>
                        {levelDelta > 0 && (
                          <span className="px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-300 border border-amber-500/30 text-[10px] font-mono font-bold">
                            +{levelDelta} Level Gap
                          </span>
                        )}
                      </div>
                    </div>

                    {/* 5-Segment Proficiency Gauge */}
                    <div className="grid grid-cols-5 gap-1.5 pt-0.5">
                      {[1, 2, 3, 4, 5].map((step) => {
                        const isCurrent = step <= currentLvl;
                        const isRequiredGap = step > currentLvl && step <= requiredLvl;

                        return (
                          <div
                            key={step}
                            className={`h-2 rounded-full transition-colors ${
                              isCurrent
                                ? 'bg-emerald-500'
                                : isRequiredGap
                                ? 'bg-indigo-500/60 border border-indigo-400/40'
                                : 'bg-[#1a2234] border border-[#232b3e]'
                            }`}
                            title={`Level ${step}: ${isCurrent ? 'Acquired' : isRequiredGap ? 'Required Proficiency Gap' : 'Target Threshold'}`}
                          />
                        );
                      })}
                    </div>
                  </div>

                  {/* Expandable Details: Rationale & Action */}
                  {isExpanded && (
                    <div className="mt-3.5 pt-3.5 border-t border-[#232b3e] space-y-3 animate-in fade-in duration-200">
                      {gap.reason && (
                        <div className="space-y-1">
                          <span className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider block">
                            Tier-1 Hiring Rationale:
                          </span>
                          <p className="text-xs text-slate-300 leading-relaxed bg-[#121624] p-3 rounded-lg border border-[#232b3e]">
                            {gap.reason}
                          </p>
                        </div>
                      )}

                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1">
                        <div className="flex items-center gap-2 text-xs text-emerald-400">
                          <Check className="w-3.5 h-3.5 shrink-0" />
                          <span><strong>Recommended Action:</strong> {gap.suggestedAction}</span>
                        </div>

                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            if (gap.actionLabel && (gap.actionLabel.includes('Roadmap') || gap.actionLabel.includes('Tasks'))) {
                              addSkillToRoadmap(gap);
                            }
                            navigate(gap.actionRoute || '/roadmap');
                          }}
                          className="shrink-0 px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 active:scale-95 text-white rounded-lg text-xs font-semibold transition-all shadow-sm flex items-center justify-center gap-1.5 self-start sm:self-auto cursor-pointer focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                        >
                          <span>{gap.actionLabel || 'Add to Roadmap'}</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              );
            })
          ) : (
            <div className="p-8 text-center text-xs text-slate-400 italic bg-[#0f131d] rounded-xl border border-[#232b3e]">
              No skill gaps match the selected filter. Try selecting "All" to view all audited competencies.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

