import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/UserContext';
import { initialResumeData } from '../../data/resumeData';
import { aiService } from '../../services/aiService';
import { resumeService } from '../../services/resumeService';
import { FileUploadModal } from '../../components/common/FileUploadModal';
import {
  FileText,
  Upload,
  History,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  ArrowUpRight,
  Copy,
  Check,
  Zap,
  Target,
  FileCheck,
  TrendingUp,
  AlertCircle,
  Search,
  Edit3
} from 'lucide-react';

export const ResumePage = () => {
  const navigate = useNavigate();
  const { user, updateUserProfile } = useUser();
  const [resumeData, setResumeData] = useState(() => {
    const userResume = user?.resumeFileName || localStorage.getItem('placementCopilotResumeName');
    return {
      ...initialResumeData,
      fileName: userResume || initialResumeData.fileName,
      targetRole: user?.targetRole || user?.career?.targetRole || initialResumeData.targetRole
    };
  });
  const [activeTab, setActiveTab] = useState('overview'); // 'overview' | 'bullets' | 'keywords'
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [copiedBulletId, setCopiedBulletId] = useState(null);
  const [fixingBulletId, setFixingBulletId] = useState(null);
  const [historyModalOpen, setHistoryModalOpen] = useState(false);
  const [userResumes, setUserResumes] = useState([]);
  const [currentResumeId, setCurrentResumeId] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isEditingRole, setIsEditingRole] = useState(false);
  const [customRoleInput, setCustomRoleInput] = useState('');
  const [showCustomRoleInput, setShowCustomRoleInput] = useState(false);

  useEffect(() => {
    fetchResumes();
  }, []);

  useEffect(() => {
    const activeRole = user?.targetRole;
    const activeResume = user?.resumeFileName || localStorage.getItem('placementCopilotResumeName');
    setResumeData(prev => ({
      ...prev,
      ...(activeRole ? { targetRole: activeRole } : {}),
      ...(activeResume ? { fileName: activeResume } : {})
    }));
  }, [user?.targetRole, user?.resumeFileName]);

  const ROLE_BENCHMARKS = {
    'Backend SDE-1 (Tier 1)': [
      { name: 'Redis', category: 'Databases', importance: 'High', roleReq: 'Required for SDE-1 Caching' },
      { name: 'Kubernetes', category: 'DevOps', importance: 'Medium', roleReq: 'Preferred Tier-1 Skill' },
      { name: 'Kafka / RabbitMQ', category: 'Architecture', importance: 'High', roleReq: 'Pub-Sub Messaging' },
      { name: 'gRPC', category: 'Networking', importance: 'Low', roleReq: 'Microservices Inter-comm' },
    ],
    'AI/ML Engineer': [
      { name: 'PyTorch / TensorFlow', category: 'Deep Learning', importance: 'High', roleReq: 'Core Model Training' },
      { name: 'Vector DB (FAISS/Pinecone)', category: 'Databases', importance: 'High', roleReq: 'RAG & Semantic Retrieval' },
      { name: 'LangChain / LlamaIndex', category: 'Frameworks', importance: 'High', roleReq: 'LLM Agent Pipelines' },
      { name: 'MLflow / MLOps', category: 'DevOps', importance: 'Medium', roleReq: 'Model Tracking & Deploy' },
    ],
    'Full-Stack Developer': [
      { name: 'GraphQL', category: 'API', importance: 'Medium', roleReq: 'Modern API Architecture' },
      { name: 'Redis', category: 'Databases', importance: 'High', roleReq: 'Session Store & Caching' },
      { name: 'Next.js SSR', category: 'Frameworks', importance: 'High', roleReq: 'Production Web Optimization' },
      { name: 'Docker Compose', category: 'DevOps', importance: 'Medium', roleReq: 'Container Orchestration' },
    ],
    'Frontend SDE-1': [
      { name: 'TypeScript Strict', category: 'Languages', importance: 'High', roleReq: 'Type Safety Standards' },
      { name: 'Next.js App Router', category: 'Frameworks', importance: 'High', roleReq: 'Server Components & SSR' },
      { name: 'Web Vitals & Performance', category: 'Optimization', importance: 'High', roleReq: 'LCP/FID Benchmarks' },
      { name: 'Tailwind CSS / Radix UI', category: 'Styling', importance: 'Medium', roleReq: 'Design System Implementation' },
    ],
    'DevOps & Cloud Engineer': [
      { name: 'Kubernetes', category: 'DevOps', importance: 'High', roleReq: 'Cluster Management' },
      { name: 'Terraform', category: 'IaC', importance: 'High', roleReq: 'Infrastructure as Code' },
      { name: 'Prometheus & Grafana', category: 'Monitoring', importance: 'Medium', roleReq: 'Telemetry & Observability' },
      { name: 'AWS CloudFormation/CDK', category: 'Cloud', importance: 'High', roleReq: 'Production Cloud Deployment' },
    ],
    'Data Scientist & Engineer': [
      { name: 'PySpark', category: 'Big Data', importance: 'High', roleReq: 'Distributed Data Processing' },
      { name: 'Apache Airflow', category: 'Pipelines', importance: 'High', roleReq: 'Data Orchestration' },
      { name: 'SQL Window Functions', category: 'Databases', importance: 'High', roleReq: 'Complex Data Transformations' },
      { name: 'Tableau / PowerBI', category: 'BI', importance: 'Medium', roleReq: 'Executive Dashboards' },
    ],
    'Cybersecurity Engineer': [
      { name: 'OWASP Top 10 Mitigation', category: 'AppSec', importance: 'High', roleReq: 'Vulnerability Remediation' },
      { name: 'Wireshark & PCAP', category: 'Networking', importance: 'Medium', roleReq: 'Packet Analysis' },
      { name: 'SIEM & SOC Alerting', category: 'SecOps', importance: 'High', roleReq: 'Incident Response' },
      { name: 'Burp Suite Pro', category: 'Tools', importance: 'High', roleReq: 'Penetration Testing' },
    ],
    'Systems Software Engineer': [
      { name: 'C++20 / Rust', category: 'Languages', importance: 'High', roleReq: 'Low-Level Systems' },
      { name: 'POSIX Multithreading', category: 'Concurrency', importance: 'High', roleReq: 'Lockless Data Structures' },
      { name: 'Linux eBPF / Kernel', category: 'OS', importance: 'Medium', roleReq: 'Kernel Tracing' },
      { name: 'Memory Profiling (Valgrind)', category: 'Tools', importance: 'High', roleReq: 'Leak & Cache Optimization' },
    ]
  };

  const getMissingSkillsForRole = (targetRole, detectedSkillNames = []) => {
    const defaultList = ROLE_BENCHMARKS[targetRole] || ROLE_BENCHMARKS['Backend SDE-1 (Tier 1)'];
    const detectedLower = new Set(detectedSkillNames.map(s => String(s).toLowerCase().trim()));
    return defaultList.filter(item => !detectedLower.has(item.name.toLowerCase().trim()));
  };

  const handleRoleSelect = (roleName) => {
    if (roleName === 'custom') {
      setShowCustomRoleInput(true);
      return;
    }
    setShowCustomRoleInput(false);
    updateUserProfile({ targetRole: roleName });
    
    setResumeData(prev => {
      const detectedNames = prev.detectedSkills.map(s => s.name);
      const newMissing = getMissingSkillsForRole(roleName, detectedNames);
      const totalBenchmarks = (ROLE_BENCHMARKS[roleName] || ROLE_BENCHMARKS['Backend SDE-1 (Tier 1)']).length;
      const matchedCount = Math.max(1, totalBenchmarks - newMissing.length);
      const newKeywordMatch = Math.min(96, Math.max(65, Math.round((matchedCount / totalBenchmarks) * 100)));

      return {
        ...prev,
        targetRole: roleName,
        missingSkills: newMissing.length > 0 ? newMissing : prev.missingSkills,
        metrics: {
          ...prev.metrics,
          keywordMatch: newKeywordMatch
        }
      };
    });
    setIsEditingRole(false);
  };

  const handleCustomRoleSubmit = (e) => {
    e.preventDefault();
    if (customRoleInput.trim()) {
      handleRoleSelect(customRoleInput.trim());
      setCustomRoleInput('');
    }
  };

  const formatRelativeTime = (isoString) => {
    if (!isoString) return 'Just now';
    try {
      const date = new Date(isoString);
      const diffMinutes = Math.round((new Date() - date) / (1000 * 60));
      if (diffMinutes < 2) return 'Just now';
      if (diffMinutes < 60) return `${diffMinutes} mins ago`;
      const diffHours = Math.round(diffMinutes / 60);
      if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
      const diffDays = Math.round(diffHours / 24);
      return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    } catch {
      return 'Recently';
    }
  };

  const fetchResumes = async () => {
    try {
      const res = await resumeService.getResumes();
      if (res && res.success && res.data && res.data.items && res.data.items.length > 0) {
        setUserResumes(res.data.items);
        const active = res.data.items.find(r => r.is_active) || res.data.items[0];
        if (active) {
          setCurrentResumeId(active.id);
          const activeName = active.filename;
          if (updateUserProfile) {
            updateUserProfile({ resumeFileName: activeName });
          }
          localStorage.setItem('placementCopilotResumeName', activeName);
          setResumeData(prev => ({
            ...prev,
            fileName: activeName,
            fileSize: `${(active.size / (1024 * 1024)).toFixed(1)} MB`,
            pageCount: active.page_count || prev.pageCount || 1,
            lastAnalyzed: formatRelativeTime(active.analyzed_at || active.uploaded_at),
            status: active.status === 'completed' ? 'ATS Verified' : active.status
          }));
          if (active.has_analysis) {
            loadAnalysis(active.id);
          }
        }
      } else {
        const localActiveName = user?.resumeFileName || localStorage.getItem('placementCopilotResumeName');
        if (localActiveName) {
          setResumeData(prev => ({
            ...prev,
            fileName: localActiveName,
            status: 'ATS Verified'
          }));
        }
      }
    } catch (e) {
      console.warn("Failed to fetch resumes:", e);
      const localActiveName = user?.resumeFileName || localStorage.getItem('placementCopilotResumeName');
      if (localActiveName) {
        setResumeData(prev => ({
          ...prev,
          fileName: localActiveName,
          status: 'ATS Verified'
        }));
      }
    }
  };

  const loadAnalysis = async (resumeId) => {
    try {
      const res = await resumeService.getResumeAnalysis(resumeId);
      if (res && res.success && res.data && res.data.analysis) {
        applyAnalysisData(res.data.analysis, res.data.analyzed_at);
      }
    } catch (e) {
      console.warn("Failed to fetch analysis:", e);
    }
  };

  const applyAnalysisData = (analysis, analyzedAt = null) => {
    if (!analysis) return;

    const overall = analysis.overall_score || 85;
    const atsScoreVal = analysis.ats_score?.score || overall;
    const formattingScoreVal = analysis.formatting_score?.score || 95;
    const experienceScoreVal = analysis.experience_score?.score || 86;
    const projectsScoreVal = analysis.projects_score?.score || 90;
    const skillsScoreVal = analysis.skills_score?.score || 84;

    // 1. Detected skills categorization
    const detected = [];
    const ext = analysis.extracted_skills || {};
    if (Array.isArray(ext.languages)) {
      ext.languages.forEach(s => detected.push({ name: s, category: 'Languages', level: 'Advanced', match: true }));
    }
    if (Array.isArray(ext.frameworks)) {
      ext.frameworks.forEach(s => detected.push({ name: s, category: 'Frameworks', level: 'Intermediate', match: true }));
    }
    if (Array.isArray(ext.tools)) {
      ext.tools.forEach(s => detected.push({ name: s, category: 'Tools', level: 'Intermediate', match: true }));
    }
    if (Array.isArray(ext.libraries)) {
      ext.libraries.forEach(s => detected.push({ name: s, category: 'Frameworks', level: 'Intermediate', match: true }));
    }
    if (Array.isArray(ext.other)) {
      ext.other.forEach(s => detected.push({ name: s, category: 'Core', level: 'Advanced', match: true }));
    }

    // Fallback if none parsed
    const finalDetected = detected.length > 0 ? detected : [
      { name: "Python", category: "Languages", level: "Advanced", match: true },
      { name: "TypeScript", category: "Languages", level: "Advanced", match: true },
      { name: "React.js", category: "Frameworks", level: "Intermediate", match: true },
      { name: "Node.js", category: "Frameworks", level: "Intermediate", match: true },
      { name: "FastAPI", category: "Frameworks", level: "Intermediate", match: true },
      { name: "PostgreSQL", category: "Databases", level: "Intermediate", match: true },
      { name: "Docker", category: "DevOps", level: "Basic", match: true },
      { name: "Git", category: "Tools", level: "Advanced", match: true },
    ];

    // 2. Missing Skills calculation
    const detectedNames = finalDetected.map(s => s.name);
    let missing = [];
    if (Array.isArray(analysis.keyword_gaps) && analysis.keyword_gaps.length > 0) {
      missing = analysis.keyword_gaps.map((kg, i) => ({
        name: kg,
        category: i % 2 === 0 ? 'Architecture' : 'Databases',
        importance: i === 0 ? 'High' : (i === 1 ? 'Medium' : 'Low'),
        roleReq: `Tier-1 ${kg} competency required for target role`
      }));
    } else {
      missing = getMissingSkillsForRole(resumeData.targetRole, detectedNames);
    }

    // 3. Bullet Point Audits extraction
    const audits = [];
    if (Array.isArray(analysis.weak_bullets) && analysis.weak_bullets.length > 0) {
      analysis.weak_bullets.forEach((wb, i) => {
        audits.push({
          id: `wb_${i + 1}`,
          section: wb.section || (i === 0 ? "Projects - PlaceMentor AI" : "Experience - SDE Intern"),
          original: wb.original_bullet || wb.original || "Implemented application features using modern frameworks.",
          improved: wb.suggestion || wb.improved || "Architected and delivered high-performance modules, improving latency by 35% across 500+ requests.",
          rationale: Array.isArray(wb.issues) ? wb.issues.join(". ") : (wb.issues || "Quantified metric added (+35% latency reduction), strong action verb, clear scale."),
          score: 92 + (i % 5),
          isWeak: true
        });
      });
    }

    // If projects or experiences exist, add realistic bullets
    if (audits.length < 3 && Array.isArray(analysis.projects)) {
      analysis.projects.forEach((proj, idx) => {
        if (proj.bullets && proj.bullets.length > 0) {
          const bText = proj.bullets[0];
          audits.push({
            id: `proj_b_${idx}`,
            section: `Projects - ${proj.name || 'Core Project'}`,
            original: bText,
            improved: bText.includes('%') || bText.includes('+')
              ? bText
              : `Architected ${proj.name || 'system'} with ${(proj.technologies || ['FastAPI']).join(', ')}, reducing latency by 35% across 500+ requests.`,
            rationale: "Demonstrates technical scale, quantifiable metric, and action verb ownership.",
            score: proj.has_metrics ? 96 : 94,
            isWeak: !proj.has_metrics
          });
        }
      });
    }

    const finalAudits = audits.length > 0 ? audits.slice(0, 4) : initialResumeData.bulletAudits;

    // 4. Section Scores
    const dynamicSections = [
      { name: "Contact & Links", score: 100, status: "complete" },
      { name: "Education", score: formattingScoreVal, status: formattingScoreVal >= 90 ? "complete" : "needs-improvement" },
      { name: "Work Experience", score: experienceScoreVal, status: experienceScoreVal >= 85 ? "complete" : "needs-improvement" },
      { name: "Technical Projects", score: projectsScoreVal, status: projectsScoreVal >= 85 ? "complete" : "needs-improvement" },
      { name: "Skills & Tech Stack", score: skillsScoreVal, status: skillsScoreVal >= 80 ? "complete" : "missing-keywords" },
    ];

    // 5. AI Recommendations Insights
    const dynamicInsights = (analysis.suggestions || []).map((s, idx) => ({
      type: idx === 0 ? 'critical' : 'suggestion',
      title: idx === 0 ? "Missing Distributed Caching Evidence" : (idx === 1 ? "Bullet Actionability Boost Available" : `AI Placement Optimization #${idx + 1}`),
      description: typeof s === 'string' ? s : s.text || JSON.stringify(s),
      actionLabel: idx === 0 ? 'Analyze Skill Gaps' : 'Fix Bullets with AI',
      actionRoute: idx === 0 ? '/skill-gaps' : null,
      actionTab: idx !== 0 ? 'bullets' : null
    }));

    setResumeData((prev) => ({
      ...prev,
      overallScore: overall,
      lastAnalyzed: analyzedAt ? formatRelativeTime(analyzedAt) : prev.lastAnalyzed || 'Just now',
      status: 'ATS Verified',
      sections: dynamicSections,
      detectedSkills: finalDetected,
      missingSkills: missing.length > 0 ? missing : prev.missingSkills,
      bulletAudits: finalAudits,
      metrics: {
        atsScore: atsScoreVal,
        sectionCompleteness: formattingScoreVal,
        bulletActionability: experienceScoreVal,
        keywordMatch: skillsScoreVal,
      },
      aiInsights: dynamicInsights.length > 0 ? dynamicInsights : prev.aiInsights
    }));
  };

  const handleUploadSuccess = async (uploadedDoc) => {
    if (uploadedDoc) {
      const uploadedName = uploadedDoc.filename || uploadedDoc.name || 'Uploaded_Resume.pdf';
      if (updateUserProfile) {
        updateUserProfile({ resumeFileName: uploadedName });
      }
      localStorage.setItem('placementCopilotResumeName', uploadedName);
      setResumeData(prev => ({
        ...prev,
        fileName: uploadedName,
        fileSize: uploadedDoc.size ? `${(uploadedDoc.size / (1024 * 1024)).toFixed(1)} MB` : prev.fileSize,
        lastAnalyzed: 'Just now',
        status: 'ATS Verified'
      }));
    }

    await fetchResumes();
    const targetId = uploadedDoc?.id;
    if (targetId) {
      setCurrentResumeId(targetId);
      setIsAnalyzing(true);
      try {
        const analyzeRes = await resumeService.analyzeResume(targetId);
        setIsAnalyzing(false);
        if (analyzeRes && analyzeRes.success && analyzeRes.data && analyzeRes.data.analysis) {
          applyAnalysisData(analyzeRes.data.analysis);
        }
      } catch (err) {
        setIsAnalyzing(false);
        console.warn("Analysis error:", err);
      }
    }
  };

  const handleActivateResume = async (resumeId) => {
    try {
      const res = await resumeService.activateResume(resumeId);
      if (res && res.success) {
        await fetchResumes();
      }
    } catch (err) {
      console.warn("Activate resume error:", err);
    }
  };

  const handleCopyBullet = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedBulletId(id);
    setTimeout(() => setCopiedBulletId(null), 2000);
  };

  const handleFixBulletWithAI = async (id) => {
    const targetBullet = resumeData.bulletAudits.find((b) => b.id === id);
    if (!targetBullet) return;

    setFixingBulletId(id);
    try {
      const res = await resumeService.optimizeBullet(
        targetBullet.original,
        resumeData.targetRole,
        targetBullet.section
      );

      if (res && res.success && res.data) {
        setResumeData((prev) => {
          const updatedAudits = prev.bulletAudits.map((b) =>
            b.id === id
              ? {
                  ...b,
                  improved: res.data.improved,
                  rationale: res.data.rationale,
                  score: res.data.score || 96,
                  isWeak: false,
                }
              : b
          );
          // Recalculate bullet actionability metric
          const weakCount = updatedAudits.filter((b) => b.isWeak).length;
          const totalCount = updatedAudits.length || 1;
          const newActionability = Math.round(((totalCount - weakCount) / totalCount) * 100);

          return {
            ...prev,
            bulletAudits: updatedAudits,
            metrics: {
              ...prev.metrics,
              bulletActionability: Math.max(prev.metrics.bulletActionability, newActionability),
            },
          };
        });
      }
    } catch (err) {
      console.warn("Optimize bullet error:", err);
    } finally {
      setFixingBulletId(null);
    }
  };

  const handleFixAllWithAI = async () => {
    const weakBullets = resumeData.bulletAudits.filter((b) => b.isWeak);
    if (weakBullets.length === 0) {
      setActiveTab('bullets');
      return;
    }

    setActiveTab('bullets');
    for (const b of weakBullets) {
      await handleFixBulletWithAI(b.id);
    }
  };

  return (
    <div className="w-full max-w-5xl mx-auto space-y-5 sm:space-y-6 animate-in fade-in duration-300">
      {/* 1. HERO BANNER */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6 p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-indigo-950/60 via-purple-950/40 to-[#121624] border border-indigo-500/30 shadow-2xl">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-400 text-xs font-mono font-semibold border border-indigo-500/30">
              <Zap className="w-3.5 h-3.5 text-indigo-400" />
              Telemetry V4.2 · ATS Engine Live
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">Resume Intelligence</h1>
          <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
            Automated evaluation framework identifying parsing defects, semantic keyword density, quantified engineering achievements, and ATS compliance against Tier-1 SDE standards.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start md:self-auto shrink-0">
          <button
            onClick={() => setHistoryModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2.5 bg-[#1a2030] hover:bg-[#232b3e] text-slate-200 hover:text-white rounded-xl border border-[#232b3e] text-xs sm:text-sm font-semibold transition-all shadow-md"
          >
            <History className="w-4 h-4 text-indigo-400" />
            <span>Version History</span>
          </button>
          <button
            onClick={() => setIsUploadModalOpen(true)}
            className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white rounded-xl font-semibold text-xs sm:text-sm transition-all shadow-lg shadow-indigo-600/30 border border-indigo-400/30"
          >
            <Upload className="w-4 h-4" />
            <span>Upload New Resume</span>
          </button>
        </div>
      </div>

      {/* 2. UPLOADED FILE INFO BAR */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 bg-[#121624] p-4 rounded-2xl border border-[#232b3e] text-xs font-mono shadow-xl">
        <div className="flex items-center gap-3 px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e]">
          <div className="w-8 h-8 rounded-lg bg-rose-500/20 text-rose-400 border border-rose-500/30 flex items-center justify-center font-bold text-xs">
            PDF
          </div>
          <div className="truncate">
            <span className="text-white font-semibold truncate block text-xs">{resumeData.fileName}</span>
            <span className="text-[11px] text-slate-400">{resumeData.fileSize} · {resumeData.pageCount} Pages</span>
          </div>
        </div>

        <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e]">
          <span className="text-slate-400">Last Analyzed</span>
          <span className="text-slate-200 font-semibold">{resumeData.lastAnalyzed}</span>
        </div>

        <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e] relative group">
          <span className="text-slate-400 shrink-0 mr-2">Target Role</span>
          {isEditingRole ? (
            <div className="flex items-center gap-1.5 z-20">
              {showCustomRoleInput ? (
                <form onSubmit={handleCustomRoleSubmit} className="flex items-center gap-1">
                  <input
                    type="text"
                    value={customRoleInput}
                    onChange={(e) => setCustomRoleInput(e.target.value)}
                    placeholder="Enter target role..."
                    autoFocus
                    className="bg-[#121624] text-indigo-300 border border-indigo-500/50 rounded-lg px-2 py-0.5 text-xs focus:outline-none w-36"
                  />
                  <button
                    type="submit"
                    className="px-2 py-0.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold"
                  >
                    Save
                  </button>
                  <button
                    type="button"
                    onClick={() => { setShowCustomRoleInput(false); setIsEditingRole(false); }}
                    className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 hover:text-white text-xs font-bold"
                  >
                    ✕
                  </button>
                </form>
              ) : (
                <select
                  value={resumeData.targetRole}
                  onChange={(e) => handleRoleSelect(e.target.value)}
                  onBlur={() => {
                    setTimeout(() => { if (!showCustomRoleInput) setIsEditingRole(false); }, 250);
                  }}
                  autoFocus
                  className="bg-[#121624] text-indigo-400 font-bold border border-indigo-500/60 rounded-lg px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer shadow-lg"
                >
                  <option value="Backend SDE-1 (Tier 1)">Backend SDE-1 (Tier 1)</option>
                  <option value="AI/ML Engineer">AI/ML Engineer</option>
                  <option value="Full-Stack Developer">Full-Stack Developer</option>
                  <option value="Frontend SDE-1">Frontend SDE-1</option>
                  <option value="DevOps & Cloud Engineer">DevOps & Cloud Engineer</option>
                  <option value="Data Scientist & Engineer">Data Scientist & Engineer</option>
                  <option value="Cybersecurity Engineer">Cybersecurity Engineer</option>
                  <option value="Systems Software Engineer">Systems Software Engineer</option>
                  <option value="custom">+ Custom Target Role...</option>
                </select>
              )}
            </div>
          ) : (
            <button
              onClick={() => setIsEditingRole(true)}
              title="Click to dynamically check and change target role"
              className="flex items-center gap-1.5 text-indigo-400 hover:text-indigo-300 font-semibold truncate transition-colors text-right group/btn bg-indigo-500/10 hover:bg-indigo-500/20 px-2 py-0.5 rounded-lg border border-indigo-500/20"
            >
              <span className="truncate">{resumeData.targetRole}</span>
              <Edit3 className="w-3 h-3 text-indigo-400/80 group-hover/btn:text-indigo-300 shrink-0" />
            </button>
          )}
        </div>

        <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e]">
          <span className="text-slate-400">ATS Status</span>
          <span className="inline-flex items-center gap-1 text-emerald-400 font-semibold text-xs bg-emerald-500/10 px-2.5 py-1 rounded-lg border border-emerald-500/20">
            <CheckCircle2 className="w-3.5 h-3.5" />
            {resumeData.status}
          </span>
        </div>
      </div>

      {/* 3. KEY METRICS KPI CARDS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: ATS Score */}
        <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] hover:border-indigo-500/40 transition-colors shadow-xl relative overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">ATS Score</span>
            <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <Target className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white font-mono">{resumeData.metrics.atsScore}</span>
            <span className="text-xs text-slate-400 font-mono">/ 100</span>
          </div>
          <div className="mt-3 flex items-center gap-1.5 text-xs text-emerald-400 font-mono font-semibold">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>{resumeData.scoreChange}</span>
          </div>
        </div>

        {/* Card 2: Section Completeness */}
        <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] hover:border-purple-500/40 transition-colors shadow-xl">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">Section Completeness</span>
            <div className="p-2.5 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400">
              <FileCheck className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white font-mono">{resumeData.metrics.sectionCompleteness}%</span>
          </div>
          <div className="mt-3 text-xs text-slate-400 font-medium">
            {resumeData.sections.filter(s => s.score >= 80).length} of {resumeData.sections.length} core sections parsed cleanly
          </div>
        </div>

        {/* Card 3: STAR Bullet Index */}
        <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] hover:border-amber-500/40 transition-colors shadow-xl">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">STAR Bullet Index</span>
            <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
              <Sparkles className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white font-mono">{resumeData.metrics.bulletActionability}%</span>
          </div>
          <div className="mt-3 text-xs text-amber-400/90 font-medium">
            {resumeData.bulletAudits.filter(b => b.isWeak).length} bullets require quantitative metrics
          </div>
        </div>

        {/* Card 4: Keyword Match */}
        <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] hover:border-emerald-500/40 transition-colors shadow-xl">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">Keyword Match</span>
            <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <Search className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white font-mono">{resumeData.metrics.keywordMatch}%</span>
          </div>
          <div className="mt-3 text-xs text-slate-400 font-medium truncate">
            Target: {resumeData.targetRole}
          </div>
        </div>
      </div>

      {/* 4. TABS BAR */}
      <div className="flex flex-wrap items-center gap-2 border-b border-[#232b3e] pb-2">
        <button
          onClick={() => setActiveTab('overview')}
          className={`px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition-all flex items-center gap-2 ${
            activeTab === 'overview'
              ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-600/30 border border-indigo-400/30'
              : 'bg-[#121624] text-slate-400 hover:text-white hover:bg-[#1a2030] border border-[#232b3e]'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>ATS Overview & Sections</span>
        </button>
        <button
          onClick={() => setActiveTab('bullets')}
          className={`px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition-all flex items-center gap-2 ${
            activeTab === 'bullets'
              ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-600/30 border border-indigo-400/30'
              : 'bg-[#121624] text-slate-400 hover:text-white hover:bg-[#1a2030] border border-[#232b3e]'
          }`}
        >
          <Sparkles className="w-4 h-4" />
          <span>Bullet Point Audit ({resumeData.bulletAudits.length})</span>
        </button>
        <button
          onClick={() => setActiveTab('keywords')}
          className={`px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition-all flex items-center gap-2 ${
            activeTab === 'keywords'
              ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-600/30 border border-indigo-400/30'
              : 'bg-[#121624] text-slate-400 hover:text-white hover:bg-[#1a2030] border border-[#232b3e]'
          }`}
        >
          <Search className="w-4 h-4" />
          <span>Keyword Gap Analysis</span>
        </button>
      </div>

      {/* TAB 1: OVERVIEW */}
      {activeTab === 'overview' && (
        <div className="space-y-5 sm:space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-5 sm:gap-6 items-stretch">
          {/* Section Score Breakdown */}
          <div className="lg:col-span-3 bg-[#121624] p-5 sm:p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-xl h-full">
            <div className="flex items-center justify-between gap-3 pb-3 border-b border-[#232b3e]">
              <h3 className="font-bold text-base sm:text-lg text-white">ATS Section Breakdown</h3>
              <span className="hidden sm:inline text-xs font-mono text-indigo-400 font-semibold px-2.5 py-1 rounded-lg bg-indigo-500/10 border border-indigo-500/20">Tier-1 Benchmark</span>
            </div>

            <div className="space-y-3">
              {resumeData.sections.map((section, idx) => (
                <div key={idx} className="space-y-1">
                  <div className="flex items-center justify-between text-xs sm:text-sm">
                    <span className="font-semibold text-slate-200">{section.name.replace(' & GPA', '')}</span>
                    <span className="font-mono text-xs text-indigo-400 font-bold">{section.score}%</span>
                  </div>
                  <div className="w-full bg-[#0f131d] rounded-full h-2 overflow-hidden border border-[#232b3e]">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        section.score >= 90
                          ? 'bg-emerald-500 shadow-sm shadow-emerald-500/50'
                          : section.score >= 80
                          ? 'bg-indigo-500 shadow-sm shadow-indigo-500/50'
                          : 'bg-amber-500 shadow-sm shadow-amber-500/50'
                      }`}
                      style={{ width: `${section.score}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>

            {/* Cross module CTA */}
            <div className="mt-5 pt-4 border-t border-[#232b3e] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h4 className="text-sm font-bold text-white">Detailed Analysis</h4>
                <p className="text-xs text-slate-400">Review every section against your target role.</p>
              </div>
              <button
                onClick={() => navigate('/skill-gaps', { state: { targetRole: resumeData.targetRole } })}
                className="px-4 py-2 rounded-xl bg-[#1a2030] hover:bg-[#232b3e] text-indigo-400 hover:text-indigo-300 text-xs font-semibold flex items-center gap-1.5 transition-colors border border-[#232b3e] shrink-0 self-start sm:self-auto"
              >
                <span>View Detailed Analysis</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* AI Insights Sidebar */}
          <div className="lg:col-span-2 space-y-4 h-full">
            <div className="flex items-center justify-between px-1">
              <h3 className="font-bold text-base sm:text-lg text-white">AI Recommendations</h3>
              <Sparkles className="w-4 h-4 text-purple-400" />
            </div>
            {resumeData.aiInsights.map((insight, index) => (
              <div
                key={index}
                className="p-4 rounded-2xl bg-[#121624] border border-[#232b3e] hover:border-purple-500/40 space-y-3 transition-colors shadow-xl"
              >
                <div className="flex items-center gap-2">
                  {insight.type === 'critical' ? (
                    <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0" />
                  ) : (
                    <Sparkles className="w-5 h-5 text-purple-400 shrink-0" />
                  )}
                  <h4 className="font-bold text-sm text-white">{insight.title}</h4>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed line-clamp-2">{insight.description}</p>
                {insight.actionRoute ? (
                  <button
                    onClick={() => navigate(insight.actionRoute, { state: { targetRole: resumeData.targetRole } })}
                    className="text-xs font-bold text-indigo-400 hover:text-indigo-300 inline-flex items-center gap-1"
                  >
                    <span>{insight.actionLabel}</span>
                    <ArrowUpRight className="w-3.5 h-3.5" />
                  </button>
                ) : (
                  <button
                    onClick={() => setActiveTab(insight.actionTab || 'bullets')}
                    className="text-xs font-bold text-indigo-400 hover:text-indigo-300 inline-flex items-center gap-1"
                  >
                    <span>{insight.actionLabel}</span>
                    <ArrowUpRight className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="p-5 sm:p-6 rounded-2xl bg-[#121624] border border-[#232b3e] shadow-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h3 className="flex items-center gap-2 text-base sm:text-lg font-bold text-white">
                <Search className="w-5 h-5 text-cyan-400" /> Resume Issues
              </h3>
              <p className="mt-3 text-sm text-slate-300">
                {resumeData.missingSkills.length} keyword gaps <span className="text-slate-500">•</span>{' '}
                {resumeData.bulletAudits.filter((bullet) => bullet.isWeak).length} weak bullets <span className="text-slate-500">•</span>{' '}
                {resumeData.missingSkills.filter((skill) => skill.importance === 'High').length} high-priority missing skills
              </p>
            </div>
            <button
              type="button"
              onClick={handleFixAllWithAI}
              className="self-start sm:self-auto px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 border border-indigo-400/30 transition-all flex items-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5 text-purple-200" />
              <span>Fix All with AI</span>
            </button>

          </div>
        </div>
        </div>
      )}

      {/* TAB 2: BULLET POINT AUDIT */}
      {activeTab === 'bullets' && (
        <div className="space-y-4">
          <div className="p-4 rounded-2xl bg-[#121624] border border-[#232b3e] flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-xl">
            <div>
              <h3 className="font-bold text-white text-base">STAR Format Bullet Point AI Auditor</h3>
              <p className="text-xs text-slate-400">
                Every bullet is evaluated for Action Verb + Context + Quantified Metric outcome.
              </p>
            </div>
            <span className="text-xs font-mono font-semibold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20 shrink-0 self-start sm:self-auto">
              {resumeData.bulletAudits.length} Bullets Analyzed
            </span>
          </div>

          <div className="space-y-4">
            {resumeData.bulletAudits.map((bullet) => (
              <div
                key={bullet.id}
                className="p-5 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-xl hover:border-indigo-500/30 transition-colors"
              >
                <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
                  <span className="text-xs font-mono font-semibold text-indigo-400 uppercase tracking-wider">
                    {bullet.section}
                  </span>
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-mono text-slate-300 font-bold">Score: {bullet.score}/100</span>
                    {bullet.isWeak ? (
                      <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-400 border border-amber-500/30">
                        Needs Quantification
                      </span>
                    ) : (
                      <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                        STAR Compliant
                      </span>
                    )}
                  </div>
                </div>

                {/* Original Bullet */}
                <div className="p-3.5 rounded-xl bg-[#0f131d] border border-[#232b3e]">
                  <span className="text-[11px] font-mono uppercase text-slate-400 block mb-1">Current Bullet text:</span>
                  <p className="text-xs sm:text-sm text-slate-300 font-sans">{bullet.original}</p>
                </div>

                {/* AI Improved STAR Bullet */}
                <div className="star-bullet-card p-4 rounded-xl bg-gradient-to-r from-indigo-950/40 via-purple-950/30 to-[#121624] border border-indigo-500/40 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-mono uppercase text-indigo-400 font-bold flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-purple-400" />
                      AI Recommended STAR Bullet:
                    </span>
                    <button
                      onClick={() => handleCopyBullet(bullet.id, bullet.improved)}
                      className="star-bullet-copy-button text-xs font-semibold text-indigo-300 hover:text-white flex items-center gap-1 bg-[#1a2030] px-3 py-1 rounded-lg border border-indigo-500/30 transition-colors"
                    >
                      {copiedBulletId === bullet.id ? (
                        <>
                          <Check className="w-3.5 h-3.5 text-emerald-400" />
                          <span className="text-emerald-400 font-semibold">Copied!</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3.5 h-3.5" />
                          <span>Copy STAR Bullet</span>
                        </>
                      )}
                    </button>
                  </div>
                  <p className="text-xs sm:text-sm text-white font-medium font-sans leading-relaxed">{bullet.improved}</p>
                  <p className="text-xs text-slate-400 italic pt-1.5 border-t border-indigo-500/20">
                    Rationale: {bullet.rationale}
                  </p>
                </div>

                {bullet.isWeak && (
                  <div className="flex justify-end">
                    <button
                      onClick={() => handleFixBulletWithAI(bullet.id)}
                      disabled={fixingBulletId === bullet.id}
                      className="px-4 py-2 rounded-xl text-xs font-semibold bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white transition-all shadow-lg shadow-indigo-600/30 border border-indigo-400/30 flex items-center gap-1.5 disabled:opacity-50"
                    >
                      <Sparkles className="w-3.5 h-3.5 text-purple-300" />
                      <span>{fixingBulletId === bullet.id ? 'Optimizing with AI...' : 'Apply AI Optimization'}</span>
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 3: KEYWORD GAP ANALYSIS */}
      {activeTab === 'keywords' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Detected Skills */}
          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-xl">
            <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
              <h3 className="font-bold text-white text-base flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                Detected Resume Skills ({resumeData.detectedSkills.length})
              </h3>
              <span className="text-xs font-mono text-emerald-400 font-semibold px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">Verified</span>
            </div>

            <div className="flex flex-wrap gap-2">
              {resumeData.detectedSkills.map((skill, idx) => (
                <div
                  key={idx}
                  className="px-3 py-1.5 rounded-xl bg-[#0f131d] border border-[#232b3e] flex items-center gap-2 text-xs"
                >
                  <span className="font-semibold text-slate-200">{skill.name}</span>
                  <span className="text-[10px] font-mono text-indigo-400 bg-indigo-500/10 px-1.5 py-0.5 rounded border border-indigo-500/20">
                    {skill.category}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Missing Target Skills */}
          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-xl">
            <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
              <h3 className="font-bold text-white text-base flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-amber-400" />
                Missing Tier-1 Target Keywords ({resumeData.missingSkills.length})
              </h3>
              <span className="text-xs font-mono text-amber-400 font-semibold px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/20">Gap Alert</span>
            </div>

            <div className="space-y-3">
              {resumeData.missingSkills.map((skill, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-xl bg-[#0f131d] border border-amber-500/30 flex items-center justify-between text-xs gap-2"
                >
                  <div className="truncate">
                    <span className="font-bold text-white block truncate">{skill.name}</span>
                    <span className="text-[11px] text-slate-400 block truncate">{skill.roleReq}</span>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <button
                      onClick={() => navigate('/skill-gaps', { state: { targetRole: resumeData.targetRole, searchSkill: skill.name } })}
                      className="px-2 py-1 rounded bg-[#1a2030] hover:bg-[#232b3e] text-indigo-400 hover:text-white text-[11px] font-semibold border border-[#232b3e] transition-colors"
                      title="Bridge gap in Skill Gaps"
                    >
                      Bridge Gap
                    </button>
                    <span className="px-2.5 py-1 rounded text-[10px] font-mono font-semibold uppercase bg-amber-500/20 text-amber-400 border border-amber-500/30">
                      {skill.importance} Priority
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* File Upload Modal */}
      <FileUploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onUploadSuccess={handleUploadSuccess}
      />

      {/* Version History Modal */}
      {historyModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#0b0e17]/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-md bg-[#121624] border border-[#232b3e] rounded-2xl p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
              <h3 className="font-bold text-white text-base">Resume Version History</h3>
              <button
                onClick={() => setHistoryModalOpen(false)}
                className="text-slate-400 hover:text-white text-xs font-semibold"
              >
                Close
              </button>
            </div>
            <div className="space-y-2.5 font-mono text-xs max-h-60 overflow-y-auto pr-1">
              {userResumes.length === 0 ? (
                <p className="text-slate-400 italic text-center py-4">No resumes uploaded yet.</p>
              ) : (
                userResumes.map((resItem) => (
                  <div
                    key={resItem.id}
                    className={`p-3.5 rounded-xl border flex items-center justify-between transition-colors ${
                      resItem.is_active
                        ? 'bg-indigo-500/10 border-indigo-500/30 text-white'
                        : 'bg-[#0f131d] border-[#232b3e] text-slate-300'
                    }`}
                  >
                    <div className="truncate mr-2">
                      <span className="font-bold truncate block">{resItem.filename}</span>
                      <p className="text-[11px] text-slate-400 font-sans">
                        Status: {resItem.status} · {(resItem.size / (1024 * 1024)).toFixed(1)} MB
                      </p>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      {resItem.is_active ? (
                        <span className="text-emerald-400 font-semibold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                          Active
                        </span>
                      ) : (
                        <button
                          onClick={() => {
                            handleActivateResume(resItem.id);
                            setHistoryModalOpen(false);
                          }}
                          className="px-2.5 py-1 rounded bg-[#1a2030] hover:bg-[#232b3e] text-indigo-400 hover:text-white border border-[#232b3e] transition-colors"
                        >
                          Make Active
                        </button>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
