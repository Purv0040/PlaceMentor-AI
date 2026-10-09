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
  const leetcodeSolved = user?.leetcodeHandle ? (user?.leetcodeSolved || 248) : 0;
  const githubHandle = user?.githubHandle || '';
  const leetcodeHandle = user?.leetcodeHandle || '';

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

  return (
    <div className="dashboard-page w-full max-w-5xl mx-auto space-y-5 sm:space-y-6">
      <div className="flex items-center gap-3 text-xl sm:text-2xl font-bold text-white"><Code2 size={20} /> <span>Dashboard</span></div>

      <Panel className="dashboard-hero flex flex-col md:flex-row md:items-center justify-between gap-5">
        <div>
          <p className="text-xl sm:text-2xl font-extrabold text-white">Good Morning, {displayName} <span aria-hidden="true">👋</span></p>
          <p className="mt-2 text-sm text-slate-300">Your placement readiness is <strong className="text-indigo-400">{readinessScore}%</strong></p>
        </div>
        <NavLink to="/tasks" className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold text-center">Start Today's Plan <ArrowUpRight className="inline ml-1" size={14} /></NavLink>
      </Panel>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <NavLink to="/placement-readiness" className="p-4 rounded-2xl bg-[#121624] border border-[#232b3e] hover:border-indigo-500/40 transition-colors">
          <span className="block text-xs text-slate-400">Readiness</span><strong className="block mt-4 text-center text-xl text-indigo-400">{readinessScore}%</strong>
        </NavLink>
        <NavLink to="/roadmap" className="p-4 rounded-2xl bg-[#121624] border border-[#232b3e] hover:border-indigo-500/40 transition-colors">
          <span className="block text-xs text-slate-400">Sprint Cadence</span><strong className="block mt-4 text-center text-xl text-white">{user?.dailyGoalMinutes || 90} Min/Day</strong>
        </NavLink>
        <NavLink to="/leetcode" className="p-4 rounded-2xl bg-[#121624] border border-[#232b3e] hover:border-purple-500/40 transition-colors">
          <span className="block text-xs text-slate-400">LeetCode</span><strong className="block mt-4 text-center text-xl text-white">{leetcodeHandle ? `@${leetcodeHandle}` : `${leetcodeSolved}`}</strong>
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
          <div className="space-y-4">
            {tasks && tasks.length > 0 ? (
              tasks.slice(0, 3).map((task) => (
                <button
                  type="button"
                  className={`flex items-center gap-3 w-full text-left text-sm ${task.completed ? 'text-slate-500 line-through' : 'text-slate-200'} hover:text-white transition-colors`}
                  key={task.id}
                  onClick={() => toggleTaskCompletion(task.id)}
                >
                  <span className={`w-4 h-4 rounded border flex items-center justify-center shrink-0 ${task.completed ? 'bg-emerald-500/20 border-emerald-500 text-emerald-400' : 'border-slate-600 text-transparent'}`}>
                    <Check size={12} />
                  </span>
                  <span className="truncate">{task.title}</span>
                </button>
              ))
            ) : (
              <p className="text-xs text-slate-400">Loading today's personalized roadmap tasks...</p>
            )}
          </div>
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
        <NavLink className="inline-flex items-center gap-2 px-3 py-2 rounded-xl bg-[#121624] border border-[#232b3e] text-xs text-slate-300 hover:border-amber-500/40" to="/leetcode"><Sparkles size={16} /> LeetCode Analytics {leetcodeHandle ? `(@${leetcodeHandle})` : ''}</NavLink>
      </div>
    </div>
  );
};

