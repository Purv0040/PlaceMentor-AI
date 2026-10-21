import React, { useState } from 'react';
import { X, Play, Sliders, Target, ShieldCheck, Sparkles, BookOpen, Layers } from 'lucide-react';
import { useUser } from '../../context/UserContext';
import { resolveDomainKey } from '../../data/interviewData';

const CANONICAL_ROLES = [
  'AI/ML Engineer',
  'Full Stack Engineer',
  'Frontend Developer',
  'Backend Developer',
  'AWS / DevOps & Cloud Engineer',
  'Data Scientist & AI Engineer',
  'Cybersecurity Analyst & Engineer',
];

const MODALITY_DETAILS = {
  'System Architecture & Design': {
    title: 'High-Level Architecture & Scalability',
    badge: 'Architecture & Scale',
  },
  'Technical / DSA Drill': {
    title: 'Data Structures, Algorithms & Technical Math',
    badge: 'DSA & Coding',
  },
  'Behavioral & HR STAR Drill': {
    title: 'Behavioral & Leadership STAR Scenarios',
    badge: 'Behavioral / STAR',
  },
  'Full Tier-1 SDE Mock': {
    title: 'Full Multi-Round Tier-1 SDE Simulation',
    badge: 'Combined Loop',
  },
};

const getRoleCategoryHighlight = (role, modality) => {
  const normRole = resolveDomainKey(role);
  const normMod = String(modality || '').toLowerCase();

  if (normMod.includes('star') || normMod.includes('behavioral') || normMod.includes('hr')) {
    const map = {
      'AI/ML Engineer': 'Model hallucination triage, ML ethics, GPU cost savings, stakeholder benchmark negotiations.',
      'Full Stack Engineer': 'Production outage resolution, API contract deadlocks, technical debt reduction, mentorship.',
      'Frontend Developer': 'UI re-render crashes, designer performance compromises, framework migrations, web accessibility.',
      'Backend Developer': 'Database migration downtime recovery, scope negotiations, high-load query bottlenecks, legacy rewrites.',
      'AWS / DevOps & Cloud Engineer': 'Multi-AZ cloud outages, DevSecOps compliance friction, cloud FinOps cost reduction, zero-downtime migrations.',
      'Data Scientist & AI Engineer': 'Data leakage triage, metric cannibalization vs executives, Occam’s razor trade-offs, algorithmic bias audits.',
      'Cybersecurity Analyst & Engineer': 'High-pressure incident triage, enforcing MFA/firewalls with developers, executive vulnerability reporting.',
    };
    return map[normRole] || 'STAR structured scenario response (Situation, Task, Action, Quantifiable Result).';
  }

  if (normMod.includes('dsa') || normMod.includes('drill') || normMod.includes('algo') || normMod.includes('tech')) {
    const map = {
      'AI/ML Engineer': 'Transformer attention math, HNSW vector search, Autograd DAG traversal, Im2Col convolution GEMM.',
      'Full Stack Engineer': 'LRU Cache O(1), Sliding Window Deque, DOM tree Lowest Common Ancestor, Topological cycle detection.',
      'Frontend Developer': 'React Fiber reconciler diffing, deep clone with WeakMap cycles, async Promise task queue, custom debounce/throttle.',
      'Backend Developer': 'Thread-safe bounded queues, Top K streaming heap, Event Loop concurrency, B+ Tree index page structures.',
      'AWS / DevOps & Cloud Engineer': 'CIDR bitwise subnetting, IaC dependency DAGs, Token Bucket algorithms, Linux CFS Red-Black Trees.',
      'Data Scientist & AI Engineer': 'Logistic Regression gradient derivation, K-Means++ probabilistic seeding, Reservoir Sampling, Gini Information Gain.',
      'Cybersecurity Analyst & Engineer': 'Count-Min Sketch rate limiting, Aho-Corasick packet payload trie, Fast Modular Exponentiation, Attack graph traversal.',
    };
    return map[normRole] || 'Data structures, algorithms, mathematical proofs, and time/space complexity analysis.';
  }

  if (normMod.includes('full') || normMod.includes('combined') || normMod.includes('tier')) {
    return `Full FAANG-calibrated loop for ${normRole}: Technical / DSA Drill → System Architecture → Behavioral STAR Drill.`;
  }

  // System Architecture & Design
  const map = {
    'AI/ML Engineer': 'RAG 10M doc retrieval, low-latency feature stores (50k rps), 70B LLM 3D parallelism, MLOps canary drift detection.',
    'Full Stack Engineer': 'React SSR/streaming, JWT refresh token rotation with XSS/CSRF defense, WebSocket Redis pub-sub, API Gateways.',
    'Frontend Developer': 'Micro-frontends Module Federation, Core Web Vitals (LCP/INP/CLS), offline-first Service Workers, scalable Design Systems.',
    'Backend Developer': 'Distributed Redis caching & stampede defense, PostgreSQL MVCC isolation, distributed rate limiters, database sharding.',
    'AWS / DevOps & Cloud Engineer': 'Multi-AZ AWS architecture, Kubernetes zero-downtime rolling updates, Terraform multi-env state, Prometheus RED telemetry.',
    'Data Scientist & AI Engineer': 'Data Lakehouse (Iceberg/Delta Lake), Flink streaming fraud analytics, A/B testing CUPED variance reduction, automated retraining.',
    'Cybersecurity Analyst & Engineer': 'Zero Trust architecture (NIST 800-207), MITRE ATT&CK SOC investigation, OWASP BOLA/SSRF defense, TLS 1.3 key exchange.',
  };
  return map[normRole] || 'Distributed systems, database design, caching layers, and high-concurrency trade-offs.';
};

