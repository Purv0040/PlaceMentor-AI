import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Code2, ArrowRight, ArrowLeft, Check, Plus } from 'lucide-react';
import { useOnboarding } from '../../context/OnboardingContext';
import { Button } from '../../components/common/Button';

export const SkillsStep = () => {
  const navigate = useNavigate();
  const { onboardingData, updateSkills, completeStep } = useOnboarding();

  const [dsaLevel, setDsaLevel] = useState(onboardingData.skills.dsaLevel || 'Intermediate');
  const [sysDesignLevel, setSysDesignLevel] = useState(onboardingData.skills.sysDesignLevel || 'Beginner');
  const [databaseLevel, setDatabaseLevel] = useState(onboardingData.skills.databaseLevel || 'Intermediate');
  const [frameworkLevel, setFrameworkLevel] = useState(onboardingData.skills.frameworkLevel || 'Advanced');
  const [selectedSkills, setSelectedSkills] = useState(
    onboardingData.skills.selectedSkills || ['Java', 'Spring Boot', 'Data Structures', 'SQL', 'Git']
  );

  const availableSkillChips = [
    'Java', 'Python', 'C++', 'JavaScript', 'Spring Boot', 'Node.js',
    'FastAPI', 'SQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Docker',
    'Kafka', 'Git', 'REST APIs', 'System Design', 'Dynamic Programming'
  ];

  const toggleSkill = (skill) => {
    setSelectedSkills(prev =>
      prev.includes(skill) ? prev.filter(s => s !== skill) : [...prev, skill]
    );
  };

  const handleNext = (e) => {
    e.preventDefault();
    updateSkills({
      dsaLevel,
      sysDesignLevel,
      databaseLevel,
      frameworkLevel,
      selectedSkills
    });
    completeStep(3);
    navigate('/onboarding/integrations');
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto w-full">
      <div className="space-y-1">
        <h2 className="text-2xl font-extrabold text-white">Skills Self-Assessment</h2>
        <p className="text-xs text-slate-400">Step 3 of 7 — Mark your current confidence level and technology stack</p>
      </div>

      <form onSubmit={handleNext} className="p-6 sm:p-8 rounded-2xl bg-obsidian-card border border-obsidian-borderLight shadow-xl space-y-6">
        {/* Domain Levels */}
        <div className="space-y-3">
          <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider font-mono">Domain Confidence Baseline</h3>

          <div className="space-y-2.5">
            <div className="p-3.5 rounded-xl bg-obsidian-surface border border-obsidian-borderLight flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <span className="text-xs font-medium text-slate-200">Data Structures & Algorithms</span>
              <select
                value={dsaLevel}
                onChange={(e) => setDsaLevel(e.target.value)}
                className="px-3 py-1.5 rounded-lg bg-obsidian-card border border-obsidian-borderLight text-slate-300 text-xs focus:outline-none focus:border-brand-500"
              >
                <option value="Beginner">Beginner (Arrays/Strings)</option>
                <option value="Intermediate">Intermediate (Trees/Graphs/DP)</option>
                <option value="Advanced">Advanced (Hard LC Drills)</option>
              </select>
            </div>

            <div className="p-3.5 rounded-xl bg-obsidian-surface border border-obsidian-borderLight flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <span className="text-xs font-medium text-slate-200">System Design & Architecture</span>
              <select
                value={sysDesignLevel}
                onChange={(e) => setSysDesignLevel(e.target.value)}
                className="px-3 py-1.5 rounded-lg bg-obsidian-card border border-obsidian-borderLight text-slate-300 text-xs focus:outline-none focus:border-brand-500"
              >
                <option value="Beginner">Beginner (Basic OOP/REST)</option>
                <option value="Intermediate">Intermediate (Microservices/Caching)</option>
                <option value="Advanced">Advanced (Distributed Systems)</option>
              </select>
            </div>

            <div className="p-3.5 rounded-xl bg-obsidian-surface border border-obsidian-borderLight flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <span className="text-xs font-medium text-slate-200">Database Management & SQL</span>
              <select
                value={databaseLevel}
                onChange={(e) => setDatabaseLevel(e.target.value)}
                className="px-3 py-1.5 rounded-lg bg-obsidian-card border border-obsidian-borderLight text-slate-300 text-xs focus:outline-none focus:border-brand-500"
              >
                <option value="Beginner">Beginner (Basic SELECT/JOIN)</option>
                <option value="Intermediate">Intermediate (Indexing/Transactions)</option>
                <option value="Advanced">Advanced (DBMS Tuning/Sharding)</option>
              </select>
            </div>

            <div className="p-3.5 rounded-xl bg-obsidian-surface border border-obsidian-borderLight flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <span className="text-xs font-medium text-slate-200">Backend Frameworks</span>
              <select
                value={frameworkLevel}
                onChange={(e) => setFrameworkLevel(e.target.value)}
                className="px-3 py-1.5 rounded-lg bg-obsidian-card border border-obsidian-borderLight text-slate-300 text-xs focus:outline-none focus:border-brand-500"
              >
                <option value="Beginner">Beginner (Tutorial Level)</option>
                <option value="Intermediate">Intermediate (Project API Level)</option>
                <option value="Advanced">Advanced (Production Deployment)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Skill Chips */}
        <div className="space-y-2">
          <label className="block text-xs font-semibold text-slate-200">
            Select Known Technologies & Languages ({selectedSkills.length} selected)
          </label>
          <div className="flex flex-wrap gap-2 pt-1">
            {availableSkillChips.map((chip) => {
              const isSelected = selectedSkills.includes(chip);
              return (
                <button
                  key={chip}
                  type="button"
                  onClick={() => toggleSkill(chip)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all flex items-center gap-1.5 ${
                    isSelected
                      ? 'bg-brand-500 text-white shadow-md shadow-brand-500/20 border border-brand-400/40'
                      : 'bg-obsidian-surface text-slate-400 hover:text-slate-200 border border-obsidian-borderLight'
                  }`}
                >
                  {chip}
                  {isSelected ? <Check className="w-3.5 h-3.5" /> : <Plus className="w-3.5 h-3.5 opacity-40" />}
                </button>
              );
            })}
          </div>
        </div>

        <div className="flex items-center justify-between pt-4">
          <Button type="button" variant="outline" onClick={() => navigate('/onboarding/career')}>
            <ArrowLeft className="w-4 h-4 mr-1.5" /> Back
          </Button>
          <Button type="submit" variant="primary">
            Next: Account Integrations <ArrowRight className="w-4 h-4 ml-1.5" />
          </Button>
        </div>
      </form>
    </div>
  );
};
