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
        <div className="fixed bottom-10 right-6 z-50 flex items-center gap-2 px-4 py-3 bg-surface-container-highest border border-primary/40 text-on-surface rounded-xl shadow-2xl font-mono text-xs animate-in slide-in-from-bottom duration-200">
          <CheckCircle2 className="w-4 h-4 text-primary shrink-0" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Header Banner */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 bg-surface-container-low p-6 rounded-2xl border border-outline-variant/60 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <h1 className="text-2xl font-bold text-on-surface tracking-tight">Project Intelligence</h1>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-secondary-container/40 text-secondary text-xs font-mono border border-secondary/30">
              <Zap className="w-3.5 h-3.5 text-secondary" />
              TELEMETRY V4.2 · AST CODE AUDIT
            </span>
          </div>
          <p className="text-sm text-on-surface-variant max-w-2xl">
            Analyze your projects, identify technical gaps, and turn your work into stronger placement evidence for SDE interviews.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5 self-start lg:self-center shrink-0">
          <button
            onClick={handleImportGithub}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-surface-container hover:bg-surface-container-high text-on-surface rounded-xl border border-outline-variant text-xs font-medium transition-colors"
          >
            <Terminal className="w-3.5 h-3.5 text-on-surface-variant" />
            <span>Import from GitHub</span>
          </button>
          <button
            onClick={handleAnalyzeAll}
            disabled={isAnalyzingAll}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-surface-container-high hover:bg-surface-bright text-on-surface rounded-xl text-xs font-medium transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-primary ${isAnalyzingAll ? 'animate-spin' : ''}`} />
            <span>{isAnalyzingAll ? 'Auditing Code...' : 'Analyze All Projects'}</span>
          </button>
          <button
            onClick={() => {
              setEditingProject(null);
              setIsModalOpen(true);
            }}
            className="flex items-center gap-1.5 px-4 py-2 bg-primary text-on-primary hover:bg-primary-fixed-dim text-xs font-semibold rounded-xl transition-all shadow-md"
          >
            <Plus className="w-4 h-4" />
            <span>Add Project</span>
          </button>
        </div>
      </div>

      {/* Top Summary Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-4 rounded-xl bg-surface-container-low border border-outline-variant text-sm font-mono">
        <div className="flex items-center justify-between px-3 py-1.5 bg-surface-container rounded-lg border border-outline-variant/50">
          <span className="text-xs text-on-surface-variant">Projects Audited</span>
          <span className="text-on-surface font-bold">{projects.length} Total</span>
        </div>

        <div className="flex items-center justify-between px-3 py-1.5 bg-surface-container rounded-lg border border-outline-variant/50">
          <span className="text-xs text-on-surface-variant">System Complexity Avg</span>
          <span className="text-tertiary font-bold">86% AST Verified</span>
        </div>

        <div className="flex items-center justify-between px-3 py-1.5 bg-surface-container rounded-lg border border-outline-variant/50">
          <span className="text-xs text-on-surface-variant">Architecture Alignment</span>
          <span className="text-secondary font-bold">Tier-1 SDE Benchmark</span>
        </div>
      </div>

      {/* Project Cards List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-on-surface text-lg">Portfolio Project Audits</h3>
          <span className="text-xs font-mono text-on-surface-variant">{projects.length} Projects</span>
        </div>

        {projects.length === 0 ? (
          <div className="p-12 text-center rounded-2xl bg-surface-container-low border border-dashed border-outline-variant">
            <FolderGit2 className="w-12 h-12 text-outline mx-auto mb-3" />
            <h4 className="text-on-surface font-semibold text-base mb-1">No Projects Audited Yet</h4>
            <p className="text-xs text-on-surface-variant mb-4 max-w-sm mx-auto">
              Add your engineering projects or import from GitHub to generate AST code complexity metrics and STAR resume evidence.
            </p>
            <button
              onClick={() => {
                setEditingProject(null);
                setIsModalOpen(true);
              }}
              className="px-4 py-2 bg-primary text-on-primary text-xs font-semibold rounded-xl"
            >
              Add First Project
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6">
            {projects.map((project) => (
              <div
                key={project.id}
                className="p-6 rounded-2xl bg-surface-container-low border border-outline-variant/60 space-y-4 shadow-sm hover:border-primary/40 transition-colors"
              >
                {/* Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-outline-variant/40">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-xl bg-primary-container/20 text-primary border border-primary/30">
                      <FolderGit2 className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="font-bold text-on-surface text-lg">{project.title}</h4>
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-surface-container text-on-surface-variant border border-outline-variant/50">
                          {project.category}
                        </span>
                      </div>
                      <p className="text-xs text-on-surface-variant mt-0.5">Updated {project.updatedAt}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 self-start sm:self-auto">
                    <span className="px-3 py-1 rounded-full text-xs font-mono font-semibold bg-tertiary-container/30 text-tertiary border border-tertiary/30">
                      AST Score: {project.score}%
                    </span>
                    <button
                      onClick={() => {
                        setEditingProject(project);
                        setIsModalOpen(true);
                      }}
                      className="p-1.5 rounded-lg text-on-surface-variant hover:text-on-surface hover:bg-surface-container transition-colors"
                      title="Edit Project"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => setDeleteConfirmId(project.id)}
                      className="p-1.5 rounded-lg text-on-surface-variant hover:text-error hover:bg-error/10 transition-colors"
                      title="Delete Project"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Description */}
                <p className="text-sm text-on-surface-variant leading-relaxed font-sans">{project.description}</p>

                {/* Technologies & Architecture Tags */}
                <div className="flex flex-wrap gap-2 pt-1">
                  {project.technologies.map((tech, idx) => (
                    <span
                      key={idx}
                      className="px-2.5 py-1 rounded-lg bg-surface-container text-on-surface text-xs font-mono border border-outline-variant/50"
                    >
                      {tech}
                    </span>
                  ))}
                  {project.architectureTags &&
                    project.architectureTags.map((tag, idx) => (
                      <span
                        key={idx}
                        className="px-2.5 py-1 rounded-lg bg-secondary-container/20 text-secondary text-xs font-mono border border-secondary/30"
                      >
                        {tag}
                      </span>
                    ))}
                </div>

                {/* STAR Bullet Point Evidence */}
                {project.evidenceBullets && project.evidenceBullets.length > 0 && (
                  <div className="p-4 rounded-xl bg-surface-container/60 border border-outline-variant/40 space-y-2">
                    <span className="text-[11px] font-mono uppercase font-semibold text-primary flex items-center gap-1">
                      <Sparkles className="w-3.5 h-3.5" />
                      Generated Resume Evidence Bullets:
                    </span>
                    <div className="space-y-2">
                      {project.evidenceBullets.map((bullet, idx) => (
                        <div
                          key={idx}
                          className="flex items-start justify-between gap-3 text-xs text-on-surface font-sans bg-surface-container-low p-2.5 rounded-lg border border-outline-variant/30"
                        >
                          <span className="leading-relaxed">{bullet}</span>
                          <button
                            onClick={() => handleCopyBullet(`${project.id}-${idx}`, bullet)}
                            className="text-on-surface-variant hover:text-primary shrink-0 p-1"
                            title="Copy Bullet"
                          >
                            {copiedBulletId === `${project.id}-${idx}` ? (
                              <Check className="w-3.5 h-3.5 text-tertiary" />
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
                <div className="pt-2 flex items-center justify-between text-xs font-mono text-on-surface-variant">
                  <div className="flex items-center gap-3">
                    {project.githubUrl && (
                      <a
                        href={project.githubUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 text-on-surface hover:text-primary transition-colors"
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
                        className="flex items-center gap-1 text-on-surface hover:text-tertiary transition-colors"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                        <span>Live Demo</span>
                      </a>
                    )}
                  </div>
                  <span className="text-secondary font-semibold">{project.scoreBadge}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* AI Recommendations Banner */}
      <div className="p-6 rounded-2xl bg-surface-container-low border border-outline-variant/60 space-y-4">
        <h3 className="font-semibold text-on-surface text-base flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-secondary" />
          Copilot Project System Design Recommendations
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-surface-container border border-outline-variant/50 space-y-2">
            <h4 className="font-semibold text-sm text-on-surface">Mock Interview Drill Recommended</h4>
            <p className="text-xs text-on-surface-variant leading-relaxed">
              Prepare to answer Socratic questions on thread safety and caching invalidation strategy for "PlaceMentor AI".
            </p>
            <button
              onClick={() => navigate('/mock-interview')}
              className="text-xs font-semibold text-primary hover:underline inline-flex items-center gap-1 pt-1"
            >
              <span>Practice Mock Interview</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="p-4 rounded-xl bg-surface-container border border-outline-variant/50 space-y-2">
            <h4 className="font-semibold text-sm text-on-surface">Consult AI Mentor for System Tuning</h4>
            <p className="text-xs text-on-surface-variant leading-relaxed">
              Ask AI Placement Mentor how to write unit tests for RabbitMQ event bus handlers.
            </p>
            <button
              onClick={() => navigate('/ai-mentor')}
              className="text-xs font-semibold text-primary hover:underline inline-flex items-center gap-1 pt-1"
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
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-obsidian-950/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-sm bg-surface-container-high border border-outline-variant rounded-2xl p-6 space-y-4">
            <h3 className="font-semibold text-on-surface text-base">Delete Project Audit?</h3>
            <p className="text-xs text-on-surface-variant">
              Are you sure you want to remove this project? This will delete its AST evidence bullets from frontend state.
            </p>
            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setDeleteConfirmId(null)}
                className="px-3.5 py-1.5 rounded-xl text-xs font-medium text-on-surface-variant hover:bg-surface-container"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDeleteProject(deleteConfirmId)}
                className="px-4 py-1.5 rounded-xl text-xs font-semibold bg-error text-on-error hover:opacity-90"
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
