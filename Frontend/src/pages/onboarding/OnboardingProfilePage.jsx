import React from 'react';
import { NavLink } from 'react-router-dom';
import { User, School, GraduationCap, ArrowRight } from 'lucide-react';

export const OnboardingProfilePage = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">Personal & Academic Details</h2>
        <p className="text-xs text-slate-400">Step 1 of 7 — Tell us about yourself</p>
      </div>

      <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4">
        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1">Full Name</label>
          <input
            type="text"
            defaultValue="Alex Patel"
            className="w-full px-4 py-2 text-xs rounded-xl bg-[#0b0e17] border border-[#232b3e] text-white focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="grid sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">College / University</label>
            <input
              type="text"
              defaultValue="CSPIT"
              className="w-full px-4 py-2 text-xs rounded-xl bg-[#0b0e17] border border-[#232b3e] text-white focus:outline-none focus:border-indigo-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Degree & Branch</label>
            <input
              type="text"
              defaultValue="B.Tech IT"
              className="w-full px-4 py-2 text-xs rounded-xl bg-[#0b0e17] border border-[#232b3e] text-white focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1">Graduation Year</label>
          <select defaultValue="2027" className="w-full px-4 py-2 text-xs rounded-xl bg-[#0b0e17] border border-[#232b3e] text-white focus:outline-none focus:border-indigo-500">
            <option value="2025">2025</option>
            <option value="2026">2026</option>
            <option value="2027">2027</option>
            <option value="2028">2028</option>
          </select>
        </div>
      </div>

      <div className="flex justify-end">
        <NavLink
          to="/onboarding/career"
          className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition-colors"
        >
          Next: Career Target <ArrowRight className="w-4 h-4" />
        </NavLink>
      </div>
    </div>
  );
};
