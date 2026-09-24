import React from 'react';
import { useNavigate } from 'react-router-dom';

export const AchievementCard = ({ achievement }) => {
  const navigate = useNavigate();
  const {
    title,
    description,
    category,
    icon,
    color,
    xp,
    requiredCount,
    currentCount,
    unlocked,
    unlockedAt,
    route,
    actionLabel
  } = achievement;

  const progressPercent = Math.min(Math.round((currentCount / requiredCount) * 100), 100);

  return (
    <div
      className={`p-5 rounded-2xl border transition-all flex flex-col justify-between gap-4 ${
        unlocked
          ? 'bg-[#171b26] border-[#262a35] hover:border-purple-500/40 shadow-lg'
          : 'bg-[#121624]/60 border-[#232b3e]/60 opacity-75 hover:opacity-100'
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div
            className={`w-11 h-11 rounded-xl flex items-center justify-center shrink-0 border ${color}`}
          >
            <span className="material-symbols-outlined text-2xl">{icon || 'emoji_events'}</span>
          </div>
          <div className="space-y-1">
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="font-bold text-sm text-white">{title}</h3>
              {unlocked ? (
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold flex items-center gap-1">
                  <span className="material-symbols-outlined text-xs">check_circle</span> Unlocked
                </span>
              ) : (
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700 font-semibold flex items-center gap-1">
                  <span className="material-symbols-outlined text-xs">lock</span> Locked
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">{description}</p>
          </div>
        </div>
        <span className="text-[11px] font-mono font-bold text-purple-300 px-2 py-0.5 rounded bg-purple-500/10 border border-purple-500/20 shrink-0">
          +{xp} XP
        </span>
      </div>

      <div className="space-y-2 pt-2 border-t border-[#262a35]/60">
        <div className="flex items-center justify-between text-[11px] font-mono">
          <span className="text-slate-400">
            Progress: <strong className="text-white">{currentCount}</strong> / {requiredCount}
          </span>
          <span className="text-slate-400">
            {unlocked ? `Unlocked ${unlockedAt || 'recently'}` : `${progressPercent}% Complete`}
          </span>
        </div>

        <div className="w-full h-1.5 rounded-full bg-[#0a0e18] overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              unlocked ? 'bg-gradient-to-r from-emerald-400 to-indigo-500' : 'bg-indigo-600/60'
            }`}
            style={{ width: `${progressPercent}%` }}
          />
        </div>

        {route && actionLabel && (
          <div className="pt-1 flex justify-end">
            <button
              type="button"
              onClick={() => navigate(route)}
              className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1 transition-colors"
            >
              <span>{actionLabel}</span>
              <span className="material-symbols-outlined text-sm">arrow_forward</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
