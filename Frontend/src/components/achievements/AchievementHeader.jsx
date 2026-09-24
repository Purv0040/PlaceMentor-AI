import React, { useState } from 'react';

export const AchievementHeader = ({ stats, onClaimDailyXp }) => {
  const [claimed, setClaimed] = useState(stats.isDailyClaimed || false);
  const [toastMessage, setToastMessage] = useState(null);

  const handleClaim = () => {
    if (claimed) return;
    const success = onClaimDailyXp();
    if (success) {
      setClaimed(true);
      setToastMessage("Milestone Signal: +50 XP Claimed! 7-Day Streak Active");
      setTimeout(() => setToastMessage(null), 4000);
    }
  };

  return (
    <div className="flex flex-col gap-5">
      {/* Toast Alert Banner */}
      {toastMessage && (
        <div className="fixed top-20 right-6 z-50 flex items-center gap-3 p-4 bg-[#1c1f2a] border border-purple-500/40 rounded-xl shadow-2xl animate-bounce">
          <div className="w-8 h-8 rounded-lg bg-purple-600/30 flex items-center justify-center text-purple-300">
            <span className="material-symbols-outlined text-lg">bolt</span>
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] font-mono uppercase text-purple-300">Milestone Signal</span>
            <span className="text-xs font-semibold text-white">{toastMessage}</span>
          </div>
        </div>
      )}

      {/* Top Header Row */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-[10px] font-mono uppercase tracking-wider text-purple-300 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">
              TELEMETRY V4.2 / ENGAGEMENT ENGINE
            </span>
            <span className="text-slate-600 font-mono text-xs">/</span>
            <span className="text-[11px] font-mono text-emerald-400 flex items-center gap-1 bg-[#171b26] px-2 py-0.5 rounded border border-[#262a35]">
              <span className="material-symbols-outlined text-xs text-amber-400">local_fire_department</span>
              7-Day Active Streak
            </span>
            <span className="text-slate-600 font-mono text-xs">/</span>
            <span className="text-[11px] font-mono text-indigo-300 flex items-center gap-1 bg-[#171b26] px-2 py-0.5 rounded border border-[#262a35]">
              <span className="material-symbols-outlined text-xs">shield</span>
              Level {stats.level}: "{stats.levelTitle}"
            </span>
          </div>

          <h1 className="text-2xl md:text-3xl font-bold text-white tracking-tight mt-1">
            Achievements & Milestones
          </h1>
          <p className="text-xs text-slate-400 max-w-3xl">
            Track technical consistency, unlocked competencies, engineering momentum, and placement readiness thresholds.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button
            type="button"
            onClick={handleClaim}
            disabled={claimed}
            className={`flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-xs font-semibold shadow-md transition-all ${
              claimed
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 cursor-default'
                : 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:opacity-90 hover:scale-[1.02] active:scale-[0.98]'
            }`}
          >
            <span className="material-symbols-outlined text-base">
              {claimed ? 'check_circle' : 'auto_awesome'}
            </span>
            <span>{claimed ? 'Claimed +50 XP' : 'Claim Daily XP (+50 XP)'}</span>
          </button>
        </div>
      </div>

      {/* Hero Level Progression Banner */}
      <div className="relative overflow-hidden bg-[#171b26] border border-[#262a35] rounded-2xl p-5 md:p-6 shadow-xl">
        <div className="absolute -right-16 -top-16 w-80 h-80 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -left-12 -bottom-12 w-64 h-64 bg-indigo-600/10 rounded-full blur-2xl pointer-events-none" />

        <div className="relative z-10 flex flex-col gap-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="relative flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-600 to-indigo-600 text-white shadow-lg shrink-0">
                <span className="material-symbols-outlined text-3xl">military_tech</span>
                <span className="absolute -bottom-1 -right-1 w-5 h-5 rounded-full bg-emerald-400 text-slate-950 font-mono text-[11px] flex items-center justify-center font-bold">
                  {stats.level}
                </span>
              </div>
              <div className="flex flex-col">
                <div className="flex items-center gap-2">
                  <span className="text-base font-bold text-white">Level {stats.level} · {stats.levelTitle}</span>
                  <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded font-medium">
                    Active Tier
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">
                  {stats.xpRemaining} XP remaining to unlock{' '}
                  <span className="text-purple-300 font-medium">Level {stats.level + 1}: Placement Ready SDE</span>
                </p>
              </div>
            </div>

            <div className="flex flex-col md:items-end gap-1">
              <div className="flex items-baseline gap-1">
                <span className="text-xl font-bold font-mono text-white">{stats.earnedXp}</span>
                <span className="text-xs text-slate-400 font-mono">/ {stats.totalXp} XP</span>
              </div>
              <span className="text-[11px] font-mono text-purple-300">
                {stats.unlockedCount} of {stats.totalCount} Achievements Unlocked ({stats.completionPercentage}%)
              </span>
            </div>
          </div>

          {/* Level Progress Bar */}
          <div className="w-full h-3 rounded-full bg-[#0a0e18] border border-[#232b3e] overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-400 transition-all duration-500"
              style={{ width: `${(stats.earnedXp / stats.totalXp) * 100}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
