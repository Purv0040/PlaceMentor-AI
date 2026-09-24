import React from 'react';
import { NavLink } from 'react-router-dom';
import { Clock, Bell, Settings, ArrowRight, ArrowLeft } from 'lucide-react';

export const OnboardingPreferencesPage = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">Study Cadence & Preferences</h2>
        <p className="text-xs text-slate-400">Step 5 of 7 — How do you prefer to prepare?</p>
      </div>

      <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4">
        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1">Daily Prep Commitment</label>
          <select defaultValue="90" className="w-full px-4 py-2 text-xs rounded-xl bg-[#0b0e17] border border-[#232b3e] text-white focus:outline-none focus:border-indigo-500">
            <option value="45">45 Minutes / Day (Light Speed)</option>
            <option value="90">90 Minutes / Day (Balanced Standard)</option>
            <option value="180">3 Hours / Day (Placement Sprint Mode)</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1">AI Mentor Tone Preference</label>
          <div className="grid sm:grid-cols-2 gap-3">
            <button type="button" className="p-3 rounded-xl bg-indigo-600/20 border border-indigo-500 text-left text-xs font-semibold text-white">
              Socratic Coach (Probing Questions)
            </button>
            <button type="button" className="p-3 rounded-xl bg-[#0b0e17] border border-[#232b3e] text-left text-xs text-slate-400 hover:border-slate-700">
              Direct Senior Engineer (Code-First)
            </button>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <NavLink to="/onboarding/integrations" className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white">
          <ArrowLeft className="w-4 h-4" /> Back
        </NavLink>
        <NavLink to="/onboarding/goals" className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs">
          Next: Placement Goal <ArrowRight className="w-4 h-4" />
        </NavLink>
      </div>
    </div>
  );
};
