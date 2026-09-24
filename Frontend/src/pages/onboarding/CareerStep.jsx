import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Target, ArrowRight, ArrowLeft, CheckCircle2, Server, Layout, Cpu, Code } from 'lucide-react';
import { useOnboarding } from '../../context/OnboardingContext';
import { Button } from '../../components/common/Button';

export const CareerStep = () => {
  const navigate = useNavigate();
  const { onboardingData, updateCareer, completeStep } = useOnboarding();

  const [targetRole, setTargetRole] = useState(onboardingData.career.targetRole || 'Backend Developer');
  const [secondaryRole, setSecondaryRole] = useState(onboardingData.career.secondaryRole || 'AI/ML Engineer');
  const [companyTier, setCompanyTier] = useState(onboardingData.career.companyTier || 'Tier-1 Product (MAANG / Unicorns)');

  const roles = [
    { id: 'Backend Developer', label: 'Backend Developer', sub: 'Java / Python / Node / Microservices', icon: Server },
    { id: 'Full Stack Engineer', label: 'Full Stack Engineer', sub: 'React / Node / Postgres / REST', icon: Code },
    { id: 'AI/ML Engineer', label: 'AI/ML Engineer', sub: 'Python / PyTorch / LLMs / MLOps', icon: Cpu },
    { id: 'Frontend Engineer', label: 'Frontend Engineer', sub: 'React / TypeScript / Tailwind / Next.js', icon: Layout },
  ];

  const tiers = [
    { id: 'Tier-1 Product (MAANG / Unicorns)', label: 'Tier-1 Product', desc: 'Google, Uber, Amazon, Razorpay (20+ LPA)' },
    { id: 'Tier-2 Mid-Size & High-Growth', label: 'Tier-2 Mid-Size', desc: 'Series B+ Startups, Mid-tier Tech (10-18 LPA)' },
    { id: 'IT Services & Campus Recruiters', label: 'IT Services', desc: 'TCS, Infosys, Wipro, Accenture (4-8 LPA)' },
  ];

  const handleNext = (e) => {
    e.preventDefault();
    updateCareer({ targetRole, secondaryRole, companyTier });
    completeStep(2);
    navigate('/onboarding/skills');
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto w-full">
      <div className="space-y-1">
        <h2 className="text-2xl font-extrabold text-white">Target Career & Role</h2>
        <p className="text-xs text-slate-400">Step 2 of 7 — Define your target role and benchmark company expectations</p>
      </div>

      <form onSubmit={handleNext} className="p-6 sm:p-8 rounded-2xl bg-obsidian-card border border-obsidian-borderLight shadow-xl space-y-6">
        {/* Primary Role Cards */}
        <div className="space-y-2">
          <label className="block text-xs font-semibold text-slate-200">
            Primary Target Role <span className="text-rose-400">*</span>
          </label>
          <div className="grid sm:grid-cols-2 gap-3">
            {roles.map((role) => {
              const Icon = role.icon;
              const isSelected = targetRole === role.id;

              return (
                <div
                  key={role.id}
                  onClick={() => setTargetRole(role.id)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all flex items-start gap-3 ${
                    isSelected
                      ? 'bg-brand-500/15 border-brand-500 text-white shadow-lg shadow-brand-500/10'
                      : 'bg-obsidian-surface border-obsidian-borderLight text-slate-300 hover:border-slate-600'
                  }`}
                >
                  <div className={`p-2 rounded-lg ${isSelected ? 'bg-brand-500 text-white' : 'bg-obsidian-card text-slate-400'}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-white truncate">{role.label}</span>
                      {isSelected && <CheckCircle2 className="w-4 h-4 text-brand-400 shrink-0" />}
                    </div>
                    <p className="text-[11px] text-slate-400 mt-0.5">{role.sub}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Secondary Role */}
        <div className="space-y-1.5">
          <label className="block text-xs font-semibold text-slate-200">Secondary Role Track (Optional)</label>
          <select
            value={secondaryRole}
            onChange={(e) => setSecondaryRole(e.target.value)}
            className="w-full px-3.5 py-2.5 rounded-xl bg-obsidian-surface border border-obsidian-borderLight text-white focus:outline-none focus:border-brand-500 text-xs transition-colors"
          >
            <option value="AI/ML Engineer">AI/ML Engineer</option>
            <option value="Full Stack Engineer">Full Stack Engineer</option>
            <option value="DevOps & Cloud Engineer">DevOps & Cloud Engineer</option>
            <option value="Data Engineer">Data Engineer</option>
          </select>
        </div>

        {/* Company Tier */}
        <div className="space-y-2">
          <label className="block text-xs font-semibold text-slate-200">Target Company Tier</label>
          <div className="grid sm:grid-cols-3 gap-3">
            {tiers.map((t) => {
              const isSelected = companyTier === t.id;
              return (
                <div
                  key={t.id}
                  onClick={() => setCompanyTier(t.id)}
                  className={`p-3.5 rounded-xl border cursor-pointer transition-all space-y-1 ${
                    isSelected
                      ? 'bg-brand-500/15 border-brand-500 text-white'
                      : 'bg-obsidian-surface border-obsidian-borderLight text-slate-400 hover:border-slate-600'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white">{t.label}</span>
                    {isSelected && <CheckCircle2 className="w-3.5 h-3.5 text-brand-400" />}
                  </div>
                  <p className="text-[10px] text-slate-400 leading-snug">{t.desc}</p>
                </div>
              );
            })}
          </div>
        </div>

        <div className="flex items-center justify-between pt-4">
          <Button type="button" variant="outline" onClick={() => navigate('/onboarding/profile')}>
            <ArrowLeft className="w-4 h-4 mr-1.5" /> Back
          </Button>
          <Button type="submit" variant="primary">
            Next: Skills Self-Assessment <ArrowRight className="w-4 h-4 ml-1.5" />
          </Button>
        </div>
      </form>
    </div>
  );
};
