import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Code2, ArrowRight, ArrowLeft, Check, Plus, Target, Sparkles } from 'lucide-react';
import { useOnboarding } from '../../context/OnboardingContext';
import { Button } from '../../components/common/Button';

export const ROLE_SKILL_CONFIGS = {
  'AWS / DevOps & Cloud Engineer': {
    domains: [
      { key: 'dsaLevel', label: 'Data Structures & Algorithms', options: ['Beginner (Arrays/Strings)', 'Intermediate (Trees/Graphs/DP)', 'Advanced (Hard LC Drills)'] },
      { key: 'sysDesignLevel', label: 'Linux, Scripting & Server Automation', options: ['Beginner (Bash/Shell)', 'Intermediate (Python/Automation)', 'Advanced (Kernel/Networking Tuning)'] },
      { key: 'databaseLevel', label: 'Containerization & Kubernetes Cluster Ops', options: ['Beginner (Docker Basics)', 'Intermediate (Docker Compose/K8s)', 'Advanced (Helm/K8s Cluster Opt)'] },
      { key: 'frameworkLevel', label: 'AWS & Infrastructure as Code (IaC)', options: ['Beginner (AWS EC2/S3)', 'Intermediate (Terraform/CloudFormation)', 'Advanced (Multi-Region Cloud Architecture)'] },
    ],
    defaultChips: ['AWS', 'Docker', 'Kubernetes', 'Terraform', 'Linux', 'GitHub Actions', 'Python', 'Git'],
    availableChips: [
      'AWS', 'Docker', 'Kubernetes', 'Terraform', 'Linux', 'Bash Scripting', 'Python', 'Go',
      'GitHub Actions', 'Jenkins', 'Prometheus', 'Grafana', 'Ansible', 'Git', 'Nginx', 'CloudWatch'
    ]
  },
  'Cybersecurity Analyst & Engineer': {
    domains: [
      { key: 'dsaLevel', label: 'Data Structures & Algorithms', options: ['Beginner (Arrays/Strings)', 'Intermediate (Trees/Graphs/Crypto Alg)', 'Advanced (Hard LC & Security Drills)'] },
      { key: 'sysDesignLevel', label: 'Network Security, Cryptography & PKI', options: ['Beginner (TCP-IP/OSI/TLS)', 'Intermediate (Firewalls/IDS/IPS/PKI)', 'Advanced (Zero Trust/VPN/Network Opt)'] },
      { key: 'databaseLevel', label: 'Application Security & PenTesting', options: ['Beginner (OWASP Top 10)', 'Intermediate (Penetration Testing/DAST)', 'Advanced (Secure Code Audit/Fuzzing)'] },
      { key: 'frameworkLevel', label: 'SIEM, Incident Response & SOC Operations', options: ['Beginner (Log Analysis)', 'Intermediate (Splunk/Wireshark/SOC)', 'Advanced (Threat Hunting/Digital Forensics)'] },
    ],
    defaultChips: ['Python', 'Linux', 'Wireshark', 'Metasploit', 'OWASP Top 10', 'Burp Suite', 'Docker', 'Git'],
    availableChips: [
      'Python', 'Bash Scripting', 'Linux Security', 'Wireshark', 'Nmap', 'Burp Suite', 'Metasploit',
      'Splunk', 'Cryptography', 'OWASP Top 10', 'Docker', 'Git', 'AWS Security', 'SIEM & SOC', 'Network Security'
    ]
  },
  'Full Stack Engineer': {
    domains: [
      { key: 'dsaLevel', label: 'Data Structures & Algorithms', options: ['Beginner (Arrays/Strings)', 'Intermediate (Trees/Graphs/DP)', 'Advanced (Hard LC Drills)'] },
      { key: 'sysDesignLevel', label: 'Frontend Architecture & UI Engineering', options: ['Beginner (HTML/CSS/Basic JS)', 'Intermediate (React/Next.js State)', 'Advanced (Performance & SSR)'] },
      { key: 'databaseLevel', label: 'Backend APIs & REST/GraphQL Services', options: ['Beginner (Basic Express/FastAPI)', 'Intermediate (Auth/ORM/REST)', 'Advanced (Scalable Microservices)'] },
      { key: 'frameworkLevel', label: 'Database & Cloud Deployment', options: ['Beginner (Basic SQL/Mongo)', 'Intermediate (ORM/Docker)', 'Advanced (CI/CD/Kubernetes)'] },
    ],
    defaultChips: ['React.js', 'Node.js', 'JavaScript', 'TypeScript', 'PostgreSQL', 'Git', 'Tailwind CSS'],
    availableChips: [
      'JavaScript', 'TypeScript', 'React.js', 'Next.js', 'Tailwind CSS', 'Node.js', 'Express.js',
      'Python', 'FastAPI', 'Java', 'Spring Boot', 'PostgreSQL', 'MongoDB', 'Redis', 'Docker',
      'Git', 'REST APIs', 'GraphQL', 'System Design'
    ]
  },
  'AI/ML Engineer': {
    domains: [
      { key: 'dsaLevel', label: 'Data Structures & Algorithms', options: ['Beginner (Arrays/Strings)', 'Intermediate (Trees/Graphs/DP)', 'Advanced (Hard LC Drills)'] },
      { key: 'sysDesignLevel', label: 'Machine Learning Foundations & Math', options: ['Beginner (Linear Algebra/Scikit-Learn)', 'Intermediate (Feature Eng/Regression/Trees)', 'Advanced (Custom Estimators/Opt)'] },
      { key: 'databaseLevel', label: 'Deep Learning & Neural Networks', options: ['Beginner (MLP/CNN Basics)', 'Intermediate (PyTorch/Transformers)', 'Advanced (Fine-Tuning/LLMs)'] },
      { key: 'frameworkLevel', label: 'MLOps & Model Deployment', options: ['Beginner (Jupyter/Export)', 'Intermediate (FastAPI/Docker)', 'Advanced (MLflow/Kubeflow/CUDA)'] },
    ],
    defaultChips: ['Python', 'PyTorch', 'Scikit-Learn', 'Pandas & NumPy', 'FastAPI', 'Git', 'Docker'],
    availableChips: [
      'Python', 'C++', 'PyTorch', 'TensorFlow', 'Scikit-Learn', 'Pandas & NumPy', 'HuggingFace / LLMs',
      'FastAPI', 'Docker', 'MLflow', 'CUDA', 'OpenCV', 'Git', 'REST APIs', 'SQL', 'Vector DBs (Chroma/FAISS)'
    ]
  }
};

