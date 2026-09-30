import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Trophy, ArrowRight, ArrowLeft, CheckCircle2 } from 'lucide-react';
import { useOnboarding } from '../../context/OnboardingContext';
import { Button } from '../../components/common/Button';

export const GoalsStep = () => {
  const navigate = useNavigate();
  const { onboardingData, updateGoals, completeStep } = useOnboarding();

  const [targetCtc, setTargetCtc] = useState(onboardingData.goals.targetCtc || '14 - 24 LPA (Product Tier)');

  const ctcOptions = [
    { id: '6 - 12 LPA (Solid Foundation)', title: '6 - 12 LPA', desc: 'Solid Foundation (Services / High Growth Startups)' },
    { id: '14 - 24 LPA (Product Tier)', title: '14 - 24 LPA', desc: 'Product Tier (Unicorns / Mid-Tier Tech Giants)' },
    { id: '25+ LPA (Top Tech / Quant)', title: '25+ LPA', desc: 'Top Tech / Quant (MAANG, Uber, High-Frequency Trading)' },
  ];

  const handleNext = (e) => {
    e.preventDefault();
    updateGoals({ targetCtc });
    completeStep(6);
    navigate('/onboarding/analysis');
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto w-full">
      <div className="space-y-1">
        <h2 className="text-2xl font-extrabold text-white">Placement CTC Target</h2>
        <p className="text-xs text-slate-400">Step 6 of 7 — Define your desired compensation bracket</p>
      </div>

      <form onSubmit={handleNext} className="p-6 sm:p-8 rounded-2xl bg-obsidian-card border border-obsidian-borderLight shadow-xl space-y-6">
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
