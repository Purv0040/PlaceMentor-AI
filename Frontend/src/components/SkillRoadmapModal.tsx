import React, { useState } from 'react';
import {
  X,
  Clock,
  CheckCircle2,
  BookOpen,
  ArrowLeft,
  Sparkles,
  Target,
  Layers,
  ChevronRight,
  ShieldCheck,
} from 'lucide-react';

export interface RoadmapPhase {
  title: string;
  duration: string;
  items: string[];
}

export interface SkillRoadmapData {
  skillName: string;
  estimatedTime: string;
  overview: string;
  phases: RoadmapPhase[];
  keyOutcome: string;
}

const PRESET_ROADMAPS: Record<string, SkillRoadmapData> = {
  'Docker & Containerized Microservices': {
    skillName: 'Docker & Containerized Microservices',
    estimatedTime: '3 - 4 Weeks (5 hrs/week)',
    overview: 'Containerization is essential for modern web applications to ensure environment parity from local development to production Cloud Run / Kubernetes environments.',
    phases: [
      {
        title: 'Phase 1: Container Core Fundamentals',
        duration: 'Week 1',
        items: [
          'Understand container virtualization vs hypervisor VMs.',
          'Master Dockerfile commands (FROM, RUN, COPY, EXPOSE, ENTRYPOINT).',
          'Learn layer caching techniques and multi-stage builds for lean production images.',
          'Manage local containers, volumes, and network bridges via Docker CLI.',
        ],
      },
      {
        title: 'Phase 2: Multi-Container Orchestration',
        duration: 'Week 2 - 3',
        items: [
          'Compose multi-service architectures using docker-compose.yml.',
          'Connect Node.js API, PostgreSQL database, and Redis cache containers.',
          'Implement health checks, environment variables, and restart policies.',
          'Configure persistent data volume mounts for development live-reloading.',
        ],
      },
      {
        title: 'Phase 3: Production Deployment & CI/CD',
        duration: 'Week 4',
        items: [
          'Push built images to Docker Hub or Google Artifact Registry.',
          'Automate image builds and vulnerabilities scanning with GitHub Actions.',
          'Deploy containerized services to Cloud Run or AWS ECS.',
          'Set up container logging and resource limits (CPU/Memory).',
        ],
      },
    ],
    keyOutcome: 'Containerize a full-stack App (Frontend + Node.js API + DB) and deploy it to Cloud Run via automated GitHub Actions.',
  },
  'System Architecture & Caching (Redis)': {
    skillName: 'System Architecture & Caching (Redis)',
    estimatedTime: '2 - 3 Weeks (4 hrs/week)',
    overview: 'In-memory caching with Redis drastically improves database response times, reduces server load, and allows sub-10ms API performance at scale.',
    phases: [
      {
        title: 'Phase 1: Redis In-Memory Data Structures',
        duration: 'Week 1',
        items: [
          'Understand Redis key-value storage model, memory eviction policies (LRU/LFU).',
          'Practice with Redis data types: Strings, Hashes, Lists, Sets, and Sorted Sets.',
          'Learn Cache-Aside, Write-Through, and Write-Behind caching strategies.',
        ],
      },
      {
        title: 'Phase 2: Express/Node.js Caching Integration',
        duration: 'Week 2',
        items: [
          'Integrate ioredis / node-redis SDK into Express REST endpoints.',
          'Implement Cache-Aside pattern for heavy SQL database queries.',
          'Configure TTL (Time-To-Live) cache invalidation and stale-while-revalidate.',
          'Implement API rate limiting middleware using Redis atomic increments.',
        ],
      },
      {
        title: 'Phase 3: Pub/Sub & Advanced Architecture',
        duration: 'Week 3',
        items: [
          'Build real-time notification brokers using Redis Pub/Sub channels.',
          'Explore Redis Streams for asynchronous event queue processing.',
          'Benchmark DB query latencies before vs. after Redis caching implementation.',
        ],
      },
    ],
    keyOutcome: 'Implement a Redis caching layer for an Express API that cuts heavy database response times from 350ms down to 8ms.',
  },
  'WebSockets & Real-time Data Streaming': {
    skillName: 'WebSockets & Real-time Data Streaming',
    estimatedTime: '2 - 3 Weeks (5 hrs/week)',
    overview: 'Bi-directional real-time communication is crucial for chat applications, live notifications, collaborative canvases, and financial tickers.',
    phases: [
      {
        title: 'Phase 1: HTTP Polling vs. WebSocket Protocol',
        duration: 'Week 1',
        items: [
          'Understand WebSocket handshake protocol (HTTP Upgrade request).',
          'Learn client-server frame communication and socket connection lifecycles.',
          'Implement basic raw WebSockets using Node.js ws module.',
        ],
      },
      {
        title: 'Phase 2: Socket.io Framework & Room Management',
        duration: 'Week 2',
        items: [
          'Set up Socket.io server and React socket hooks.',
          'Handle room join/leave events, broadcast messaging, and socket acknowledgements.',
          'Implement socket authentication via JWT headers.',
          'Handle reconnection attempts, heartbeat pings, and graceful fallbacks.',
        ],
      },
      {
        title: 'Phase 3: Scaling & Real-time Features',
        duration: 'Week 3',
        items: [
          'Build a multi-user collaborative whiteboard or live chat widget.',
          'Scale WebSockets across multiple server instances using Redis Adapter.',
          'Implement optimistic UI updates with server-authoritative reconciliation.',
        ],
      },
    ],
    keyOutcome: 'Build a multi-room live messaging dashboard with real-time user typing indicators and online presence tracking.',
  },
  'Kubernetes Cluster Orchestration': {
    skillName: 'Kubernetes Cluster Orchestration',
    estimatedTime: '4 - 5 Weeks (6 hrs/week)',
    overview: 'Kubernetes is the industry-standard orchestrator for managing auto-scaling, self-healing containerized workloads across cloud clusters.',
    phases: [
      {
        title: 'Phase 1: K8s Core Architecture & Pods',
        duration: 'Week 1 - 2',
        items: [
          'Understand Master Node (API Server, etcd, Scheduler) vs. Worker Nodes.',
          'Write YAML manifests for Pods, Deployments, and ReplicaSets.',
          'Inspect cluster status using kubectl commands (get, describe, logs, exec).',
        ],
      },
      {
        title: 'Phase 2: Networking, Services & Ingress',
        duration: 'Week 3',
        items: [
          'Expose pods internally using ClusterIP and externally using NodePort / LoadBalancer.',
          'Configure NGINX Ingress Controller for path-based SSL routing.',
          'Manage secrets and configuration data with ConfigMaps and K8s Secrets.',
        ],
      },
      {
        title: 'Phase 3: Auto-Scaling & Helm Deployments',
        duration: 'Week 4 - 5',
        items: [
          'Configure Horizontal Pod Autoscaler (HPA) based on CPU/RAM metrics.',
          'Package applications into reusable Helm Charts.',
          'Deploy local multi-node clusters using Minikube or Kind.',
        ],
      },
    ],
    keyOutcome: 'Deploy a multi-microservice application on Minikube with automated CPU horizontal scaling and ingress routing.',
  },
};

