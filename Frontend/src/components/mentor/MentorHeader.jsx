import React from 'react';

export const MentorHeader = ({ mentorContext }) => {
  const candidateName = mentorContext?.user?.name || 'Alex Patel';
  const targetRole = mentorContext?.user?.targetRole || 'Backend Developer';
  const solvedCount = mentorContext?.leetcode?.totalSolved || 385;
  const currentDay = mentorContext?.roadmap?.currentDay || 42;

  return (
    <section className="flex flex-col gap-4 pb-5">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        {/* Title and Live Mentor Tag */}
        <div className="flex items-center gap-3.5">
          <div className="relative flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br from-purple-900/50 via-[#1c1f2a] to-indigo-950/60 border border-purple-500/30 shadow-lg shrink-0">
            <span className="material-symbols-outlined text-purple-400 text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>
              psychology
            </span>
            <span className="absolute -bottom-1 -right-1 flex h-3.5 w-3.5 items-center justify-center rounded-full bg-[#0f131d]">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
            </span>
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-2.5 flex-wrap">
              <h1 className="text-xl md:text-2xl font-bold text-white tracking-tight">
                AI Placement Mentor & Copilot
              </h1>
              <span className="text-[11px] font-mono uppercase px-2.5 py-0.5 rounded-full bg-purple-500/20 text-purple-300 font-semibold border border-purple-500/30">
                Tier-1 SDE Engine
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              24/7 Context-aware Senior Staff Engineer AI for DSA verification, System Design, and Interview Stress Control.
            </p>
          </div>
        </div>

        {/* Student Context Banner Chip */}
        <div className="flex items-center gap-3 px-3.5 py-2 rounded-xl bg-[#171b26] border border-[#262a35] shadow-sm self-start lg:self-auto shrink-0">
          <span className="material-symbols-outlined text-indigo-400 text-lg">sync_saved_locally</span>
          <div className="flex flex-col">
            <span className="text-[10px] font-mono uppercase text-slate-400">Active Student Pipeline Context</span>
            <div className="flex items-center gap-2 text-xs flex-wrap">
              <strong className="text-white font-medium">{candidateName}</strong>
              <span className="text-slate-600">/</span>
              <span className="text-emerald-400 font-mono font-medium">{solvedCount} Solved</span>
              <span className="text-slate-600">/</span>
              <span className="text-indigo-400 font-mono font-medium">Roadmap: Day {currentDay}</span>
              <span className="text-slate-600">/</span>
              <span className="text-purple-300 font-medium">Target: {targetRole}</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
