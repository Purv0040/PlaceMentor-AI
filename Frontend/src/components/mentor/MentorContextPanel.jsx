import React from 'react';
import { useNavigate } from 'react-router-dom';

export const MentorContextPanel = ({ mentorContext }) => {
  const navigate = useNavigate();

  const activeProblem = {
    title: "Course Schedule II",
    number: "#210",
    difficulty: "Medium",
    description: "Determine valid prerequisite order of n courses, or return empty list if impossible.",
    patterns: ["Topological Sort", "Kahn's BFS", "DAG Verification", "In-degree Array"]
  };

  const navLinks = [
    { label: "View Skill Gaps", route: "/skill-gaps", icon: "radar", badge: "6 Gaps", badgeColor: "text-rose-400 bg-rose-500/10 border-rose-500/20" },
    { label: "Open 90-Day Roadmap", route: "/roadmap", icon: "route", badge: "Day 42", badgeColor: "text-indigo-400 bg-indigo-500/10 border-indigo-500/20" },
    { label: "View Today's Tasks", route: "/tasks", icon: "check_box", badge: "2 Pending", badgeColor: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20" },
    { label: "Review Resume", route: "/resume", icon: "description", badge: "84/100", badgeColor: "text-amber-400 bg-amber-500/10 border-amber-500/20" },
    { label: "Start Mock Interview", route: "/mock-interview", icon: "videocam", badge: "Practice", badgeColor: "text-purple-300 bg-purple-500/10 border-purple-500/20" },
    { label: "Practice Communication", route: "/communication", icon: "mic", badge: "82% Clarity", badgeColor: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20" }
  ];

  return (
    <aside className="xl:col-span-4 flex flex-col gap-4">
      {/* Active Problem & Algorithmic Patterns Card */}
      <div className="flex flex-col p-4 rounded-2xl bg-[#171b26] border border-[#262a35] shadow-lg gap-3">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-mono uppercase tracking-wider text-purple-300 flex items-center gap-1">
            <span className="material-symbols-outlined text-base">code_blocks</span>
            <span>Active Problem Context</span>
          </span>
          <span className="px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 text-[10px] font-mono font-semibold border border-emerald-500/30">
            {activeProblem.difficulty} {activeProblem.number}
          </span>
        </div>
        <div>
          <h3 className="text-sm font-bold text-white">{activeProblem.title}</h3>
          <p className="text-xs text-slate-400 mt-1">{activeProblem.description}</p>
        </div>
        <div className="flex flex-col gap-1.5 pt-1">
          <span className="text-[10px] font-mono text-slate-500">Detected Pattern Signatures:</span>
          <div className="flex flex-wrap gap-1.5">
            {activeProblem.patterns.map((ptn, idx) => (
              <span key={idx} className="px-2 py-0.5 rounded bg-[#1c1f2a] text-slate-300 text-[11px] font-mono border border-[#262a35]">
                {ptn}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Real-Time Code Reviewer Telemetry Card */}
      <div className="flex flex-col p-4 rounded-2xl bg-[#171b26] border border-[#262a35] shadow-lg gap-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <span className="material-symbols-outlined text-indigo-400 text-lg">fact_check</span>
            <span className="text-xs font-bold text-white">Submission Review</span>
          </div>
          <span className="text-[11px] font-mono text-emerald-400 font-bold px-2 py-0.5 rounded bg-[#1c1f2a] border border-emerald-500/30">
            94% Score
          </span>
        </div>

        {/* Circular Metric & Efficiency Rings */}
        <div className="grid grid-cols-2 gap-2">
          <div className="p-2.5 rounded-xl bg-[#1c1f2a] border border-[#262a35] flex flex-col items-center text-center">
            <span className="text-[10px] font-mono text-slate-400">Time Complexity</span>
            <span className="text-xs font-bold font-mono text-emerald-400 mt-1">O(V + E)</span>
            <span className="text-[10px] text-slate-500">Beats 89.2% in C++</span>
          </div>
          <div className="p-2.5 rounded-xl bg-[#1c1f2a] border border-[#262a35] flex flex-col items-center text-center">
            <span className="text-[10px] font-mono text-slate-400">Space Complexity</span>
            <span className="text-xs font-bold font-mono text-indigo-400 mt-1">O(V + E)</span>
            <span className="text-[10px] text-slate-500">Adjacency List</span>
          </div>
        </div>

        {/* Code Quality Health Checklist */}
        <div className="flex flex-col gap-2 text-xs pt-1 border-t border-[#262a35]">
          <div className="flex items-center justify-between text-slate-300">
            <span className="flex items-center gap-1.5 text-[11px]">
              <span className="material-symbols-outlined text-sm text-emerald-400">check_circle</span>
              Disconnected components
            </span>
            <span className="text-[10px] font-mono text-emerald-400 font-medium">PASS</span>
          </div>
          <div className="flex items-center justify-between text-slate-300">
            <span className="flex items-center gap-1.5 text-[11px]">
              <span className="material-symbols-outlined text-sm text-emerald-400">check_circle</span>
              Cycle deadlock safety
            </span>
            <span className="text-[10px] font-mono text-emerald-400 font-medium">PASS</span>
          </div>
          <div className="flex items-center justify-between text-slate-300">
            <span className="flex items-center gap-1.5 text-[11px]">
              <span className="material-symbols-outlined text-sm text-amber-400">warning</span>
              Vector reallocation (Line 24)
            </span>
            <span className="text-[10px] font-mono text-amber-400 font-medium">WARN</span>
          </div>
        </div>
      </div>

      {/* Strategic Navigation Shortcuts Card */}
      <div className="flex flex-col p-4 rounded-2xl bg-[#171b26] border border-[#262a35] shadow-lg gap-2.5">
        <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
          Preparation Quick Links:
        </span>
        <div className="flex flex-col gap-1.5">
          {navLinks.map((link, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => navigate(link.route)}
              className="flex items-center justify-between px-3 py-2 rounded-xl bg-[#1c1f2a] hover:bg-[#262a35] text-slate-200 hover:text-white transition-all text-xs border border-[#262a35]"
            >
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-base text-slate-400">{link.icon}</span>
                <span>{link.label}</span>
              </div>
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${link.badgeColor}`}>
                {link.badge}
              </span>
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
};
