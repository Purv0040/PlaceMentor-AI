import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Github, Code2, FileText, ArrowRight, ArrowLeft, CheckCircle2, Upload, Link2 } from 'lucide-react';
import { useOnboarding } from '../../context/OnboardingContext';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';

export const IntegrationsStep = () => {
  const navigate = useNavigate();
  const { onboardingData, updateIntegrations, completeStep } = useOnboarding();

  const [githubConnected, setGithubConnected] = useState(onboardingData.integrations.githubConnected ?? true);
  const [githubHandle, setGithubHandle] = useState(onboardingData.integrations.githubHandle || 'alexpatel-dev');
  const [leetcodeConnected, setLeetcodeConnected] = useState(onboardingData.integrations.leetcodeConnected ?? true);
  const [leetcodeHandle, setLeetcodeHandle] = useState(onboardingData.integrations.leetcodeHandle || 'alex_patel99');
  const [resumeUploaded, setResumeUploaded] = useState(onboardingData.integrations.resumeUploaded ?? true);
  const [resumeFileName, setResumeFileName] = useState(onboardingData.integrations.resumeFileName || 'Alex_Patel_Backend_Resume.pdf');

  const handleNext = (e) => {
    e.preventDefault();
    updateIntegrations({
      githubConnected,
      githubHandle,
      leetcodeConnected,
      leetcodeHandle,
      resumeUploaded,
      resumeFileName
    });
    completeStep(4);
    navigate('/onboarding/preferences');
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto w-full">
      <div className="space-y-1">
        <h2 className="text-2xl font-extrabold text-white">Connect Preparation Telemetry</h2>
        <p className="text-xs text-slate-400">Step 4 of 7 — Enable GitHub, LeetCode, and Resume sync for real-time baseline auditing</p>
      </div>

      <form onSubmit={handleNext} className="p-6 sm:p-8 rounded-2xl bg-obsidian-card border border-obsidian-borderLight shadow-xl space-y-6">
        {/* GitHub Integration Card */}
        <div className="p-4 sm:p-5 rounded-xl bg-obsidian-surface border border-obsidian-borderLight space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-obsidian-card text-white">
                <Github className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-white">GitHub Account Integration</h4>
                <p className="text-[11px] text-slate-400">Auto-audit commit frequency & repo architecture complexity</p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setGithubConnected(!githubConnected)}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition-colors flex items-center gap-1 ${
                githubConnected
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  : 'bg-obsidian-card text-slate-400 hover:text-white border border-obsidian-borderLight'
              }`}
            >
              {githubConnected ? <><CheckCircle2 className="w-3.5 h-3.5" /> Connected</> : <><Link2 className="w-3.5 h-3.5" /> Connect</>}
            </button>
          </div>

          {githubConnected && (
            <Input
              label="GitHub Handle"
              id="github-handle"
              value={githubHandle}
              onChange={(e) => setGithubHandle(e.target.value)}
              placeholder="alexpatel-dev"
            />
          )}
        </div>

        {/* LeetCode Sync Card */}
        <div className="p-4 sm:p-5 rounded-xl bg-obsidian-surface border border-obsidian-borderLight space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-obsidian-card text-amber-400">
                <Code2 className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-white">LeetCode Analytics Sync</h4>
                <p className="text-[11px] text-slate-400">Fetch solved counts & topic accuracy stats</p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setLeetcodeConnected(!leetcodeConnected)}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition-colors flex items-center gap-1 ${
                leetcodeConnected
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  : 'bg-obsidian-card text-slate-400 hover:text-white border border-obsidian-borderLight'
              }`}
            >
              {leetcodeConnected ? <><CheckCircle2 className="w-3.5 h-3.5" /> Connected</> : <><Link2 className="w-3.5 h-3.5" /> Connect</>}
            </button>
          </div>

          {leetcodeConnected && (
            <Input
              label="LeetCode Username"
              id="leetcode-handle"
              value={leetcodeHandle}
              onChange={(e) => setLeetcodeHandle(e.target.value)}
              placeholder="alex_patel99"
            />
          )}
        </div>

        {/* Resume Dropzone Card */}
        <div className="p-4 sm:p-5 rounded-xl bg-obsidian-surface border border-obsidian-borderLight space-y-3">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-obsidian-card text-brand-400">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-white">Resume ATS Audit Document</h4>
              <p className="text-[11px] text-slate-400">Upload PDF for AI bullet point & keyword scoring</p>
            </div>
          </div>

          {resumeUploaded ? (
            <div className="p-3 rounded-xl bg-obsidian-card border border-brand-500/30 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2 text-slate-200">
                <FileText className="w-4 h-4 text-brand-400" />
                <span className="font-mono font-medium">{resumeFileName}</span>
              </div>
              <button
                type="button"
                onClick={() => setResumeUploaded(false)}
                className="text-[11px] text-rose-400 hover:underline"
              >
                Remove
              </button>
            </div>
          ) : (
            <div
              onClick={() => {
                setResumeFileName('Alex_Patel_Backend_Resume.pdf');
                setResumeUploaded(true);
              }}
              className="border-2 border-dashed border-obsidian-borderLight hover:border-brand-500/50 rounded-xl p-6 text-center cursor-pointer transition-colors space-y-2"
            >
              <Upload className="w-6 h-6 text-slate-500 mx-auto" />
              <p className="text-xs font-semibold text-slate-300">Click to upload or drag & drop Resume PDF</p>
              <p className="text-[10px] text-slate-500">PDF format, max 5MB</p>
            </div>
          )}
        </div>

        <div className="flex items-center justify-between pt-4">
          <Button type="button" variant="outline" onClick={() => navigate('/onboarding/skills')}>
            <ArrowLeft className="w-4 h-4 mr-1.5" /> Back
          </Button>
          <Button type="submit" variant="primary">
            Next: Prep Preferences <ArrowRight className="w-4 h-4 ml-1.5" />
          </Button>
        </div>
      </form>
    </div>
  );
};
