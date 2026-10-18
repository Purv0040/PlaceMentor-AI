import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, Calendar, ArrowRight, ArrowLeft, CheckCircle2 } from 'lucide-react';
import { useOnboarding } from '../../context/OnboardingContext';
import { Button } from '../../components/common/Button';

export const PreferencesStep = () => {
  const navigate = useNavigate();
  const { onboardingData, updatePreferences, completeStep } = useOnboarding();

  const [dailyGoalMinutes, setDailyGoalMinutes] = useState(onboardingData.preferences.dailyGoalMinutes || '90');
  const [studyDurationDays, setStudyDurationDays] = useState(onboardingData.preferences.studyDurationDays || '45');
  const [isCustomDuration, setIsCustomDuration] = useState(
    ![15, 30, 45, 60, 90].includes(Number(onboardingData.preferences.studyDurationDays || '45'))
  );
  const [customDaysInput, setCustomDaysInput] = useState(
    ![15, 30, 45, 60, 90].includes(Number(onboardingData.preferences.studyDurationDays || '45'))
      ? String(onboardingData.preferences.studyDurationDays || '45')
      : ''
  );

  const [isCustomDaily, setIsCustomDaily] = useState(
    ![30, 45, 90, 120, 180].includes(Number(onboardingData.preferences.dailyGoalMinutes || '90'))
  );
  const [customDailyInput, setCustomDailyInput] = useState(
    ![30, 45, 90, 120, 180].includes(Number(onboardingData.preferences.dailyGoalMinutes || '90'))
      ? String(onboardingData.preferences.dailyGoalMinutes || '90')
      : ''
  );

  const mentorTone = onboardingData.preferences.mentorTone || 'Socratic Coach (Probing Questions)';
  const [studyCadence, setStudyCadence] = useState(onboardingData.preferences.studyCadence || 'Daily Evening Sprint');

  const durationOptions = [
    { value: 15, label: '15 Days' },
    { value: 30, label: '30 Days' },
    { value: 45, label: '45 Days' },
    { value: 60, label: '60 Days' },
    { value: 90, label: '90 Days' },
  ];

  const dailyCommitOptions = [
    { value: '30', label: '30 Mins / Day', sub: 'Light Speed' },
    { value: '45', label: '45 Mins / Day', sub: 'Focused Sprint' },
    { value: '90', label: '90 Mins / Day', sub: 'Balanced Standard' },
    { value: '120', label: '2 Hours / Day', sub: 'Fast Track' },
    { value: '180', label: '3 Hours / Day', sub: 'Intensive Sprint' },
  ];

  const handleDurationSelect = (days) => {
    setIsCustomDuration(false);
    setStudyDurationDays(String(days));
  };

  const handleDailySelect = (mins) => {
    setIsCustomDaily(false);
    setDailyGoalMinutes(String(mins));
  };

  const handleNext = (e) => {
    e.preventDefault();
    const finalDays = isCustomDuration && customDaysInput ? customDaysInput : studyDurationDays;
    const finalDaily = isCustomDaily && customDailyInput ? customDailyInput : dailyGoalMinutes;

    const preferencesData = {
      dailyGoalMinutes: String(finalDaily || '90'),
      studyDurationDays: String(finalDays || '45'),
      mentorTone,
      studyCadence,
    };
    updatePreferences(preferencesData);
    completeStep(5, { preferences: preferencesData });
    navigate('/onboarding/goals');
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto w-full">
      <div className="space-y-1">
        <h2 className="text-2xl font-extrabold text-white">Study Cadence & Roadmap Runway</h2>
        <p className="text-xs text-slate-400">Step 5 of 7 — Choose your target preparation days and daily study cadence</p>
      </div>

      <form onSubmit={handleNext} className="p-6 sm:p-8 rounded-2xl bg-obsidian-card border border-obsidian-borderLight shadow-xl space-y-6">
        {/* Study Duration (Days) */}
        <div className="space-y-2">
          <label className="block text-xs font-semibold text-slate-200 flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <Calendar className="w-4 h-4 text-brand-400" /> Study Runway Duration
            </span>
            <span className="text-brand-300 font-bold text-xs">
              {isCustomDuration && customDaysInput ? `${customDaysInput} Days` : `${studyDurationDays} Days`}
            </span>
          </label>
          <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
            {durationOptions.map((opt) => {
              const isSelected = !isCustomDuration && Number(studyDurationDays) === opt.value;
              return (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => handleDurationSelect(opt.value)}
                  className={`p-3 rounded-xl border text-center transition-all ${
                    isSelected
                      ? 'bg-brand-500/20 border-brand-500 text-white font-bold shadow-md shadow-brand-500/10'
                      : 'bg-obsidian-surface border-obsidian-borderLight text-slate-400 hover:border-slate-600 hover:text-white'
                  }`}
                >
                  <span className="text-xs">{opt.label}</span>
                </button>
              );
            })}
            <button
              type="button"
              onClick={() => {
                setIsCustomDuration(true);
                if (!customDaysInput) setCustomDaysInput(String(studyDurationDays || '45'));
              }}
              className={`p-3 rounded-xl border text-center transition-all ${
                isCustomDuration
                  ? 'bg-brand-500/20 border-brand-500 text-white font-bold shadow-md shadow-brand-500/10'
                  : 'bg-obsidian-surface border-obsidian-borderLight text-slate-400 hover:border-slate-600 hover:text-white'
              }`}
            >
              <span className="text-xs">Custom</span>
            </button>
          </div>
          {isCustomDuration && (
            <div className="flex items-center gap-2 pt-1">
              <input
                type="number"
                min="1"
                max="365"
                value={customDaysInput}
                onChange={(e) => {
                  setCustomDaysInput(e.target.value);
                  setStudyDurationDays(e.target.value);
                }}
                placeholder="Days (1–365)"
                className="w-36 px-3 py-1.5 rounded-lg bg-obsidian-surface border border-obsidian-borderLight text-white text-xs focus:outline-none focus:border-brand-500"
              />
              <span className="text-xs text-slate-400">total roadmap days</span>
            </div>
          )}
        </div>

        {/* Daily Study Time */}
        <div className="space-y-2 pt-2 border-t border-obsidian-borderLight/60">
          <label className="block text-xs font-semibold text-slate-200 flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <Clock className="w-4 h-4 text-brand-400" /> Daily Preparation Commitment
            </span>
            <span className="text-brand-300 font-bold text-xs">
              {isCustomDaily && customDailyInput
                ? `${customDailyInput} Mins/day`
                : `${dailyGoalMinutes} Mins/day`}
            </span>
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
            {dailyCommitOptions.map((opt) => {
              const isSelected = !isCustomDaily && dailyGoalMinutes === opt.value;
              return (
                <div
                  key={opt.value}
                  onClick={() => handleDailySelect(opt.value)}
                  className={`p-3.5 rounded-xl border cursor-pointer transition-all space-y-1 ${
                    isSelected
                      ? 'bg-brand-500/20 border-brand-500 text-white shadow-md shadow-brand-500/10'
                      : 'bg-obsidian-surface border-obsidian-borderLight text-slate-400 hover:border-slate-600'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white">{opt.label}</span>
                    {isSelected && <CheckCircle2 className="w-4 h-4 text-brand-400" />}
                  </div>
                  <p className="text-[10px] text-slate-400 leading-snug">{opt.sub}</p>
                </div>
              );
            })}
            <div
              onClick={() => {
                setIsCustomDaily(true);
                if (!customDailyInput) setCustomDailyInput(String(dailyGoalMinutes || '60'));
              }}
              className={`p-3.5 rounded-xl border cursor-pointer transition-all space-y-1 ${
                isCustomDaily
                  ? 'bg-brand-500/20 border-brand-500 text-white shadow-md shadow-brand-500/10'
                  : 'bg-obsidian-surface border-obsidian-borderLight text-slate-400 hover:border-slate-600'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-white">Custom Mins</span>
                {isCustomDaily && <CheckCircle2 className="w-4 h-4 text-brand-400" />}
              </div>
              <p className="text-[10px] text-slate-400 leading-snug">Personalized Pace</p>
            </div>
          </div>
          {isCustomDaily && (
            <div className="flex items-center gap-2 pt-1">
              <input
                type="number"
                min="15"
                max="480"
                value={customDailyInput}
                onChange={(e) => {
                  setCustomDailyInput(e.target.value);
                  setDailyGoalMinutes(e.target.value);
                }}
                placeholder="Minutes (15–480)"
                className="w-36 px-3 py-1.5 rounded-lg bg-obsidian-surface border border-obsidian-borderLight text-white text-xs focus:outline-none focus:border-brand-500"
              />
              <span className="text-xs text-slate-400">minutes per day</span>
            </div>
          )}
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
