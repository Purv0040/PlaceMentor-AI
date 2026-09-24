import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Target, Trophy, Calendar, ArrowRight, ArrowLeft, CheckCircle2 } from 'lucide-react';
import { useOnboarding } from '../../context/OnboardingContext';
import { Button } from '../../components/common/Button';

export const GoalsStep = () => {
  const navigate = useNavigate();
  const { onboardingData, updateGoals, completeStep } = useOnboarding();

  const [targetDrive, setTargetDrive] = useState(onboardingData.goals.targetDrive || 'August 2026 (Campus Phase 1)');
  const [targetCtc, setTargetCtc] = useState(onboardingData.goals.targetCtc || '14 - 24 LPA (Product Tier)');
  const [primaryGoal, setPrimaryGoal] = useState(onboardingData.goals.primaryGoal || 'Master Graph Algorithms & System Microservices');

  const driveOptions = [
    'August 2026 (Campus Phase 1)',
    'November 2026 (Campus Phase 2)',
    'Immediate Off-Campus / Referral Drive'
  ];

  const ctcOptions = [
    { id: '6 - 12 LPA (Solid Foundation)', title: '6 - 12 LPA', desc: 'Solid Foundation (Services / High Growth Startups)' },
    { id: '14 - 24 LPA (Product Tier)', title: '14 - 24 LPA', desc: 'Product Tier (Unicorns / Mid-Tier Tech Giants)' },
    { id: '25+ LPA (Top Tech / Quant)', title: '25+ LPA', desc: 'Top Tech / Quant (MAANG, Uber, High-Frequency Trading)' },
  ];

  const handleNext = (e) => {
    e.preventDefault();
    updateGoals({ targetDrive, targetCtc, primaryGoal });
    completeStep(6);
    navigate('/onboarding/analysis');
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto w-full">
      <div className="space-y-1">
        <h2 className="text-2xl font-extrabold text-white">Placement Timeline & CTC Targets</h2>
        <p className="text-xs text-slate-400">Step 6 of 7 — Define your target timeline and desired compensation bracket</p>
      </div>

      <form onSubmit={handleNext} className="p-6 sm:p-8 rounded-2xl bg-obsidian-card border border-obsidian-borderLight shadow-xl space-y-6">
        {/* Drive Season */}
        <div className="space-y-1.5">
          <label className="block text-xs font-semibold text-slate-200 flex items-center gap-1.5">
            <Calendar className="w-4 h-4 text-brand-400" /> Target Placement Drive Season
          </label>
          <select
            value={targetDrive}
            onChange={(e) => setTargetDrive(e.target.value)}
            className="w-full px-3.5 py-2.5 rounded-xl bg-obsidian-surface border border-obsidian-borderLight text-white focus:outline-none focus:border-brand-500 text-xs transition-colors"
          >
            {driveOptions.map((opt) => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
        </div>

        {/* Target CTC Bracket */}
        <div className="space-y-2">
          <label className="block text-xs font-semibold text-slate-200 flex items-center gap-1.5">
            <Trophy className="w-4 h-4 text-amber-400" /> Target CTC Bracket
          </label>
          <div className="grid sm:grid-cols-3 gap-3">
            {ctcOptions.map((c) => {
              const isSelected = targetCtc === c.id;
              return (
                <div
                  key={c.id}
                  onClick={() => setTargetCtc(c.id)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all space-y-1 ${
                    isSelected
                      ? 'bg-amber-500/15 border-amber-500 text-white shadow-md shadow-amber-500/10'
                      : 'bg-obsidian-surface border-obsidian-borderLight text-slate-400 hover:border-slate-600'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white">{c.title}</span>
                    {isSelected && <CheckCircle2 className="w-4 h-4 text-amber-400" />}
                  </div>
                  <p className="text-[10px] text-slate-400 leading-snug">{c.desc}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Primary Goal Text */}
        <div className="space-y-1.5">
          <label className="block text-xs font-semibold text-slate-200">
            Primary Prep Objective (Optional)
          </label>
          <input
            type="text"
            value={primaryGoal}
            onChange={(e) => setPrimaryGoal(e.target.value)}
            placeholder="e.g., Master Graph Algorithms & Spring Boot Microservices"
            className="w-full px-3.5 py-2.5 rounded-xl bg-obsidian-surface border border-obsidian-borderLight text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 text-xs transition-colors"
          />
        </div>

        <div className="flex items-center justify-between pt-4">
          <Button type="button" variant="outline" onClick={() => navigate('/onboarding/preferences')}>
            <ArrowLeft className="w-4 h-4 mr-1.5" /> Back
          </Button>
          <Button type="submit" variant="purple">
            Generate AI Placement Analysis <ArrowRight className="w-4 h-4 ml-1.5" />
          </Button>
        </div>
      </form>
    </div>
  );
};