// Fallback generator for generic or unlisted skills
export function getOrGenerateRoadmap(skillName: string, reason?: string): SkillRoadmapData {
  if (PRESET_ROADMAPS[skillName]) {
    return PRESET_ROADMAPS[skillName];
  }

  // Generate dynamic 3-phase roadmap for any custom skill
  return {
    skillName,
    estimatedTime: '3 - 4 Weeks (4-5 hrs/week)',
    overview: reason || `Mastering ${skillName} bridges a critical technical competency gap identified in your target domain benchmark.`,
    phases: [
      {
        title: `Phase 1: ${skillName} Theoretical & Core Concepts`,
        duration: 'Week 1',
        items: [
          `Learn foundational architecture, core syntax, and underlying mechanics of ${skillName}.`,
          `Set up local development toolchain and study official documentation.`,
          `Complete 5-10 targeted introductory exercises and code samples.`,
        ],
      },
      {
        title: `Phase 2: Practical Implementation & Lab Projects`,
        duration: 'Week 2 - 3',
        items: [
          `Integrate ${skillName} into a standalone mini-project or REST service.`,
          `Follow industry best practices for error handling, testing, and debugging.`,
          `Implement key features matching standard technical interview expectations.`,
        ],
      },
      {
        title: `Phase 3: Portfolio Integration & Production Prep`,
        duration: 'Week 4',
        items: [
          `Add ${skillName} implementation to your primary GitHub portfolio repository.`,
          `Document architectural choices, API specifications, and setup steps in README.md.`,
          `Prepare answer stories for technical interview scenario questions.`,
        ],
      },
    ],
    keyOutcome: `Build and publish a portfolio project demonstrating hands-on proficiency with ${skillName}.`,
  };
}

interface SkillRoadmapModalProps {
  skill: { skill: string; reason: string } | null;
  onClose: () => void;
  roadmapData: SkillRoadmapData;
}

