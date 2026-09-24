import React from 'react';
import { NavLink } from 'react-router-dom';
import { Code2, ArrowRight, ArrowLeft } from 'lucide-react';

export const OnboardingSkillsPage = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">Skills Self-Assessment</h2>
        <p className="text-xs text-slate-400">Step 3 of 7 — Mark your current confidence level across core domains</p>
      </div>

      <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4">
        {['Data Structures & Algorithms', 'System Design & Distributed Systems', 'Database Management & SQL', 'Backend Frameworks (Spring Boot / Express / FastAPI)', 'Git & Version Control'].map((domain) => (
          <div key={domain} className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-3 rounded-xl bg-[#0b0e17] border border-[#232b3e]">
            <span className="text-xs font-medium text-slate-200">{domain}</span>
            <select defaultValue="Intermediate" className="px-3 py-1 text-xs rounded-lg bg-[#121624] border border-[#232b3e] text-slate-300 focus:outline-none focus:border-indigo-500">
              <option value="Beginner">Beginner (Needs Ground Up)</option>
              <option value="Intermediate">Intermediate (Practicing)</option>
              <option value="Advanced">Advanced (Interview Ready)</option>
            </select>
          </div>
        ))}
      </div>

      <div className="flex items-center justify-between">
        <NavLink to="/onboarding/career" className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white">
          <ArrowLeft className="w-4 h-4" /> Back
        </NavLink>
        <NavLink to="/onboarding/integrations" className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs">
          Next: Integrations Sync <ArrowRight className="w-4 h-4" />
        </NavLink>
      </div>
    </div>
  );
};
