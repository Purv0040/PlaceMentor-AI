import React from 'react';

export const MentorHeader = () => {
  return (
    <header className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-[#1f2433]">
      {/* Title & Status */}
      <div className="flex items-center gap-3.5">
        <div className="relative flex items-center justify-center w-11 h-11 rounded-xl bg-purple-500/10 border border-purple-500/25 text-purple-400 shrink-0 shadow-sm">
          <span className="material-symbols-outlined text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>
            psychology
          </span>
          <span className="absolute -top-0.5 -right-0.5 flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-60"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500 border-2 border-[#0f131d]"></span>
          </span>
        </div>
        <div className="flex flex-col">
          <div className="flex items-center gap-2.5 flex-wrap">
            <h1 className="text-xl md:text-2xl font-bold text-white tracking-tight">
              AI Mentor
            </h1>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              Active
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Unified AI guidance for technical preparation, DSA coding, behavioral interviews, and placement strategy.
          </p>
        </div>
      </div>
    </header>
  );
};
