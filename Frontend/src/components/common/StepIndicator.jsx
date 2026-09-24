import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { CheckCircle2 } from 'lucide-react';
import { useOnboarding } from '../../context/OnboardingContext';

export const StepIndicator = () => {
  const location = useLocation();
  const { onboardingData } = useOnboarding();

  const steps = [
    { num: 1, label: 'Profile', path: '/onboarding/profile' },
    { num: 2, label: 'Career', path: '/onboarding/career' },
    { num: 3, label: 'Skills', path: '/onboarding/skills' },
    { num: 4, label: 'Integrations', path: '/onboarding/integrations' },
    { num: 5, label: 'Preferences', path: '/onboarding/preferences' },
    { num: 6, label: 'Goals', path: '/onboarding/goals' },
    { num: 7, label: 'Analysis', path: '/onboarding/analysis' },
  ];

  return (
    <div className="w-full max-w-4xl mx-auto py-2">
      <div className="flex items-center justify-between overflow-x-auto pb-2 scrollbar-none">
        {steps.map((step, idx) => {
          const isActive = location.pathname === step.path;
          const isCompleted = onboardingData.completedSteps.includes(step.num);

          return (
            <React.Fragment key={step.path}>
              <NavLink
                to={step.path}
                className={`flex items-center gap-2 text-xs font-semibold whitespace-nowrap transition-colors ${
                  isActive
                    ? 'text-brand-400 font-bold'
                    : isCompleted
                    ? 'text-emerald-400'
                    : 'text-slate-500 hover:text-slate-300'
                }`}
              >
                <div
                  className={`w-6 h-6 rounded-full flex items-center justify-center text-[11px] font-mono transition-all ${
                    isActive
                      ? 'bg-brand-500 text-white shadow-lg shadow-brand-500/30 ring-2 ring-brand-400/40'
                      : isCompleted
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                      : 'bg-obsidian-surface border border-obsidian-borderLight text-slate-500'
                  }`}
                >
                  {isCompleted && !isActive ? (
                    <CheckCircle2 className="w-3.5 h-3.5" />
                  ) : (
                    step.num
                  )}
                </div>
                <span className="hidden sm:inline">{step.label}</span>
              </NavLink>

              {idx < steps.length - 1 && (
                <div
                  className={`flex-1 h-[1px] min-w-[12px] mx-2 transition-colors ${
                    isCompleted ? 'bg-emerald-500/30' : 'bg-obsidian-borderLight'
                  }`}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};
