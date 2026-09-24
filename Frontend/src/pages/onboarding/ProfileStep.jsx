import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, School, GraduationCap, ArrowRight } from 'lucide-react';
import { useOnboarding } from '../../context/OnboardingContext';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';

export const ProfileStep = () => {
  const navigate = useNavigate();
  const { onboardingData, updateProfile, completeStep } = useOnboarding();

  const [name, setName] = useState(onboardingData.profile.name || 'Alex Patel');
  const [college, setCollege] = useState(onboardingData.profile.college || 'CSPIT');
  const [degree, setDegree] = useState(onboardingData.profile.degree || 'B.Tech IT');
  const [graduationYear, setGraduationYear] = useState(onboardingData.profile.graduationYear || '2027');
  const [errors, setErrors] = useState({});

  const validate = () => {
    const errs = {};
    if (!name.trim()) errs.name = 'Full name is required.';
    if (!college.trim()) errs.college = 'College name is required.';
    if (!degree.trim()) errs.degree = 'Degree & branch is required.';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleNext = (e) => {
    e.preventDefault();
    if (!validate()) return;

    updateProfile({ name, college, degree, graduationYear });
    completeStep(1);
    navigate('/onboarding/career');
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto w-full">
      <div className="space-y-1">
        <h2 className="text-2xl font-extrabold text-white">Personal & Academic Profile</h2>
        <p className="text-xs text-slate-400">Step 1 of 7 — Tell us about yourself to calibrate target benchmarks</p>
      </div>

      <form onSubmit={handleNext} className="p-6 sm:p-8 rounded-2xl bg-obsidian-card border border-obsidian-borderLight shadow-xl space-y-5">
        <Input
          label="Full Name"
          id="profile-name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          error={errors.name}
          icon={User}
          placeholder="Alex Patel"
          required
        />

        <div className="grid sm:grid-cols-2 gap-4">
          <Input
            label="College / University"
            id="profile-college"
            value={college}
            onChange={(e) => setCollege(e.target.value)}
            error={errors.college}
            icon={School}
            placeholder="CSPIT"
            required
          />

          <Input
            label="Degree & Branch"
            id="profile-degree"
            value={degree}
            onChange={(e) => setDegree(e.target.value)}
            error={errors.degree}
            icon={GraduationCap}
            placeholder="B.Tech IT"
            required
          />
        </div>

        <div className="space-y-1.5">
          <label htmlFor="graduation-year" className="block text-xs font-medium text-slate-300">
            Graduation Year <span className="text-rose-400">*</span>
          </label>
          <select
            id="graduation-year"
            value={graduationYear}
            onChange={(e) => setGraduationYear(e.target.value)}
            className="w-full px-3.5 py-2.5 rounded-xl bg-obsidian-surface border border-obsidian-borderLight text-white focus:outline-none focus:border-brand-500 text-xs transition-colors"
          >
            <option value="2025">2025 (Final Year)</option>
            <option value="2026">2026 (Pre-Final Year)</option>
            <option value="2027">2027 (2nd Year)</option>
            <option value="2028">2028 (1st Year)</option>
          </select>
        </div>

        <div className="flex justify-end pt-4">
          <Button type="submit" variant="primary">
            Next: Target Career <ArrowRight className="w-4 h-4 ml-1.5" />
          </Button>
        </div>
      </form>
    </div>
  );
};
