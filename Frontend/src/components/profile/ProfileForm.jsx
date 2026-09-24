import React, { useState } from 'react';

export const ProfileForm = ({ profile, isEditing, onSave, onCancel }) => {
  const [formData, setFormData] = useState({ ...profile });
  const [successMsg, setSuccessMsg] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
    setSuccessMsg('Profile updated and persisted successfully!');
    setTimeout(() => setSuccessMsg(null), 3000);
  };

  if (!isEditing) {
    return (
      <div className="space-y-6">
        {/* Success Alert */}
        {successMsg && (
          <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono flex items-center gap-2 shadow-sm">
            <span className="material-symbols-outlined text-base">check_circle</span>
            <span>{successMsg}</span>
          </div>
        )}

        {/* View Mode Grid */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Academic & Career Identity */}
          <div className="p-5 rounded-2xl bg-[#171b26] border border-[#262a35] space-y-4">
            <h3 className="font-bold text-sm text-white flex items-center gap-2 border-b border-[#262a35] pb-2">
              <span className="material-symbols-outlined text-indigo-400 text-base">school</span>
              Academic & Career Identity
            </h3>

            <div className="grid grid-cols-2 gap-4 text-xs">
              <div>
                <p className="text-[11px] text-slate-400">Full Name</p>
                <p className="font-semibold text-white mt-0.5">{profile.name}</p>
              </div>
              <div>
                <p className="text-[11px] text-slate-400">Email Address</p>
                <p className="font-semibold text-white font-mono mt-0.5">{profile.email}</p>
              </div>
              <div>
                <p className="text-[11px] text-slate-400">College / University</p>
                <p className="font-semibold text-white mt-0.5">{profile.college}</p>
              </div>
              <div>
                <p className="text-[11px] text-slate-400">Degree & Branch</p>
                <p className="font-semibold text-white mt-0.5">{profile.degree} ({profile.branch || 'IT'})</p>
              </div>
              <div>
                <p className="text-[11px] text-slate-400">Graduation Year</p>
                <p className="font-semibold text-white font-mono mt-0.5">{profile.graduationYear}</p>
              </div>
              <div>
                <p className="text-[11px] text-slate-400">Company Tier</p>
                <p className="font-semibold text-purple-300 mt-0.5">{profile.companyTier}</p>
              </div>
            </div>
          </div>

          {/* Career Target & Placement Goals */}
          <div className="p-5 rounded-2xl bg-[#171b26] border border-[#262a35] space-y-4">
            <h3 className="font-bold text-sm text-white flex items-center gap-2 border-b border-[#262a35] pb-2">
              <span className="material-symbols-outlined text-purple-400 text-base">track_changes</span>
              Career Target & Placement Goals
            </h3>

            <div className="grid grid-cols-2 gap-4 text-xs">
              <div>
                <p className="text-[11px] text-slate-400">Primary Target Role</p>
                <p className="font-semibold text-indigo-300 mt-0.5">{profile.targetRole}</p>
              </div>
              <div>
                <p className="text-[11px] text-slate-400">Secondary Role</p>
                <p className="font-semibold text-white mt-0.5">{profile.secondaryRole}</p>
              </div>
              <div>
                <p className="text-[11px] text-slate-400">Target CTC Bracket</p>
                <p className="font-semibold text-emerald-400 font-mono mt-0.5">{profile.targetCtc}</p>
              </div>
              <div>
                <p className="text-[11px] text-slate-400">Target Drive Season</p>
                <p className="font-semibold text-white mt-0.5">{profile.targetDrive}</p>
              </div>
              <div>
                <p className="text-[11px] text-slate-400">Daily Commitment</p>
                <p className="font-semibold text-white font-mono mt-0.5">{profile.dailyGoalMinutes} Minutes / Day</p>
              </div>
              <div>
                <p className="text-[11px] text-slate-400">AI Mentor Persona</p>
                <p className="font-semibold text-purple-300 mt-0.5">{profile.mentorTone}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Connected Platforms Grid */}
        <div className="p-5 rounded-2xl bg-[#171b26] border border-[#262a35] space-y-3">
          <h3 className="font-bold text-sm text-white flex items-center gap-2 border-b border-[#262a35] pb-2">
            <span className="material-symbols-outlined text-emerald-400 text-base">hub</span>
            Connected Platform Accounts
          </h3>

          <div className="grid sm:grid-cols-3 gap-3 text-xs">
            <div className="p-3 rounded-xl bg-[#0a0e18] border border-[#232b3e] flex items-center justify-between">
              <div>
                <p className="text-[11px] text-slate-400">GitHub Profile</p>
                <p className="font-mono font-semibold text-indigo-400">@{profile.githubHandle}</p>
              </div>
              <span className="text-[10px] font-mono text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10">Connected</span>
            </div>

            <div className="p-3 rounded-xl bg-[#0a0e18] border border-[#232b3e] flex items-center justify-between">
              <div>
                <p className="text-[11px] text-slate-400">LeetCode Profile</p>
                <p className="font-mono font-semibold text-amber-400">@{profile.leetcodeHandle}</p>
              </div>
              <span className="text-[10px] font-mono text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10">Connected</span>
            </div>

            <div className="p-3 rounded-xl bg-[#0a0e18] border border-[#232b3e] flex items-center justify-between">
              <div>
                <p className="text-[11px] text-slate-400">Uploaded Resume</p>
                <p className="font-semibold text-white truncate max-w-[120px]">{profile.resumeFileName}</p>
              </div>
              <span className="text-[10px] font-mono text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10">ATS Verified</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Edit Mode Form
  return (
    <form onSubmit={handleSubmit} className="p-6 rounded-2xl bg-[#171b26] border border-[#262a35] space-y-6">
      <h3 className="font-bold text-base text-white flex items-center gap-2 border-b border-[#262a35] pb-3">
        <span className="material-symbols-outlined text-indigo-400 text-lg">edit</span>
        Edit Candidate Profile Details
      </h3>

      <div className="grid sm:grid-cols-2 gap-4 text-xs">
        <div className="space-y-1">
          <label className="text-[11px] font-medium text-slate-300">Full Name</label>
          <input
            type="text"
            name="name"
            value={formData.name || ''}
            onChange={handleChange}
            className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500"
            required
          />
        </div>

        <div className="space-y-1">
          <label className="text-[11px] font-medium text-slate-300">Email Address</label>
          <input
            type="email"
            name="email"
            value={formData.email || ''}
            onChange={handleChange}
            className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500"
            required
          />
        </div>

        <div className="space-y-1">
          <label className="text-[11px] font-medium text-slate-300">College / University</label>
          <input
            type="text"
            name="college"
            value={formData.college || ''}
            onChange={handleChange}
            className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="space-y-1">
          <label className="text-[11px] font-medium text-slate-300">Degree & Branch</label>
          <input
            type="text"
            name="degree"
            value={formData.degree || ''}
            onChange={handleChange}
            className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="space-y-1">
          <label className="text-[11px] font-medium text-slate-300">Graduation Year</label>
          <input
            type="text"
            name="graduationYear"
            value={formData.graduationYear || ''}
            onChange={handleChange}
            className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="space-y-1">
          <label className="text-[11px] font-medium text-slate-300">Primary Target Role</label>
          <select
            name="targetRole"
            value={formData.targetRole || 'Backend Developer'}
            onChange={handleChange}
            className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500"
          >
            <option value="Backend Developer">Backend Developer</option>
            <option value="Full Stack Developer">Full Stack Developer</option>
            <option value="AI/ML Engineer">AI/ML Engineer</option>
            <option value="Frontend Engineer">Frontend Engineer</option>
            <option value="DevOps / Cloud Engineer">DevOps / Cloud Engineer</option>
          </select>
        </div>

        <div className="space-y-1">
          <label className="text-[11px] font-medium text-slate-300">Secondary Role</label>
          <input
            type="text"
            name="secondaryRole"
            value={formData.secondaryRole || ''}
            onChange={handleChange}
            className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="space-y-1">
          <label className="text-[11px] font-medium text-slate-300">Company Tier Target</label>
          <input
            type="text"
            name="companyTier"
            value={formData.companyTier || ''}
            onChange={handleChange}
            className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="space-y-1">
          <label className="text-[11px] font-medium text-slate-300">GitHub Handle</label>
          <input
            type="text"
            name="githubHandle"
            value={formData.githubHandle || ''}
            onChange={handleChange}
            className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500 font-mono"
          />
        </div>

        <div className="space-y-1">
          <label className="text-[11px] font-medium text-slate-300">LeetCode Handle</label>
          <input
            type="text"
            name="leetcodeHandle"
            value={formData.leetcodeHandle || ''}
            onChange={handleChange}
            className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500 font-mono"
          />
        </div>
      </div>

      <div className="flex items-center justify-end gap-3 pt-4 border-t border-[#262a35]">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 rounded-xl bg-[#0a0e18] hover:bg-[#1c1f2a] text-slate-300 text-xs font-semibold border border-[#232b3e] transition-colors"
        >
          Cancel
        </button>
        <button
          type="submit"
          className="px-5 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 text-white text-xs font-semibold shadow-md hover:opacity-90 transition-all"
        >
          Save Profile Changes
        </button>
      </div>
    </form>
  );
};
