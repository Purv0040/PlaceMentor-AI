import React from 'react';
import { NavLink } from 'react-router-dom';
import { Github, Code2, FileText, ArrowRight, ArrowLeft, CheckCircle2 } from 'lucide-react';

export const OnboardingIntegrationsPage = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">Connect Preparation Accounts</h2>
        <p className="text-xs text-slate-400">Step 4 of 7 — Enable telemetry to auto-sync your activity</p>
      </div>

      <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4">
        <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#232b3e] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Github className="w-6 h-6 text-white" />
            <div>
              <p className="text-xs font-semibold text-white">GitHub Integration</p>
              <p className="text-[11px] text-slate-400">Auto-audit commit frequency & project architecture</p>
            </div>
          </div>
          <button type="button" className="px-3 py-1.5 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-mono flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" /> Connected
          </button>
        </div>

        <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#232b3e] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Code2 className="w-6 h-6 text-amber-400" />
            <div>
              <p className="text-xs font-semibold text-white">LeetCode Sync</p>
              <p className="text-[11px] text-slate-400">Fetch solved counts & topic accuracy stats</p>
            </div>
          </div>
          <button type="button" className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium">
            Connect Account
          </button>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <NavLink to="/onboarding/skills" className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white">
          <ArrowLeft className="w-4 h-4" /> Back
        </NavLink>
        <NavLink to="/onboarding/preferences" className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs">
          Next: Preferences <ArrowRight className="w-4 h-4" />
        </NavLink>
      </div>
    </div>
  );
};
