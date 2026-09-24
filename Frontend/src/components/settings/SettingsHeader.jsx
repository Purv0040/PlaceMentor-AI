import React from 'react';

export const SettingsHeader = ({ onSaveAll, onDiscard, isSaved }) => {
  return (
    <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-[#262a35]">
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-2 flex-wrap">
          <div className="w-7 h-7 rounded bg-purple-500/20 border border-purple-500/30 flex items-center justify-center text-purple-300">
            <span className="material-symbols-outlined text-base">settings_suggest</span>
          </div>
          <span className="text-[10px] font-mono text-purple-300 uppercase tracking-widest">
            Engineering Suite · Engine Config
          </span>
          <span className="px-2 py-0.5 rounded bg-[#1c1f2a] border border-[#262a35] text-[10px] font-mono text-emerald-400">
            KERNEL v4.2-ACTIVE
          </span>
        </div>

        <h1 className="text-2xl font-bold text-white tracking-tight mt-0.5">
          System & AI Settings
        </h1>
        <p className="text-xs text-slate-400 max-w-2xl">
          Configure your placement targets, AI reasoning parameters, telemetry weights, notification cadence, and account privacy.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-2 shrink-0">
        <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 bg-[#171b26] border border-[#262a35] rounded-xl text-[11px] font-mono text-slate-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>Synced to local engine: <strong className="text-white">0ms delta</strong></span>
        </div>

        <button
          type="button"
          onClick={onDiscard}
          className="px-4 py-2 bg-[#171b26] hover:bg-[#262a35] text-slate-300 hover:text-white rounded-xl text-xs font-medium transition-colors border border-[#262a35]"
        >
          Discard
        </button>

        <button
          type="button"
          onClick={onSaveAll}
          className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl text-xs font-semibold shadow-md hover:opacity-90 transition-all"
        >
          <span className="material-symbols-outlined text-base">auto_awesome</span>
          <span>{isSaved ? 'Saved!' : 'Save All Changes'}</span>
        </button>
      </div>
    </div>
  );
};
