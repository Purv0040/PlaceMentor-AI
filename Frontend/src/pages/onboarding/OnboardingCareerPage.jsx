import React from 'react';
import { NavLink } from 'react-router-dom';
import { Target, ArrowRight, ArrowLeft } from 'lucide-react';

export const OnboardingCareerPage = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">Target Career & Role</h2>
        <p className="text-xs text-slate-400">Step 2 of 7 — Define your benchmark placement targets</p>
      </div>

      <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4">
        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1">Primary Target Role</label>
          <select defaultValue="Backend Developer" className="w-full px-4 py-2 text-xs rounded-xl bg-[#0b0e17] border border-[#232b3e] text-white focus:outline-none focus:border-indigo-500">
            <option value="Backend Developer">Backend Developer (SDE-1)</option>
            <option value="Full Stack Developer">Full Stack Engineer</option>
            <option value="AI/ML Engineer">AI/ML Engineer</option>
            <option value="Frontend Developer">Frontend Engineer</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1">Target Company Tier</label>
          <div className="grid sm:grid-cols-3 gap-3">
            <button type="button" className="p-3 rounded-xl bg-indigo-600/20 border border-indigo-500 text-left text-xs font-semibold text-white">
              Tier-1 Product (MAANG / Unicorns)
            </button>
            <button type="button" className="p-3 rounded-xl bg-[#0b0e17] border border-[#232b3e] text-left text-xs text-slate-400 hover:border-slate-700">
              Tier-2 Mid-Size & High-Growth
            </button>
            <button type="button" className="p-3 rounded-xl bg-[#0b0e17] border border-[#232b3e] text-left text-xs text-slate-400 hover:border-slate-700">
              IT Services & Campus Recruiters
            </button>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <NavLink to="/onboarding/profile" className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white">
          <ArrowLeft className="w-4 h-4" /> Back
        </NavLink>
        <NavLink to="/onboarding/skills" className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs">
          Next: Skills Self-Assessment <ArrowRight className="w-4 h-4" />
        </NavLink>
      </div>
    </div>
  );
};
