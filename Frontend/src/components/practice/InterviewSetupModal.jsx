import React, { useState, useEffect } from 'react';
import { X, Play, Sliders, Target, ShieldCheck, Layers, Code2, Award, Clock } from 'lucide-react';
import { useUser } from '../../context/UserContext';

export const InterviewSetupModal = ({ isOpen, onClose, onStartInterview, initialConfig }) => {
  const { user } = useUser();
  const studentTargetRole = user?.targetRole || user?.career?.targetRole || 'Full Stack Engineer';

  const [role, setRole] = useState(studentTargetRole);
  const [modality, setModality] = useState('technical');
  const [difficulty, setDifficulty] = useState('medium');
  const [questionCount, setQuestionCount] = useState(3);

  // Sync state with user profile and initialConfig when opened
  useEffect(() => {
    if (isOpen) {
      setRole(initialConfig?.role || studentTargetRole);
      if (initialConfig?.modality) {
        setModality(initialConfig.modality.toLowerCase().replace(/[^a-z0-9_]/g, '_'));
      }
      if (initialConfig?.difficulty) {
        setDifficulty(initialConfig.difficulty.toLowerCase());
      }
      if (initialConfig?.questionCount) {
        setQuestionCount(initialConfig.questionCount);
      }
    }
  }, [isOpen, initialConfig, studentTargetRole]);

  // Handle ESC key to close
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    onStartInterview({
      role: role.trim() || studentTargetRole,
      modality,
      difficulty,
      questionCount: parseInt(questionCount, 10),
    });
    onClose();
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="setup-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-in fade-in duration-200"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-lg bg-[#121624] border border-[#232b3e] rounded-2xl shadow-2xl overflow-hidden p-5 sm:p-6 space-y-5"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-[#1e2638]">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <Sliders className="w-5 h-5" />
            </div>
            <div>
              <h3 id="setup-modal-title" className="font-semibold text-lg text-white">
                Configure Mock Interview
              </h3>
              <p className="text-xs text-slate-400">
                Personalized role-calibrated technical interview simulation
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-[#1a2133] transition-colors"
            aria-label="Close setup modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Configuration Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Target Role */}
          <div>
            <label htmlFor="target-role-input" className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Target Candidate Role
            </label>
<<<<<<< HEAD
            <select
              value={config.role}
              onChange={(e) => setConfig({ ...config, role: e.target.value })}
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#0b0e17] border border-[#232b3e] text-white text-sm focus:outline-none focus:border-indigo-500 transition-colors"
            >
              <option value="Full Stack Engineer">Full Stack Engineer</option>
              <option value="AI/ML Engineer">AI/ML Engineer</option>
              <option value="AWS / DevOps & Cloud Engineer">AWS / DevOps & Cloud Engineer</option>
              <option value="Cybersecurity Analyst & Engineer">Cybersecurity Analyst & Engineer</option>
              <option value="Backend Developer">Backend Developer</option>
              <option value="Software Engineer">Software Engineer</option>
              <option value="Data Scientist">Data Scientist</option>
            </select>
=======
            <input
              id="target-role-input"
              type="text"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              placeholder="e.g. Full Stack Engineer, Backend SDE, DevOps Engineer"
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#0b0e17] border border-[#232b3e] text-white text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
              required
            />
            <span className="text-[11px] text-slate-500 mt-1 block">
              Pre-filled from your profile. Questions will be grounded in this role&apos;s requirements.
            </span>
>>>>>>> f5f3d0fa4107f7c6729cfe2cb922a1872ad02460
          </div>

          {/* Interview Modality */}
          <div>
            <label htmlFor="modality-select" className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Interview Mode / Category
            </label>
            <select
              id="modality-select"
              value={modality}
              onChange={(e) => setModality(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#0b0e17] border border-[#232b3e] text-white text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
            >
              {role.toLowerCase().includes('devops') || role.toLowerCase().includes('cloud') || role.toLowerCase().includes('aws') ? (
                <>
                  <option value="technical">Cloud & Infrastructure Automation (CI/CD, Docker, K8s, Linux, Terraform)</option>
                  <option value="system_design">Cloud Architecture & Resilience (AWS Multi-Region, High Availability, VPC)</option>
                  <option value="behavioral">Incident & On-Call Leadership (STAR Method, SEV-1 Outages, Post-Mortems)</option>
                  <option value="dsa">Core DSA & Scripting Complexity</option>
                </>
              ) : role.toLowerCase().includes('security') || role.toLowerCase().includes('cyber') ? (
                <>
                  <option value="technical">Threat & Vulnerability Analysis (OWASP, PenTesting, Cryptography)</option>
                  <option value="system_design">Security Architecture & Zero Trust (IAM, PKI, SIEM/SOC)</option>
                  <option value="behavioral">Incident Response & Crisis Management (STAR Method)</option>
                  <option value="dsa">Core DSA & Security Algorithms</option>
                </>
              ) : role.toLowerCase().includes('ai') || role.toLowerCase().includes('ml') ? (
                <>
                  <option value="technical">ML Foundations & Deep Learning (PyTorch, Math, Loss Optimization)</option>
                  <option value="system_design">ML System Design & MLOps (Pipelines, Vector DBs, Low-latency Serving)</option>
                  <option value="behavioral">AI Leadership & Ethics (STAR Method)</option>
                  <option value="dsa">Core DSA & Graph / DP Complexity</option>
                </>
              ) : role.toLowerCase().includes('data') ? (
                <>
                  <option value="technical">Data & SQL / Python Analytics (Aggregations, Pandas, Stats)</option>
                  <option value="system_design">Data Architecture & Pipelines (ETL/ELT, Warehousing, Streaming)</option>
                  <option value="behavioral">Stakeholder & Business Alignment (STAR Method)</option>
                  <option value="dsa">Core DSA & Matrix Traversal</option>
                </>
              ) : (
                <>
                  <option value="technical">Technical Core & Architecture (Role Specific)</option>
                  <option value="system_design">System Architecture & Scalability (Redis, Caching, DB Sharding)</option>
                  <option value="behavioral">Behavioral & Leadership (STAR Method, Crisis & Collaboration)</option>
                  <option value="dsa">Data Structures & Algorithms (Coding / Complexity Analysis)</option>
                </>
              )}
            </select>
          </div>

          {/* Difficulty & Length Row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label htmlFor="difficulty-select" className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Difficulty Level
              </label>
              <select
                id="difficulty-select"
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#0b0e17] border border-[#232b3e] text-white text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
              >
                <option value="easy">Easy (Fundamentals & Core Concepts)</option>
                <option value="medium">Medium (Standard Placement Level)</option>
                <option value="hard">Hard (Tier-1 Scale & Deep Edge Cases)</option>
              </select>
            </div>

            <div>
              <label htmlFor="question-count-select" className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Session Length
              </label>
              <select
                id="question-count-select"
                value={questionCount}
                onChange={(e) => setQuestionCount(parseInt(e.target.value, 10))}
                className="w-full px-3.5 py-2.5 rounded-xl bg-[#0b0e17] border border-[#232b3e] text-white text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
              >
                <option value={1}>1 Question (~5–10 mins quick drill)</option>
                <option value={3}>3 Questions (~15–20 mins standard)</option>
                <option value={5}>5 Questions (~30–45 mins full mock)</option>
              </select>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="pt-4 flex items-center justify-end gap-3 border-t border-[#1e2638]">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-[#1a2133] transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2.5 rounded-xl text-xs sm:text-sm font-semibold bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white transition-all shadow-md shadow-indigo-600/25 flex items-center gap-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <Play className="w-3.5 h-3.5 fill-white" />
              <span>Launch Mock Session</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
