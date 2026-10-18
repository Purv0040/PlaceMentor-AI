import React from 'react';

export const MentorHeader = ({
  isHistoryOpen,
  onToggleHistory,
  activePersona = 'tech',
  onNewChat
}) => {
  const personaLabels = {
    tech: 'Technical & Coding Interviewer',
    dsa: 'DSA & Pattern Tutor',
    story: 'STAR Behavioral Coach',
    strat: 'Placement Strategist'
  };

  return (
    <header className="flex items-center justify-between gap-4 pb-4 border-b border-[#1f2433]">
      {/* Title & Status */}
      <div className="flex items-center gap-3.5">
        {/* Toggle History Sidebar button */}
        <button
          type="button"
          onClick={onToggleHistory}
          className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium border transition-all ${
            isHistoryOpen
              ? 'bg-purple-600/20 text-purple-300 border-purple-500/40 shadow-sm'
              : 'bg-[#141824] hover:bg-[#1b2132] text-slate-300 border-[#232838]'
          }`}
          title="Toggle chat history sidebar"
        >
          <span className="material-symbols-outlined text-base">
            {isHistoryOpen ? 'dock_to_right' : 'history'}
          </span>
          <span className="hidden sm:inline">
            {isHistoryOpen ? 'Hide History' : 'History'}
          </span>
        </button>

        <div className="relative flex items-center justify-center w-10 h-10 md:w-11 md:h-11 rounded-xl bg-purple-500/10 border border-purple-500/25 text-purple-400 shrink-0 shadow-sm">
          <span className="material-symbols-outlined text-xl md:text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>
            psychology
          </span>
          <span className="absolute -top-0.5 -right-0.5 flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-60"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500 border-2 border-[#0f131d]"></span>
          </span>
        </div>
        <div className="flex flex-col">
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-lg md:text-2xl font-bold text-white tracking-tight">
              AI Mentor
            </h1>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              Active
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5 hidden sm:block">
            Unified AI guidance for technical preparation, DSA coding, behavioral interviews, and placement strategy.
          </p>
        </div>
      </div>

      {/* Right Action: New Chat Shortcut */}
      {onNewChat && (
        <button
          type="button"
          onClick={onNewChat}
          className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold shadow-md hover:shadow-purple-500/25 transition-all"
          title="Start fresh chat"
        >
          <span className="material-symbols-outlined text-sm">add</span>
          <span className="hidden sm:inline">New Chat</span>
        </button>
      )}
    </header>
  );
};
