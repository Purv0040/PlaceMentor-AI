import React, { useEffect } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight, CheckCircle2, ShieldCheck } from 'lucide-react';
import { useOnboarding } from '../../context/OnboardingContext';

export const OnboardingIntroPage = () => {
  const navigate = useNavigate();
  const { isOnboardingComplete } = useOnboarding();

  useEffect(() => {
    if (isOnboardingComplete()) {
      navigate('/dashboard', { replace: true });
    }
  }, [isOnboardingComplete, navigate]);

  return (
    <div className="text-center space-y-8 py-6">
      <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-brand-600 via-ai-500 to-emerald-500 flex items-center justify-center mx-auto shadow-2xl shadow-brand-500/30 animate-pulse">
        <Sparkles className="w-8 h-8 text-white" />
      </div>

      <div className="space-y-3">
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white">Welcome to PlaceMentor AI</h1>
        <p className="text-xs sm:text-sm text-slate-400 max-w-lg mx-auto leading-relaxed">
          Calibrate your 7-vector placement profile and generate your adaptive 90-day preparation roadmap in 7 quick steps.
        </p>
      </div>

      <div className="max-w-md mx-auto p-6 rounded-2xl bg-obsidian-card border border-obsidian-borderLight text-left space-y-3.5 shadow-xl">
        <div className="flex items-center gap-3 text-xs text-slate-200">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>Step 1: Academic & Personal Context</span>
        </div>
        <div className="flex items-center gap-3 text-xs text-slate-200">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>Step 2: Target Role & Tier Benchmarking</span>
        </div>
        <div className="flex items-center gap-3 text-xs text-slate-200">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>Step 3: Domain Skills Self-Assessment</span>
        </div>
        <div className="flex items-center gap-3 text-xs text-slate-200">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>Step 4: GitHub, LeetCode & Resume Telemetry</span>
        </div>
        <div className="flex items-center gap-3 text-xs text-slate-200">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>Step 5 & 6: Prep Preferences & Placement Goals</span>
        </div>
        <div className="flex items-center gap-3 text-xs text-slate-200">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>Step 7: AI Readiness Baseline & Roadmap Synthesis</span>
        </div>
      </div>

      <div>
        <NavLink
          to="/onboarding/profile"
          className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl bg-brand-500 hover:bg-brand-600 text-white font-semibold text-xs sm:text-sm shadow-xl shadow-brand-500/25 transition-all transform hover:-translate-y-0.5"
        >
          Begin Onboarding Setup <ArrowRight className="w-4 h-4" />
        </NavLink>
      </div>
    </div>
  );
};
