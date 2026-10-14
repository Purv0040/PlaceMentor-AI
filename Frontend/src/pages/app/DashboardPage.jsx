import React, { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  ArrowUpRight,
  Bot,
  Check,
  Code2,
  FileText,
  Github,
  LineChart,
  Sparkles,
  Target
} from 'lucide-react';
import { useUser } from '../../context/UserContext';
import { usePlanning } from '../../context/PlanningContext';
import { readinessService } from '../../services/readinessService';
import { skillGapService } from '../../services/skillGapService';
import { leetcodeService } from '../../services/leetcodeService';

const Panel = ({ children, className = '' }) => (
  <section className={`p-5 sm:p-6 rounded-2xl bg-[#121624] border border-[#232b3e] shadow-xl ${className}`}>{children}</section>
);

const PanelTitle = ({ icon, children, action }) => (
  <div className="flex items-center justify-between gap-4 mb-6">
    <h2 className="flex items-center gap-2 text-base font-bold text-white">{icon}{children}</h2>
    {action}
  </div>
);

export const DashboardPage = () => {
  const { user } = useUser();
  const { tasks, toggleTaskCompletion } = usePlanning();

  const initialScore = user?.overallReadinessScore || 85;
  const [readinessScore, setReadinessScore] = useState(initialScore);
  const [vectorScores, setVectorScores] = useState([]);
  const [aiInsights, setAiInsights] = useState([]);

  const displayName = user?.name || user?.full_name || 'Candidate';
  const targetRole = user?.targetRole || user?.target_role || 'Cybersecurity Analyst & Engineer';
  const companyTier = user?.companyTier || 'Tier-2 Mid-Size & High-Growth';
  const githubHandle = user?.githubHandle || '';
  
  // Real LeetCode profile dynamic state
  const candidateLcHandle = user?.leetcodeHandle || user?.leetcode_username || user?.integrations?.leetcodeHandle || '';
  const [realLcHandle, setRealLcHandle] = useState(() => {
    return candidateLcHandle || localStorage.getItem('placementor_leetcode_handle') || '';
  });
  const [realLcSolved, setRealLcSolved] = useState(user?.leetcodeSolved || 0);

  useEffect(() => {
    let isMounted = true;
    const fetchRealLeetcode = async () => {
      try {
        const res = await leetcodeService.getProfile();
        if (res?.data && isMounted) {
          const profile = res.data;
          const username = profile.username || profile.handle;
          if (username) {
            setRealLcHandle(username);
            localStorage.setItem('placementor_leetcode_handle', username);
          }
          if (typeof profile.total_solved === 'number') {
            setRealLcSolved(profile.total_solved);
          } else if (typeof profile.solved_count === 'number') {
            setRealLcSolved(profile.solved_count);
          }
        }
      } catch (err) {
        console.warn('Failed to load LeetCode profile on dashboard:', err);
      }
    };
    fetchRealLeetcode();
    return () => { isMounted = false; };
  }, [user?.leetcodeHandle, user?.leetcode_username]);

  // Synchronize dynamic vector scores based on 7-step onboarding skills if backend doesn't provide them
  useEffect(() => {
    if (user?.overallReadinessScore) {
      setReadinessScore(user.overallReadinessScore);
    }

    const dsaScore = user?.dsaLevel?.includes('Expert') || user?.dsaLevel?.includes('Master')
      ? 92
      : user?.dsaLevel?.includes('Advanced') || user?.dsaLevel?.includes('Hard')
      ? 86
      : user?.dsaLevel?.includes('Intermediate')
      ? 78
      : 60;

    const sysScore = user?.sysDesignLevel?.includes('Advanced')
      ? 88
      : user?.sysDesignLevel?.includes('Intermediate')
      ? 76
      : 58;

    const domainScore = user?.frameworkLevel?.includes('Advanced')
      ? 88
      : user?.frameworkLevel?.includes('Intermediate')
      ? 78
      : 65;

    const fallbackVectors = [
      { id: 'dsa', vector: 'DSA & Algorithms', score: dsaScore, target: 85, color: '#6366f1' },
      { id: 'domain', vector: `${targetRole.split('&')[0].trim()} Core`, score: domainScore, target: 85, color: '#10b981' },
      { id: 'sysdesign', vector: 'System Design & Architecture', score: sysScore, target: 80, color: '#a855f7' }
    ];

    setVectorScores(fallbackVectors);

    readinessService.getSummary().then((summary) => {
      if (!summary) return;
      if (typeof summary.overall_score === 'number' && summary.overall_score > 0) {
        setReadinessScore(Math.round(summary.overall_score));
      }
      if (summary.vector_scores?.length) {
        setVectorScores(summary.vector_scores.map((vector) => ({
          id: vector.id || vector.vector_id,
          vector: vector.name || vector.vector,
          score: Math.round(vector.score || 0),
          target: vector.target || 85,
          color: vector.color || '#6366f1'
        })));
      }
    });

    // Dynamic AI Mentor insights tailored to the candidate's chosen role & tier
    const primarySkill = (user?.selectedSkills && user.selectedSkills[0]) || 'Core Stack';
    const cleanTier = companyTier.split('(')[0].trim();

    let roleSpecificRec = {
      id: 'ins-1',
      title: `High Priority: ${primarySkill} Core Architecture & Practice`,
      description: `Targeting ${cleanTier} technical benchmark requirements.`,
      route: '/projects'
    };

    if (targetRole.includes('Cybersecurity') || targetRole.includes('Security')) {
      roleSpecificRec = {
        id: 'ins-1',
        title: 'High Priority: OWASP Security Audit & Vulnerability Scanning',
        description: 'Audit REST endpoints for auth vulnerabilities, JWT security, and SIEM logging.',
        route: '/projects'
      };
    } else if (targetRole.includes('AI/ML') || targetRole.includes('Machine Learning')) {
      roleSpecificRec = {
        id: 'ins-1',
        title: 'High Priority: PyTorch Neural Architecture & Model Serving',
        description: 'Implement distributed inference pipelines with sub-100ms latency targets.',
        route: '/projects'
      };
    } else if (targetRole.includes('DevOps') || targetRole.includes('Cloud')) {
      roleSpecificRec = {
        id: 'ins-1',
        title: 'High Priority: Multi-Stage Docker & Terraform IaC Provisioning',
        description: 'Set up automated CI/CD pipeline deployments with zero-downtime rollouts.',
        route: '/projects'
      };
    } else {
      roleSpecificRec = {
        id: 'ins-1',
        title: 'High Priority: Redis Invalidation & Query Indexing',
        description: 'Optimize high-throughput microservices architecture and caching policies.',
        route: '/projects'
      };
    }

    const initialAiInsights = [
      roleSpecificRec,
      {
        id: 'ins-2',
        title: `Calibrate ${user?.dsaLevel || 'Advanced'} DSA for ${cleanTier} Screening`,
        description: 'Master Graph Topological Sort & DP problem sets on LeetCode.',
        route: '/leetcode'
      },
      {
        id: 'ins-3',
        title: `Daily ${user?.dailyGoalMinutes || '90'}-min Cadence for ${user?.targetDrive ? user.targetDrive.split('(')[0].trim() : 'Campus'} Drives`,
        description: 'Active telemetry synced with AI mentor for automated code & resume audits.',
        route: '/skill-gaps'
      }
    ];

    setAiInsights(initialAiInsights);

    skillGapService.getSummary().then((summary) => {
      if (summary?.top_priority_gaps?.length) {
        setAiInsights(summary.top_priority_gaps.slice(0, 3).map((gap, index) => ({
          id: `gap-${index}`,
          title: gap.skill,
          description: gap.reason || gap.suggested_action,
          route: '/skill-gaps'
        })));
      }
    });
  }, [user, targetRole, companyTier]);

  // Compute 5-Week Progress Curve dynamically leading to current score
  const dynamicWeeklyCurve = [
    { week: 'W1', readiness: Math.max(25, readinessScore - 26) },
    { week: 'W2', readiness: Math.max(35, readinessScore - 18) },
    { week: 'W3', readiness: Math.max(48, readinessScore - 12) },
    { week: 'W4', readiness: Math.max(62, readinessScore - 5) },
    { week: 'W5', readiness: readinessScore }
  ];

  const visibleSkills = vectorScores.slice(0, 3);

  // Typewriter effect for "Hello, {displayName} 👋"
  const fullGreeting = `Hello, ${displayName} 👋`;
  const [typedGreeting, setTypedGreeting] = useState('');

  useEffect(() => {
    let currentIndex = 0;
    setTypedGreeting('');
    const interval = setInterval(() => {
      if (currentIndex <= fullGreeting.length) {
        setTypedGreeting(fullGreeting.slice(0, currentIndex));
        currentIndex++;
      } else {
        clearInterval(interval);
      }
    }, 75);

    return () => clearInterval(interval);
  }, [fullGreeting]);

  return (
    <div className="dashboard-page w-full max-w-5xl mx-auto space-y-5 sm:space-y-6">
      <div className="flex items-center gap-3 text-xl sm:text-2xl font-bold text-white"><Code2 size={20} /> <span>Dashboard</span></div>

      <Panel className="dashboard-hero flex flex-col md:flex-row md:items-center justify-between gap-5">
        <div>
          <p className="text-xl sm:text-2xl font-extrabold text-white min-h-[32px] flex items-center">
            <span>{typedGreeting}</span>
            <span className="inline-block w-2 h-5 ml-1 bg-indigo-400 animate-pulse" />
          </p>
          <p className="mt-2 text-sm text-slate-300">Your placement readiness is <strong className="text-indigo-400">{readinessScore}%</strong></p>
        </div>
        <NavLink to="/tasks" className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold text-center">Start Today's Plan <ArrowUpRight className="inline ml-1" size={14} /></NavLink>
      </Panel>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <NavLink to="/placement-readiness" className="p-4 rounded-2xl bg-[#121624] border border-[#232b3e] hover:border-indigo-500/40 transition-colors">
          <span className="block text-xs text-slate-400">Readiness</span><strong className="block mt-4 text-center text-xl text-indigo-400">{readinessScore}%</strong>
        </NavLink>
        <NavLink to="/roadmap" className="p-4 rounded-2xl bg-[#121624] border border-[#232b3e] hover:border-indigo-500/40 transition-colors group">
          <div className="flex items-center justify-between">
            <span className="block text-xs text-slate-400">Sprint Cadence</span>
            <span className="text-[10px] text-indigo-400/80 bg-indigo-500/10 px-1.5 py-0.5 rounded font-mono">
              {user?.studyCadence ? user.studyCadence.split(' ')[0] : 'Daily'}
            </span>
          </div>
          <strong className="block mt-4 text-center text-xl text-white">
            {user?.dailyGoalMinutes || user?.preferences?.dailyGoalMinutes || 90} Min/Day
          </strong>
        </NavLink>
        <NavLink to="/leetcode" className="p-4 rounded-2xl bg-[#121624] border border-[#232b3e] hover:border-purple-500/40 transition-colors group">
          <div className="flex items-center justify-between">
            <span className="block text-xs text-slate-400">LeetCode</span>
            <span className={`inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded font-medium ${
              realLcHandle ? 'text-emerald-400 bg-emerald-500/10' : 'text-amber-400 bg-amber-500/10'
            }`}>
              <span className={`w-1.5 h-1.5 rounded-full ${realLcHandle ? 'bg-emerald-400' : 'bg-amber-400'}`} />
              {realLcHandle ? 'Linked' : 'Unlinked'}
            </span>
          </div>
          <strong className="block mt-4 text-center text-xl text-white truncate" title={realLcHandle ? `@${realLcHandle}` : 'Click to link profile'}>
            {realLcHandle ? `@${realLcHandle}` : (realLcSolved > 0 ? `${realLcSolved} Solved` : 'Connect')}
          </strong>
        </NavLink>
        <NavLink to="/profile" className="p-4 rounded-2xl bg-[#121624] border border-[#232b3e] hover:border-emerald-500/40 transition-colors">
          <span className="block text-xs text-slate-400">Target Role</span><strong className="block mt-4 text-center text-sm text-white truncate" title={targetRole}>{targetRole}</strong>
        </NavLink>
      </div>

      <div className="grid lg:grid-cols-3 items-stretch gap-5 sm:gap-6">
        <Panel className="terminal-progress-panel h-full">
          <PanelTitle
            icon={<LineChart size={16} className="text-indigo-400" />}
            action={<NavLink className="text-xs text-indigo-400 hover:underline" to="/placement-readiness">View Details →</NavLink>}
          >
            Your Progress
          </PanelTitle>
          <div className="h-40 flex items-end gap-3 border-b border-[#232b3e]" aria-label="Five-week progress chart">
            {dynamicWeeklyCurve.map((week) => (
              <div className="flex-1 h-full flex flex-col justify-end items-center gap-2 text-[10px] text-slate-500" key={week.week}>
                <div className="w-full max-w-10 bg-indigo-500 rounded-t transition-all duration-500" style={{ height: `${Math.max(18, week.readiness)}%` }} />
                <span className="pb-2">{week.week}</span>
              </div>
            ))}
          </div>
          <p className="flex items-center gap-2 mt-5 text-sm text-slate-300"><LineChart size={16} /> 5-Week Progress ({readinessScore}% Baseline)</p>
        </Panel>

        <Panel className="lg:col-span-2 h-full">
          <PanelTitle action={<NavLink className="text-xs text-indigo-400 hover:underline" to="/tasks">View All →</NavLink>}>Today's Action Plan</PanelTitle>
          <div className="space-y-3">
            {tasks && tasks.length > 0 ? (
              tasks.slice(0, 3).map((task) => (
                <button
                  type="button"
                  key={task.id}
                  onClick={() => toggleTaskCompletion(task.id)}
                  className={`group flex items-start gap-3 w-full text-left rounded-xl p-3 border transition-all duration-200 ${
                    task.completed
                      ? 'bg-emerald-500/5 border-emerald-500/20 hover:border-emerald-500/40'
                      : 'bg-[#0f131d] border-[#232b3e] hover:border-indigo-500/40 hover:bg-indigo-500/5'
                  }`}
                >
                  <span className={`mt-0.5 w-5 h-5 rounded-md border flex items-center justify-center shrink-0 transition-colors ${
                    task.completed
                      ? 'bg-emerald-500/20 border-emerald-500 text-emerald-400'
                      : 'border-slate-600 text-transparent group-hover:border-indigo-400'
                  }`}>
                    <Check size={12} />
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className={`text-sm font-medium leading-snug ${task.completed ? 'line-through text-slate-500' : 'text-slate-200'}`}>
                      {task.title}
                    </p>
                    {task.category && (
                      <span className="inline-block mt-1 text-[10px] px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-400 font-medium">
                        {task.category}
                      </span>
                    )}
                  </div>
                  {task.duration && (
                    <span className="shrink-0 text-[10px] text-slate-500 mt-0.5 whitespace-nowrap">{task.duration}</span>
                  )}
                </button>
              ))
            ) : (
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="flex items-start gap-3 p-3 rounded-xl bg-[#0f131d] border border-[#232b3e] animate-pulse">
                    <div className="mt-0.5 w-5 h-5 rounded-md bg-slate-700 shrink-0" />
                    <div className="flex-1 space-y-2">
                      <div className="h-3.5 rounded bg-slate-700 w-full" />
                      <div className="h-3.5 rounded bg-slate-800 w-3/4" />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          {tasks && tasks.length > 3 && (
            <p className="mt-4 text-[11px] text-slate-500">
              +{tasks.length - 3} more tasks — <NavLink to="/tasks" className="text-indigo-400 hover:underline">view all</NavLink>
            </p>
          )}
        </Panel>
      </div>

      <div className="grid lg:grid-cols-2 items-stretch gap-5 sm:gap-6">
        <Panel className="h-full">
          <PanelTitle
            icon={<Target size={20} />}
            action={<NavLink className="text-xs text-indigo-400 hover:underline" to="/skill-gaps">View Full Analysis →</NavLink>}
          >
            Skills to Improve
          </PanelTitle>
          <div className="space-y-4">
            {visibleSkills.map((skill) => (
              <div className="grid grid-cols-[1fr_110px_42px] items-center gap-3 text-xs" key={skill.id}>
                <span className="text-slate-300 truncate">{skill.vector.replace(/ &.*$/, '')}</span>
                <div className="h-2 rounded-full bg-[#0f131d] overflow-hidden"><i className="block h-full bg-indigo-500 rounded-full" style={{ width: `${Math.min(100, skill.score)}%` }} /></div>
                <strong className="text-indigo-400">{skill.score}%</strong>
              </div>
            ))}
          </div>
        </Panel>

        <Panel className="h-full">
          <PanelTitle icon={<Bot size={16} className="text-purple-400" />}>AI Mentor</PanelTitle>
          <div className="space-y-4">
            {aiInsights.slice(0, 3).map((insight) => (
              <NavLink className="block text-sm text-slate-200 hover:text-purple-400 transition-colors" to={insight.route} key={insight.id}>
                <p className="font-semibold">{insight.title}</p>
                <p className="text-xs text-slate-400 truncate mt-0.5">{insight.description}</p>
              </NavLink>
            ))}
          </div>
          <NavLink className="inline-flex items-center gap-1 mt-6 text-xs text-indigo-400 hover:underline" to="/mentor">View All <ArrowUpRight size={15} /></NavLink>
        </Panel>
      </div>

      <div className="flex flex-wrap gap-3">
        <NavLink className="inline-flex items-center gap-2 px-3 py-2 rounded-xl bg-[#121624] border border-[#232b3e] text-xs text-slate-300 hover:border-indigo-500/40" to="/resume"><FileText size={16} /> Resume Audit</NavLink>
        <NavLink className="inline-flex items-center gap-2 px-3 py-2 rounded-xl bg-[#121624] border border-[#232b3e] text-xs text-slate-300 hover:border-slate-400" to="/github"><Github size={16} /> GitHub Sync {githubHandle ? `(@${githubHandle})` : ''}</NavLink>
        <NavLink className="inline-flex items-center gap-2 px-3 py-2 rounded-xl bg-[#121624] border border-[#232b3e] text-xs text-slate-300 hover:border-amber-500/40" to="/leetcode"><Sparkles size={16} /> LeetCode Analytics {realLcHandle ? `(@${realLcHandle})` : ''}</NavLink>
      </div>
    </div>
  );
};

