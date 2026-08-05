import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useOnboarding } from '../context/OnboardingContext';
import { domainApi, DomainItem } from '../api';
import {
  Globe,
  Brain,
  Smartphone,
  ShieldAlert,
  Cloud,
  Terminal,
  CheckCircle2,
  ArrowRight,
  Sparkles,
  Loader2,
} from 'lucide-react';

interface DomainOption {
  id: string;
  title: string;
  description: string;
  icon: React.ElementType;
  popularBadge?: boolean;
}

const DEFAULT_DOMAINS: DomainOption[] = [
  {
    id: 'Web Development',
    title: 'Web Development',
    description: 'Frontend, Backend, and Full-Stack web architecture & frameworks.',
    icon: Globe,
    popularBadge: true,
  },
  {
    id: 'AI/ML',
    title: 'AI/ML',
    description: 'Machine Learning, Neural Networks, NLP, and Generative AI systems.',
    icon: Brain,
    popularBadge: true,
  },
  {
    id: 'App Development',
    title: 'App Development',
    description: 'Native & Cross-platform iOS/Android mobile applications.',
    icon: Smartphone,
  },
  {
    id: 'Cybersecurity',
    title: 'Cybersecurity',
    description: 'Network security, ethical hacking, cryptography & audit compliance.',
    icon: ShieldAlert,
  },
  {
    id: 'Cloud Computing',
    title: 'Cloud Computing',
    description: 'AWS, GCP, Azure, DevOps pipelines, Kubernetes & infrastructure.',
    icon: Cloud,
  },
  {
    id: 'Core Software Engineering / DSA',
    title: 'Core Software Engineering / DSA',
    description: 'Data Structures, Algorithms, System Design & OS fundamentals.',
    icon: Terminal,
  },
];

const getDomainIcon = (titleOrId: string): React.ElementType => {
  const t = titleOrId.toLowerCase();
  if (t.includes('web')) return Globe;
  if (t.includes('ai') || t.includes('ml')) return Brain;
  if (t.includes('app') || t.includes('mobile')) return Smartphone;
  if (t.includes('security') || t.includes('cyber')) return ShieldAlert;
  if (t.includes('cloud') || t.includes('devops')) return Cloud;
  return Terminal;
};