export const InterviewSetupModal = ({ isOpen, onClose, onStartInterview }) => {
  const { user } = useUser();
  const profileRole = user?.targetRole || user?.career?.targetRole || 'AI/ML Engineer';

  const [config, setConfig] = useState({
    role: profileRole,
    modality: 'System Architecture & Design',
    difficulty: 'Medium',
    questionCount: 3,
    duration: '15 mins',
  });

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    onStartInterview({ ...config, role: config.role || profileRole });
    onClose();
  };

  const selectedModalityInfo = MODALITY_DETAILS[config.modality] || MODALITY_DETAILS['System Architecture & Design'];
  const previewHighlights = getRoleCategoryHighlight(config.role, config.modality);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg bg-[#121624] border border-[#232b3e] rounded-2xl shadow-2xl overflow-hidden p-6">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-[#232b3e]">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
              <Sliders className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-lg text-white">Configure Mock Interview Session</h3>
              <p className="text-xs text-slate-400">Adaptive Role & Modality Grounding</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-[#1a2133] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          {/* Role Selector */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Candidate Target Role
              </label>
              {config.role === profileRole && (
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  Active Profile Role
                </span>
              )}
            </div>
            <div className="relative">
              <select
                value={config.role}
                onChange={(e) => setConfig({ ...config, role: e.target.value })}
                className="w-full pl-9 pr-4 py-2.5 rounded-xl bg-[#0b0e17] border border-indigo-500/40 text-white text-sm focus:outline-none focus:border-indigo-400 transition-colors font-medium appearance-none cursor-pointer"
              >
                {CANONICAL_ROLES.map((role) => (
                  <option key={role} value={role} className="bg-[#121624] text-white">
                    {role} {role === profileRole ? '★ (Your Active Target)' : ''}
                  </option>
                ))}
              </select>
              <Target className="w-4 h-4 text-indigo-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>
          </div>

          {/* Modality Selector */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Interview Modality / Category
            </label>
            <select
              value={config.modality}
              onChange={(e) => setConfig({ ...config, modality: e.target.value })}
              className="w-full px-3.5 py-2.5 rounded-xl bg-[#0b0e17] border border-[#232b3e] text-white text-sm focus:outline-none focus:border-indigo-500 transition-colors cursor-pointer"
            >
              <option value="System Architecture & Design">System Architecture & Design</option>
              <option value="Technical / DSA Drill">Technical / DSA Drill</option>
              <option value="Behavioral & HR STAR Drill">Behavioral & HR STAR Drill</option>
              <option value="Full Tier-1 SDE Mock">Full Tier-1 SDE Mock (Combined)</option>
            </select>

            {/* Dynamic Modality Guidance Banner with Role Grounding */}
            <div className="mt-2.5 p-3 rounded-xl bg-[#0b0e17] border border-indigo-500/30 flex items-start gap-2.5">
              <Sparkles className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
              <div className="space-y-1 w-full">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-semibold text-white">
                    {selectedModalityInfo.title}
                  </span>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 shrink-0">
                    {selectedModalityInfo.badge}
                  </span>
                </div>
                <p className="text-[11px] text-indigo-200/90 leading-relaxed font-sans">
                  <span className="text-slate-400 font-semibold">Calibrated Focus for {config.role}: </span>
                  {previewHighlights}
                </p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Difficulty
              </label>
              <select
                value={config.difficulty}
                onChange={(e) => setConfig({ ...config, difficulty: e.target.value })}
                className="w-full px-3 py-2 rounded-xl bg-[#0b0e17] border border-[#232b3e] text-white text-sm focus:outline-none focus:border-indigo-500 transition-colors cursor-pointer"
              >
                <option value="Easy">Easy</option>
                <option value="Medium">Medium</option>
                <option value="Hard">Hard</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Questions
              </label>
              <select
                value={config.questionCount}
                onChange={(e) => setConfig({ ...config, questionCount: parseInt(e.target.value) })}
                className="w-full px-3 py-2 rounded-xl bg-[#0b0e17] border border-[#232b3e] text-white text-sm focus:outline-none focus:border-indigo-500 transition-colors cursor-pointer"
              >
                <option value={1}>1 Question</option>
                <option value={3}>3 Questions</option>
                <option value={5}>5 Questions</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Duration
              </label>
              <select
                value={config.duration}
                onChange={(e) => setConfig({ ...config, duration: e.target.value })}
                className="w-full px-3 py-2 rounded-xl bg-[#0b0e17] border border-[#232b3e] text-white text-sm focus:outline-none focus:border-indigo-500 transition-colors cursor-pointer"
              >
                <option value="10 mins">10 mins</option>
                <option value="15 mins">15 mins</option>
                <option value="30 mins">30 mins</option>
              </select>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="pt-4 flex items-center justify-end gap-3 border-t border-[#232b3e]">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-sm font-medium text-slate-400 hover:text-white hover:bg-[#1a2133] transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 rounded-xl text-sm font-semibold bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white transition-all shadow-md shadow-indigo-600/25 flex items-center gap-2 cursor-pointer"
            >
              <Play className="w-4 h-4 fill-white" />
              <span>Launch Mock Session</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
