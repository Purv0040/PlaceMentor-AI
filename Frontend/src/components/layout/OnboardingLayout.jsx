import React from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { Sparkles, ArrowRight } from 'lucide-react';
import { OnboardingProvider } from '../../context/OnboardingContext';
import { StepIndicator } from '../common/StepIndicator';

export const OnboardingLayoutContent = () => {
  const location = useLocation();
  const isIntro = location.pathname === '/onboarding';

  return (
    <div className="min-h-screen bg-obsidian-base text-slate-100 flex flex-col font-sans antialiased selection:bg-brand-500/30 selection:text-white">
      {/* Onboarding Header */}
      <header className="border-b border-obsidian-border bg-obsidian-surface/90 backdrop-blur-md sticky top-0 z-40 px-4 sm:px-8 py-3">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <NavLink to="/" className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-brand-600 to-ai-500 flex items-center justify-center shadow-lg shadow-brand-500/20">
              <Sparkles className="w-4.5 h-4.5 text-white" />
            </div>
            <div className="font-bold text-base text-white tracking-wide">
              PlaceMentor <span className="text-[10px] px-1.5 py-0.5 rounded bg-brand-500/20 text-brand-400 font-mono">Setup</span>
            </div>
          </NavLink>

          <NavLink
            to="/dashboard"
            className="text-xs text-slate-400 hover:text-white transition-colors flex items-center gap-1 font-medium"
          >
            Skip Setup to Dashboard <ArrowRight className="w-3.5 h-3.5" />
          </NavLink>
        </div>

        {/* Render Step Indicator unless on intro landing */}
        {!isIntro && (
          <div className="mt-3">
            <StepIndicator />
          </div>
        )}
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-4xl w-full mx-auto p-4 sm:p-6 lg:p-8 flex flex-col justify-center">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="py-4 border-t border-obsidian-border text-center text-xs text-slate-500 font-mono">
        Step-by-Step AI Placement Profile Calibration • PlaceMentor AI 2026
      </footer>
    </div>
  );
};

export const OnboardingLayout = () => {
  return (
    <OnboardingProvider>
      <OnboardingLayoutContent />
    </OnboardingProvider>
  );
};
