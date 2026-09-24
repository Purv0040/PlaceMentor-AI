import React from 'react';

export const ProfileHeader = ({ profile, completionPercent, isEditing, onToggleEdit }) => {
  const name = profile?.name || 'Alex Patel';
  const role = profile?.targetRole || 'Backend Developer';
  const college = profile?.college || 'CSPIT';
  const degree = profile?.degree || 'B.Tech IT';
  const email = profile?.email || 'alex.patel@cspit.ac.in';

  return (
    <div className="p-6 rounded-2xl bg-gradient-to-r from-indigo-950/70 via-[#171b26] to-purple-950/50 border border-[#262a35] shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
      <div className="flex items-center gap-4">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-indigo-600/30 shrink-0">
          {name.split(' ').map(n => n[0]).join('')}
        </div>
        <div className="space-y-1">
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-xl md:text-2xl font-bold text-white">{name}</h1>
            <span className="text-xs font-mono uppercase px-2.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-semibold border border-indigo-500/30">
              {role}
            </span>
          </div>
          <p className="text-xs text-slate-300">
            {college} • {degree} ({profile.graduationYear || '2027'}) • <span className="font-mono text-slate-400">{email}</span>
          </p>
        </div>
      </div>

      <div className="flex items-center gap-4 self-start md:self-auto shrink-0">
        <div className="flex flex-col items-end gap-1">
          <div className="flex items-baseline gap-1">
            <span className="text-xs text-slate-400">Profile Completion:</span>
            <span className="text-sm font-bold font-mono text-emerald-400">{completionPercent}%</span>
          </div>
          <div className="w-32 h-2 rounded-full bg-[#0a0e18] border border-[#232b3e] overflow-hidden">
            <div
              className="h-full rounded-full bg-emerald-400 transition-all duration-500"
              style={{ width: `${completionPercent}%` }}
            />
          </div>
        </div>

        <button
          type="button"
          onClick={onToggleEdit}
          className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all shadow-md ${
            isEditing
              ? 'bg-[#1c1f2a] text-slate-300 border border-[#262a35] hover:text-white'
              : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-600/20'
          }`}
        >
          <span className="material-symbols-outlined text-base">
            {isEditing ? 'close' : 'edit'}
          </span>
          <span>{isEditing ? 'Cancel Edit' : 'Edit Profile'}</span>
        </button>
      </div>
    </div>
  );
};
