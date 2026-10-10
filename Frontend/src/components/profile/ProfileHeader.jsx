import React from 'react';

export const ProfileHeader = ({ profile, completionPercent, isEditing, onToggleEdit }) => {
  const name = profile?.name || 'Student Candidate';
  const role = profile?.targetRole || 'Full Stack Engineer';
  const college = profile?.college || 'University Student';
  const degree = profile?.degree || 'B.Tech / B.E.';
  const branch = profile?.branch || 'Computer Engineering';
  const graduationYear = profile?.graduationYear || '2026';
  const email = profile?.email || '';
  const bio = profile?.bio || '';
  const cgpa = profile?.cgpa;
  const linkedinUrl = profile?.linkedinUrl;
  const portfolioUrl = profile?.portfolioUrl;

  const initials = name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map(n => n[0].toUpperCase())
    .join('') || 'U';

  return (
    <div className="p-6 rounded-2xl bg-gradient-to-r from-indigo-950/70 via-[#171b26] to-purple-950/50 border border-[#262a35] shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
      <div className="flex items-start sm:items-center gap-4">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-600 via-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-indigo-600/30 shrink-0 border border-indigo-400/20">
          {initials}
        </div>
        <div className="space-y-1.5">
          <div className="flex items-center gap-2.5 flex-wrap">
            <h1 className="text-xl md:text-2xl font-bold text-white tracking-tight">{name}</h1>
            <span className="text-xs font-mono uppercase px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 font-semibold border border-indigo-500/30">
              {role}
            </span>
            {cgpa && (
              <span className="text-xs font-mono px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/20">
                CGPA: {cgpa}
              </span>
            )}
          </div>

          <p className="text-xs text-slate-300 flex items-center flex-wrap gap-x-2 gap-y-1">
            <span>{college}</span>
            <span>•</span>
            <span>{degree} ({branch})</span>
            <span>•</span>
            <span className="font-mono text-indigo-300 font-medium">Class of {graduationYear}</span>
            {email && (
              <>
                <span>•</span>
                <span className="font-mono text-slate-400">{email}</span>
              </>
            )}
          </p>

          <div className="flex items-center gap-2 pt-1">
            {linkedinUrl && (
              <a
                href={linkedinUrl.startsWith('http') ? linkedinUrl : `https://${linkedinUrl}`}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-[11px] font-medium text-indigo-400 hover:text-indigo-300 bg-indigo-500/10 hover:bg-indigo-500/20 px-2 py-0.5 rounded border border-indigo-500/20 transition-all"
              >
                <span className="material-symbols-outlined text-sm">link</span>
                LinkedIn
              </a>
            )}

            {profile?.githubHandle && (
              <a
                href={`https://github.com/${profile.githubHandle}`}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-[11px] font-medium text-slate-300 hover:text-white bg-slate-800/60 hover:bg-slate-700/60 px-2 py-0.5 rounded border border-slate-700/50 transition-all font-mono"
              >
                <span className="material-symbols-outlined text-sm">code</span>
                github/{profile.githubHandle}
              </a>
            )}
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4 self-start md:self-auto shrink-0 pt-2 md:pt-0">
        <div className="flex flex-col items-end gap-1">
          <div className="flex items-baseline gap-1.5">
            <span className="text-xs text-slate-400">Profile Readiness:</span>
            <span className="text-sm font-bold font-mono text-emerald-400">{completionPercent}%</span>
          </div>
          <div className="w-32 h-2 rounded-full bg-[#0a0e18] border border-[#232b3e] overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-teal-400 transition-all duration-500"
              style={{ width: `${completionPercent}%` }}
            />
          </div>
        </div>

        <button
          type="button"
          onClick={onToggleEdit}
          className={`px-4 py-2.5 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all shadow-md ${
            isEditing
              ? 'bg-[#1c1f2a] text-slate-300 border border-[#262a35] hover:text-white hover:border-slate-600'
              : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-600/25 hover:shadow-indigo-600/40'
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
