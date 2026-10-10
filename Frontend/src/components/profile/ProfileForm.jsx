import React, { useState, useEffect } from 'react';

export const ProfileForm = ({ profile, isEditing, onSave, onCancel, isSaving }) => {
  const [formData, setFormData] = useState({ ...profile });
  const [newSkill, setNewSkill] = useState('');

  // Keep formData synced when profile prop updates from API
  useEffect(() => {
    setFormData({ ...profile });
  }, [profile]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleAddSkill = (e) => {
    e.preventDefault();
    if (!newSkill.trim()) return;
    const trimmed = newSkill.trim();
    const current = formData.skills || [];
    if (!current.includes(trimmed)) {
      setFormData(prev => ({
        ...prev,
        skills: [...current, trimmed]
      }));
    }
    setNewSkill('');
  };

  const handleRemoveSkill = (skillToRemove) => {
    setFormData(prev => ({
      ...prev,
      skills: (prev.skills || []).filter(s => s !== skillToRemove)
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  if (!isEditing) {
    return (
      <div className="space-y-6">
        {/* View Mode Grid */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Academic & Personal Identity */}
          <div className="p-5 rounded-2xl bg-[#171b26] border border-[#262a35] space-y-4 shadow-sm">
            <h3 className="font-bold text-sm text-white flex items-center gap-2 border-b border-[#262a35] pb-2">
              <span className="material-symbols-outlined text-indigo-400 text-base">school</span>
              Academic & Personal Information
            </h3>

            <div className="grid grid-cols-2 gap-4 text-xs">
              <div>
                <p className="text-[11px] text-slate-400">Full Name</p>
                <p className="font-semibold text-white mt-0.5">{profile.name || 'Not specified'}</p>
              </div>
              <div>
                <p className="text-[11px] text-slate-400">Email Address</p>
                <p className="font-semibold text-white font-mono mt-0.5">{profile.email || 'Not specified'}</p>
              </div>
              <div>
                <p className="text-[11px] text-slate-400">College / University</p>
                <p className="font-semibold text-white mt-0.5">{profile.college || 'Not specified'}</p>
              </div>
              <div>
                <p className="text-[11px] text-slate-400">Degree & Branch</p>
                <p className="font-semibold text-white mt-0.5">
                  {profile.degree || 'B.Tech'} ({profile.branch || 'Computer Engineering'})
                </p>
              </div>
              <div>
                <p className="text-[11px] text-slate-400">Graduation Year</p>
                <p className="font-semibold text-indigo-300 font-mono mt-0.5">{profile.graduationYear || '2026'}</p>
              </div>
              <div>
                <p className="text-[11px] text-slate-400">Current CGPA</p>
                <p className="font-semibold text-emerald-400 font-mono mt-0.5">{profile.cgpa || 'Not provided'}</p>
              </div>
              <div>
                <p className="text-[11px] text-slate-400">Contact Number</p>
                <p className="font-semibold text-white font-mono mt-0.5">{profile.phone || 'Not provided'}</p>
              </div>
              <div>
                <p className="text-[11px] text-slate-400">Current Location</p>
                <p className="font-semibold text-white mt-0.5">{profile.location || 'Not provided'}</p>
              </div>
            </div>
          </div>

          {/* Placement Goals & Preferences */}
          <div className="p-5 rounded-2xl bg-[#171b26] border border-[#262a35] space-y-4 shadow-sm">
            <h3 className="font-bold text-sm text-white flex items-center gap-2 border-b border-[#262a35] pb-2">
              <span className="material-symbols-outlined text-purple-400 text-base">track_changes</span>
              Career Target & Placement Goals
            </h3>

            <div className="grid grid-cols-2 gap-4 text-xs">
              <div>
                <p className="text-[11px] text-slate-400">Primary Target Role</p>
                <p className="font-semibold text-indigo-300 mt-0.5">{profile.targetRole || 'Full Stack Engineer'}</p>
              </div>
              <div>
                <p className="text-[11px] text-slate-400">Secondary Role</p>
                <p className="font-semibold text-white mt-0.5">{profile.secondaryRole || 'Not specified'}</p>
              </div>
              <div>
                <p className="text-[11px] text-slate-400">Target Company Tier</p>
                <p className="font-semibold text-purple-300 mt-0.5">{profile.companyTier || 'Tier-1 Product'}</p>
              </div>
              <div>
                <p className="text-[11px] text-slate-400">Target CTC Bracket</p>
                <p className="font-semibold text-emerald-400 font-mono mt-0.5">{profile.targetCtc || '14 - 24 LPA'}</p>
              </div>
              <div>
                <p className="text-[11px] text-slate-400">Target Drive Season</p>
                <p className="font-semibold text-white mt-0.5">{profile.targetDrive || 'Campus Phase 1'}</p>
              </div>
              <div>
                <p className="text-[11px] text-slate-400">Daily Prep Commitment</p>
                <p className="font-semibold text-white font-mono mt-0.5">{profile.dailyGoalMinutes || '90'} Mins/Day</p>
              </div>
              <div>
                <p className="text-[11px] text-slate-400">AI Mentor Persona</p>
                <p className="font-semibold text-purple-300 mt-0.5">{profile.mentorTone || 'Socratic Coach'}</p>
              </div>
              <div>
                <p className="text-[11px] text-slate-400">Study Cadence</p>
                <p className="font-semibold text-white mt-0.5">{profile.studyCadence || 'Evening Sprint'}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Technical Competencies & Skills */}
        <div className="p-5 rounded-2xl bg-[#171b26] border border-[#262a35] space-y-4 shadow-sm">
          <h3 className="font-bold text-sm text-white flex items-center justify-between border-b border-[#262a35] pb-2">
            <span className="flex items-center gap-2">
              <span className="material-symbols-outlined text-amber-400 text-base">psychology</span>
              Technical Competencies & Core Skills
            </span>
            <span className="text-[11px] text-slate-400 font-mono">
              DSA: <span className="text-indigo-300">{profile.dsaLevel || 'Intermediate'}</span> | SysDesign: <span className="text-purple-300">{profile.sysDesignLevel || 'Beginner'}</span>
            </span>
          </h3>

          <div className="flex flex-wrap gap-2">
            {(profile.skills && profile.skills.length > 0) ? (
              profile.skills.map((skill, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-mono font-medium"
                >
                  {skill}
                </span>
              ))
            ) : (
              <span className="text-xs text-slate-500 italic">No skills specified yet.</span>
            )}
          </div>
        </div>

        {/* Connected Platforms Grid */}
        <div className="p-5 rounded-2xl bg-[#171b26] border border-[#262a35] space-y-3 shadow-sm">
          <h3 className="font-bold text-sm text-white flex items-center gap-2 border-b border-[#262a35] pb-2">
            <span className="material-symbols-outlined text-emerald-400 text-base">hub</span>
            Verified Platform Integrations & Profiles
          </h3>

          <div className="grid sm:grid-cols-3 gap-3 text-xs">
            <div className="p-3.5 rounded-xl bg-[#0a0e18] border border-[#232b3e] flex items-center justify-between">
              <div>
                <p className="text-[11px] text-slate-400">GitHub Handle</p>
                <p className="font-mono font-semibold text-indigo-400 mt-0.5">
                  {profile.githubHandle ? `@${profile.githubHandle}` : 'Not connected'}
                </p>
              </div>
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                profile.githubHandle ? 'text-emerald-400 bg-emerald-500/10 border border-emerald-500/20' : 'text-slate-500 bg-slate-800'
              }`}>
                {profile.githubHandle ? 'Active' : 'Unlinked'}
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-[#0a0e18] border border-[#232b3e] flex items-center justify-between">
              <div>
                <p className="text-[11px] text-slate-400">LeetCode Profile</p>
                <p className="font-mono font-semibold text-amber-400 mt-0.5">
                  {profile.leetcodeHandle ? `@${profile.leetcodeHandle}` : 'Not connected'}
                </p>
              </div>
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                profile.leetcodeHandle ? 'text-emerald-400 bg-emerald-500/10 border border-emerald-500/20' : 'text-slate-500 bg-slate-800'
              }`}>
                {profile.leetcodeHandle ? 'Active' : 'Unlinked'}
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-[#0a0e18] border border-[#232b3e] flex items-center justify-between">
              <div>
                <p className="text-[11px] text-slate-400">Active Resume</p>
                <p className="font-semibold text-white truncate max-w-[130px] mt-0.5">
                  {profile.resumeFileName || 'None uploaded'}
                </p>
              </div>
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                profile.resumeFileName ? 'text-emerald-400 bg-emerald-500/10 border border-emerald-500/20' : 'text-amber-400 bg-amber-500/10 border border-amber-500/20'
              }`}>
                {profile.resumeFileName ? 'ATS Verified' : 'Pending'}
              </span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Edit Mode Form
  return (
    <form onSubmit={handleSubmit} className="p-6 rounded-2xl bg-[#171b26] border border-[#262a35] space-y-6 shadow-xl">
      <div className="flex items-center justify-between border-b border-[#262a35] pb-3">
        <h3 className="font-bold text-base text-white flex items-center gap-2">
          <span className="material-symbols-outlined text-indigo-400 text-lg">edit</span>
          Edit Real Student Profile
        </h3>
        <span className="text-xs text-slate-400 font-mono">Syncs directly with Database</span>
      </div>

      {/* Section 1: Academic & Personal */}
      <div className="space-y-3">
        <h4 className="text-xs font-semibold text-indigo-300 uppercase tracking-wider flex items-center gap-1.5">
          <span className="material-symbols-outlined text-sm">person</span>
          Personal & Academic Info
        </h4>
        <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-4 text-xs">
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
              required
            />
          </div>

          <div className="space-y-1">
            <label className="text-[11px] font-medium text-slate-300">Degree</label>
            <input
              type="text"
              name="degree"
              value={formData.degree || ''}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500"
              required
            />
          </div>

          <div className="space-y-1">
            <label className="text-[11px] font-medium text-slate-300">Branch / Specialization</label>
            <input
              type="text"
              name="branch"
              value={formData.branch || ''}
              onChange={handleChange}
              placeholder="e.g. Information Technology"
              className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="space-y-1">
            <label className="text-[11px] font-medium text-slate-300">Graduation Year</label>
            <input
              type="text"
              name="graduationYear"
              value={formData.graduationYear || '2026'}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500 font-mono"
            />
          </div>

          <div className="space-y-1">
            <label className="text-[11px] font-medium text-slate-300">CGPA / Percentage</label>
            <input
              type="text"
              name="cgpa"
              value={formData.cgpa || ''}
              onChange={handleChange}
              placeholder="e.g. 8.75"
              className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500 font-mono"
            />
          </div>

          <div className="space-y-1">
            <label className="text-[11px] font-medium text-slate-300">Phone</label>
            <input
              type="text"
              name="phone"
              value={formData.phone || ''}
              onChange={handleChange}
              placeholder="+91 9876543210"
              className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500 font-mono"
            />
          </div>

          <div className="space-y-1">
            <label className="text-[11px] font-medium text-slate-300">Location</label>
            <input
              type="text"
              name="location"
              value={formData.location || ''}
              onChange={handleChange}
              placeholder="e.g. Gujarat, India"
              className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>
      </div>

      {/* Section 2: Career Targets */}
      <div className="space-y-3 pt-2 border-t border-[#262a35]">
        <h4 className="text-xs font-semibold text-purple-300 uppercase tracking-wider flex items-center gap-1.5">
          <span className="material-symbols-outlined text-sm">track_changes</span>
          Target Role & Placement Goals
        </h4>
        <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-4 text-xs">
          <div className="space-y-1">
            <label className="text-[11px] font-medium text-slate-300">Primary Target Role</label>
            <select
              name="targetRole"
              value={formData.targetRole || 'Full Stack Engineer'}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500"
            >
              <option value="Full Stack Engineer">Full Stack Engineer</option>
              <option value="Backend Developer">Backend Developer</option>
              <option value="AI/ML Engineer">AI/ML Engineer</option>
              <option value="Frontend Engineer">Frontend Engineer</option>
              <option value="DevOps / Cloud Engineer">DevOps / Cloud Engineer</option>
              <option value="Cybersecurity Analyst & Engineer">Cybersecurity Analyst & Engineer</option>
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
            <label className="text-[11px] font-medium text-slate-300">Target Company Tier</label>
            <input
              type="text"
              name="companyTier"
              value={formData.companyTier || ''}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="space-y-1">
            <label className="text-[11px] font-medium text-slate-300">Target CTC</label>
            <input
              type="text"
              name="targetCtc"
              value={formData.targetCtc || ''}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500 font-mono"
            />
          </div>

          <div className="space-y-1">
            <label className="text-[11px] font-medium text-slate-300">Target Drive Season</label>
            <input
              type="text"
              name="targetDrive"
              value={formData.targetDrive || ''}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="space-y-1">
            <label className="text-[11px] font-medium text-slate-300">Daily Prep (Minutes)</label>
            <input
              type="number"
              name="dailyGoalMinutes"
              value={formData.dailyGoalMinutes || '90'}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500 font-mono"
            />
          </div>
        </div>
      </div>

      {/* Section 3: Social & Platform Handles */}
      <div className="space-y-3 pt-2 border-t border-[#262a35]">
        <h4 className="text-xs font-semibold text-emerald-300 uppercase tracking-wider flex items-center gap-1.5">
          <span className="material-symbols-outlined text-sm">hub</span>
          Social & Platform Handles
        </h4>
        <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-4 text-xs">
          <div className="space-y-1">
            <label className="text-[11px] font-medium text-slate-300">GitHub Username</label>
            <input
              type="text"
              name="githubHandle"
              value={formData.githubHandle || ''}
              onChange={handleChange}
              placeholder="e.g. Purv0040"
              className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500 font-mono"
            />
          </div>

          <div className="space-y-1">
            <label className="text-[11px] font-medium text-slate-300">LeetCode Username</label>
            <input
              type="text"
              name="leetcodeHandle"
              value={formData.leetcodeHandle || ''}
              onChange={handleChange}
              placeholder="e.g. Purv_Leetcode"
              className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500 font-mono"
            />
          </div>

          <div className="space-y-1">
            <label className="text-[11px] font-medium text-slate-300">LinkedIn Profile URL</label>
            <input
              type="text"
              name="linkedinUrl"
              value={formData.linkedinUrl || ''}
              onChange={handleChange}
              placeholder="https://linkedin.com/in/username"
              className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500 font-mono"
            />
          </div>
        </div>
      </div>

      {/* Section 4: Skills Management */}
      <div className="space-y-3 pt-2 border-t border-[#262a35]">
        <h4 className="text-xs font-semibold text-amber-300 uppercase tracking-wider flex items-center gap-1.5">
          <span className="material-symbols-outlined text-sm">psychology</span>
          Technical Skills & Stack
        </h4>

        <div className="flex gap-2">
          <input
            type="text"
            value={newSkill}
            onChange={(e) => setNewSkill(e.target.value)}
            placeholder="Type a skill and press Add (e.g. Docker, TypeScript, FastApi)"
            className="flex-1 px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500 text-xs"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                handleAddSkill(e);
              }
            }}
          />
          <button
            type="button"
            onClick={handleAddSkill}
            className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
          >
            Add Skill
          </button>
        </div>

        <div className="flex flex-wrap gap-2 pt-1">
          {(formData.skills || []).map((skill, index) => (
            <span
              key={index}
              className="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-indigo-500/15 border border-indigo-500/30 text-indigo-300 text-xs font-mono"
            >
              <span>{skill}</span>
              <button
                type="button"
                onClick={() => handleRemoveSkill(skill)}
                className="text-slate-400 hover:text-red-400 font-bold ml-1"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center justify-end gap-3 pt-4 border-t border-[#262a35]">
        <button
          type="button"
          onClick={onCancel}
          disabled={isSaving}
          className="px-4 py-2.5 rounded-xl bg-[#0a0e18] hover:bg-[#1c1f2a] text-slate-300 text-xs font-semibold border border-[#232b3e] transition-colors disabled:opacity-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isSaving}
          className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 text-white text-xs font-semibold shadow-md hover:opacity-90 transition-all flex items-center gap-2 disabled:opacity-50"
        >
          {isSaving ? (
            <>
              <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
              <span>Saving to Database...</span>
            </>
          ) : (
            <>
              <span className="material-symbols-outlined text-sm">cloud_upload</span>
              <span>Save & Sync to Database</span>
            </>
          )}
        </button>
      </div>
    </form>
  );
};
