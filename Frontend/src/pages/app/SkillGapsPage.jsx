import React, { useState, useEffect, useMemo, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useUser } from '../../context/UserContext';
import { usePlanning } from '../../context/PlanningContext';
import {
  AVAILABLE_ROLES,
  COMMON_CATEGORIES,
  initialSkillGapData,
  getRoleSkillGapData,
  getCanonicalRoleName
} from '../../data/skillGapData';
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
  BookOpen,
  Briefcase,
  Globe,
  Compass,
  ShieldCheck,
  Zap
} from 'lucide-react';

export const SkillGapsPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, updateUser } = useUser();
  const { roadmap, addSkillToRoadmap } = usePlanning();

  // Derive initial target role strictly from active UserContext or cached session
  const initialRole = getCanonicalRoleName(
    location.state?.targetRole ||
    user?.targetRole ||
    user?.career?.targetRole ||
    (() => {
      try {
        const u = JSON.parse(localStorage.getItem('placementor_user_data') || '{}');
        return u.targetRole;
      } catch (e) { return null; }
    })() ||
    'AI/ML Engineer'
  );

  const [selectedRole, setSelectedRole] = useState(initialRole);
  const [isRoleDropdownOpen, setIsRoleDropdownOpen] = useState(false);
  const roleDropdownRef = useRef(null);

  // Initialize immediately with dynamic role-calibrated data
  const [data, setData] = useState(() => getRoleSkillGapData(selectedRole, user));
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Scope filters for Category Coverage and Skill Gap Audit
  // 'all' | 'role' | 'common'
  const [categoryScopeFilter, setCategoryScopeFilter] = useState('all');
  const [gapScopeFilter, setGapScopeFilter] = useState('all');
  const [activeCategoryFilter, setActiveCategoryFilter] = useState('All');

  const [expandedGapIds, setExpandedGapIds] = useState(new Set());
  const [expandedCategoryIdx, setExpandedCategoryIdx] = useState(null);

  // Close role dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event) {
      if (roleDropdownRef.current && !roleDropdownRef.current.contains(event.target)) {
        setIsRoleDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const loadSkillGaps = async (roleToLoad = selectedRole) => {
    setIsRefreshing(true);
    try {
      const res = await skillGapService.getLatestSkillGaps(roleToLoad, user);
      if (res) setData(res);
    } catch (err) {
      console.error('Error fetching skill gaps:', err);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    loadSkillGaps(selectedRole);
  }, [selectedRole]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      const updated = await skillGapService.analyzeSkillGaps(selectedRole, user);
      if (updated) setData(updated);
    } catch (err) {
      console.error('Error analyzing skill gaps:', err);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleRoleChange = (newRole) => {
    if (newRole === selectedRole) {
      setIsRoleDropdownOpen(false);
      return;
    }
    setSelectedRole(newRole);
    setIsRoleDropdownOpen(false);
    // Instant fallback update for immediate UI responsiveness
    const instantData = getRoleSkillGapData(newRole, user);
    setData(instantData);
    setActiveCategoryFilter('All');
    setExpandedCategoryIdx(null);
    setExpandedGapIds(new Set());
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

  const toggleAllGaps = (currentFilteredList) => {
    if (expandedGapIds.size === currentFilteredList.length && currentFilteredList.length > 0) {
      setExpandedGapIds(new Set());
    } else {
      setExpandedGapIds(new Set(currentFilteredList.map((g) => g.id)));
    }
  };

  // Dynamic helper to extract skills relevant to a specific category
  const getSkillsForCategory = (catName) => {
    if (!catName) return [];
    const cLower = catName.toLowerCase().trim();
    return (data.gaps || []).filter((g) => {
      const gCat = (g.category || '').toLowerCase().trim();
      if (gCat === cLower || gCat.includes(cLower) || cLower.includes(gCat)) return true;
      const words = cLower.split(/[\s&/(),-]+/).filter((w) => w.length > 2);
      return words.some((w) => gCat.includes(w) || (g.skill || '').toLowerCase().includes(w));
    });
  };

  // Filter categories by Scope (All | Role-Specific | Common for All Roles)
  const categoryCoverageList = useMemo(() => {
    const rawList = data.categoryCoverage || [];
    const seen = new Set();
    const unique = [];
    rawList.forEach((c) => {
      const key = (c.category || '').toLowerCase().trim();
      if (key && !seen.has(key)) {
        seen.add(key);
        unique.push(c);
      }
    });
    return unique;
  }, [data.categoryCoverage]);

  const roleCategoriesCount = useMemo(() => {
    return categoryCoverageList.filter((c) => c.scope === 'role').length;
  }, [categoryCoverageList]);

  const commonCategoriesCount = useMemo(() => {
    return categoryCoverageList.filter((c) => c.scope === 'common').length;
  }, [categoryCoverageList]);

  const filteredCategories = useMemo(() => {
    if (categoryScopeFilter === 'role') {
      return categoryCoverageList.filter((c) => c.scope === 'role');
    }
    if (categoryScopeFilter === 'common') {
      return categoryCoverageList.filter((c) => c.scope === 'common');
    }
    return categoryCoverageList;
  }, [categoryCoverageList, categoryScopeFilter]);

  // Multi-Vector Skill Gaps: Filter by Scope and Category
  const allGapsList = data.gaps || [];

  const roleGapsCount = useMemo(() => {
    return allGapsList.filter((g) => g.scope === 'role').length;
  }, [allGapsList]);

  const commonGapsCount = useMemo(() => {
    return allGapsList.filter((g) => g.scope === 'common').length;
  }, [allGapsList]);

  const gapsScopedBySelection = useMemo(() => {
    if (gapScopeFilter === 'role') {
      return allGapsList.filter((g) => g.scope === 'role');
    }
    if (gapScopeFilter === 'common') {
      return allGapsList.filter((g) => g.scope === 'common');
    }
    return allGapsList;
  }, [allGapsList, gapScopeFilter]);

  // Dynamic category pills list for filtering based on scoped gaps
  const categoryFilters = useMemo(() => {
    const cats = new Set(gapsScopedBySelection.map((g) => g.category).filter(Boolean));
    return ['All', ...cats];
  }, [gapsScopedBySelection]);

  useEffect(() => {
    if (activeCategoryFilter !== 'All' && !categoryFilters.includes(activeCategoryFilter)) {
      setActiveCategoryFilter('All');
    }
  }, [categoryFilters, activeCategoryFilter]);

  const finalFilteredGaps = useMemo(() => {
    return gapsScopedBySelection.filter((g) => {
      if (activeCategoryFilter === 'All') return true;
      const cLower = activeCategoryFilter.toLowerCase().trim();
      const gCat = (g.category || '').toLowerCase().trim();
      if (gCat === cLower || gCat.includes(cLower) || cLower.includes(gCat)) return true;
      const words = cLower.split(/[\s&/(),-]+/).filter((w) => w.length > 2);
      return words.some((w) => gCat.includes(w) || (g.skill || '').toLowerCase().includes(w));
    });
  }, [gapsScopedBySelection, activeCategoryFilter]);

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

  const getStatusBadge = (status, coverage, benchmarkTarget = 80) => {
    if (status === 'Benchmark Met' || coverage >= benchmarkTarget) {
      return {
        label: 'Benchmark Met',
        className: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
      };
    }
    if (status === 'In Progress' || coverage >= 40) {
      return {
        label: 'In Progress',
        className: 'bg-indigo-500/15 text-indigo-300 border-indigo-500/30'
      };
    }
    if (status === 'Foundational' || coverage > 0) {
      return {
        label: 'Foundational',
        className: 'bg-amber-500/15 text-amber-300 border-amber-500/30'
      };
    }
    return {
      label: 'Remediation Needed',
      className: 'bg-rose-500/15 text-rose-300 border-rose-500/30'
    };
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto animate-in fade-in duration-300">
      {/* 1. DYNAMIC HEADER WITH INTERACTIVE ROLE SELECTOR */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-[#181d33] via-[#121624] to-[#121624] border border-[#232b3e] shadow-lg">
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-2.5">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">AI Skill Gap Analyzer</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/15 text-indigo-300 border border-indigo-500/30 flex items-center gap-1 font-mono">
              <Sparkles className="w-3 h-3 text-indigo-400" />
              Role-Calibrated
            </span>
          </div>
          <p className="text-xs sm:text-sm text-slate-300 max-w-2xl">
            Evaluate your proficiency against verified hiring benchmarks across <strong className="text-indigo-300">Role-Specific Competencies</strong> and <strong className="text-emerald-300">Universal Placement Core Standards</strong>.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex flex-wrap items-center gap-2.5 self-start md:self-center shrink-0">
          {/* Target Role Selector Dropdown */}
          <div className="relative" ref={roleDropdownRef}>
            <button
              type="button"
              onClick={() => setIsRoleDropdownOpen(!isRoleDropdownOpen)}
              className="inline-flex items-center gap-2 px-3.5 py-2 bg-[#161c2c] hover:bg-[#1f273d] active:scale-95 text-white text-xs sm:text-sm font-semibold rounded-xl border border-indigo-500/40 hover:border-indigo-400 transition-all shadow-md shadow-indigo-900/20 cursor-pointer focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
              title="Switch Target Role to view specialized competencies and benchmarks"
            >
              <Target className="w-3.5 h-3.5 text-indigo-400" />
              <span className="max-w-[160px] truncate">{selectedRole}</span>
              <ChevronDown className={`w-3.5 h-3.5 text-slate-400 transition-transform duration-200 ${isRoleDropdownOpen ? 'rotate-180' : ''}`} />
            </button>

            {/* Dropdown Menu */}
            {isRoleDropdownOpen && (
              <div className="absolute right-0 mt-2 w-64 rounded-xl bg-[#0f131d] border border-[#232b3e] shadow-2xl py-2 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
                <div className="px-3 py-1.5 border-b border-[#232b3e] text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                  Select Canonical Target Role
                </div>
                <div className="max-h-72 overflow-y-auto py-1">
                  {AVAILABLE_ROLES.map((role) => {
                    const isSelected = role === selectedRole;
                    return (
                      <button
                        key={role}
                        type="button"
                        onClick={() => handleRoleChange(role)}
                        className={`w-full text-left px-3.5 py-2 text-xs flex items-center justify-between transition-colors cursor-pointer ${
                          isSelected
                            ? 'bg-indigo-600/20 text-indigo-300 font-semibold border-l-2 border-indigo-500'
                            : 'text-slate-300 hover:bg-[#161c2c] hover:text-white'
                        }`}
                      >
                        <span className="truncate">{role}</span>
                        {isSelected && <Check className="w-3.5 h-3.5 text-indigo-400 shrink-0 ml-2" />}
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          <button
            type="button"
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="inline-flex items-center gap-2 px-3 py-2 bg-[#1a2030] hover:bg-[#232b3e] active:scale-95 text-slate-200 hover:text-white text-xs sm:text-sm font-semibold rounded-xl border border-[#232b3e] transition-all shadow-sm disabled:opacity-50 cursor-pointer focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-indigo-400 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>{isRefreshing ? 'Recalibrating...' : 'Refresh'}</span>
          </button>

          <button
            type="button"
            onClick={() => navigate('/roadmap', { state: { targetRole: selectedRole } })}
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 active:scale-95 text-white text-xs sm:text-sm font-semibold rounded-xl transition-all shadow-md shadow-indigo-600/20 cursor-pointer focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
            title={`Open dynamic ${selectedRole} placement roadmap (${Number(roadmap?.totalDays) || 90} Days)`}
          >
            <span>View Roadmap</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* 2. TARGET PROFILE & CALIBRATION BAR */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 p-3.5 rounded-xl bg-[#121624] border border-[#232b3e] text-xs shadow-md">
        {/* Target Profile Active Selection */}
        <div className="flex items-center justify-between px-3 py-1.5 rounded-lg bg-[#0f131d] border border-[#232b3e]/60">
          <span className="text-[11px] text-slate-400">Target Role</span>
          <span className="text-indigo-300 font-semibold truncate ml-2 font-mono">
            {selectedRole}
          </span>
        </div>

        {/* Competency Scope */}
        <div className="flex items-center justify-between px-3 py-1.5 rounded-lg bg-[#0f131d] border border-[#232b3e]/60">
          <span className="text-[11px] text-slate-400">Audited Scope</span>
          <span className="text-emerald-400 font-semibold truncate ml-2 flex items-center gap-1">
            <ShieldCheck className="w-3 h-3" />
            Role + Core Common
          </span>
        </div>

        {/* Last Calibrated */}
        <div className="flex items-center justify-between px-3 py-1.5 rounded-lg bg-[#0f131d] border border-[#232b3e]/60">
          <span className="text-[11px] text-slate-400">Last Calibrated</span>
          <span className="text-slate-200 font-medium truncate ml-2 font-mono text-[11px]">
            {data.lastCalibrated}
          </span>
        </div>

        {/* Confidence Index with guaranteed percentage */}
        <div className="flex items-center justify-between px-3 py-1.5 rounded-lg bg-[#0f131d] border border-[#232b3e]/60">
          <span className="text-[11px] text-slate-400">Confidence Index</span>
          <span className="text-emerald-400 font-semibold font-mono">
            {typeof data.confidenceIndex === 'number'
              ? `${Math.round(data.confidenceIndex)}%`
              : (String(data.confidenceIndex || '').endsWith('%') ? data.confidenceIndex : `${data.confidenceIndex || 95}%`)}
          </span>
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
              Calibrated against <strong className="text-indigo-300">{selectedRole}</strong> hiring benchmarks
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
              <span className="text-xs font-medium text-slate-400">Audited Skills</span>
            </div>
            <p className="mt-1 text-xs text-slate-400">
              Evaluated across core <strong className="text-indigo-300">{selectedRole}</strong> competencies
            </p>
          </div>
        </div>

        {/* Critical/High Gaps - 100% Mathematically Accurate */}
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
            {(() => {
              const allGaps = data.gaps || [];
              const critCount = allGaps.filter((g) => g.priority === 'Critical').length;
              const highCount = allGaps.filter((g) => g.priority === 'High').length;
              const critHighCount = critCount + highCount;
              const totalGapsCount = allGaps.length || data.gapsIdentifiedCount || 0;

              return (
                <>
                  <div className="flex items-baseline gap-1.5">
                    <span className="text-3xl sm:text-4xl font-extrabold text-amber-300 font-mono">
                      {critHighCount}
                    </span>
                    <span className="text-xs font-medium text-slate-400">
                      Key Gaps (of {totalGapsCount} total)
                    </span>
                  </div>
                  <p className="mt-1 text-xs text-amber-400/90 font-medium">
                    {critHighCount > 0
                      ? 'Requires active roadmap remediation'
                      : 'All high-severity gaps remediated! 🎉'}
                  </p>
                </>
              );
            })()}
          </div>
        </div>
      </div>

      {/* 4. CATEGORY COVERAGE BREAKDOWN WITH PROPER SCOPE TABS */}
      <div className="bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-lg">
        {/* Section Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3 border-b border-[#232b3e]">
          <div>
            <h3 className="font-bold text-white text-base">Category Coverage Breakdown</h3>
            <p className="text-xs text-slate-400">
              Proficiency calibrated for <span className="text-indigo-300 font-medium">{selectedRole}</span> alongside universal placement standards
            </p>
          </div>

          {/* Scope Selector Tabs */}
          <div className="flex items-center p-1 rounded-xl bg-[#0f131d] border border-[#232b3e] text-xs">
            <button
              type="button"
              onClick={() => setCategoryScopeFilter('all')}
              className={`px-3 py-1.5 rounded-lg font-medium transition-all cursor-pointer ${
                categoryScopeFilter === 'all'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              All Categories ({categoryCoverageList.length})
            </button>
            <button
              type="button"
              onClick={() => setCategoryScopeFilter('role')}
              className={`px-3 py-1.5 rounded-lg font-medium transition-all cursor-pointer flex items-center gap-1.5 ${
                categoryScopeFilter === 'role'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <span>🎯 Role-Specific</span>
              <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-indigo-950/60 text-indigo-300 font-mono">
                {roleCategoriesCount}
              </span>
            </button>
            <button
              type="button"
              onClick={() => setCategoryScopeFilter('common')}
              className={`px-3 py-1.5 rounded-lg font-medium transition-all cursor-pointer flex items-center gap-1.5 ${
                categoryScopeFilter === 'common'
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <span>🌐 Common for All Roles</span>
              <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-emerald-950/60 text-emerald-300 font-mono">
                {commonCategoriesCount}
              </span>
            </button>
          </div>
        </div>

        {/* Category Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
          {filteredCategories.map((cat, idx) => {
            const isExpanded = expandedCategoryIdx === idx;
            const relevantSkills = getSkillsForCategory(cat.category);
            const isCommon = cat.scope === 'common' || COMMON_CATEGORIES.has(cat.category);
            const benchmarkTarget = cat.benchmarkTarget || (isCommon ? 80 : 85);
            const cov = Math.max(0, Math.min(100, Number(cat.coverage) || 0));
            const statusBadge = getStatusBadge(cat.status, cov, benchmarkTarget);

            return (
              <div
                key={cat.category || idx}
                className="p-4 rounded-xl bg-[#0f131d] border border-[#232b3e] hover:border-indigo-500/40 transition-colors space-y-3"
              >
                {/* Header: Title, Scope Badge, and Status */}
                <div className="flex items-start justify-between gap-2">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-semibold text-white text-sm">{cat.category}</span>
                      {isCommon ? (
                        <span
                          className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-300 border border-emerald-500/25 flex items-center gap-1"
                          title="Universal placement competency tested in software interviews across all companies"
                        >
                          <Globe className="w-2.5 h-2.5" />
                          Common Core
                        </span>
                      ) : (
                        <span
                          className="px-2 py-0.5 rounded text-[10px] font-semibold bg-indigo-500/10 text-indigo-300 border border-indigo-500/25 flex items-center gap-1"
                          title={`Specialized competency required for ${selectedRole}`}
                        >
                          <Target className="w-2.5 h-2.5" />
                          Role-Specific
                        </span>
                      )}
                    </div>
                    {cat.description && (
                      <p className="text-[11px] text-slate-400 line-clamp-1">{cat.description}</p>
                    )}
                  </div>

                  <div className="flex items-center gap-1.5 shrink-0">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border ${statusBadge.className}`}>
                      {statusBadge.label}
                    </span>
                    <button
                      type="button"
                      onClick={() => setExpandedCategoryIdx(isExpanded ? null : idx)}
                      className="p-1 text-slate-400 hover:text-indigo-300 transition-colors cursor-pointer rounded"
                      title={isExpanded ? 'Hide tracked skills' : 'View tracked skills in this domain'}
                    >
                      {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                </div>

                {/* Coverage Numbers: Current vs Target Benchmark */}
                <div className="flex items-center justify-between text-xs font-mono">
                  <div className="flex items-center gap-1.5">
                    <span className="text-slate-400 text-[11px]">Current:</span>
                    <span className={`font-bold ${cov >= benchmarkTarget ? 'text-emerald-400' : cov > 0 ? 'text-indigo-300' : 'text-slate-400'}`}>
                      {cov}%
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
                    <span>Hiring Benchmark:</span>
                    <span className="text-slate-200 font-semibold">{benchmarkTarget}%</span>
                  </div>
                </div>

                {/* Progress Bar with Benchmark Target Marker Indicator */}
                <div className="relative pt-1">
                  <div className="w-full bg-[#121624] rounded-full h-2.5 overflow-hidden border border-[#232b3e] relative">
                    {/* Progress Fill */}
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{
                        width: `${cov}%`,
                        backgroundColor: cat.color || (isCommon ? '#4edea3' : '#8083ff')
                      }}
                    />
                  </div>
                  {/* Subtle Benchmark Tick Indicator */}
                  <div
                    className="absolute top-0 bottom-0 w-0.5 bg-white/40 pointer-events-none"
                    style={{ left: `${benchmarkTarget}%` }}
                    title={`Target Benchmark: ${benchmarkTarget}%`}
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
                            className={`px-2 py-0.5 rounded text-[11px] font-medium border ${
                              sk.scope === 'common'
                                ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20'
                                : 'bg-indigo-500/10 text-indigo-300 border-indigo-500/20'
                            }`}
                          >
                            {sk.skill} ({sk.currentLevel}/{sk.requiredLevel})
                          </span>
                        ))}
                      </div>
                    ) : (
                      <p className="text-[11px] text-slate-400 italic">
                        No critical priority gaps detected in this domain. Keep practicing roadmap tasks to maintain proficiency.
                      </p>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* 5. MULTI-VECTOR SKILL GAP AUDIT WITH PROPER ROLE & COMMON SCOPE FILTERS */}
      <div className="bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-lg">
        {/* Section Header with Expand All */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3 border-b border-[#232b3e]">
          <div>
            <h3 className="font-bold text-white text-base">Multi-Vector Skill Gap Audit</h3>
            <p className="text-xs text-slate-400">
              Evaluated candidate proficiency vs target benchmark for <span className="text-indigo-300 font-medium">{selectedRole}</span>
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => toggleAllGaps(finalFilteredGaps)}
              className="text-xs text-indigo-300 hover:text-white font-medium px-3 py-1.5 rounded-lg bg-[#0f131d] border border-[#232b3e] hover:border-indigo-500/40 transition-colors cursor-pointer flex items-center gap-1.5"
            >
              {expandedGapIds.size === finalFilteredGaps.length && finalFilteredGaps.length > 0 ? (
                <>
                  <ChevronUp className="w-3.5 h-3.5" />
                  <span>Collapse All</span>
                </>
              ) : (
                <>
                  <ChevronDown className="w-3.5 h-3.5" />
                  <span>Expand All</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Scope Filter Controls: All | Role-Specific | Common Core */}
        <div className="flex flex-wrap items-center gap-2 pt-1 pb-2 border-b border-[#232b3e]/60">
          <span className="text-slate-400 text-xs font-semibold mr-1 flex items-center gap-1">
            <Compass className="w-3.5 h-3.5 text-indigo-400" />
            Audit Scope:
          </span>
          <button
            type="button"
            onClick={() => setGapScopeFilter('all')}
            className={`px-3 py-1.5 rounded-lg font-medium text-xs transition-all cursor-pointer flex items-center gap-1.5 ${
              gapScopeFilter === 'all'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'bg-[#0f131d] text-slate-300 hover:text-white border border-[#232b3e] hover:border-indigo-500/30'
            }`}
          >
            <span>All Audited Skills</span>
            <span className={`text-[10px] px-1.5 py-0.2 rounded-full font-mono font-semibold ${
              gapScopeFilter === 'all' ? 'bg-indigo-700/80 text-white' : 'bg-slate-800 text-slate-400'
            }`}>
              {allGapsList.length}
            </span>
          </button>
          <button
            type="button"
            onClick={() => setGapScopeFilter('role')}
            className={`px-3 py-1.5 rounded-lg font-medium text-xs transition-all cursor-pointer flex items-center gap-1.5 ${
              gapScopeFilter === 'role'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'bg-[#0f131d] text-slate-300 hover:text-white border border-[#232b3e] hover:border-indigo-500/30'
            }`}
          >
            <Target className="w-3 h-3 text-indigo-400" />
            <span>Role-Specific ({selectedRole})</span>
            <span className={`text-[10px] px-1.5 py-0.2 rounded-full font-mono font-semibold ${
              gapScopeFilter === 'role' ? 'bg-indigo-700/80 text-white' : 'bg-slate-800 text-slate-400'
            }`}>
              {roleGapsCount}
            </span>
          </button>
          <button
            type="button"
            onClick={() => setGapScopeFilter('common')}
            className={`px-3 py-1.5 rounded-lg font-medium text-xs transition-all cursor-pointer flex items-center gap-1.5 ${
              gapScopeFilter === 'common'
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'bg-[#0f131d] text-slate-300 hover:text-white border border-[#232b3e] hover:border-emerald-500/30'
            }`}
          >
            <Globe className="w-3 h-3 text-emerald-400" />
            <span>Common for All Roles</span>
            <span className={`text-[10px] px-1.5 py-0.2 rounded-full font-mono font-semibold ${
              gapScopeFilter === 'common' ? 'bg-emerald-700/80 text-white' : 'bg-slate-800 text-slate-400'
            }`}>
              {commonGapsCount}
            </span>
          </button>
        </div>

        {/* Category Sub-Filter Pills */}
        <div className="flex flex-wrap items-center gap-1.5 text-xs">
          <span className="text-slate-400 text-xs font-medium mr-1 flex items-center gap-1">
            <Filter className="w-3.5 h-3.5" />
            Category:
          </span>
          {categoryFilters.map((catName) => {
            const isActive = activeCategoryFilter === catName;
            const count = catName === 'All'
              ? gapsScopedBySelection.length
              : gapsScopedBySelection.filter((g) => {
                  const cLower = catName.toLowerCase().trim();
                  const gCat = (g.category || '').toLowerCase().trim();
                  return gCat === cLower || gCat.includes(cLower) || cLower.includes(gCat);
                }).length;

            return (
              <button
                key={catName}
                type="button"
                onClick={() => setActiveCategoryFilter(catName)}
                className={`px-2.5 py-1 rounded-lg font-medium text-xs transition-all cursor-pointer flex items-center gap-1.5 ${
                  isActive
                    ? 'bg-indigo-600/80 text-white border border-indigo-400/50 shadow-sm'
                    : 'bg-[#0f131d] text-slate-300 hover:text-white border border-[#232b3e] hover:border-indigo-500/30'
                }`}
              >
                <span>{catName}</span>
                <span className={`text-[10px] px-1.5 py-0.2 rounded-full font-mono font-semibold ${
                  isActive ? 'bg-indigo-800 text-white' : 'bg-slate-800 text-slate-400'
                }`}>
                  {count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Skill Gap Cards Grid */}
        <div className="grid grid-cols-1 gap-3.5 pt-2">
          {finalFilteredGaps.length > 0 ? (
            finalFilteredGaps.map((gap) => {
              const isExpanded = expandedGapIds.has(gap.id);
              const badge = getPriorityBadge(gap.priority);
              const isCommon = gap.scope === 'common' || COMMON_CATEGORIES.has(gap.category);
              const currentLvl = Math.max(1, Math.min(5, gap.currentLevel || 1));
              const requiredLvl = Math.max(1, Math.min(5, gap.requiredLevel || 3));
              const levelDelta = Math.max(0, requiredLvl - currentLvl);

              const currentPercent = (currentLvl / 5) * 100;
              const gapPercent = ((requiredLvl - currentLvl) / 5) * 100;

              return (
                <div
                  key={gap.id}
                  onClick={() => toggleGapExpand(gap.id)}
                  className={`p-4 sm:p-5 rounded-xl bg-[#0f131d] border transition-all duration-200 cursor-pointer ${
                    isExpanded ? 'border-indigo-500/50 shadow-md ring-1 ring-indigo-500/20' : 'border-[#232b3e] hover:border-indigo-500/30'
                  }`}
                >
                  {/* Top Bar: Skill Name, Scope Badge, Category, Priority, and Expand Toggle */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
                    <div className="flex flex-wrap items-center gap-2">
                      <h4 className="font-bold text-white text-sm sm:text-base tracking-tight">{gap.skill}</h4>

                      {/* Scope Badge */}
                      {isCommon ? (
                        <span
                          className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-300 border border-emerald-500/25 flex items-center gap-1"
                          title="Universal core competency evaluated across all placement roles"
                        >
                          <Globe className="w-2.5 h-2.5" />
                          Common Core
                        </span>
                      ) : (
                        <span
                          className="px-2 py-0.5 rounded text-[10px] font-semibold bg-indigo-500/10 text-indigo-300 border border-indigo-500/25 flex items-center gap-1"
                          title={`Role-specific competency for ${selectedRole}`}
                        >
                          <Target className="w-2.5 h-2.5" />
                          Role-Specific
                        </span>
                      )}

                      <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-slate-800/80 text-slate-300 border border-[#232b3e]">
                        {gap.category}
                      </span>
                    </div>

                    <div className="flex items-center gap-2 self-start sm:self-auto shrink-0">
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

                  {/* Clean Level Comparison & Progression Bar */}
                  <div className="mt-3.5 space-y-2">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-xs">
                      <div className="flex items-center gap-1.5 text-slate-400">
                        <span>Current:</span>
                        <span className="text-emerald-400 font-semibold">{gap.currentLevelText || `Level ${currentLvl}/5`}</span>
                      </div>

                      <div className="flex items-center gap-2">
                        <span className="text-slate-400">Target Benchmark:</span>
                        <span className="text-indigo-300 font-semibold">{gap.requiredLevelText || `Level ${requiredLvl}/5`}</span>
                        {levelDelta > 0 && (
                          <span className="px-2 py-0.5 rounded-md bg-amber-500/15 text-amber-300 border border-amber-500/30 text-[11px] font-mono font-bold">
                            +{levelDelta} Level Gap
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Sleek Dual-Tone Progress Bar */}
                    <div className="relative pt-0.5">
                      <div className="h-2 w-full bg-[#161c2c] rounded-full overflow-hidden flex border border-[#232b3e]">
                        {/* Acquired / Current level (Emerald) */}
                        <div
                          style={{ width: `${currentPercent}%` }}
                          className="bg-emerald-500 h-full transition-all duration-300"
                          title={`Current proficiency: Level ${currentLvl}/5`}
                        />
                        {/* Gap to bridge (Indigo gradient) */}
                        {levelDelta > 0 && (
                          <div
                            style={{ width: `${gapPercent}%` }}
                            className="bg-gradient-to-r from-indigo-500 to-purple-500 h-full transition-all duration-300"
                            title={`Required gap: +${levelDelta} Level${levelDelta > 1 ? 's' : ''}`}
                          />
                        )}
                      </div>

                      {/* 5-Level Scale Markers */}
                      <div className="flex justify-between px-0.5 pt-1 text-[10px] text-slate-500 font-mono">
                        <span>L1 Novice</span>
                        <span>L2 Basic</span>
                        <span>L3 Intermediate</span>
                        <span>L4 Advanced</span>
                        <span>L5 Expert</span>
                      </div>
                    </div>
                  </div>

                  {/* Expandable Details: Rationale & Action */}
                  {isExpanded && (
                    <div className="mt-3.5 pt-3.5 border-t border-[#232b3e] space-y-3.5 animate-in fade-in duration-200">
                      {gap.reason && (
                        <div className="p-3 rounded-lg bg-[#121624] border-l-2 border-indigo-500 text-xs text-slate-300 leading-relaxed space-y-1">
                          <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider block">
                            Tier-1 Hiring Rationale ({isCommon ? 'Common Placement Standard' : `${selectedRole} Requirement`})
                          </span>
                          <p>{gap.reason}</p>
                        </div>
                      )}

                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1">
                        <div className="flex items-start sm:items-center gap-2 text-xs text-slate-200">
                          <div className="p-1 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shrink-0 mt-0.5 sm:mt-0">
                            <Check className="w-3.5 h-3.5" />
                          </div>
                          <p className="leading-snug">
                            <strong className="text-emerald-400 font-semibold">Recommended Action:</strong>{' '}
                            <span className="text-slate-300">{gap.suggestedAction}</span>
                          </p>
                        </div>

                        {(() => {
                          const isLegacyProject = gap.actionLabel === 'View Projects' || gap.actionRoute === '/projects';
                          const isLegacyLeetcode = (gap.actionLabel && gap.actionLabel.includes('LeetCode')) || gap.actionRoute === '/leetcode';

                          const resolvedLabel = isLegacyProject
                            ? 'Add to Roadmap'
                            : isLegacyLeetcode
                            ? 'Start Practice Tasks'
                            : (gap.actionLabel || 'Add to Roadmap');

                          const resolvedRoute = isLegacyProject
                            ? '/roadmap'
                            : isLegacyLeetcode
                            ? '/tasks'
                            : (gap.actionRoute || '/roadmap');

                          return (
                            <button
                              type="button"
                              onClick={(e) => {
                                e.stopPropagation();
                                addSkillToRoadmap(gap);
                                navigate(resolvedRoute, { state: { targetRole: selectedRole } });
                              }}
                              className="shrink-0 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 active:scale-95 text-white rounded-lg text-xs font-semibold transition-all shadow-md shadow-indigo-600/20 flex items-center justify-center gap-1.5 self-start sm:self-auto cursor-pointer focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                            >
                              <span>{resolvedLabel}</span>
                              <ArrowRight className="w-3.5 h-3.5" />
                            </button>
                          );
                        })()}
                      </div>
                    </div>
                  )}
                </div>
              );
            })
          ) : (
            <div className="p-8 text-center text-xs text-slate-400 italic bg-[#0f131d] rounded-xl border border-[#232b3e]">
              No skill gaps match the selected filter. Try selecting "All Audited Skills" to view all competencies.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
