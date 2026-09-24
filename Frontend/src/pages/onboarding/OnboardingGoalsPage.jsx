import React from 'react';
import { NavLink } from 'react-router-dom';
import { Target, Calendar, Trophy, ArrowRight, ArrowLeft } from 'lucide-react';

export const OnboardingGoalsPage = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">Placement Timeline & Targets</h2>
        <p className="text-xs text-slate-400">Step 6 of 7 — Define your target timeline and desired compensation tier</p>
      </div>

      <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4">
        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1">Target Placement Drive Season</label>
          <select defaultValue="August 2026 (Campus Phase 1)" className="w-full px-4 py-2 text-xs rounded-xl bg-[#0b0e17] border border-[#232b3e] text-white focus:outline-none focus:border-indigo-500">
            <option value="August 2026 (Campus Phase 1)">August 2026 (Campus Phase 1)</option>
            <option value="November 2026 (Campus Phase 2)">November 2026 (Campus Phase 2)</option>
            <option value="Immediate Off-Campus / Referral">Immediate Off-Campus / Referral</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1">Target CTC Bracket</label>
          <div className="grid sm:grid-cols-3 gap-3">
            <button type="button" className="p-3 rounded-xl bg-[#0b0e17] border border-[#232b3e] text-left text-xs text-slate-400 hover:border-slate-700">
              6 - 12 LPA (Solid Foundation)
            </button>
            <button type="button" className="p-3 rounded-xl bg-indigo-600/20 border border-indigo-500 text-left text-xs font-semibold text-white">
              14 - 24 LPA (Product Tier)
            </button>
            <button type="button" className="p-3 rounded-xl bg-[#0b0e17] border border-[#232b3e] text-left text-xs text-slate-400 hover:border-slate-700">
              25+ LPA (Top Tech / Quant)
            </button>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <NavLink to="/onboarding/preferences" className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white">
          <ArrowLeft className="w-4 h-4" /> Back
        </NavLink>
        <NavLink to="/onboarding/analysis" className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs">
          Generate AI Analysis <ArrowRight className="w-4 h-4" />
        </NavLink>
      </div>
    </div>
  );
};
