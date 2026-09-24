import React from 'react';
import { NavLink } from 'react-router-dom';
import { Sparkles, CheckCircle2, TrendingUp, ArrowRight } from 'lucide-react';

export const OnboardingAnalysisPage = () => {
  return (
    <div className="space-y-6 text-center">
      <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-emerald-500 flex items-center justify-center mx-auto shadow-xl shadow-indigo-600/30">
        <Sparkles className="w-7 h-7 text-white" />
      </div>

      <div>
        <h2 className="text-2xl font-bold text-white">Your Placement Profile is Ready!</h2>
        <p className="text-xs text-slate-400">Step 7 of 7 — Telemetry analyzed and 90-day roadmap compiled</p>
      </div>

      <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] text-left max-w-lg mx-auto space-y-4">
        <div className="flex items-center justify-between p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20">
          <span className="text-xs font-medium text-slate-300">Initial Readiness Baseline</span>
          <span className="text-base font-bold text-indigo-400 font-mono">78 / 100</span>
        </div>

        <div className="space-y-2 text-xs text-slate-300">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>Target Role: Backend Developer (SDE-1)</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>Day 1 Action Plan: Graph BFS/DFS & Microservices</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>AI Mentor Persona: Socratic Senior Engineer</span>
          </div>
        </div>
      </div>

      <div>
        <NavLink
          to="/dashboard"
          className="inline-flex items-center gap-2 px-8 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-xs transition-all shadow-lg shadow-indigo-600/30"
        >
          Enter Copilot Dashboard <ArrowRight className="w-4 h-4" />
        </NavLink>
      </div>
    </div>
  );
};
