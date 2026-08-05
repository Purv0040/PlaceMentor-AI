import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useOnboarding, ReportData } from '../context/OnboardingContext';
import { reportApi } from '../api';
import {
  Sparkles,
  ArrowLeft,
  FileText,
  UploadCloud,
  Github,
  Code2,
  Terminal,
  Linkedin,
  CheckCircle2,
  AlertCircle,
  Loader2,
  FileCheck,
  Check,
  X,
  Zap,
} from 'lucide-react';

interface AnalysisStep {
  id: string;
  label: string;
}

export const OnboardingProfiles: React.FC = () => {
  const navigate = useNavigate();
  const { selectedDomain, academicDetails, profileLinks, setProfileLinks, setReportData } =
    useOnboarding();

  const [resumeMode, setResumeMode] = useState<'file' | 'text'>(
    profileLinks.resumeMode || 'file'
  );
  const [resumeFileName, setResumeFileName] = useState<string>(
    profileLinks.resumeFileName || ''
  );
  const [resumeText, setResumeText] = useState<string>(
    profileLinks.resumeText || ''
  );

  const [githubUrl, setGithubUrl] = useState<string>(profileLinks.githubUrl || '');
  const [leetcodeUrl, setLeetcodeUrl] = useState<string>(
    profileLinks.leetcodeUrl || ''
  );
  const [hackerRankUrl, setHackerRankUrl] = useState<string>(
    profileLinks.hackerRankUrl || ''
  );
  const [linkedinUrl, setLinkedinUrl] = useState<string>(
    profileLinks.linkedinUrl || ''
  );

  // Errors state
  const [githubError, setGithubError] = useState<string>('');
  const [leetcodeError, setLeetcodeError] = useState<string>('');
  const [hackerRankError, setHackerRankError] = useState<string>('');
  const [linkedinError, setLinkedinError] = useState<string>('');

  // Analysis Animation state
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [currentStepIndex, setCurrentStepIndex] = useState<number>(0);

  // Drag and drop state
  const [isDragging, setIsDragging] = useState<boolean>(false);

  const validateUrl = (url: string, platform: string): boolean => {
    if (!url.trim()) return true; // Optional fields check empty separately
    const urlPattern = /^(https?:\/\/)?([\w.-]+)+[\w\-_~:/?#[\]@!$&'()*+,;=.]+$/i;
    if (!urlPattern.test(url.trim())) {
      return false;
    }
    const lower = url.toLowerCase();
    if (platform === 'github' && !lower.includes('github.com')) {
      return false;
    }
    if (platform === 'leetcode' && !lower.includes('leetcode.com')) {
      return false;
    }
    if (platform === 'hackerrank' && !lower.includes('hackerrank.com')) {
      return false;
    }
    if (platform === 'linkedin' && !lower.includes('linkedin.com')) {
      return false;
    }
    return true;
  };

  const handleGithubChange = (val: string) => {
    setGithubUrl(val);
    if (!val.trim()) {
      setGithubError('GitHub profile URL is required');
    } else if (!validateUrl(val, 'github')) {
      setGithubError('Please enter a valid GitHub profile URL (e.g. https://github.com/username)');
    } else {
      setGithubError('');
    }
  };

  const handleLeetcodeChange = (val: string) => {
    setLeetcodeUrl(val);
    if (!val.trim()) {
      setLeetcodeError('LeetCode profile URL is required');
    } else if (!validateUrl(val, 'leetcode')) {
      setLeetcodeError('Please enter a valid LeetCode profile URL (e.g. https://leetcode.com/username)');
    } else {
      setLeetcodeError('');
    }
  };

  const handleHackerRankChange = (val: string) => {
    setHackerRankUrl(val);
    if (!val.trim()) {
      setHackerRankError('HackerRank profile URL is required');
    } else if (!validateUrl(val, 'hackerrank')) {
      setHackerRankError('Please enter a valid HackerRank URL (e.g. https://hackerrank.com/username)');
    } else {
      setHackerRankError('');
    }
  };

  const handleLinkedinChange = (val: string) => {
    setLinkedinUrl(val);
    if (!val.trim()) {
      setLinkedinError('');
    } else if (!validateUrl(val, 'linkedin')) {
      setLinkedinError('Please enter a valid LinkedIn URL (e.g. https://linkedin.com/in/username)');
    } else {
      setLinkedinError('');
    }
  };

  const handleFileUpload = (file: File) => {
    const validExtensions = ['.pdf', '.doc', '.docx'];
    const hasValidExt = validExtensions.some((ext) =>
      file.name.toLowerCase().endsWith(ext)
    );
    if (hasValidExt) {
      setResumeFileName(file.name);
    } else {
      alert('Please upload a valid PDF, DOC, or DOCX resume document.');
    }
  };

  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  // Check required validation
  const isResumeValid =
    resumeMode === 'file'
      ? Boolean(resumeFileName)
      : resumeText.trim().length >= 20;

  const isGithubValid = Boolean(githubUrl.trim()) && !githubError && validateUrl(githubUrl, 'github');
  const isLeetcodeValid = Boolean(leetcodeUrl.trim()) && !leetcodeError && validateUrl(leetcodeUrl, 'leetcode');
  const isHackerRankValid = Boolean(hackerRankUrl.trim()) && !hackerRankError && validateUrl(hackerRankUrl, 'hackerrank');
  const isLinkedinValid = !linkedinUrl.trim() || (!linkedinError && validateUrl(linkedinUrl, 'linkedin'));

  const isFormValid = isResumeValid && isGithubValid && isLeetcodeValid && isHackerRankValid && isLinkedinValid;

  const getAnalysisSteps = (): AnalysisStep[] => {
    const steps: AnalysisStep[] = [
      { id: 'resume', label: 'Reading resume' },
      { id: 'github', label: 'Evaluating GitHub' },
      { id: 'leetcode_hackerrank', label: 'Checking LeetCode & HackerRank' },
    ];

    if (Boolean(linkedinUrl.trim())) {
      steps.push({ id: 'linkedin', label: 'Checking LinkedIn' });
    }

    steps.push(
      { id: 'comparing', label: 'Comparing with domain' },
      { id: 'report', label: 'Generating report' }
    );

    return steps;
  };

  const generateMockReport = (): ReportData => {
    const domain = selectedDomain || 'Web Development';
    const student = academicDetails.studentName || 'Student Candidate';
    const college = academicDetails.collegeName || 'University Institute';
    const branch = academicDetails.branch || 'CSE';

    let readinessScore = 85;
    let grade = 'Placement Ready (Top 15%)';
    let matchedSkills: { skill: string; foundIn: string }[] = [];
    let missingSkills: { skill: string; reason: string }[] = [];
    let comparisonSummary: string[] = [];
    let projectSuggestions: string[] = [];

    if (domain === 'AI/ML') {
      readinessScore = 81;
      matchedSkills = [
        { skill: 'Python & NumPy/Pandas', foundIn: 'GitHub Repositories' },
        { skill: 'Scikit-Learn Modeling', foundIn: 'Resume Projects' },
        { skill: 'Deep Learning Frameworks (PyTorch/TensorFlow)', foundIn: 'GitHub Repositories' },
        { skill: 'Data Cleaning & EDA', foundIn: 'Academic Transcripts' },
        { skill: 'SQL & Vector Databases', foundIn: 'Resume Technical Skills' },
      ];
      missingSkills = [
        { skill: 'Model Deployment (MLOps/Docker)', reason: 'No containerization configs or cloud API serving endpoints found in GitHub repositories.' },
        { skill: 'LLM Fine-tuning & Quantization', reason: 'Absent from listed project descriptions and technical coursework.' },
        { skill: 'Distributed Training (Ray/Spark)', reason: 'Not detected in code commits or resume experience sections.' },
      ];
      comparisonSummary = [
        `Strong mathematical and ML foundation matching top AI research requirements at ${college}.`,
        'Active GitHub repository commit pattern shows consistent hands-on project implementations.',
        'LeetCode problem count reflects solid foundational algorithmic reasoning.',
        'Gap identified in end-to-end model serving via containerized microservices.',
      ];
      projectSuggestions = [
        'Build a RAG-based AI document assistant with vector search.',
        'Deploy a quantized model container on AWS EC2 with FastAPI.',
      ];
    } else if (domain === 'Cybersecurity') {
      readinessScore = 78;
      matchedSkills = [
        { skill: 'Network Protocol Analysis (Wireshark)', foundIn: 'Resume Projects' },
        { skill: 'Linux System Administration', foundIn: 'GitHub Dotfiles & Labs' },
        { skill: 'Penetration Testing Fundamentals', foundIn: 'HackerRank Profile' },
        { skill: 'Cryptography & Hashing', foundIn: 'Academic Coursework' },
        { skill: 'Vulnerability Assessment (Nmap/Metasploit)', foundIn: 'Resume Certifications' },
      ];
      missingSkills = [
        { skill: 'Cloud Security Posture Management (CSPM)', reason: 'No IAM policy auditing or cloud compliance projects detected in GitHub.' },
        { skill: 'Reverse Engineering & Malware Analysis', reason: 'Missing assembly or binary disassembly references in profile submission.' },
        { skill: 'SOC Analyst Log Analysis (SIEM/Splunk)', reason: 'Not demonstrated in practical lab history or resume experience.' },
      ];
      comparisonSummary = [
        'Demonstrates good foundational security auditing knowledge aligned with entry-level SOC benchmarks.',
        'Hands-on lab completion on HackerRank / security platforms shows strong problem solving.',
        'Needs documented experience with enterprise cloud security compliance standards.',
      ];
      projectSuggestions = [
        'Setup a home SIEM lab using Elastic Stack to monitor simulated attack vectors.',
      ];
    } else if (domain === 'Cloud Computing') {
      readinessScore = 86;
      matchedSkills = [
        { skill: 'Linux Administration & Bash Scripting', foundIn: 'GitHub Repositories' },
        { skill: 'Docker Containerization', foundIn: 'Resume Projects' },
        { skill: 'AWS Core Infrastructure (EC2, S3, IAM)', foundIn: 'Resume Certifications' },
        { skill: 'Git & CI/CD Pipelines', foundIn: 'GitHub Workflow Actions' },
        { skill: 'Terraform Infrastructure as Code', foundIn: 'GitHub Repositories' },
      ];
      missingSkills = [
        { skill: 'Kubernetes Cluster Orchestration', reason: 'No Helm charts or K8s manifest files detected in public repositories.' },
        { skill: 'Prometheus & Grafana Observability', reason: 'Metrics monitoring setup missing from cloud architecture projects.' },
        { skill: 'Site Reliability Engineering (SRE) Post-mortems', reason: 'Not highlighted in resume project documentation.' },
      ];
      comparisonSummary = [
        'Excellent cloud platform understanding with hands-on IaC configuration.',
        'Solid repository architecture on GitHub demonstrating continuous deployment automation.',
        'Ready for junior Cloud/DevOps engineer interview panels.',
      ];
      projectSuggestions = [
        'Deploy a multi-node Kubernetes cluster with automated ingress controller management.',
      ];
    } else if (domain === 'App Development') {
      readinessScore = 83;
      matchedSkills = [
        { skill: 'Mobile UI Development (React Native / Flutter)', foundIn: 'GitHub Repositories' },
        { skill: 'RESTful API Integration', foundIn: 'Resume Projects' },
        { skill: 'State Management (Redux/Zustand)', foundIn: 'GitHub Repositories' },
        { skill: 'Asynchronous Storage & Caching', foundIn: 'Resume Skills' },
        { skill: 'Git Version Control', foundIn: 'GitHub Activity' },
      ];
      missingSkills = [
        { skill: 'Native iOS/Android Bridge Code (Swift/Kotlin)', reason: 'Only cross-platform JavaScript/Dart code detected in GitHub repositories.' },
        { skill: 'Mobile App Store CI/CD Deployment', reason: 'Fastlane or Play Console automated deployment scripts missing.' },
        { skill: 'Offline Synchronization Strategies', reason: 'No local SQLite or WatermelonDB caching strategy found in project code.' },
      ];
      comparisonSummary = [
        'Demonstrates high proficiency in cross-platform mobile user interfaces.',
        'Clean component hierarchy and state structure in public code repositories.',
        'Needs additional native device API integration projects to unlock senior role consideration.',
      ];
      projectSuggestions = [
        'Create a location-aware mobile tracker with offline SQLite fallback.',
      ];
    } else if (domain === 'Core Software Engineering / DSA') {
      readinessScore = 88;
      matchedSkills = [
        { skill: 'Data Structures (Trees, Graphs, Heaps)', foundIn: 'LeetCode Profile' },
        { skill: 'Algorithm Complexity & Optimization (O(N))', foundIn: 'HackerRank Profile' },
        { skill: 'Object-Oriented Design (Java/C++)', foundIn: 'GitHub Repositories' },
        { skill: 'Database Querying (SQL & Indexing)', foundIn: 'Academic Transcripts' },
        { skill: 'System OS & Multi-threading Basics', foundIn: 'Resume Skills' },
      ];
      missingSkills = [
        { skill: 'High-Scale Distributed System Design', reason: 'No architectural diagrams or system design case studies found in portfolio.' },
        { skill: 'Message Queue Architecture (Kafka/RabbitMQ)', reason: 'Asynchronous task queues absent from project backend implementations.' },
        { skill: 'Microservices Load Balancing', reason: 'Projects rely primarily on monolithic backend architectures.' },
      ];
      comparisonSummary = [
        'Exceptional algorithmic problem solving rating across LeetCode & HackerRank.',
        'Clean object-oriented coding principles demonstrated in core project submissions.',
        'Well prepared for Tier-1 technology company technical screening rounds.',
      ];
      projectSuggestions = [
        'Design an in-memory key-value cache with LRU eviction and thread synchronization.',
      ];
    } else {
      // Default: Web Development
      readinessScore = 85;
      matchedSkills = [
        { skill: 'React.js & Modern TypeScript', foundIn: 'GitHub Repositories' },
        { skill: 'Tailwind CSS Responsive UI', foundIn: 'Resume Projects' },
        { skill: 'Node.js & Express REST APIs', foundIn: 'GitHub Repositories' },
        { skill: 'SQL & NoSQL Database Integration', foundIn: 'Resume Skills' },
        { skill: 'Git & Team Collaboration', foundIn: 'GitHub Activity Log' },
      ];
      missingSkills = [
        { skill: 'Docker & Containerized Microservices', reason: 'No Dockerfile or docker-compose manifests found in submitted GitHub repositories.' },
        { skill: 'System Architecture & Caching (Redis)', reason: 'In-memory caching mechanisms absent from API backend projects.' },
        { skill: 'WebSockets & Real-time Data Streaming', reason: 'Socket.io or event-driven streaming not observed in project code.' },
      ];
      comparisonSummary = [
        `Academic background in ${branch} at ${college} aligns smoothly with enterprise Web Dev roles.`,
        'GitHub profile highlights strong understanding of full-stack component lifecycle and state management.',
        'LeetCode data demonstrates solid core problem-solving capability (Medium level speed).',
        'Minor skill gap in production deployment and cloud caching layers.',
      ];
      projectSuggestions = [
        'Build a real-time collaborative workspace with WebSockets and Redis Pub/Sub.',
        'Implement Docker multi-stage builds and GitHub Actions automated integration.',
      ];
    }

    return {
      readinessScore,
      grade,
      matchedSkills,
      missingSkills,
      comparisonSummary,
      domainName: domain,
      studentName: student,
      collegeName: college,
      branch: branch,
      generatedAt: new Date().toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      }),
      recommendations: [
        {
          title: `Master ${missingSkills[0]?.skill || 'Cloud Deployment'}`,
          desc: `Top recruiters for ${domain} actively look for hands-on experience with ${missingSkills[0]?.skill || 'Cloud Deployment'}.`,
          priority: 'High',
        },
        {
          title: 'Strengthen System Design Documentation',
          desc: 'Add architectural diagrams and README API docs to your GitHub repositories to impress senior interviewers.',
          priority: 'Medium',
        },
        {
          title: 'Practice Timed Problem Solving',
          desc: 'Solve 15-20 additional Medium-difficulty data structure problems in a timed test setting.',
          priority: 'Medium',
        },
      ],
      projectSuggestions,
      profileAnalysis: {
        github: {
          repoCount: 18,
          reposCount: 18,
          topLanguages: ['TypeScript', 'Python', 'Go', 'React'],
          summary: 'Strong public repositories featuring modular architecture, active contribution streaks, and clean code structure.',
          highlights: ['Public repository with CI/CD pipeline', 'Clean OOP modular structure', 'Open source contributions'],
          contributionsThisYear: 342,
        },
        leetcode: {
          solved: {
            easy: 85,
            medium: 110,
            hard: 20,
          },
          solvedCount: 215,
          topTags: ['Dynamic Programming', 'Trees & Graphs', 'Binary Search', 'Sliding Window'],
          contestRating: 1680,
          badge: 'Knight',
          topicBreakdown: { 'Data Structures': 110, 'Algorithms': 85, 'System Design': 20 },
        },
        hackerrank: {
          badges: ['Problem Solving 5★', 'Python 5★', 'SQL 4★', 'Gold Developer'],
          badgesCount: 5,
          topCategories: ['Data Structures', 'Algorithms', 'Databases'],
          stars: 5,
          primarySkills: ['Problem Solving', 'SQL', 'Python Core'],
        },
        linkedin: {
          provided: Boolean(linkedinUrl.trim()),
          summary: linkedinUrl.trim()
            ? 'All-Star profile strength with 500+ connections and endorsements in React, TypeScript, and System Architecture.'
            : undefined,
          connections: linkedinUrl.trim() ? '500+' : undefined,
          profileStrength: linkedinUrl.trim() ? 'All-Star' : undefined,
          endorsements: linkedinUrl.trim() ? ['React.js', 'System Architecture', 'TypeScript', 'Software Development'] : [],
        },
        resume: {
          skillsDetected: matchedSkills.map((s) => s.skill),
          experienceSummary: `Verified academic projects and coursework in ${domain}`,
        },
      },
    };
  };

  const handleStartAnalysis = async () => {
    if (!isFormValid) return;

    const payloadProfileLinks = {
      githubUrl: githubUrl.trim(),
      leetcodeUrl: leetcodeUrl.trim(),
      hackerRankUrl: hackerRankUrl.trim(),
      linkedinUrl: linkedinUrl.trim(),
      resumeFileName: resumeMode === 'file' ? resumeFileName : '',
      resumeText: resumeMode === 'text' ? resumeText.trim() : '',
      resumeMode,
    };

    // Save profile state to context
    setProfileLinks(payloadProfileLinks);

    const steps = getAnalysisSteps();
    setIsAnalyzing(true);
    setCurrentStepIndex(0);

    // Multi-step timer: 1 second per step
    let step = 0;
    const interval = setInterval(async () => {
      step++;
      if (step < steps.length) {
        setCurrentStepIndex(step);
      } else {
        clearInterval(interval);
        try {
          // Send real API request to POST /api/reports
          const apiRes = await reportApi.createReport({
            domain: selectedDomain || 'Web Development',
            academicDetails: academicDetails,
            profileLinks: payloadProfileLinks,
          });

          const localMock = generateMockReport();
          const finalReport: ReportData = {
            id: apiRes?.id || apiRes?.report_id || `rep_${Date.now()}`,
            readinessScore: apiRes?.readinessScore ?? apiRes?.readiness_score ?? localMock.readinessScore,
            grade: apiRes?.grade ?? localMock.grade,
            matchedSkills: apiRes?.matchedSkills ?? apiRes?.matched_skills ?? localMock.matchedSkills,
            missingSkills: apiRes?.missingSkills ?? apiRes?.missing_skills ?? localMock.missingSkills,
            comparisonSummary: apiRes?.comparisonSummary ?? apiRes?.comparison_summary ?? localMock.comparisonSummary,
            domainName: apiRes?.domainName ?? apiRes?.domain_name ?? localMock.domainName,
            studentName: apiRes?.studentName ?? apiRes?.student_name ?? localMock.studentName,
            collegeName: apiRes?.collegeName ?? apiRes?.college_name ?? localMock.collegeName,
            branch: apiRes?.branch ?? localMock.branch,
            generatedAt: apiRes?.generatedAt ?? apiRes?.generated_at ?? localMock.generatedAt,
            recommendations: apiRes?.recommendations ?? localMock.recommendations,
            projectSuggestions: apiRes?.projectSuggestions ?? apiRes?.project_suggestions ?? localMock.projectSuggestions,
            profileAnalysis: apiRes?.profileAnalysis ?? apiRes?.profile_analysis ?? localMock.profileAnalysis,
          };
          setReportData(finalReport);
        } catch (err) {
          console.warn('POST /api/reports backend call error, falling back to client analysis:', err);
          const fallback = generateMockReport();
          fallback.id = `rep_${Date.now()}`;
          setReportData(fallback);
        } finally {
          navigate('/report');
        }
      }
    }, 1000);
  };

  const stepsList = getAnalysisSteps();

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col justify-between p-4 sm:p-6 md:p-10 antialiased selection:bg-indigo-500 selection:text-white relative">
      {/* Top Header Step Indicator */}
      <header className="w-full max-w-3xl mx-auto flex items-center justify-between pb-6">
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
          <span>Step 3 of 3</span>
          <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
          <span className="text-slate-600">Resume & Profiles</span>
        </div>
      </header>

      {/* Main Container Card */}
      <main className="w-full max-w-3xl mx-auto my-auto">
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-md p-6 sm:p-8 md:p-10">
          {/* Back Link */}
          <Link
            to="/onboarding/details"
            id="back-to-details-link"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-indigo-600 transition-colors mb-6"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Student Details</span>
          </Link>

          {/* Form Header */}
          <div className="mb-8">
            <h1 id="profiles-heading" className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              Resume & Technical Profiles
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 mt-1">
              Upload your resume and link coding profiles so our AI model can evaluate candidate readiness for{' '}
              <strong className="text-indigo-600">{selectedDomain || 'Web Development'}</strong>.
            </p>
          </div>

          <div className="space-y-8">
            {/* Section 1: Resume Upload / Text */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700">
                  1. Resume Submission <span className="text-red-500">*</span>
                </label>

                {/* Resume Mode Toggle */}
                <div className="inline-flex p-1 bg-slate-100 rounded-xl">
                  <button
                    id="toggle-file-mode"
                    type="button"
                    onClick={() => setResumeMode('file')}
                    className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                      resumeMode === 'file'
                        ? 'bg-white text-indigo-600 shadow-xs'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    Upload File
                  </button>
                  <button
                    id="toggle-text-mode"
                    type="button"
                    onClick={() => setResumeMode('text')}
                    className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                      resumeMode === 'text'
                        ? 'bg-white text-indigo-600 shadow-xs'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    Paste Text
                  </button>
                </div>
              </div>

              {resumeMode === 'file' ? (
                /* File Upload Dropzone */
                <div>
                  <div
                    onDragOver={(e) => {
                      e.preventDefault();
                      setIsDragging(true);
                    }}
                    onDragLeave={() => setIsDragging(false)}
                    onDrop={handleFileDrop}
                    className={`relative border-2 border-dashed rounded-2xl p-6 sm:p-8 text-center transition-all ${
                      isDragging
                        ? 'border-indigo-500 bg-indigo-50/50'
                        : resumeFileName
                        ? 'border-indigo-200 bg-indigo-50/20'
                        : 'border-slate-300 bg-slate-50 hover:bg-slate-100/60'
                    }`}
                  >
                    <input
                      id="resume-file-input"
                      type="file"
                      accept=".pdf,.doc,.docx"
                      onChange={(e) => {
                        if (e.target.files && e.target.files[0]) {
                          handleFileUpload(e.target.files[0]);
                        }
                      }}
                      className="hidden"
                    />

                    {resumeFileName ? (
                      <div className="flex flex-col items-center justify-center">
                        <div className="p-3 bg-indigo-600 text-white rounded-xl shadow-xs mb-3">
                          <FileCheck className="w-8 h-8" />
                        </div>
                        <p className="text-sm font-bold text-slate-900">{resumeFileName}</p>
                        <p className="text-xs text-indigo-600 font-medium mt-1">
                          Resume file uploaded & ready for analysis
                        </p>
                        <div className="flex gap-2 mt-4">
                          <label
                            htmlFor="resume-file-input"
                            className="px-3 py-1.5 text-xs font-semibold text-indigo-600 bg-white border border-indigo-200 rounded-lg cursor-pointer hover:bg-indigo-50"
                          >
                            Change File
                          </label>
                          <button
                            type="button"
                            onClick={() => setResumeFileName('')}
                            className="px-3 py-1.5 text-xs font-semibold text-red-600 bg-white border border-red-200 rounded-lg hover:bg-red-50"
                          >
                            Remove
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex flex-col items-center justify-center">
                        <div className="p-3 bg-indigo-50 text-indigo-600 rounded-xl mb-3">
                          <UploadCloud className="w-8 h-8" />
                        </div>
                        <p className="text-sm font-semibold text-slate-900 mb-1">
                          Click to upload or drag & drop resume
                        </p>
                        <p className="text-xs text-slate-400 mb-4">
                          Supports PDF, DOC, or DOCX formats (Max 10MB)
                        </p>
                        <label
                          htmlFor="resume-file-input"
                          className="px-4 py-2 text-xs font-semibold text-white bg-indigo-600 rounded-xl cursor-pointer hover:bg-indigo-700 shadow-xs transition-all"
                        >
                          Select File
                        </label>
                      </div>
                    )}
                  </div>
                  {/* Quick sample button if user wants to prefill mock resume */}
                  {!resumeFileName && (
                    <button
                      type="button"
                      onClick={() => setResumeFileName('Alex_Rivera_Resume_2026.pdf')}
                      className="mt-2 text-xs text-indigo-600 hover:underline inline-flex items-center gap-1 font-medium"
                    >
                      <Sparkles className="w-3 h-3" />
                      <span>Use sample resume file (Alex_Rivera_Resume.pdf)</span>
                    </button>
                  )}
                </div>
              ) : (
                /* Textarea Paste Mode */
                <div>
                  <textarea
                    id="resume-textarea"
                    rows={5}
                    value={resumeText}
                    onChange={(e) => setResumeText(e.target.value)}
                    placeholder="Paste raw resume text, work experience summary, projects list, technical skills, and educational background..."
                    className="w-full p-3.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-slate-900 placeholder:text-slate-400"
                  />
                  <div className="flex justify-between items-center mt-1 text-xs text-slate-400">
                    <span>
                      {resumeText.trim().length >= 20 ? (
                        <span className="text-emerald-600 font-semibold flex items-center gap-1">
                          <Check className="w-3.5 h-3.5" /> Sufficient text length
                        </span>
                      ) : (
                        <span>Minimum 20 characters required</span>
                      )}
                    </span>
                    <span>{resumeText.length} characters</span>
                  </div>
                </div>
              )}
            </div>

            {/* Section 2: Technical Profile Links */}
            <div className="space-y-4 pt-2 border-t border-slate-100">
              <div className="flex items-center justify-between">
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700">
                  2. Technical & Coding Profiles <span className="text-red-500">*</span>
                </label>
                <span className="text-xs text-slate-400">GitHub, LeetCode & HackerRank required</span>
              </div>

              {/* GitHub URL */}
              <div>
                <label htmlFor="github-url-input" className="block text-xs font-semibold text-slate-700 mb-1">
                  GitHub Profile URL <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                    <Github className="w-4 h-4 text-slate-600" />
                  </div>
                  <input
                    id="github-url-input"
                    type="url"
                    value={githubUrl}
                    onChange={(e) => handleGithubChange(e.target.value)}
                    placeholder="https://github.com/your-username"
                    className={`w-full pl-10 pr-9 py-2.5 text-sm bg-slate-50 border ${
                      githubError
                        ? 'border-red-400 bg-red-50/20'
                        : githubUrl && !githubError
                        ? 'border-emerald-300 bg-emerald-50/10'
                        : 'border-slate-200'
                    } rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-slate-900 placeholder:text-slate-400`}
                  />
                  {githubUrl && !githubError && (
                    <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-emerald-600">
                      <CheckCircle2 className="w-4 h-4" />
                    </div>
                  )}
                </div>
                {githubError && (
                  <p className="flex items-center gap-1 text-xs text-red-500 mt-1 font-medium">
                    <AlertCircle className="w-3.5 h-3.5" />
                    <span>{githubError}</span>
                  </p>
                )}
              </div>

              {/* LeetCode URL */}
              <div>
                <label htmlFor="leetcode-url-input" className="block text-xs font-semibold text-slate-700 mb-1">
                  LeetCode Profile URL <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-amber-500">
                    <Code2 className="w-4 h-4" />
                  </div>
                  <input
                    id="leetcode-url-input"
                    type="url"
                    value={leetcodeUrl}
                    onChange={(e) => handleLeetcodeChange(e.target.value)}
                    placeholder="https://leetcode.com/your-username"
                    className={`w-full pl-10 pr-9 py-2.5 text-sm bg-slate-50 border ${
                      leetcodeError
                        ? 'border-red-400 bg-red-50/20'
                        : leetcodeUrl && !leetcodeError
                        ? 'border-emerald-300 bg-emerald-50/10'
                        : 'border-slate-200'
                    } rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-slate-900 placeholder:text-slate-400`}
                  />
                  {leetcodeUrl && !leetcodeError && (
                    <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-emerald-600">
                      <CheckCircle2 className="w-4 h-4" />
                    </div>
                  )}
                </div>
                {leetcodeError && (
                  <p className="flex items-center gap-1 text-xs text-red-500 mt-1 font-medium">
                    <AlertCircle className="w-3.5 h-3.5" />
                    <span>{leetcodeError}</span>
                  </p>
                )}
              </div>

              {/* HackerRank URL */}
              <div>
                <label htmlFor="hackerrank-url-input" className="block text-xs font-semibold text-slate-700 mb-1">
                  HackerRank Profile URL <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-emerald-600">
                    <Terminal className="w-4 h-4" />
                  </div>
                  <input
                    id="hackerrank-url-input"
                    type="url"
                    value={hackerRankUrl}
                    onChange={(e) => handleHackerRankChange(e.target.value)}
                    placeholder="https://hackerrank.com/your-username"
                    className={`w-full pl-10 pr-9 py-2.5 text-sm bg-slate-50 border ${
                      hackerRankError
                        ? 'border-red-400 bg-red-50/20'
                        : hackerRankUrl && !hackerRankError
                        ? 'border-emerald-300 bg-emerald-50/10'
                        : 'border-slate-200'
                    } rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-slate-900 placeholder:text-slate-400`}
                  />
                  {hackerRankUrl && !hackerRankError && (
                    <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-emerald-600">
                      <CheckCircle2 className="w-4 h-4" />
                    </div>
                  )}
                </div>
                {hackerRankError && (
                  <p className="flex items-center gap-1 text-xs text-red-500 mt-1 font-medium">
                    <AlertCircle className="w-3.5 h-3.5" />
                    <span>{hackerRankError}</span>
                  </p>
                )}
              </div>

              {/* LinkedIn URL (Optional) */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <label htmlFor="linkedin-url-input" className="block text-xs font-semibold text-slate-700">
                    LinkedIn Profile URL
                  </label>
                  <span className="text-[11px] font-semibold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-md border border-indigo-100">
                    Optional
                  </span>
                </div>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-blue-600">
                    <Linkedin className="w-4 h-4" />
                  </div>
                  <input
                    id="linkedin-url-input"
                    type="url"
                    value={linkedinUrl}
                    onChange={(e) => handleLinkedinChange(e.target.value)}
                    placeholder="https://linkedin.com/in/your-username (Optional)"
                    className={`w-full pl-10 pr-9 py-2.5 text-sm bg-slate-50 border ${
                      linkedinError
                        ? 'border-red-400 bg-red-50/20'
                        : linkedinUrl && !linkedinError
                        ? 'border-emerald-300 bg-emerald-50/10'
                        : 'border-slate-200'
                    } rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-slate-900 placeholder:text-slate-400`}
                  />
                  {linkedinUrl && !linkedinError && (
                    <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-emerald-600">
                      <CheckCircle2 className="w-4 h-4" />
                    </div>
                  )}
                </div>
                {linkedinError && (
                  <p className="flex items-center gap-1 text-xs text-red-500 mt-1 font-medium">
                    <AlertCircle className="w-3.5 h-3.5" />
                    <span>{linkedinError}</span>
                  </p>
                )}
              </div>

              {/* Sample Auto-Fill Button */}
              {(!githubUrl || !leetcodeUrl || !hackerRankUrl) && (
                <button
                  type="button"
                  onClick={() => {
                    handleGithubChange('https://github.com/alexrivera-dev');
                    handleLeetcodeChange('https://leetcode.com/alexrivera');
                    handleHackerRankChange('https://hackerrank.com/alexrivera');
                    handleLinkedinChange('https://linkedin.com/in/alexrivera');
                  }}
                  className="text-xs text-indigo-600 hover:underline inline-flex items-center gap-1 font-medium pt-1"
                >
                  <Sparkles className="w-3 h-3" />
                  <span>Autofill sample profile URLs</span>
                </button>
              )}
            </div>

            {/* Form Action Controls */}
            <div className="pt-6 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4">
              <Link
                to="/onboarding/details"
                id="back-btn-profiles"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-3 text-sm font-semibold text-slate-600 bg-slate-100 rounded-xl hover:bg-slate-200 transition-all text-center"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back</span>
              </Link>

              <button
                id="analyze-readiness-btn"
                type="button"
                onClick={handleStartAnalysis}
                disabled={!isFormValid || isAnalyzing}
                className={`w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-8 py-3.5 text-base font-bold rounded-xl transition-all ${
                  isFormValid && !isAnalyzing
                    ? 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-md hover:shadow-indigo-200 cursor-pointer'
                    : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                }`}
              >
                <Zap className="w-5 h-5 text-amber-300 fill-amber-300" />
                <span>Analyze Placement Readiness Now</span>
              </button>
            </div>

            {!isFormValid && (
              <div className="text-center text-xs text-slate-400 space-y-1">
                {!isResumeValid && <p>• Please upload a resume file or paste resume text.</p>}
                {(!isGithubValid || !isLeetcodeValid || !isHackerRankValid) && (
                  <p>• Please provide valid required URLs for GitHub, LeetCode, and HackerRank.</p>
                )}
                {!isLinkedinValid && <p>• Please fix the invalid LinkedIn URL.</p>}
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Multi-step Loading Animation Modal */}
      {isAnalyzing && (
        <div className="fixed inset-0 z-50 bg-slate-900/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl shadow-2xl border border-indigo-100 p-8 sm:p-10 max-w-lg w-full text-center animate-in fade-in zoom-in-95 duration-200">
            {/* Spinning Header Icon */}
            <div className="w-16 h-16 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-inner">
              <Loader2 className="w-8 h-8 animate-spin" />
            </div>

            <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight mb-2">
              Analyzing Placement Readiness
            </h2>
            <p className="text-xs sm:text-sm text-slate-500 mb-8">
              Our AI engine is benchmarking your technical footprint against current industry hiring standards for{' '}
              <strong className="text-indigo-600">{selectedDomain || 'Web Development'}</strong>.
            </p>

            {/* Sequence Steps */}
            <div className="space-y-3.5 text-left mb-8 bg-slate-50 p-5 rounded-2xl border border-slate-100">
              {stepsList.map((step, idx) => {
                const isDone = idx < currentStepIndex;
                const isCurrent = idx === currentStepIndex;

                return (
                  <div key={step.id} className="flex items-center gap-3">
                    <div className="shrink-0">
                      {isDone ? (
                        <div className="w-6 h-6 rounded-full bg-emerald-500 text-white flex items-center justify-center shadow-xs">
                          <Check className="w-3.5 h-3.5 stroke-[3]" />
                        </div>
                      ) : isCurrent ? (
                        <div className="w-6 h-6 rounded-full bg-indigo-600 text-white flex items-center justify-center shadow-xs animate-pulse">
                          <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        </div>
                      ) : (
                        <div className="w-6 h-6 rounded-full bg-slate-200 text-slate-400 flex items-center justify-center text-xs font-semibold">
                          {idx + 1}
                        </div>
                      )}
                    </div>

                    <span
                      className={`text-sm font-semibold transition-colors ${
                        isDone
                          ? 'text-emerald-700 line-through/30'
                          : isCurrent
                          ? 'text-indigo-900 font-bold'
                          : 'text-slate-400'
                      }`}
                    >
                      {step.label}
                    </span>
                  </div>
                );
              })}
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
              <div
                className="bg-indigo-600 h-full transition-all duration-500 ease-out"
                style={{
                  width: `${((currentStepIndex + 1) / stepsList.length) * 100}%`,
                }}
              />
            </div>
            <p className="text-[11px] text-slate-400 mt-2 font-medium">
              Step {currentStepIndex + 1} of {stepsList.length}
            </p>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="w-full max-w-3xl mx-auto text-center py-4 text-xs text-slate-400">
        Placement Readiness Analyzer • Technical Profiles Step
      </footer>
    </div>
  );
};

export default OnboardingProfiles;