export const OnboardingDomain: React.FC = () => {
  const navigate = useNavigate();
  const { selectedDomain, setSelectedDomain } = useOnboarding();
  const [domainList, setDomainList] = useState<DomainOption[]>(DEFAULT_DOMAINS);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    let isMounted = true;
    domainApi
      .getDomains()
      .then((data) => {
        if (isMounted && Array.isArray(data) && data.length > 0) {
          const mapped = data.map((d: DomainItem) => ({
            id: d.id || d.title,
            title: d.title || d.id,
            description: d.description || '',
            icon: getDomainIcon(d.title || d.id),
            popularBadge: d.popularBadge ?? (d.title?.includes('Web') || d.title?.includes('AI')),
          }));
          setDomainList(mapped);
        }
      })
      .catch((err) => {
        console.warn('Backend GET /api/domains unreachable or error, using default domain presets:', err);
      })
      .finally(() => {
        if (isMounted) setIsLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const handleNext = () => {
    if (selectedDomain) {
      navigate('/onboarding/details');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col justify-between p-4 sm:p-6 md:p-10 antialiased selection:bg-indigo-500 selection:text-white">
      {/* Top Header Step Indicator */}
      <header className="w-full max-w-4xl mx-auto flex items-center justify-between pb-6">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-indigo-600 text-white rounded-xl shadow-sm">
            <Sparkles className="w-5 h-5" />
          </div>
          <span className="font-bold text-slate-900 text-base tracking-tight">
            PlaceMentor AI
          </span>
        </div>

        {/* Step Counter */}
        <div className="flex items-center gap-2 bg-indigo-50/80 px-3.5 py-1.5 rounded-full border border-indigo-100 text-xs font-semibold text-indigo-700">
          <span>Step 1 of 3</span>
          <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
          <span className="text-slate-600">Target Domain</span>
        </div>
      </header>

      {/* Main Container */}
      <main className="w-full max-w-4xl mx-auto my-auto py-4">
        {/* Title Section */}
        <div className="text-center max-w-2xl mx-auto mb-8 sm:mb-10">
          <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight leading-tight mb-3">
            Select Your Target Domain
          </h1>
          <p className="text-sm sm:text-base text-slate-600 leading-relaxed">
            Choose the core tech specialization you are preparing for. Our AI analyzer will customize skill benchmarks and industry readiness evaluations for this domain.
          </p>
        </div>

        {/* Domain Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5 mb-10">
          {domainList.map((domain) => {
            const Icon = domain.icon;
            const isSelected = selectedDomain === domain.id;

            return (
              <button
                key={domain.id}
                id={`domain-card-${domain.id.toLowerCase().replace(/[^a-z0-9]/g, '-')}`}
                type="button"
                onClick={() => setSelectedDomain(domain.id)}
                className={`relative group text-left p-5 sm:p-6 rounded-2xl border transition-all duration-200 cursor-pointer focus:outline-none ${
                  isSelected
                    ? 'bg-white border-indigo-600 ring-2 ring-indigo-600/30 shadow-md shadow-indigo-100/50'
                    : 'bg-white border-slate-200 hover:border-indigo-300 hover:shadow-sm'
                }`}
              >
                {/* Checkmark Indicator */}
                <div className="flex items-center justify-between mb-4">
                  <div
                    className={`p-3 rounded-xl transition-colors ${
                      isSelected
                        ? 'bg-indigo-600 text-white shadow-xs'
                        : 'bg-slate-100 text-slate-600 group-hover:bg-indigo-50 group-hover:text-indigo-600'
                    }`}
                  >
                    <Icon className="w-6 h-6" />
                  </div>

                  <div className="flex items-center gap-2">
                    {domain.popularBadge && !isSelected && (
                      <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-amber-50 text-amber-700 border border-amber-200/60">
                        Popular
                      </span>
                    )}
                    <div
                      className={`w-6 h-6 rounded-full flex items-center justify-center border transition-all ${
                        isSelected
                          ? 'bg-indigo-600 border-indigo-600 text-white'
                          : 'border-slate-300 group-hover:border-indigo-300'
                      }`}
                    >
                      {isSelected && <CheckCircle2 className="w-4 h-4 text-white" />}
                    </div>
                  </div>
                </div>

                {/* Domain Title */}
                <h3
                  className={`text-base font-bold mb-1.5 transition-colors ${
                    isSelected ? 'text-indigo-950' : 'text-slate-900 group-hover:text-indigo-600'
                  }`}
                >
                  {domain.title}
                </h3>

                {/* Domain Description */}
                <p className="text-xs text-slate-500 leading-relaxed">
                  {domain.description}
                </p>
              </button>
            );
          })}
        </div>

        {/* Action Controls */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-6 border-t border-slate-200/80">
          <div className="text-xs text-slate-500">
            {selectedDomain ? (
              <span className="text-indigo-700 font-medium">
                Selected: <strong>{selectedDomain}</strong>
              </span>
            ) : (
              <span>Please click a domain card above to continue.</span>
            )}
          </div>

          <button
            id="next-details-btn"
            type="button"
            onClick={handleNext}
            disabled={!selectedDomain}
            className={`w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-3.5 text-sm font-semibold rounded-xl transition-all ${
              selectedDomain
                ? 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-md hover:shadow-indigo-200 cursor-pointer'
                : 'bg-slate-200 text-slate-400 cursor-not-allowed'
            }`}
          >
            <span>Next: Enter Academic Details</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full max-w-4xl mx-auto text-center py-4 text-xs text-slate-400">
        Placement Readiness Analyzer • Domain Selection
      </footer>
    </div>
  );
};

export default OnboardingDomain;