export const SkillRoadmapModal: React.FC<SkillRoadmapModalProps> = ({
  skill,
  onClose,
  roadmapData,
}) => {
  const [completedItems, setCompletedItems] = useState<Record<string, boolean>>({});

  if (!skill) return null;

  const toggleItem = (key: string) => {
    setCompletedItems((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-200 overflow-y-auto"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] flex flex-col shadow-2xl border border-slate-100 my-auto overflow-hidden animate-in zoom-in-95 duration-200"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="p-5 sm:p-6 bg-slate-900 text-white flex items-start justify-between gap-4 border-b border-slate-800 shrink-0">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-[10px] font-bold uppercase tracking-wider">
                <Sparkles className="w-3 h-3 text-indigo-400" />
                Curated Learning Plan
              </span>
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[10px] font-bold uppercase tracking-wider">
                <Clock className="w-3 h-3 text-amber-400" />
                {roadmapData.estimatedTime}
              </span>
            </div>

            <h2 className="text-lg sm:text-xl font-extrabold text-white tracking-tight pt-1">
              Learning Roadmap: {roadmapData.skillName}
            </h2>
          </div>

          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white rounded-xl hover:bg-slate-800 cursor-pointer transition-colors shrink-0"
            title="Close Roadmap"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Scrollable Body */}
        <div className="p-5 sm:p-6 overflow-y-auto space-y-6 flex-1 text-slate-800 antialiased">
          {/* Overview & Gap Reason Box */}
          <div className="p-4 rounded-xl bg-indigo-50/60 border border-indigo-100 space-y-2">
            <h3 className="text-xs font-bold text-indigo-950 uppercase tracking-wider flex items-center gap-1.5">
              <Target className="w-4 h-4 text-indigo-600" />
              <span>Skill Gap Context & Objective</span>
            </h3>
            <p className="text-xs sm:text-sm text-slate-700 leading-relaxed font-normal">
              {roadmapData.overview}
            </p>
          </div>

          {/* Time Line Banner */}
          <div className="flex items-center justify-between p-3.5 bg-slate-50 rounded-xl border border-slate-200/80">
            <div className="flex items-center gap-2 text-xs text-slate-700">
              <Clock className="w-4 h-4 text-indigo-600 shrink-0" />
              <span className="font-semibold text-slate-900">Estimated Timeline:</span>
              <span className="text-indigo-700 font-bold">{roadmapData.estimatedTime}</span>
            </div>
            <span className="text-[11px] font-medium text-slate-500">3 Structured Phases</span>
          </div>

          {/* Ordered List of Phases */}
          <div className="space-y-6">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2 border-b border-slate-100 pb-2">
              <Layers className="w-4 h-4 text-indigo-600" />
              <span>Step-by-Step Execution Phases</span>
            </h3>

            <div className="space-y-5">
              {roadmapData.phases.map((phase, pIdx) => (
                <div
                  key={pIdx}
                  className="rounded-xl border border-slate-200/90 bg-white p-4 sm:p-5 space-y-3 shadow-2xs relative"
                >
                  {/* Phase Number Header */}
                  <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                    <div className="flex items-center gap-3">
                      <div className="w-7 h-7 rounded-lg bg-indigo-600 text-white flex items-center justify-center text-xs font-bold shadow-xs shrink-0">
                        {pIdx + 1}
                      </div>
                      <h4 className="text-sm font-bold text-slate-900">{phase.title}</h4>
                    </div>

                    <span className="text-[11px] font-semibold text-indigo-600 bg-indigo-50 px-2.5 py-0.5 rounded-full border border-indigo-100">
                      {phase.duration}
                    </span>
                  </div>

                  {/* Phase Items List */}
                  <ul className="space-y-2.5 pt-1">
                    {phase.items.map((item, itemIdx) => {
                      const itemKey = `${pIdx}-${itemIdx}`;
                      const isChecked = !!completedItems[itemKey];

                      return (
                        <li
                          key={itemIdx}
                          onClick={() => toggleItem(itemKey)}
                          className="flex items-start gap-3 text-xs sm:text-sm text-slate-700 leading-relaxed cursor-pointer group p-1.5 rounded-lg hover:bg-slate-50 transition-colors"
                        >
                          <div
                            className={`w-4 h-4 rounded-md border flex items-center justify-center shrink-0 mt-0.5 transition-colors ${
                              isChecked
                                ? 'bg-emerald-600 border-emerald-600 text-white'
                                : 'border-slate-300 group-hover:border-indigo-500 bg-white'
                            }`}
                          >
                            {isChecked && <CheckCircle2 className="w-3.5 h-3.5 stroke-[3]" />}
                          </div>
                          <span className={isChecked ? 'line-through text-slate-400' : ''}>
                            {item}
                          </span>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              ))}
            </div>
          </div>

          {/* Key Outcome Banner */}
          <div className="p-4 rounded-xl bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200/80 flex items-start gap-3">
            <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
            <div>
              <h4 className="text-xs font-bold text-emerald-950 uppercase tracking-wider mb-0.5">
                Target Capstone Milestone
              </h4>
              <p className="text-xs sm:text-sm text-emerald-900 font-medium leading-relaxed">
                {roadmapData.keyOutcome}
              </p>
            </div>
          </div>
        </div>

        {/* Modal Footer with "Back to Report" Button */}
        <div className="p-4 sm:p-5 bg-slate-50 border-t border-slate-200/80 flex items-center justify-between gap-3 shrink-0">
          <div className="text-xs text-slate-500 font-medium">
            Cached in session • Step-by-step roadmap
          </div>

          <button
            onClick={onClose}
            className="inline-flex items-center gap-2 px-4 py-2 text-xs sm:text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-xs cursor-pointer transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Report</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default SkillRoadmapModal;
