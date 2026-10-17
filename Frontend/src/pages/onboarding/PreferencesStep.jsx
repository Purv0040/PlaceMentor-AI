import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, ArrowRight, ArrowLeft, CheckCircle2 } from 'lucide-react';
import { useOnboarding } from '../../context/OnboardingContext';
import { Button } from '../../components/common/Button';

export const PreferencesStep = () => {
  const navigate = useNavigate();
  const { onboardingData, updatePreferences, completeStep } = useOnboarding();

  const [dailyGoalMinutes, setDailyGoalMinutes] = useState(onboardingData.preferences.dailyGoalMinutes || '90');
  const mentorTone = onboardingData.preferences.mentorTone || 'Socratic Coach (Probing Questions)';
  const [studyCadence, setStudyCadence] = useState(onboardingData.preferences.studyCadence || 'Daily Evening Sprint');

  const commitOptions = [
    { value: '45', title: '45 Mins / Day', sub: 'Light Speed (Maintenance & Revision)' },
    { value: '90', title: '90 Mins / Day', sub: 'Balanced Standard (Recommended Sprint)' },
    { value: '180', title: '3 Hours / Day', sub: 'Placement Marathon (Intensive Bootcamp)' },
  ];

  const handleNext = (e) => {
    e.preventDefault();
    const preferencesData = { dailyGoalMinutes, mentorTone, studyCadence };
    updatePreferences(preferencesData);
    completeStep(5, { preferences: preferencesData });
    navigate('/onboarding/goals');
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto w-full">
      <div className="space-y-1">
        <h2 className="text-2xl font-extrabold text-white">Study Cadence & Preferences</h2>
        <p className="text-xs text-slate-400">Step 5 of 7 — Customize your daily preparation commitment</p>
      </div>

      <form onSubmit={handleNext} className="p-6 sm:p-8 rounded-2xl bg-obsidian-card border border-obsidian-borderLight shadow-xl space-y-6">
        {/* Daily Prep Time */}
        <div className="space-y-2">
          <label className="block text-xs font-semibold text-slate-200 flex items-center gap-1.5">
            <Clock className="w-4 h-4 text-brand-400" /> Daily Preparation Commitment
          </label>
          <div className="grid sm:grid-cols-3 gap-3">
            {commitOptions.map((opt) => {
              const isSelected = dailyGoalMinutes === opt.value;
              return (
                <div
                  key={opt.value}
                  onClick={() => setDailyGoalMinutes(opt.value)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all space-y-1 ${
                    isSelected
                      ? 'bg-brand-500/15 border-brand-500 text-white shadow-md shadow-brand-500/10'
                      : 'bg-obsidian-surface border-obsidian-borderLight text-slate-400 hover:border-slate-600'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white">{opt.title}</span>
                    {isSelected && <CheckCircle2 className="w-4 h-4 text-brand-400" />}
                  </div>
                  <p className="text-[10px] text-slate-400 leading-snug">{opt.sub}</p>
                </div>
              );
            })}
          </div>
        </div>

        <div className="flex items-center justify-between pt-4">
          <Button type="button" variant="outline" onClick={() => navigate('/onboarding/integrations')}>
            <ArrowLeft className="w-4 h-4 mr-1.5" /> Back
          </Button>
          <Button type="submit" variant="primary">
            Next: Placement Goals <ArrowRight className="w-4 h-4 ml-1.5" />
          </Button>
        </div>
      </form>
    </div>
  );
};
