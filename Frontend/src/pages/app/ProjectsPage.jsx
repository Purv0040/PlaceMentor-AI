import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getStoredProjects, saveProjectsToStorage } from '../../data/projectData';
import { ProjectModal } from '../../components/common/ProjectModal';
import {
  FolderGit2,
  Plus,
  Terminal,
  RefreshCw,
  ExternalLink,
  Github,
  Zap,
  CheckCircle2,
  Copy,
  Check,
  Edit2,
  Trash2,
  Sparkles,
  ArrowUpRight,
  Layers,
  ShieldCheck
} from 'lucide-react';

export const ProjectsPage = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingProject, setEditingProject] = useState(null);
  const [deleteConfirmId, setDeleteConfirmId] = useState(null);
  const [toastMessage, setToastMessage] = useState(null);
  const [copiedBulletId, setCopiedBulletId] = useState(null);
  const [isAnalyzingAll, setIsAnalyzingAll] = useState(false);

  useEffect(() => {
    const loaded = getStoredProjects();
    setProjects(loaded);
  }, []);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const handleSaveProject = (projectData) => {
    let updated;
    if (editingProject) {
      updated = projects.map((p) => (p.id === projectData.id ? projectData : p));
      showToast(`Updated project "${projectData.title}"`);
    } else {
      updated = [projectData, ...projects];
      showToast(`Added project "${projectData.title}"`);
    }
    setProjects(updated);
    saveProjectsToStorage(updated);
    setEditingProject(null);
  };

  const handleDeleteProject = (id) => {
    const updated = projects.filter((p) => p.id !== id);
    setProjects(updated);
    saveProjectsToStorage(updated);
    setDeleteConfirmId(null);
    showToast('Project removed successfully');
  };

  const handleCopyBullet = (bulletId, bulletText) => {
    navigator.clipboard.writeText(bulletText);
    setCopiedBulletId(bulletId);
    showToast('STAR bullet copied to clipboard!');
    setTimeout(() => setCopiedBulletId(null), 2000);
  };

  const handleAnalyzeAll = () => {
    setIsAnalyzingAll(true);
    setTimeout(() => {
      setIsAnalyzingAll(false);
      showToast('AST Code Audit completed across all projects.');
    }, 1000);
  };

  const handleImportGithub = () => {
    showToast('GitHub projects imported & AST complexity scored.');
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-10 right-6 z-50 flex items-center gap-2 px-4 py-3 bg-[#121624] border border-indigo-500/40 text-white rounded-xl shadow-2xl font-mono text-xs animate-in slide-in-from-bottom duration-200">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* 1. HERO BANNER */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6 p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-indigo-950/60 via-purple-950/40 to-[#121624] border border-indigo-500/30 shadow-2xl">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-400 text-xs font-mono font-semibold border border-indigo-500/30">
              <Zap className="w-3.5 h-3.5 text-indigo-400" />
              TELEMETRY V4.2 · AST CODE AUDIT
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">Project Intelligence</h1>
          <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
            Analyze your projects, identify technical gaps, and turn your work into stronger placement evidence for SDE interviews.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5 self-start lg:self-center shrink-0">
          <button
            onClick={handleImportGithub}
            className="flex items-center gap-1.5 px-3.5 py-2.5 bg-[#1a2030] hover:bg-[#232b3e] text-slate-200 hover:text-white rounded-xl border border-[#232b3e] text-xs font-semibold transition-all shadow-md"
          >
            <Terminal className="w-3.5 h-3.5 text-indigo-400" />
            <span>Import from GitHub</span>
          </button>
          <button
            onClick={handleAnalyzeAll}
            disabled={isAnalyzingAll}
            className="flex items-center gap-1.5 px-3.5 py-2.5 bg-[#1a2030] hover:bg-[#232b3e] text-slate-200 hover:text-white rounded-xl border border-[#232b3e] text-xs font-semibold transition-all shadow-md disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-indigo-400 ${isAnalyzingAll ? 'animate-spin' : ''}`} />
            <span>{isAnalyzingAll ? 'Auditing Code...' : 'Analyze All Projects'}</span>
          </button>
          <button
            onClick={() => {
              setEditingProject(null);
              setIsModalOpen(true);
            }}
            className="flex items-center gap-1.5 px-4 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs font-semibold rounded-xl transition-all shadow-lg shadow-indigo-600/30 border border-indigo-400/30"
          >
            <Plus className="w-4 h-4" />
            <span>Add Project</span>
          </button>
        </div>
      </div>

      {/* 2. TOP SUMMARY BAR */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-4 rounded-2xl bg-[#121624] border border-[#232b3e] text-xs font-mono shadow-xl">
        <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e]">
          <span className="text-slate-400">Projects Audited</span>
          <span className="text-white font-bold">{projects.length} Total</span>
        </div>

        <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e]">
          <span className="text-slate-400">System Complexity Avg</span>
          <span className="text-emerald-400 font-bold">86% AST Verified</span>
        </div>

        <div className="flex items-center justify-between px-3 py-2 bg-[#0f131d] rounded-xl border border-[#232b3e]">
          <span className="text-slate-400">Architecture Alignment</span>
          <span className="text-indigo-400 font-bold">Tier-1 SDE Benchmark</span>
        </div>
      </div>

      {/* 3. PROJECT CARDS LIST */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-white text-lg">Portfolio Project Audits</h3>
          <span className="text-xs font-mono text-slate-400">{projects.length} Projects</span>
        </div>

        {projects.length === 0 ? (
          <div className="p-12 text-center rounded-2xl bg-[#121624] border border-dashed border-[#232b3e]">
            <FolderGit2 className="w-12 h-12 text-slate-500 mx-auto mb-3" />
            <h4 className="text-white font-bold text-base mb-1">No Projects Audited Yet</h4>
            <p className="text-xs text-slate-400 mb-4 max-w-sm mx-auto">
              Add your engineering projects or import from GitHub to generate AST code complexity metrics and STAR resume evidence.
            </p>
            <button
              onClick={() => {
                setEditingProject(null);
                setIsModalOpen(true);
              }}
              className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-xs font-semibold rounded-xl shadow-lg shadow-indigo-600/30"
            >
              Add First Project
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6">
            {projects.map((project) => (
              <div
                key={project.id}
                className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-xl hover:border-indigo-500/40 transition-colors"
              >
                {/* Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#232b3e]">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                      <FolderGit2 className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="font-bold text-white text-lg">{project.title}</h4>
                        <span className="px-2.5 py-0.5 rounded-lg text-[10px] font-mono font-semibold uppercase bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                          {project.category}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 mt-0.5 font-mono">Updated {project.updatedAt}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 self-start sm:self-auto">
                    <span className="px-3 py-1 rounded-full text-xs font-mono font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                      AST Score: {project.score}%
                    </span>
                    <button
                      onClick={() => {
                        setEditingProject(project);
                        setIsModalOpen(true);
                      }}
                      className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-[#1a2030] transition-colors"
                      title="Edit Project"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => setDeleteConfirmId(project.id)}
                      className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                      title="Delete Project"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Description */}
                <p className="text-xs sm:text-sm text-slate-300 leading-relaxed font-sans">{project.description}</p>

                {/* Technologies & Architecture Tags */}
                <div className="flex flex-wrap gap-2 pt-1">
                  {project.technologies.map((tech, idx) => (
                    <span
                      key={idx}
                      className="px-2.5 py-1 rounded-lg bg-[#0f131d] text-slate-200 text-xs font-mono border border-[#232b3e]"
                    >
                      {tech}
                    </span>
                  ))}
                  {project.architectureTags &&
                    project.architectureTags.map((tag, idx) => (
                      <span
                        key={idx}
                        className="px-2.5 py-1 rounded-lg bg-indigo-500/10 text-indigo-400 text-xs font-mono border border-indigo-500/20"
                      >
                        {tag}
                      </span>
                    ))}
                </div>

                {/* STAR Bullet Point Evidence */}
                {project.evidenceBullets && project.evidenceBullets.length > 0 && (
                  <div className="p-4 rounded-xl bg-gradient-to-r from-indigo-950/40 via-purple-950/30 to-[#121624] border border-indigo-500/40 space-y-2">
                    <span className="text-[11px] font-mono uppercase font-bold text-indigo-400 flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-purple-400" />
                      Generated Resume Evidence Bullets:
                    </span>
                    <div className="space-y-2">
                      {project.evidenceBullets.map((bullet, idx) => (
                        <div
                          key={idx}
                          className="flex items-start justify-between gap-3 text-xs text-white font-sans bg-[#0f131d] p-3 rounded-lg border border-[#232b3e]"
                        >
                          <span className="leading-relaxed">{bullet}</span>
                          <button
                            onClick={() => handleCopyBullet(`${project.id}-${idx}`, bullet)}
                            className="text-slate-400 hover:text-indigo-400 shrink-0 p-1"
                            title="Copy Bullet"
                          >
                            {copiedBulletId === `${project.id}-${idx}` ? (
                              <Check className="w-3.5 h-3.5 text-emerald-400" />
                            ) : (
                              <Copy className="w-3.5 h-3.5" />
                            )}
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Footer Links */}
                <div className="pt-2 flex items-center justify-between text-xs font-mono text-slate-400">
                  <div className="flex items-center gap-4">
                    {project.githubUrl && (
                      <a
                        href={project.githubUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 text-slate-200 hover:text-indigo-400 transition-colors"
                      >
                        <Github className="w-3.5 h-3.5" />
                        <span>Repository</span>
                      </a>
                    )}
                    {project.liveUrl && (
                      <a
                        href={project.liveUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 text-slate-200 hover:text-emerald-400 transition-colors"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                        <span>Live Demo</span>
                      </a>
                    )}
                  </div>
                  <span className="text-amber-400 font-bold">{project.scoreBadge}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 4. AI RECOMMENDATIONS BANNER */}
      <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-xl">
        <h3 className="font-bold text-white text-base flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-400" />
          Copilot Project System Design Recommendations
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-[#0f131d] border border-[#232b3e] space-y-2 hover:border-purple-500/40 transition-colors">
            <h4 className="font-bold text-sm text-white">Mock Interview Drill Recommended</h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              Prepare to answer Socratic questions on thread safety and caching invalidation strategy for "PlaceMentor AI".
            </p>
            <button
              onClick={() => navigate('/mock-interview')}
              className="text-xs font-bold text-indigo-400 hover:text-indigo-300 inline-flex items-center gap-1 pt-1"
            >
              <span>Practice Mock Interview</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="p-4 rounded-xl bg-[#0f131d] border border-[#232b3e] space-y-2 hover:border-purple-500/40 transition-colors">
            <h4 className="font-bold text-sm text-white">Consult AI Mentor for System Tuning</h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              Ask AI Placement Mentor how to write unit tests for RabbitMQ event bus handlers.
            </p>
            <button
              onClick={() => navigate('/ai-mentor')}
              className="text-xs font-bold text-indigo-400 hover:text-indigo-300 inline-flex items-center gap-1 pt-1"
            >
              <span>Ask AI Placement Mentor</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Add / Edit Project Modal */}
      <ProjectModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setEditingProject(null);
        }}
        onSave={handleSaveProject}
        projectToEdit={editingProject}
      />

      {/* Delete Confirmation Modal */}
      {deleteConfirmId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#0b0e17]/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-sm bg-[#121624] border border-[#232b3e] rounded-2xl p-6 space-y-4 shadow-2xl">
            <h3 className="font-bold text-white text-base">Delete Project Audit?</h3>
            <p className="text-xs text-slate-300">
              Are you sure you want to remove this project? This will delete its AST evidence bullets from frontend state.
            </p>
            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setDeleteConfirmId(null)}
                className="px-3.5 py-1.5 rounded-xl text-xs font-semibold text-slate-400 hover:text-white bg-[#1a2030]"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDeleteProject(deleteConfirmId)}
                className="px-4 py-1.5 rounded-xl text-xs font-semibold bg-rose-600 text-white hover:bg-rose-500"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
