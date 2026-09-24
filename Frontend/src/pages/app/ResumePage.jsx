import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { initialResumeData } from '../../data/resumeData';
import { aiService } from '../../services/aiService';
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
  Search
} from 'lucide-react';

export const ResumePage = () => {
  const navigate = useNavigate();
  const [resumeData, setResumeData] = useState(initialResumeData);
  const [activeTab, setActiveTab] = useState('overview'); // 'overview' | 'bullets' | 'keywords'
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [copiedBulletId, setCopiedBulletId] = useState(null);
  const [fixingBulletId, setFixingBulletId] = useState(null);
  const [historyModalOpen, setHistoryModalOpen] = useState(false);

  const handleUploadSuccess = async (fileMetadata) => {
    const aiAnalysis = await aiService.analyzeResume(fileMetadata.fileName);
    setResumeData((prev) => ({
      ...prev,
      fileName: fileMetadata.fileName,
      fileSize: fileMetadata.fileSize,
      lastAnalyzed: 'Just now',
      overallScore: aiAnalysis.atsScore,
      scoreChange: '+4% vs previous upload',
      metrics: {
        ...prev.metrics,
        atsScore: aiAnalysis.atsScore,
        sectionCompleteness: aiAnalysis.sectionScore,
      }
    }));
  };

  const handleCopyBullet = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedBulletId(id);
    setTimeout(() => setCopiedBulletId(null), 2000);
  };

  const handleFixBulletWithAI = (id) => {
    setFixingBulletId(id);
    setTimeout(() => {
      setResumeData((prev) => ({
        ...prev,
        bulletAudits: prev.bulletAudits.map((b) =>
          b.id === id ? { ...b, score: 98, isWeak: false } : b
        )
      }));
      setFixingBulletId(null);
    }, 800);
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-surface-container-low p-6 rounded-2xl border border-outline-variant/60 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <h1 className="text-2xl font-bold text-on-surface tracking-tight">Resume Intelligence</h1>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-secondary-container/40 text-secondary text-xs font-mono border border-secondary/30">
              <Zap className="w-3.5 h-3.5 text-secondary" />
              Telemetry V4.2 · ATS Engine Live
            </span>
          </div>
          <p className="text-sm text-on-surface-variant max-w-2xl">
            Automated evaluation framework identifying parsing defects, semantic keyword density, quantified engineering achievements, and ATS compliance against Tier-1 SDE standards.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start md:self-auto shrink-0">
          <button
            onClick={() => setHistoryModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-surface-container hover:bg-surface-container-high text-on-surface-variant hover:text-on-surface rounded-xl border border-outline-variant text-sm font-medium transition-colors"
          >
            <History className="w-4 h-4" />
            <span>Version History</span>
          </button>
          <button
            onClick={() => setIsUploadModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-on-primary hover:bg-primary-fixed-dim rounded-xl font-semibold text-sm transition-all shadow-md"
          >
            <Upload className="w-4 h-4" />
            <span>Upload New Resume</span>
          </button>
        </div>
      </div>

      {/* Uploaded File Info Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 bg-surface-container-low p-4 rounded-xl border border-outline-variant text-sm font-mono">
        <div className="flex items-center gap-3 px-3 py-1.5 bg-surface-container rounded-lg border border-outline-variant/50">
          <div className="w-7 h-7 rounded bg-error/15 text-error flex items-center justify-center font-bold text-xs">
            PDF
          </div>
          <div className="truncate">
            <span className="text-on-surface font-semibold truncate block">{resumeData.fileName}</span>
            <span className="text-xs text-on-surface-variant">{resumeData.fileSize} · {resumeData.pageCount} Pages</span>
          </div>
        </div>

        <div className="flex items-center justify-between px-3 py-1.5 bg-surface-container rounded-lg border border-outline-variant/50">
          <span className="text-xs text-on-surface-variant">Last Analyzed</span>
          <span className="text-on-surface font-medium">{resumeData.lastAnalyzed}</span>
        </div>

        <div className="flex items-center justify-between px-3 py-1.5 bg-surface-container rounded-lg border border-outline-variant/50">
          <span className="text-xs text-on-surface-variant">Target Role</span>
          <span className="text-primary font-medium truncate">{resumeData.targetRole}</span>
        </div>

        <div className="flex items-center justify-between px-3 py-1.5 bg-surface-container rounded-lg border border-outline-variant/50">
          <span className="text-xs text-on-surface-variant">ATS Status</span>
          <span className="inline-flex items-center gap-1 text-tertiary font-semibold text-xs bg-tertiary-container/20 px-2 py-0.5 rounded border border-tertiary/30">
            <CheckCircle2 className="w-3.5 h-3.5" />
            {resumeData.status}
          </span>
        </div>
      </div>

      {/* Key Metrics KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: ATS Compatibility */}
        <div className="p-5 bg-surface-container-low rounded-2xl border border-outline-variant/60 shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-on-surface-variant">ATS Score</span>
            <div className="p-2 rounded-xl bg-primary-container/20 text-primary">
              <Target className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-on-surface">{resumeData.metrics.atsScore}</span>
            <span className="text-xs text-on-surface-variant font-mono">/ 100</span>
          </div>
          <div className="mt-3 flex items-center gap-1.5 text-xs text-tertiary font-medium">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>{resumeData.scoreChange}</span>
          </div>
        </div>

        {/* Card 2: Section Completeness */}
        <div className="p-5 bg-surface-container-low rounded-2xl border border-outline-variant/60 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-on-surface-variant">Section Completeness</span>
            <div className="p-2 rounded-xl bg-tertiary-container/20 text-tertiary">
              <FileCheck className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-on-surface">{resumeData.metrics.sectionCompleteness}%</span>
          </div>
          <div className="mt-3 text-xs text-on-surface-variant">
            5 of 5 core sections parsed cleanly
          </div>
        </div>

        {/* Card 3: Bullet Actionability */}
        <div className="p-5 bg-surface-container-low rounded-2xl border border-outline-variant/60 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-on-surface-variant">STAR Bullet Index</span>
            <div className="p-2 rounded-xl bg-secondary-container/20 text-secondary">
              <Sparkles className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-on-surface">{resumeData.metrics.bulletActionability}%</span>
          </div>
          <div className="mt-3 text-xs text-on-surface-variant">
            2 bullets require quantitative metrics
          </div>
        </div>

        {/* Card 4: Keyword Density */}
        <div className="p-5 bg-surface-container-low rounded-2xl border border-outline-variant/60 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-on-surface-variant">Keyword Match</span>
            <div className="p-2 rounded-xl bg-surface-bright text-on-surface">
              <Search className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-on-surface">{resumeData.metrics.keywordMatch}%</span>
          </div>
          <div className="mt-3 text-xs text-on-surface-variant">
            Target: Tier-1 SDE-1 Backend Cutoff
          </div>
        </div>
      </div>

      {/* Tabs Bar */}
      <div className="flex items-center gap-2 border-b border-outline-variant/60 pb-1">
        <button
          onClick={() => setActiveTab('overview')}
          className={`px-4 py-2.5 rounded-xl text-sm font-semibold transition-all flex items-center gap-2 ${
            activeTab === 'overview'
              ? 'bg-primary text-on-primary shadow-sm'
              : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>ATS Overview & Sections</span>
        </button>
        <button
          onClick={() => setActiveTab('bullets')}
          className={`px-4 py-2.5 rounded-xl text-sm font-semibold transition-all flex items-center gap-2 ${
            activeTab === 'bullets'
              ? 'bg-primary text-on-primary shadow-sm'
              : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container'
          }`}
        >
          <Sparkles className="w-4 h-4" />
          <span>Bullet Point Audit ({resumeData.bulletAudits.length})</span>
        </button>
        <button
          onClick={() => setActiveTab('keywords')}
          className={`px-4 py-2.5 rounded-xl text-sm font-semibold transition-all flex items-center gap-2 ${
            activeTab === 'keywords'
              ? 'bg-primary text-on-primary shadow-sm'
              : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container'
          }`}
        >
          <Search className="w-4 h-4" />
          <span>Keyword Gap Analysis</span>
        </button>
      </div>

      {/* TAB 1: OVERVIEW */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Section Score Breakdown */}
          <div className="lg:col-span-2 bg-surface-container-low p-6 rounded-2xl border border-outline-variant/60 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-outline-variant/50">
              <h3 className="font-semibold text-lg text-on-surface">ATS Section Breakdown</h3>
              <span className="text-xs font-mono text-on-surface-variant">Tier-1 Benchmark</span>
            </div>

            <div className="space-y-4">
              {resumeData.sections.map((section, idx) => (
                <div key={idx} className="space-y-1.5">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium text-on-surface">{section.name}</span>
                    <span className="font-mono text-xs text-on-surface-variant">{section.score}% Score</span>
                  </div>
                  <div className="w-full bg-surface-container rounded-full h-2.5 overflow-hidden border border-outline-variant/40">
                    <div
                      className={`h-full transition-all duration-500 ${
                        section.score >= 90
                          ? 'bg-tertiary'
                          : section.score >= 80
                          ? 'bg-primary'
                          : 'bg-secondary'
                      }`}
                      style={{ width: `${section.score}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>

            {/* Cross module CTA */}
            <div className="mt-6 pt-4 border-t border-outline-variant/50 flex items-center justify-between">
              <div>
                <h4 className="text-sm font-semibold text-on-surface">Target Role Benchmark</h4>
                <p className="text-xs text-on-surface-variant">Missing critical backend technologies required by Tier-1 companies.</p>
              </div>
              <button
                onClick={() => navigate('/skill-gaps')}
                className="px-4 py-2 rounded-xl bg-surface-container-high hover:bg-surface-bright text-on-surface text-xs font-semibold flex items-center gap-1.5 transition-colors"
              >
                <span>Analyze Skill Gaps</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* AI Insights Sidebar */}
          <div className="space-y-4">
            <h3 className="font-semibold text-lg text-on-surface px-1">AI Optimization Suggestions</h3>
            {resumeData.aiInsights.map((insight, index) => (
              <div
                key={index}
                className="p-5 rounded-2xl bg-surface-container-low border border-outline-variant/60 space-y-3"
              >
                <div className="flex items-center gap-2">
                  {insight.type === 'critical' ? (
                    <AlertTriangle className="w-5 h-5 text-secondary" />
                  ) : (
                    <Sparkles className="w-5 h-5 text-primary" />
                  )}
                  <h4 className="font-semibold text-sm text-on-surface">{insight.title}</h4>
                </div>
                <p className="text-xs text-on-surface-variant leading-relaxed">{insight.description}</p>
                {insight.actionRoute ? (
                  <button
                    onClick={() => navigate(insight.actionRoute)}
                    className="text-xs font-semibold text-primary hover:underline inline-flex items-center gap-1"
                  >
                    <span>{insight.actionLabel}</span>
                    <ArrowUpRight className="w-3 h-3" />
                  </button>
                ) : (
                  <button
                    onClick={() => setActiveTab(insight.actionTab || 'bullets')}
                    className="text-xs font-semibold text-primary hover:underline inline-flex items-center gap-1"
                  >
                    <span>{insight.actionLabel}</span>
                    <ArrowUpRight className="w-3 h-3" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 2: BULLET POINT AUDIT */}
      {activeTab === 'bullets' && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-surface-container-low border border-outline-variant/60 flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-on-surface text-base">STAR Format Bullet Point AI Auditor</h3>
              <p className="text-xs text-on-surface-variant">
                Every bullet is evaluated for Action Verb + Context + Quantified Metric outcome.
              </p>
            </div>
            <span className="text-xs font-mono text-tertiary bg-tertiary-container/20 px-3 py-1 rounded-full border border-tertiary/30">
              3 Bullets Analyzed
            </span>
          </div>

          <div className="space-y-4">
            {resumeData.bulletAudits.map((bullet) => (
              <div
                key={bullet.id}
                className="p-5 rounded-2xl bg-surface-container-low border border-outline-variant/60 space-y-4"
              >
                <div className="flex items-center justify-between pb-3 border-b border-outline-variant/40">
                  <span className="text-xs font-mono font-semibold text-secondary uppercase tracking-wider">
                    {bullet.section}
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-on-surface-variant">Score: {bullet.score}/100</span>
                    {bullet.isWeak ? (
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-secondary-container/40 text-secondary border border-secondary/30">
                        Needs Quantification
                      </span>
                    ) : (
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-tertiary-container/30 text-tertiary border border-tertiary/30">
                        STAR Compliant
                      </span>
                    )}
                  </div>
                </div>

                {/* Original Bullet */}
                <div className="p-3.5 rounded-xl bg-surface-container/60 border border-outline-variant/40">
                  <span className="text-[11px] font-mono uppercase text-outline block mb-1">Current Bullet text:</span>
                  <p className="text-sm text-on-surface-variant font-sans">{bullet.original}</p>
                </div>

                {/* AI Improved STAR Bullet */}
                <div className="p-3.5 rounded-xl bg-primary-container/10 border border-primary/30 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-mono uppercase text-primary font-semibold flex items-center gap-1">
                      <Sparkles className="w-3.5 h-3.5" />
                      AI Recommended STAR Bullet:
                    </span>
                    <button
                      onClick={() => handleCopyBullet(bullet.id, bullet.improved)}
                      className="text-xs font-medium text-primary hover:text-on-surface flex items-center gap-1 bg-surface-container px-2.5 py-1 rounded-lg border border-outline-variant/60 transition-colors"
                    >
                      {copiedBulletId === bullet.id ? (
                        <>
                          <Check className="w-3.5 h-3.5 text-tertiary" />
                          <span className="text-tertiary font-semibold">Copied!</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3.5 h-3.5" />
                          <span>Copy STAR Bullet</span>
                        </>
                      )}
                    </button>
                  </div>
                  <p className="text-sm text-on-surface font-medium font-sans leading-relaxed">{bullet.improved}</p>
                  <p className="text-xs text-on-surface-variant italic pt-1 border-t border-primary/20">
                    Rationale: {bullet.rationale}
                  </p>
                </div>

                {bullet.isWeak && (
                  <div className="flex justify-end">
                    <button
                      onClick={() => handleFixBulletWithAI(bullet.id)}
                      disabled={fixingBulletId === bullet.id}
                      className="px-4 py-2 rounded-xl text-xs font-semibold bg-primary text-on-primary hover:bg-primary-fixed-dim transition-all shadow-sm flex items-center gap-1.5 disabled:opacity-50"
                    >
                      <Sparkles className="w-3.5 h-3.5" />
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
          <div className="p-6 rounded-2xl bg-surface-container-low border border-outline-variant/60 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-outline-variant/50">
              <h3 className="font-semibold text-on-surface text-base flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-tertiary" />
                Detected Resume Skills ({resumeData.detectedSkills.length})
              </h3>
              <span className="text-xs font-mono text-tertiary">Verified</span>
            </div>

            <div className="flex flex-wrap gap-2">
              {resumeData.detectedSkills.map((skill, idx) => (
                <div
                  key={idx}
                  className="px-3 py-1.5 rounded-xl bg-surface-container border border-outline-variant/60 flex items-center gap-2 text-xs"
                >
                  <span className="font-medium text-on-surface">{skill.name}</span>
                  <span className="text-[10px] font-mono text-on-surface-variant bg-surface-container-high px-1.5 py-0.5 rounded">
                    {skill.category}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Missing Target Skills */}
          <div className="p-6 rounded-2xl bg-surface-container-low border border-outline-variant/60 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-outline-variant/50">
              <h3 className="font-semibold text-on-surface text-base flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-secondary" />
                Missing Tier-1 Target Keywords ({resumeData.missingSkills.length})
              </h3>
              <span className="text-xs font-mono text-secondary">Gap Alert</span>
            </div>

            <div className="space-y-3">
              {resumeData.missingSkills.map((skill, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-xl bg-surface-container border border-secondary/30 flex items-center justify-between text-xs"
                >
                  <div>
                    <span className="font-semibold text-on-surface block">{skill.name}</span>
                    <span className="text-[11px] text-on-surface-variant">{skill.roleReq}</span>
                  </div>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold uppercase bg-secondary-container/40 text-secondary">
                    {skill.importance} Priority
                  </span>
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
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-obsidian-950/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-md bg-surface-container-high border border-outline-variant rounded-2xl p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-outline-variant/50">
              <h3 className="font-semibold text-on-surface">Resume Version History</h3>
              <button
                onClick={() => setHistoryModalOpen(false)}
                className="text-on-surface-variant hover:text-on-surface text-sm"
              >
                Close
              </button>
            </div>
            <div className="space-y-2 font-mono text-xs">
              <div className="p-3 rounded-xl bg-primary-container/20 border border-primary/40 flex items-center justify-between">
                <div>
                  <span className="text-on-surface font-bold">V4.2 (Current)</span>
                  <p className="text-[11px] text-on-surface-variant">Uploaded Today · Score 84</p>
                </div>
                <span className="text-tertiary font-semibold">Active</span>
              </div>
              <div className="p-3 rounded-xl bg-surface-container border border-outline-variant/50 flex items-center justify-between text-on-surface-variant">
                <div>
                  <span className="font-semibold">V4.1</span>
                  <p className="text-[11px]">Uploaded 1 week ago · Score 78</p>
                </div>
                <button
                  onClick={() => setHistoryModalOpen(false)}
                  className="text-primary hover:underline text-[11px]"
                >
                  View Audit
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
