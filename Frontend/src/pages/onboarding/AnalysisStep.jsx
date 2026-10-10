import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, CheckCircle2, ArrowRight, ShieldCheck, Zap, Bot, Loader2, Award } from 'lucide-react';
import { useOnboarding } from '../../context/OnboardingContext';
import { useUser } from '../../context/UserContext';
import { aiService } from '../../services/aiService';
import { Button } from '../../components/common/Button';

import { settingsService } from '../../services/settingsService';
import { onboardingService } from '../../services/onboardingService';
import { readinessService } from '../../services/readinessService';
import { planningService } from '../../services/planningService';

export const AnalysisStep = () => {
  const navigate = useNavigate();
  const { onboardingData, markOnboardingComplete } = useOnboarding();
  const { updateUserProfile } = useUser();

  const [isLoading, setIsLoading] = useState(true);
  const [loadingStep, setLoadingStep] = useState(1);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    // Step progression timer
    const t1 = setTimeout(() => setLoadingStep(2), 600);
    const t2 = setTimeout(() => setLoadingStep(3), 1200);
    const t3 = setTimeout(() => setLoadingStep(4), 1800);

    // Call mock AI analysis service
    aiService.analyzeStudentProfile(onboardingData).then((res) => {
      setTimeout(() => {
        setAnalysisResult(res);
        setIsLoading(false);
      }, 2200);
    });

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  }, [onboardingData]);

  const handleFinish = async () => {
    if (isSubmitting) return;
    setIsSubmitting(true);

    // Sync onboarding values into UserContext & localStorage
    const profilePayload = {
      name: onboardingData.profile?.name || '',
      college: onboardingData.profile?.college || '',
      degree: onboardingData.profile?.degree || '',
      graduationYear: onboardingData.profile?.graduationYear || '2026',
      targetRole: onboardingData.career?.targetRole || 'Full Stack Engineer',
      secondaryRole: onboardingData.career?.secondaryRole || 'Cybersecurity Analyst & Engineer',
      companyTier: onboardingData.career?.companyTier || 'Tier-1 Product (MAANG / Unicorns)',
      githubHandle: onboardingData.integrations?.githubHandle || '',
      leetcodeHandle: onboardingData.integrations?.leetcodeHandle || '',
      resumeFileName: onboardingData.integrations?.resumeFileName || '',
      overallReadinessScore: analysisResult?.baselineScore || 85,
      dsaLevel: onboardingData.skills?.dsaLevel || 'Intermediate',
      sysDesignLevel: onboardingData.skills?.sysDesignLevel || 'Beginner',
      databaseLevel: onboardingData.skills?.databaseLevel || 'Intermediate',
      frameworkLevel: onboardingData.skills?.frameworkLevel || 'Advanced',
      selectedSkills: onboardingData.skills?.selectedSkills || [],
      mentorTone: onboardingData.preferences?.mentorTone || 'Socratic Coach (Probing Questions)',
      dailyGoalMinutes: onboardingData.preferences?.dailyGoalMinutes || '90',
      studyCadence: onboardingData.preferences?.studyCadence || 'Daily Evening Sprint',
      targetDrive: onboardingData.goals?.targetDrive || 'August 2026 (Campus Phase 1)',
      targetCtc: onboardingData.goals?.targetCtc || '14 - 24 LPA (Product Tier)',
      primaryGoal: onboardingData.goals?.primaryGoal || 'Master Technical Algorithms & System Architecture'
    };

    try {
      updateUserProfile(profilePayload);
    } catch (e) {}

    try {
      settingsService.saveSettings({
        ...settingsService.getSettings(),
        placement: {
          targetRole: profilePayload.targetRole,
          companyTier: profilePayload.companyTier,
          targetCtc: profilePayload.targetCtc,
          targetDrive: profilePayload.targetDrive
        },
        mentor: {
          ...settingsService.getSettings()?.mentor,
          mentorTone: profilePayload.mentorTone
        }
      });
    } catch (e) {}

    try {
      planningService.resetForRole(profilePayload.targetRole, profilePayload.selectedSkills);
    } catch (e) {}

    // Mark completed locally so client route guards never block entry
    markOnboardingComplete();

    // Trigger backend synchronization with strict timeout so backend latency or unavailability never traps user
    try {
      await Promise.race([
        Promise.allSettled([
          onboardingService.updateStep(7, {
            step_number: 7,
            career: {
              targetRole: profilePayload.targetRole,
              secondaryRole: profilePayload.secondaryRole,
              companyTier: profilePayload.companyTier
            },
            skills: {
              dsaLevel: profilePayload.dsaLevel,
              sysDesignLevel: profilePayload.sysDesignLevel,
              databaseLevel: profilePayload.databaseLevel,
              frameworkLevel: profilePayload.frameworkLevel,
              selectedSkills: profilePayload.selectedSkills
            },
            overallReadinessScore: profilePayload.overallReadinessScore
          }),
          onboardingService.completeOnboarding(),
          readinessService.calculateReadiness(profilePayload.targetRole)
        ]),
        new Promise((resolve) => setTimeout(resolve, 1200))
      ]);
    } catch (err) {
      console.warn('Backend complete sync note:', err);
    }

    navigate('/dashboard', { replace: true });
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto w-full text-center">
      {isLoading ? (
        /* LOADING STATE matching #analysis-loading-state */
        <div className="p-8 sm:p-12 rounded-2xl bg-obsidian-card border border-obsidian-borderLight shadow-2xl space-y-8 my-8">
          <div className="relative w-20 h-20 mx-auto flex items-center justify-center">
            <div className="absolute inset-0 rounded-full border-2 border-brand-500/30 border-t-brand-500 animate-spin" />
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-brand-600 via-ai-500 to-emerald-500 flex items-center justify-center shadow-lg shadow-brand-500/30">
              <Sparkles className="w-7 h-7 text-white" />
            </div>
          </div>

          <div className="space-y-2">
            <h2 className="text-2xl font-extrabold text-white">AI is building your placement profile...</h2>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              Synthesizing GitHub commit telemetry, LeetCode accuracy & Tier-1 target benchmarks
            </p>
          </div>

          <div className="max-w-md mx-auto space-y-3 text-left">
            <div className="flex items-center gap-3 p-3 rounded-xl bg-obsidian-surface border border-obsidian-borderLight">
              {loadingStep >= 1 ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              ) : (
                <Loader2 className="w-4 h-4 text-slate-500 animate-spin shrink-0" />
              )}
              <span className={`text-xs ${loadingStep >= 1 ? 'text-slate-200 font-semibold' : 'text-slate-500'}`}>
                Collecting profile & academic metadata
              </span>
            </div>

            <div className="flex items-center gap-3 p-3 rounded-xl bg-obsidian-surface border border-obsidian-borderLight">
              {loadingStep >= 2 ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              ) : loadingStep === 2 ? (
                <Loader2 className="w-4 h-4 text-brand-400 animate-spin shrink-0" />
              ) : (
                <div className="w-4 h-4 rounded-full border border-slate-700 shrink-0" />
              )}
              <span className={`text-xs ${loadingStep >= 2 ? 'text-slate-200 font-semibold' : 'text-slate-500'}`}>
                Analyzing GitHub repo complexity & LeetCode solve speed
              </span>
            </div>

            <div className="flex items-center gap-3 p-3 rounded-xl bg-obsidian-surface border border-obsidian-borderLight">
              {loadingStep >= 3 ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              ) : loadingStep === 3 ? (
                <Loader2 className="w-4 h-4 text-brand-400 animate-spin shrink-0" />
              ) : (
                <div className="w-4 h-4 rounded-full border border-slate-700 shrink-0" />
              )}
              <span className={`text-xs ${loadingStep >= 3 ? 'text-slate-200 font-semibold' : 'text-slate-500'}`}>
                Synthesizing 7-vector readiness score baseline
              </span>
            </div>

            <div className="flex items-center gap-3 p-3 rounded-xl bg-obsidian-surface border border-obsidian-borderLight">
              {loadingStep >= 4 ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              ) : loadingStep === 4 ? (
                <Loader2 className="w-4 h-4 text-brand-400 animate-spin shrink-0" />
              ) : (
                <div className="w-4 h-4 rounded-full border border-slate-700 shrink-0" />
              )}
              <span className={`text-xs ${loadingStep >= 4 ? 'text-slate-200 font-semibold' : 'text-slate-500'}`}>
                Compiling adaptive 90-day placement roadmap
              </span>
            </div>
          </div>
        </div>
      ) : (
        /* RESULT STATE matching #analysis-result-state */
        <div className="p-6 sm:p-8 rounded-2xl bg-obsidian-card border border-obsidian-borderLight shadow-2xl space-y-6 text-left animate-fadeIn">
          <div className="text-center space-y-2">
            <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center mx-auto text-emerald-400">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <h2 className="text-2xl font-extrabold text-white">Your Initial Placement Analysis</h2>
            <p className="text-xs text-slate-400">Step 7 of 7 — Placement profile calibrated & 90-day roadmap compiled</p>
          </div>

          <div className="p-4 rounded-xl bg-gradient-to-r from-brand-950/40 via-purple-950/30 to-obsidian-surface border border-brand-500/30 flex items-center justify-between">
            <div>
              <span className="text-[11px] font-mono uppercase text-brand-400 font-semibold">Readiness Score Baseline</span>
              <p className="text-xs text-slate-300">Benchmarked against {onboardingData.career.companyTier}</p>
            </div>
            <div className="text-3xl font-extrabold text-brand-400 font-mono">
              {analysisResult?.baselineScore || 78} <span className="text-xs text-slate-400 font-sans font-normal">/ 100</span>
            </div>
          </div>

          <div className="grid sm:grid-cols-3 gap-3 text-xs">
            <div className="p-3.5 rounded-xl bg-obsidian-surface border border-obsidian-borderLight space-y-1">
              <span className="text-[10px] text-slate-400 font-mono">TARGET ROLE</span>
              <p className="font-bold text-white truncate">{onboardingData?.career?.targetRole || 'Full Stack Engineer'}</p>
            </div>
            <div className="p-3.5 rounded-xl bg-obsidian-surface border border-obsidian-borderLight space-y-1">
              <span className="text-[10px] text-slate-400 font-mono">DAY 1 ROADMAP TASK</span>
              <p className="font-bold text-brand-400 truncate">{analysisResult?.day1RoadmapTask || 'LC 207: Course Schedule'}</p>
            </div>
            <div className="p-3.5 rounded-xl bg-obsidian-surface border border-obsidian-borderLight space-y-1">
              <span className="text-[10px] text-slate-400 font-mono">AI MENTOR PERSONA</span>
              <p className="font-bold text-ai-400 truncate">
                {onboardingData?.preferences?.mentorTone
                  ? onboardingData.preferences.mentorTone.split('(')[0].trim()
                  : 'Socratic Coach'}
              </p>
            </div>
          </div>



          <div className="space-y-2 pt-2">
            <h4 className="text-xs font-bold text-white flex items-center gap-1.5">
              <Zap className="w-4 h-4 text-brand-400" /> Key AI Recommendations for Sprint Phase 1
            </h4>
            <div className="space-y-2 text-xs text-slate-300">
              {analysisResult?.aiRecommendations?.map((rec, i) => (
                <div key={i} className="p-3 rounded-xl bg-obsidian-surface border border-obsidian-borderLight flex items-start gap-2.5">
                  <span className="text-brand-400 font-mono font-bold">•</span>
                  <span>{rec}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-4 text-center">
            <Button
              onClick={handleFinish}
              variant="purple"
              className="w-full py-3.5 text-sm flex items-center justify-center gap-2"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4.5 h-4.5 animate-spin" />
                  <span>Entering Dashboard...</span>
                </>
              ) : (
                <>
                  <span>Enter Copilot Dashboard</span>
                  <ArrowRight className="w-4.5 h-4.5 ml-2" />
                </>
              )}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};
