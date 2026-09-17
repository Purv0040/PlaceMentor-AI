import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { jsPDF } from 'jspdf';
import { useOnboarding, ReportData, MatchedSkill, MissingSkill } from '../context/OnboardingContext';
import { reportApi } from '../api';
import {
  SkillRoadmapModal,
  getOrGenerateRoadmap,
  SkillRoadmapData,
} from '../components/SkillRoadmapModal';
import {
  Sparkles,
  CheckCircle2,
  XCircle,
  TrendingUp,
  BookOpen,
  FolderGit2,
  RotateCcw,
  Download,
  Building2,
  GraduationCap,
  Briefcase,
  ExternalLink,
  Award,
  Github,
  Code2,
  Terminal,
  Tag,
  Info,
  Layers,
} from 'lucide-react';

const fallbackReport: ReportData = {
  readinessScore: 84,
  grade: 'Placement Ready (Top 15%)',
  domainName: 'Web Development',
  studentName: 'Alex Rivera',
  collegeName: 'State Institute of Technology',
  branch: 'CSE',
  generatedAt: new Date().toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }),
  matchedSkills: [
    { skill: 'React.js & Modern TypeScript', foundIn: 'GitHub Repositories' },
    { skill: 'Tailwind CSS Responsive UI', foundIn: 'Resume Projects' },
    { skill: 'Node.js & Express REST APIs', foundIn: 'GitHub Repositories' },
    { skill: 'SQL & NoSQL Database Integration', foundIn: 'Resume Technical Skills' },
    { skill: 'Git & Team Collaboration', foundIn: 'GitHub Activity Log' },
  ],
  missingSkills: [
    { skill: 'Docker & Containerized Microservices', reason: 'No Dockerfile or docker-compose manifests detected in GitHub repositories.' },
    { skill: 'System Architecture & Caching (Redis)', reason: 'In-memory caching and system design documentation absent from portfolio.' },
    { skill: 'WebSockets & Real-time Data Streaming', reason: 'Event-driven streaming mechanisms not observed in project code.' },
  ],
  comparisonSummary: [
    'Academic background in CSE at State Institute of Technology aligns smoothly with enterprise Web Dev roles.',
    'GitHub profile highlights strong understanding of full-stack component lifecycle and state management.',
    'LeetCode data demonstrates solid core problem-solving capability (Medium level speed).',
    'Minor skill gap in production deployment and cloud caching layers.',
  ],
  recommendations: [
    {
      title: 'Master Docker & Microservices',
      desc: 'Top recruiters for Web Development actively look for hands-on experience with Docker containerization.',
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
  projectSuggestions: [
    'Build a real-time collaborative workspace with WebSockets and Redis Pub/Sub.',
    'Implement Docker multi-stage builds and GitHub Actions automated integration.',
  ],
  profileAnalysis: {
    github: {
      repoCount: 18,
      reposCount: 18,
      topLanguages: ['TypeScript', 'Python', 'Go', 'React'],
      summary: 'Public repositories exhibit clean modular TypeScript code, robust architectural patterns, and continuous integration workflows.',
    },
    leetcode: {
      solved: {
        easy: 85,
        medium: 110,
        hard: 20,
      },
      solvedCount: 215,
      topTags: ['Dynamic Programming', 'Trees & Graphs', 'Binary Search', 'Sliding Window'],
    },
    hackerrank: {
      badges: ['Problem Solving 5★', 'Python 5★', 'SQL 4★', 'Gold Developer'],
      topCategories: ['Data Structures', 'Algorithms', 'Databases'],
    },
  },
};

export const Report: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { reportData, resetOnboarding, profileLinks } = useOnboarding();

  // Selected skill for opening the learning roadmap modal
  const [activeModalSkill, setActiveModalSkill] = useState<{ skill: string; reason: string } | null>(null);
  const [downloadNotice, setDownloadNotice] = useState(false);

  // Local state cache for roadmap data per skill name
  const [roadmapCache, setRoadmapCache] = useState<Record<string, SkillRoadmapData>>({});

  const handleOpenSkillModal = async (item: { skill: string; reason: string }) => {
    setActiveModalSkill(item);
    if (!roadmapCache[item.skill]) {
      const reportId = report.id || 'current';
      try {
        const resData = await reportApi.getSkillRoadmap(reportId, item.skill, item.reason);
        if (resData && (resData.phases || resData.skillName)) {
          setRoadmapCache((prev) => ({
            ...prev,
            [item.skill]: {
              skillName: resData.skillName || resData.skill_name || item.skill,
              estimatedTime: resData.estimatedTime || resData.estimated_time || '3 - 4 Weeks (5 hrs/week)',
              overview: resData.overview || item.reason,
              phases: resData.phases || [],
              keyOutcome: resData.keyOutcome || resData.key_outcome || `Master ${item.skill} for production readiness.`,
            },
          }));
          return;
        }
      } catch (err) {
        console.warn('POST /api/reports/{id}/roadmap failed or unreachable, using client roadmap generator:', err);
      }

      const generated = getOrGenerateRoadmap(item.skill, item.reason);
      setRoadmapCache((prev) => ({
        ...prev,
        [item.skill]: generated,
      }));
    }
  };

  // Read report data from location.state or context or fallback
  const rawReport = (location.state as { reportData?: ReportData })?.reportData || location.state || reportData || fallbackReport;

  // Normalize matchedSkills (handle string[] or MatchedSkill[])
  const matchedSkillsList: MatchedSkill[] = (rawReport.matchedSkills || []).map((item: any) => {
    if (typeof item === 'string') {
      return { skill: item, foundIn: 'Submitted Artifacts' };
    }
    return { skill: item.skill || 'Unknown Skill', foundIn: item.foundIn || 'Submitted Profile' };
  });

  // Normalize missingSkills (handle string[] or MissingSkill[])
  const missingSkillsList: MissingSkill[] = (rawReport.missingSkills || []).map((item: any) => {
    if (typeof item === 'string') {
      return { skill: item, reason: 'Skill gap identified during analysis.' };
    }
    return { skill: item.skill || 'Unknown Skill', reason: item.reason || 'Not found in submitted data.' };
  });

  const report: ReportData = {
    ...fallbackReport,
    ...rawReport,
    matchedSkills: matchedSkillsList,
    missingSkills: missingSkillsList,
  };

  const handleRetake = () => {
    resetOnboarding();
    navigate('/onboarding/domain');
  };

  const handleDownload = async () => {
    setDownloadNotice(true);
    const reportId = report.id || 'current';
    try {
      const blob = await reportApi.downloadReport(reportId);
      if (blob && blob.size > 0 && blob.type?.includes('pdf')) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const student = (report.studentName || 'Student').replace(/[^a-z0-9]/gi, '_');
        const domain = (report.domainName || 'Domain').replace(/[^a-z0-9]/gi, '_');
        a.download = `PlacementReport_${student}_${domain}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        setTimeout(() => setDownloadNotice(false), 3000);
        return;
      }
    } catch (err) {
      console.warn('GET /api/reports/{id}/download unreachable or failed, generating client PDF:', err);
    }

    try {
      const doc = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4',
      });

      const marginX = 15;
      const contentWidth = 180;
      let y = 15;

      const checkAddPage = (neededHeight: number) => {
        if (y + neededHeight > 275) {
          doc.addPage();
          y = 15;
        }
      };

      // Header Banner
      doc.setFillColor(79, 70, 229); // Indigo 600
      doc.rect(15, y, 180, 24, 'F');

      doc.setTextColor(255, 255, 255);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(14);
      doc.text('PlaceMentor AI — Placement Readiness Report', 20, y + 9);

      doc.setFont('helvetica', 'normal');
      doc.setFontSize(9);
      doc.text(`Target Domain: ${report.domainName}  |  Generated: ${report.generatedAt}`, 20, y + 17);

      y += 30;

      // Candidate Profile Box
      checkAddPage(32);
      doc.setFillColor(248, 250, 252);
      doc.setDrawColor(226, 232, 240);
      doc.roundedRect(15, y, 180, 28, 2, 2, 'FD');

      doc.setTextColor(15, 23, 42);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(11);
      doc.text(`Student: ${report.studentName} (${report.branch})`, 20, y + 8);

      doc.setFont('helvetica', 'normal');
      doc.setFontSize(9.5);
      doc.setTextColor(71, 85, 105);
      doc.text(`Institution: ${report.collegeName}`, 20, y + 15);
      doc.text(`Readiness Index: ${report.readinessScore}/100 — ${report.grade}`, 20, y + 22);

      y += 34;

      // 1. Comparison Report & Benchmarking
      checkAddPage(20);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(11);
      doc.setTextColor(15, 23, 42);
      doc.text('1. Profile Benchmarking Summary', marginX, y);
      y += 6;

      doc.setFont('helvetica', 'normal');
      doc.setFontSize(9);
      doc.setTextColor(51, 65, 85);

      report.comparisonSummary.forEach((bullet, idx) => {
        const textLines = doc.splitTextToSize(`${idx + 1}. ${bullet}`, contentWidth - 5);
        checkAddPage(textLines.length * 4.5 + 2);
        doc.text(textLines, marginX + 2, y);
        y += textLines.length * 4.5 + 2;
      });

      y += 6;

      // 2. Matched Skills
      checkAddPage(20);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(11);
      doc.setTextColor(15, 23, 42);
      doc.text(`2. Verified Matched Skills (${report.matchedSkills.length})`, marginX, y);
      y += 6;

      doc.setFont('helvetica', 'normal');
      doc.setFontSize(9);
      doc.setTextColor(51, 65, 85);

      report.matchedSkills.forEach((item) => {
        const textLines = doc.splitTextToSize(`• ${item.skill} (Found in: ${item.foundIn})`, contentWidth - 5);
        checkAddPage(textLines.length * 4.5 + 1);
        doc.text(textLines, marginX + 2, y);
        y += textLines.length * 4.5 + 1;
      });

      y += 6;

      // 3. Missing Skills
      checkAddPage(20);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(11);
      doc.setTextColor(15, 23, 42);
      doc.text(`3. Identified Skill Gaps (${report.missingSkills.length})`, marginX, y);
      y += 6;

      doc.setFont('helvetica', 'normal');
      doc.setFontSize(9);
      doc.setTextColor(51, 65, 85);

      report.missingSkills.forEach((item) => {
        const textLines = doc.splitTextToSize(`• ${item.skill}: ${item.reason}`, contentWidth - 5);
        checkAddPage(textLines.length * 4.5 + 2);
        doc.text(textLines, marginX + 2, y);
        y += textLines.length * 4.5 + 2;
      });

      y += 8;

      // 4. Learning Roadmaps for All Missing Skills
      checkAddPage(20);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(12);
      doc.setTextColor(79, 70, 229);
      doc.text('4. Actionable Learning Roadmaps for Missing Skills', marginX, y);
      y += 8;

      report.missingSkills.forEach((missingItem, idx) => {
        const roadmap = roadmapCache[missingItem.skill] || getOrGenerateRoadmap(missingItem.skill, missingItem.reason);

        checkAddPage(25);
        doc.setFillColor(243, 244, 246);
        doc.rect(marginX, y, contentWidth, 8, 'F');
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(10);
        doc.setTextColor(15, 23, 42);
        doc.text(`Roadmap ${idx + 1}: ${roadmap.skillName} (${roadmap.estimatedTime})`, marginX + 3, y + 5.5);
        y += 12;

        doc.setFont('helvetica', 'normal');
        doc.setFontSize(8.5);
        doc.setTextColor(71, 85, 105);
        const overviewLines = doc.splitTextToSize(`Overview: ${roadmap.overview}`, contentWidth - 4);
        checkAddPage(overviewLines.length * 4 + 2);
        doc.text(overviewLines, marginX + 2, y);
        y += overviewLines.length * 4 + 3;

        roadmap.phases.forEach((phase) => {
          checkAddPage(15);
          doc.setFont('helvetica', 'bold');
          doc.setFontSize(9);
          doc.setTextColor(30, 41, 59);
          doc.text(`${phase.title} [${phase.duration}]`, marginX + 4, y);
          y += 5;

          doc.setFont('helvetica', 'normal');
          doc.setFontSize(8.5);
          doc.setTextColor(51, 65, 85);
          phase.items.forEach((item) => {
            const itemLines = doc.splitTextToSize(`  - ${item}`, contentWidth - 10);
            checkAddPage(itemLines.length * 4);
            doc.text(itemLines, marginX + 4, y);
            y += itemLines.length * 4 + 1;
          });
          y += 2;
        });

        checkAddPage(12);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(8.5);
        doc.setTextColor(16, 185, 129);
        const milestoneLines = doc.splitTextToSize(`Capstone Goal: ${roadmap.keyOutcome}`, contentWidth - 6);
        doc.text(milestoneLines, marginX + 4, y);
        y += milestoneLines.length * 4 + 6;
      });

      // Filename: PlacementReport_[StudentName]_[Domain].pdf
      const cleanStudentName = (report.studentName || 'Student').replace(/[^a-zA-Z0-9]/g, '');
      const cleanDomain = (report.domainName || 'Domain').replace(/[^a-zA-Z0-9]/g, '');
      const fileName = `PlacementReport_${cleanStudentName}_${cleanDomain}.pdf`;

      doc.save(fileName);
    } catch (err) {
      console.error('Failed to generate PDF:', err);
    } finally {
      setDownloadNotice(false);
    }
  };

  // Profile Analysis Data
  const pa = report.profileAnalysis || fallbackReport.profileAnalysis;

  const githubData = {
    repoCount: pa?.github?.repoCount ?? pa?.github?.reposCount ?? 18,
    topLanguages: pa?.github?.topLanguages ?? ['TypeScript', 'Python', 'Go', 'React'],
    summary:
      pa?.github?.summary ||
      (pa?.github?.highlights && pa.github.highlights.length > 0
        ? pa.github.highlights.join('. ')
        : 'Public repositories exhibit clean modular TypeScript code, robust architectural patterns, and continuous integration workflows.'),
  };

  const leetcodeData = {
    solved: pa?.leetcode?.solved ?? { easy: 85, medium: 110, hard: 20 },
    solvedCount:
      pa?.leetcode?.solvedCount ??
      (pa?.leetcode?.solved
        ? pa.leetcode.solved.easy + pa.leetcode.solved.medium + pa.leetcode.solved.hard
        : 215),
    topTags: pa?.leetcode?.topTags ?? ['Dynamic Programming', 'Trees & Graphs', 'Binary Search', 'Sliding Window'],
  };

  const hackerRankData = {
    badges: pa?.hackerrank?.badges ?? pa?.hackerrank?.primarySkills ?? ['Problem Solving 5★', 'Python 5★', 'SQL 4★', 'Gold Developer'],
    topCategories: pa?.hackerrank?.topCategories ?? ['Data Structures', 'Algorithms', 'Databases'],
  };

  const githubLink = profileLinks?.githubUrl?.trim() || 'https://github.com';
  const leetcodeLink = profileLinks?.leetcodeUrl?.trim() || 'https://leetcode.com';
  const hackerRankLink = profileLinks?.hackerRankUrl?.trim() || 'https://hackerrank.com';

  // Circular gauge calculations
  const radius = 46;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (report.readinessScore / 100) * circumference;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col justify-between p-4 sm:p-6 md:p-10 antialiased selection:bg-indigo-500 selection:text-white print:p-0 print:bg-white">
      {/* Top Header Navigation */}
      <header className="w-full max-w-5xl mx-auto flex items-center justify-between pb-6 print:hidden">
        <Link to="/" className="flex items-center gap-2">
          <div className="p-2 bg-indigo-600 text-white rounded-xl shadow-sm">
            <Sparkles className="w-5 h-5" />
          </div>
          <span className="font-bold text-slate-900 text-base tracking-tight">
            PlaceMentor AI
          </span>
        </Link>

        <div className="flex items-center gap-2">
          <button
            onClick={handleDownload}
            disabled={downloadNotice}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-slate-800 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 shadow-xs cursor-pointer transition-colors disabled:opacity-60"
          >
            <Download className={`w-3.5 h-3.5 text-indigo-600 ${downloadNotice ? 'animate-bounce' : ''}`} />
            <span>{downloadNotice ? 'Generating PDF...' : 'Download Report'}</span>
          </button>
          <button
            onClick={handleRetake}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-indigo-600 bg-indigo-50 border border-indigo-100 rounded-xl hover:bg-indigo-100 cursor-pointer transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>New Analysis</span>
          </button>
        </div>
      </header>

      {/* Main Report Container */}
      <main className="w-full max-w-5xl mx-auto space-y-6">
        {/* Header Summary Card with Circular Readiness Score Gauge */}
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 sm:p-8 flex flex-col md:flex-row items-center justify-between gap-8">
          {/* Candidate Metadata */}
          <div className="flex-1 space-y-3 text-center md:text-left">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-100 text-xs font-bold uppercase tracking-wider">
              <Briefcase className="w-3.5 h-3.5" />
              <span>Target Domain: {report.domainName}</span>
            </div>
            
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              Placement Readiness Analysis
            </h1>

            <div className="flex flex-wrap items-center justify-center md:justify-start gap-4 text-xs sm:text-sm text-slate-600 pt-1">
              <span className="flex items-center gap-1.5 font-semibold text-slate-800">
                <GraduationCap className="w-4 h-4 text-indigo-500" />
                {report.studentName} ({report.branch})
              </span>
              <span className="flex items-center gap-1.5 text-slate-500">
                <Building2 className="w-4 h-4 text-slate-400" />
                {report.collegeName}
              </span>
              <span className="text-slate-400">Generated: {report.generatedAt}</span>
            </div>
          </div>

          {/* Circular Readiness-Score Gauge */}
          <div className="flex items-center gap-6 p-5 bg-gradient-to-br from-slate-900 to-indigo-950 text-white rounded-2xl shadow-md shrink-0 w-full md:w-auto justify-center">
            <div className="relative flex items-center justify-center w-28 h-28 shrink-0">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                {/* Background Track */}
                <circle
                  cx="50"
                  cy="50"
                  r={radius}
                  className="stroke-slate-800"
                  strokeWidth="8"
                  fill="transparent"
                />
                {/* Score Fill Line */}
                <circle
                  cx="50"
                  cy="50"
                  r={radius}
                  className="stroke-indigo-400 transition-all duration-1000 ease-out"
                  strokeWidth="8"
                  strokeDasharray={circumference}
                  strokeDashoffset={strokeDashoffset}
                  strokeLinecap="round"
                  fill="transparent"
                />
              </svg>

              {/* Score Value Overlay */}
              <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                <span className="text-3xl font-black text-indigo-200 tracking-tight leading-none">
                  {report.readinessScore}
                </span>
                <span className="text-[10px] text-indigo-300 font-semibold uppercase mt-0.5">
                  / 100
                </span>
              </div>
            </div>

            <div className="space-y-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-300">
                Readiness Index
              </span>
              <h3 className="text-lg font-bold text-white leading-tight">
                {report.grade}
              </h3>
              <p className="text-xs text-emerald-400 font-medium flex items-center gap-1 pt-0.5">
                <Award className="w-3.5 h-3.5" />
                Verified Competency Index
              </p>
            </div>
          </div>
        </div>

        {/* Profile Analysis Section */}
        <section className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 sm:p-8 space-y-6">
          <div className="flex items-center justify-between pb-4 border-b border-slate-100 flex-wrap gap-2">
            <div className="flex items-center gap-2.5">
              <div className="p-2.5 bg-indigo-50 text-indigo-600 rounded-xl border border-indigo-100">
                <FolderGit2 className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                  <span>Profile Analysis</span>
                  <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-100">
                    Platform Breakdown
                  </span>
                </h2>
                <p className="text-xs text-slate-500">
                  Extracted metrics and verified insights from your submitted developer profiles
                </p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {/* GitHub Card */}
            <div className="bg-slate-50/70 rounded-xl border border-slate-200/80 p-5 flex flex-col justify-between space-y-4 hover:border-slate-300 transition-colors">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="p-2 bg-slate-900 text-white rounded-lg">
                      <Github className="w-4 h-4" />
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-slate-900">GitHub Profile</h3>
                      <p className="text-[11px] font-medium text-slate-500">
                        {githubData.repoCount} Public Repositories
                      </p>
                    </div>
                  </div>
                  <a
                    href={githubLink}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-700 hover:underline"
                  >
                    <span>View Profile</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>

                <div className="space-y-2 pt-1">
                  <div className="flex flex-wrap items-center gap-1.5">
                    <span className="text-[11px] font-semibold text-slate-500 mr-1">Top Languages:</span>
                    {githubData.topLanguages.map((lang, idx) => (
                      <span
                        key={idx}
                        className="text-[11px] font-medium px-2.5 py-0.5 rounded-md bg-white border border-slate-200 text-slate-700 shadow-xs"
                      >
                        {lang}
                      </span>
                    ))}
                  </div>

                  <p className="text-xs text-slate-600 leading-relaxed bg-white/70 p-3 rounded-lg border border-slate-100">
                    {githubData.summary}
                  </p>
                </div>
              </div>
            </div>

            {/* LeetCode Card */}
            <div className="bg-slate-50/70 rounded-xl border border-slate-200/80 p-5 flex flex-col justify-between space-y-4 hover:border-slate-300 transition-colors">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="p-2 bg-amber-500 text-white rounded-lg">
                      <Code2 className="w-4 h-4" />
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-slate-900">LeetCode Analytics</h3>
                      <p className="text-[11px] font-medium text-amber-700">
                        {leetcodeData.solvedCount} Problems Solved
                      </p>
                    </div>
                  </div>
                  <a
                    href={leetcodeLink}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-700 hover:underline"
                  >
                    <span>View Profile</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>

                <div className="space-y-2.5 pt-1">
                  {/* Difficulty breakdown */}
                  <div className="grid grid-cols-3 gap-2">
                    <div className="bg-emerald-50 border border-emerald-100 rounded-lg p-2 text-center">
                      <span className="block text-[10px] font-bold text-emerald-600 uppercase">Easy</span>
                      <span className="text-sm font-extrabold text-emerald-800">{leetcodeData.solved.easy}</span>
                    </div>
                    <div className="bg-amber-50 border border-amber-100 rounded-lg p-2 text-center">
                      <span className="block text-[10px] font-bold text-amber-600 uppercase">Medium</span>
                      <span className="text-sm font-extrabold text-amber-800">{leetcodeData.solved.medium}</span>
                    </div>
                    <div className="bg-rose-50 border border-rose-100 rounded-lg p-2 text-center">
                      <span className="block text-[10px] font-bold text-rose-600 uppercase">Hard</span>
                      <span className="text-sm font-extrabold text-rose-800">{leetcodeData.solved.hard}</span>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-1.5 pt-1">
                    <span className="text-[11px] font-semibold text-slate-500 mr-1">Top Tags:</span>
                    {leetcodeData.topTags.map((tag, idx) => (
                      <span
                        key={idx}
                        className="text-[11px] font-medium px-2.5 py-0.5 rounded-md bg-white border border-slate-200 text-slate-700 shadow-xs"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* HackerRank Card */}
            <div className="bg-slate-50/70 rounded-xl border border-slate-200/80 p-5 flex flex-col justify-between space-y-4 hover:border-slate-300 transition-colors">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="p-2 bg-emerald-600 text-white rounded-lg">
                      <Terminal className="w-4 h-4" />
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-slate-900">HackerRank Credentials</h3>
                      <p className="text-[11px] font-medium text-emerald-700">
                        {hackerRankData.badges.length} Verified Badges
                      </p>
                    </div>
                  </div>
                  <a
                    href={hackerRankLink}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-700 hover:underline"
                  >
                    <span>View Profile</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>

                <div className="space-y-2.5 pt-1">
                  <div>
                    <span className="block text-[11px] font-semibold text-slate-500 mb-1.5">Earned Badges:</span>
                    <div className="flex flex-wrap gap-1.5">
                      {hackerRankData.badges.map((badge, idx) => (
                        <span
                          key={idx}
                          className="inline-flex items-center gap-1 text-[11px] font-semibold px-2.5 py-0.5 rounded-md bg-emerald-50 border border-emerald-200 text-emerald-800"
                        >
                          <Award className="w-3 h-3 text-emerald-600" />
                          <span>{badge}</span>
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-1.5 pt-1">
                    <span className="text-[11px] font-semibold text-slate-500 mr-1">Top Categories:</span>
                    {hackerRankData.topCategories.map((cat, idx) => (
                      <span
                        key={idx}
                        className="text-[11px] font-medium px-2.5 py-0.5 rounded-md bg-white border border-slate-200 text-slate-700 shadow-xs"
                      >
                        {cat}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

          </div>
        </section>

        {/* Comparison Report Bullet List */}
        <section className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 sm:p-8 space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-xl">
              <TrendingUp className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-900">
                Comparison Report & Benchmarking Summary
              </h2>
              <p className="text-xs text-slate-500">
                Evaluating candidate strengths against industry hiring standards for {report.domainName}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-3 pt-2">
            {report.comparisonSummary && report.comparisonSummary.length > 0 ? (
              report.comparisonSummary.map((bullet, idx) => (
                <div
                  key={idx}
                  className="flex items-start gap-3.5 p-3.5 rounded-xl border border-slate-100 bg-slate-50/60 hover:bg-slate-50 transition-colors"
                >
                  <div className="w-6 h-6 rounded-lg bg-indigo-600 text-white flex items-center justify-center text-xs font-bold shrink-0 mt-0.5 shadow-xs">
                    {idx + 1}
                  </div>
                  <p className="text-sm text-slate-700 leading-relaxed font-normal">
                    {bullet}
                  </p>
                </div>
              ))
            ) : (
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-500 text-center">
                No benchmarking items available for this domain analysis.
              </div>
            )}
          </div>
        </section>

        {/* 2 Grids: Matched Skills & Missing Skills */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Matched Skills Grid */}
          <section className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <div className="p-2 bg-emerald-50 text-emerald-600 rounded-xl">
                  <CheckCircle2 className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-900">
                    Matched Skills ({report.matchedSkills.length})
                  </h3>
                  <p className="text-xs text-slate-500">Verified from profiles & resume</p>
                </div>
              </div>
              <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200/60">
                Verified Match
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
              {report.matchedSkills && report.matchedSkills.length > 0 ? (
                report.matchedSkills.map((item, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded-xl border border-emerald-100 bg-emerald-50/30 flex flex-col justify-between gap-3 shadow-2xs"
                  >
                    <div className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                      <span className="text-xs sm:text-sm font-semibold text-slate-900 leading-snug">
                        {item.skill}
                      </span>
                    </div>
                    <div>
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-white border border-emerald-200 text-[11px] font-medium text-emerald-800">
                        <span className="text-emerald-500 font-bold">Found in:</span> {item.foundIn}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="col-span-full p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-500 text-center">
                  No matched skills found for this profile. Try linking GitHub or uploading a detailed resume.
                </div>
              )}
            </div>
          </section>

          {/* Missing Skills Grid */}
          <section className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <div className="p-2 bg-amber-50 text-amber-600 rounded-xl">
                  <XCircle className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-900">
                    Missing Skills ({report.missingSkills.length})
                  </h3>
                  <p className="text-xs text-slate-500">Click any card to view detailed learning modal</p>
                </div>
              </div>
              <span className="text-[10px] font-bold text-amber-800 bg-amber-50 px-2.5 py-1 rounded-full border border-amber-200/60">
                Skill Gaps
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
              {report.missingSkills && report.missingSkills.length > 0 ? (
                report.missingSkills.map((item, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleOpenSkillModal(item)}
                    className="p-4 rounded-xl border border-amber-200/70 bg-amber-50/20 hover:bg-amber-50/60 hover:border-amber-300 text-left flex flex-col justify-between gap-2 shadow-2xs cursor-pointer transition-all group"
                  >
                    <div>
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-start gap-2">
                          <XCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                          <span className="text-xs sm:text-sm font-bold text-slate-900 leading-snug group-hover:text-amber-900">
                            {item.skill}
                          </span>
                        </div>
                        <ExternalLink className="w-3.5 h-3.5 text-slate-400 group-hover:text-amber-600 shrink-0" />
                      </div>
                      <p className="text-xs text-slate-500 line-clamp-2 mt-2 leading-relaxed">
                        {item.reason}
                      </p>
                    </div>

                    <span className="inline-block text-[10px] font-bold text-amber-700 underline underline-offset-2 mt-1">
                      Click to view roadmap →
                    </span>
                  </button>
                ))
              ) : (
                <div className="col-span-full p-4 rounded-xl bg-emerald-50/50 border border-emerald-200 text-xs text-emerald-800 text-center font-medium">
                  No missing skill gaps identified! You meet all essential technical benchmarks.
                </div>
              )}
            </div>
          </section>
        </div>

        {/* Actionable Recommendations */}
        <section className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 sm:p-8 space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-xl">
              <BookOpen className="w-5 h-5" />
            </div>
            <h2 className="text-lg font-bold text-slate-900">
              Personalized Upskilling Action Plan
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
            {report.recommendations && report.recommendations.length > 0 ? (
              report.recommendations.map((rec, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-xl border border-slate-100 bg-slate-50/50 flex flex-col justify-between space-y-3"
                >
                  <div>
                    <span
                      className={`inline-block text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md mb-2 ${
                        rec.priority === 'High'
                          ? 'bg-red-50 text-red-700 border border-red-200'
                          : 'bg-indigo-50 text-indigo-700 border border-indigo-200'
                      }`}
                    >
                      {rec.priority} Priority
                    </span>
                    <h4 className="text-sm font-bold text-slate-900 mb-1">{rec.title}</h4>
                    <p className="text-xs text-slate-500 leading-relaxed">{rec.desc}</p>
                  </div>
                </div>
              ))
            ) : (
              <div className="col-span-full p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-500 text-center">
                No active upskilling recommendations available.
              </div>
            )}
          </div>
        </section>

        {/* Portfolio Suggestions */}
        {report.projectSuggestions && report.projectSuggestions.length > 0 && (
          <section className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 sm:p-8 space-y-4">
            <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
              <div className="p-2 bg-indigo-50 text-indigo-600 rounded-xl">
                <FolderGit2 className="w-5 h-5" />
              </div>
              <h2 className="text-lg font-bold text-slate-900">
                Recommended Portfolio Boosters
              </h2>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              {report.projectSuggestions.map((proj, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-xl bg-indigo-50/40 border border-indigo-100 flex items-start gap-3"
                >
                  <Sparkles className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
                  <div>
                    <h4 className="text-xs font-bold text-indigo-950 uppercase tracking-wider mb-0.5">
                      Suggested Portfolio Project #{idx + 1}
                    </h4>
                    <p className="text-sm text-slate-700 font-medium">{proj}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="w-full max-w-5xl mx-auto text-center py-6 text-xs text-slate-400 print:hidden">
        PlaceMentor AI • Placement Readiness Report
      </footer>

      {/* Missing Skill Learning Roadmap Modal */}
      {activeModalSkill && (
        <SkillRoadmapModal
          skill={activeModalSkill}
          onClose={() => setActiveModalSkill(null)}
          roadmapData={
            roadmapCache[activeModalSkill.skill] ||
            getOrGenerateRoadmap(activeModalSkill.skill, activeModalSkill.reason)
          }
        />
      )}
    </div>
  );
};

export default Report;