export const SkillsStep = () => {
  const navigate = useNavigate();
  const { onboardingData, updateSkills, completeStep } = useOnboarding();

  const targetRole = onboardingData.career?.targetRole || 'Full Stack Engineer';
  const roleConfig = ROLE_SKILL_CONFIGS[targetRole] || ROLE_SKILL_CONFIGS['AWS / DevOps & Cloud Engineer'] || ROLE_SKILL_CONFIGS['Full Stack Engineer'];

  const [dsaLevel, setDsaLevel] = useState(onboardingData.skills?.dsaLevel || 'Intermediate');
  const [sysDesignLevel, setSysDesignLevel] = useState(onboardingData.skills?.sysDesignLevel || 'Beginner');
  const [databaseLevel, setDatabaseLevel] = useState(onboardingData.skills?.databaseLevel || 'Intermediate');
  const [frameworkLevel, setFrameworkLevel] = useState(onboardingData.skills?.frameworkLevel || 'Advanced');
  const [selectedSkills, setSelectedSkills] = useState(
    onboardingData.skills?.selectedSkills?.length > 0
      ? onboardingData.skills.selectedSkills
      : roleConfig.defaultChips
  );

  useEffect(() => {
    if (!onboardingData.skills?.selectedSkills || onboardingData.skills.selectedSkills.length === 0) {
      setSelectedSkills(roleConfig.defaultChips);
    }
  }, [targetRole]);

  const toggleSkill = (skill) => {
    setSelectedSkills(prev =>
      prev.includes(skill) ? prev.filter(s => s !== skill) : [...prev, skill]
    );
  };

  const handleNext = (e) => {
    e.preventDefault();
    const skillsData = {
      dsaLevel,
      sysDesignLevel,
      databaseLevel,
      frameworkLevel,
      selectedSkills
    };
    updateSkills(skillsData);
    completeStep(3, { skills: skillsData });
    navigate('/onboarding/integrations');
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto w-full">
      <div className="space-y-1">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-extrabold text-white">Skills Self-Assessment</h2>
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-brand-500/20 border border-brand-500/30 text-brand-400 text-xs font-mono font-semibold">
            <Sparkles className="w-3.5 h-3.5" /> Tailored for: {targetRole}
          </span>
        </div>
        <p className="text-xs text-slate-400">Step 3 of 7 — Mark your current confidence level and technology stack for {targetRole}</p>
      </div>

      <form onSubmit={handleNext} className="p-6 sm:p-8 rounded-2xl bg-obsidian-card border border-obsidian-borderLight shadow-xl space-y-6">
        {/* Domain Levels */}
        <div className="space-y-3">
          <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider font-mono">
            {targetRole} Domain Baseline
          </h3>

          <div className="space-y-2.5">
            {/* Domain 1: Always Data Structures & Algorithms */}
            <div className="p-3.5 rounded-xl bg-obsidian-surface border border-obsidian-borderLight flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <span className="text-xs font-medium text-white flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-brand-500" />
                {roleConfig.domains[0].label}
              </span>
              <select
                value={dsaLevel}
                onChange={(e) => setDsaLevel(e.target.value)}
                className="px-3 py-1.5 rounded-lg bg-obsidian-card border border-obsidian-borderLight text-slate-200 text-xs focus:outline-none focus:border-brand-500"
              >
                {roleConfig.domains[0].options.map((opt) => (
                  <option key={opt} value={opt.split(' ')[0]}>{opt}</option>
                ))}
              </select>
            </div>

            {/* Domain 2: Dynamic Role Spec */}
            <div className="p-3.5 rounded-xl bg-obsidian-surface border border-obsidian-borderLight flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <span className="text-xs font-medium text-white flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-purple-500" />
                {roleConfig.domains[1].label}
              </span>
              <select
                value={sysDesignLevel}
                onChange={(e) => setSysDesignLevel(e.target.value)}
                className="px-3 py-1.5 rounded-lg bg-obsidian-card border border-obsidian-borderLight text-slate-200 text-xs focus:outline-none focus:border-brand-500"
              >
                {roleConfig.domains[1].options.map((opt) => (
                  <option key={opt} value={opt.split(' ')[0]}>{opt}</option>
                ))}
              </select>
            </div>

            {/* Domain 3: Dynamic Role Spec */}
            <div className="p-3.5 rounded-xl bg-obsidian-surface border border-obsidian-borderLight flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <span className="text-xs font-medium text-white flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-500" />
                {roleConfig.domains[2].label}
              </span>
              <select
                value={databaseLevel}
                onChange={(e) => setDatabaseLevel(e.target.value)}
                className="px-3 py-1.5 rounded-lg bg-obsidian-card border border-obsidian-borderLight text-slate-200 text-xs focus:outline-none focus:border-brand-500"
              >
                {roleConfig.domains[2].options.map((opt) => (
                  <option key={opt} value={opt.split(' ')[0]}>{opt}</option>
                ))}
              </select>
            </div>

            {/* Domain 4: Dynamic Role Spec */}
            <div className="p-3.5 rounded-xl bg-obsidian-surface border border-obsidian-borderLight flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <span className="text-xs font-medium text-white flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-amber-500" />
                {roleConfig.domains[3].label}
              </span>
              <select
                value={frameworkLevel}
                onChange={(e) => setFrameworkLevel(e.target.value)}
                className="px-3 py-1.5 rounded-lg bg-obsidian-card border border-obsidian-borderLight text-slate-200 text-xs focus:outline-none focus:border-brand-500"
              >
                {roleConfig.domains[3].options.map((opt) => (
                  <option key={opt} value={opt.split(' ')[0]}>{opt}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Dynamic Skill Chips */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="block text-xs font-semibold text-slate-200">
              Select Known Technologies & Languages ({selectedSkills.length} selected)
            </label>
            <span className="text-[10px] text-slate-400 font-mono">Tailored for {targetRole}</span>
          </div>
          <div className="flex flex-wrap gap-2 pt-1">
            {roleConfig.availableChips.map((chip) => {
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
