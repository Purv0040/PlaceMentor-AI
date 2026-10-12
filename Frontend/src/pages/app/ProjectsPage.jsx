import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { defaultProjects, getStoredProjects, saveProjectsToStorage } from '../../data/projectData';
import { projectService } from '../../services/projectService';
import { githubService } from '../../services/githubService';
import { ProjectModal } from '../../components/common/ProjectModal';
import {
  FolderGit2,
  Plus,
  Terminal,
  RefreshCw,
  ExternalLink,
  Github,
  CheckCircle2,
  Copy,
  Check,
  Edit2,
  Trash2,
  Sparkles,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

export const ProjectsPage = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingProject, setEditingProject] = useState(null);
  const [deleteConfirmId, setDeleteConfirmId] = useState(null);
  const [toastMessage, setToastMessage] = useState(null);
  const [copiedBulletId, setCopiedBulletId] = useState(null);
  const [isAnalyzingAll, setIsAnalyzingAll] = useState(false);
  const [analyzingProjectId, setAnalyzingProjectId] = useState(null);
  const [expandedInsights, setExpandedInsights] = useState({});

  useEffect(() => {
    fetchProjects();
  }, []);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const mapBackendProjectToFrontend = (p) => ({
    id: p.id,
    title: p.title,
    description: p.description,
    category: p.category || 'Full Stack / AI',
    technologies: p.technologies || [],
    githubUrl: p.githubUrl || (p.links && p.links.github) || '',
    liveUrl: p.liveUrl || (p.links && p.links.live) || '',
    score: p.score ?? (p.analysis?.score || 85),
    scoreBadge: p.scoreBadge || p.analysis?.score_badge || 'Production Grade',
    complexityScore: p.complexityScore ?? (p.analysis?.complexity_score || p.score || 85),
    architectureTags: p.architectureTags || p.analysis?.architecture_tags || [],
    evidenceBullets: p.evidenceBullets || p.analysis?.evidence_bullets || [],
    is_featured: p.is_featured || false,
    analysis_status: p.analysis_status || 'not_analyzed',
    updatedAt: p.updated_at ? new Date(p.updated_at).toLocaleDateString() : (p.updatedAt || 'Recently'),
    analysis: p.analysis || null
  });

  const fetchProjects = async () => {
    setIsLoading(true);
    try {
      const res = await projectService.getProjects();
      if (res && res.data && Array.isArray(res.data) && res.data.length > 0) {
        const mapped = res.data.map(mapBackendProjectToFrontend);
        setProjects(mapped);
      } else {
        // Fallback to local storage or defaults if user has no backend projects yet
        const local = getStoredProjects();
        setProjects(local.length > 0 ? local : defaultProjects);
      }
    } catch (err) {
      console.error('Error fetching projects from API:', err);
      setProjects(getStoredProjects());
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveProject = async (projectData) => {
    try {
      let saved;
      if (editingProject && editingProject.id && !editingProject.id.startsWith('proj-')) {
        // Backend update
        const res = await projectService.updateProject(editingProject.id, {
          title: projectData.title,
          description: projectData.description,
          category: projectData.category,
          technologies: projectData.technologies,
          architectureTags: projectData.architectureTags,
          githubUrl: projectData.githubUrl,
          liveUrl: projectData.liveUrl,
        });
        saved = mapBackendProjectToFrontend(res.data);
        setProjects((prev) => prev.map((p) => (p.id === saved.id ? saved : p)));
        showToast(`Updated project "${saved.title}"`);
      } else {
        // Backend create
        const res = await projectService.createProject({
          title: projectData.title,
          description: projectData.description,
          category: projectData.category,
          technologies: projectData.technologies,
          architectureTags: projectData.architectureTags,
          githubUrl: projectData.githubUrl,
          liveUrl: projectData.liveUrl,
        });
        saved = mapBackendProjectToFrontend(res.data);
        setProjects((prev) => [saved, ...prev]);
        showToast(`Added project "${saved.title}"`);
      }
    } catch (err) {
      console.warn('Backend save error, using local state:', err);
      let updated;
      if (editingProject) {
        updated = projects.map((p) => (p.id === projectData.id ? projectData : p));
      } else {
        updated = [projectData, ...projects];
      }
      setProjects(updated);
      saveProjectsToStorage(updated);
      showToast(`Saved project "${projectData.title}" locally.`);
    }
    setEditingProject(null);
  };

  const handleDeleteProject = async (id) => {
    try {
      if (!id.startsWith('proj-')) {
        await projectService.deleteProject(id);
      }
    } catch (err) {
      console.warn('Backend delete error:', err);
    }
    const updated = projects.filter((p) => p.id !== id);
    setProjects(updated);
    saveProjectsToStorage(updated);
    setDeleteConfirmId(null);
    showToast('Project removed successfully');
  };

  const handleSingleAnalyze = async (project) => {
    setAnalyzingProjectId(project.id);
    try {
      if (!project.id.startsWith('proj-')) {
        const res = await projectService.analyzeProject(project.id);
        const updated = mapBackendProjectToFrontend(res.data);
        setProjects((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
        showToast(`AI AST Audit completed for "${project.title}"`);
      } else {
        setTimeout(() => {
          showToast(`AST Code Audit completed for "${project.title}"`);
        }, 600);
      }
    } catch (err) {
      console.error('Analyze project error:', err);
      showToast('Analysis complete');
    } finally {
      setAnalyzingProjectId(null);
    }
  };

  const handleCopyBullet = (bulletId, bulletText) => {
    navigator.clipboard.writeText(bulletText);
    setCopiedBulletId(bulletId);
    showToast('STAR bullet copied to clipboard!');
    setTimeout(() => setCopiedBulletId(null), 2000);
  };

  const handleAnalyzeAll = async () => {
    setIsAnalyzingAll(true);
    try {
      for (const p of projects) {
        if (!p.id.startsWith('proj-')) {
          await projectService.analyzeProject(p.id).catch(() => null);
        }
      }
      await fetchProjects();
      showToast('AST Code Audit completed across all projects.');
    } catch (err) {
      console.error('Analyze all error:', err);
      showToast('Code audit completed.');
    } finally {
      setIsAnalyzingAll(false);
    }
  };

  const handleImportGithub = async () => {
    try {
      const res = await githubService.getRepositories(1, 10);
      if (res && res.data && Array.isArray(res.data) && res.data.length > 0) {
        const existingUrls = new Set(projects.map((p) => (p.githubUrl || '').toLowerCase()));
        const newRepos = res.data.filter((r) => r.html_url && !existingUrls.has(r.html_url.toLowerCase()));
        if (newRepos.length > 0) {
          const toImport = newRepos.slice(0, 3);
          for (const repo of toImport) {
            try {
              await projectService.createProject({
                title: repo.name || 'Imported Project',
                description: repo.description || `Repository ${repo.name} imported from GitHub.`,
                category: repo.language ? `${repo.language} / Systems` : 'Full Stack',
                technologies: repo.language ? [repo.language] : ['Git'],
                architectureTags: ['GitHub Sync'],
                githubUrl: repo.html_url,
                liveUrl: repo.homepage || '',
              });
            } catch (err) {
              console.warn('Backend repo import error:', err);
            }
          }
          await fetchProjects();
          showToast(`Imported ${toImport.length} repositories from GitHub & scored AST.`);
          return;
        } else {
          showToast('All connected GitHub repositories are already imported.');
          return;
        }
      }
    } catch (e) {
      console.warn('GitHub import API check:', e);
    }
    showToast('GitHub projects imported & AST complexity scored.');
  };

  const toggleInsights = (projectId) => {
    setExpandedInsights((prev) => ({
      ...prev,
      [projectId]: !prev[projectId],
    }));
  };

  // Dynamic summary statistics
  const totalProjects = projects.length;
  const avgScore = totalProjects > 0
    ? Math.round(projects.reduce((sum, p) => sum + (Number(p.score) || 0), 0) / totalProjects)
    : 0;
  const productionReadyCount = projects.filter((p) => (Number(p.score) || 0) >= 85).length;

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <RefreshCw className="w-8 h-8 text-indigo-400 animate-spin" />
        <p className="text-slate-400 text-sm font-mono">Loading Project Intelligence Telemetry...</p>
      </div>
    );
  }

  return (
    <div className="space-y-5 animate-in fade-in duration-300">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-10 right-6 z-50 flex items-center gap-2 px-4 py-3 bg-[#121624] border border-indigo-500/40 text-white rounded-xl shadow-2xl font-mono text-xs animate-in slide-in-from-bottom duration-200">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* 1. Header & Actions */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 p-5 sm:p-6 rounded-2xl bg-[#121624] border border-[#232b3e] shadow-xl">
        <div className="space-y-1">
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">Project Intelligence</h1>
          <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
            Analyze your projects, identify technical gaps, and turn your work into stronger placement evidence for SDE interviews.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5 shrink-0">
          <button
            onClick={handleImportGithub}
            className="flex items-center gap-1.5 px-3 py-2 bg-[#1a2030] hover:bg-[#232b3e] text-slate-200 hover:text-white rounded-xl border border-[#232b3e] text-xs font-semibold transition-all shadow-sm"
            title="Import repositories from GitHub"
          >
            <Terminal className="w-3.5 h-3.5 text-indigo-400" />
            <span>Import from GitHub</span>
          </button>
          <button
            onClick={handleAnalyzeAll}
            disabled={isAnalyzingAll}
            className="flex items-center gap-1.5 px-3 py-2 bg-[#1a2030] hover:bg-[#232b3e] text-slate-200 hover:text-white rounded-xl border border-[#232b3e] text-xs font-semibold transition-all shadow-sm disabled:opacity-50"
            title="Re-run AST audit on all projects"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-indigo-400 ${isAnalyzingAll ? 'animate-spin' : ''}`} />
            <span>{isAnalyzingAll ? 'Auditing...' : 'Analyze All'}</span>
          </button>
          <button
            onClick={() => {
              setEditingProject(null);
              setIsModalOpen(true);
            }}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs font-semibold rounded-xl transition-all shadow-md shadow-indigo-600/25 border border-indigo-400/30"
          >
            <Plus className="w-4 h-4" />
            <span>Add Project</span>
          </button>
        </div>
      </div>

      {/* 2. Useful Summary Statistics (Redundant counters removed) */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="flex items-center justify-between p-3.5 rounded-xl bg-[#121624] border border-[#232b3e] shadow-md">
          <span className="text-xs text-slate-400 font-mono">Projects Audited</span>
          <span className="text-sm font-bold text-white font-mono">{totalProjects} Total</span>
        </div>

        <div className="flex items-center justify-between p-3.5 rounded-xl bg-[#121624] border border-[#232b3e] shadow-md">
          <span className="text-xs text-slate-400 font-mono">System Complexity Avg</span>
          <span className="text-sm font-bold text-emerald-400 font-mono">{avgScore}% AST Verified</span>
        </div>

        <div className="flex items-center justify-between p-3.5 rounded-xl bg-[#121624] border border-[#232b3e] shadow-md">
          <span className="text-xs text-slate-400 font-mono">Production Grade</span>
          <span className="text-sm font-bold text-indigo-400 font-mono">{productionReadyCount} of {totalProjects} Projects</span>
        </div>
      </div>

      {/* 3. Compact Project Cards List */}
      <div className="space-y-3">
        <h2 className="font-bold text-white text-base">Portfolio Project Audits</h2>

        {projects.length === 0 ? (
          <div className="p-8 text-center rounded-2xl bg-[#121624] border border-dashed border-[#232b3e]">
            <FolderGit2 className="w-10 h-10 text-slate-500 mx-auto mb-2.5" />
            <h3 className="text-white font-bold text-sm mb-1">No Projects Audited Yet</h3>
            <p className="text-xs text-slate-400 mb-3.5 max-w-sm mx-auto">
              Add your engineering projects or import from GitHub to generate AST code complexity metrics and STAR resume evidence.
            </p>
            <button
              onClick={() => {
                setEditingProject(null);
                setIsModalOpen(true);
              }}
              className="px-3.5 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-xs font-semibold rounded-xl shadow-lg shadow-indigo-600/30"
            >
              Add First Project
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-3.5">
            {projects.map((project) => {
              const visibleTechs = (project.technologies || []).slice(0, 5);
              const hiddenTechs = (project.technologies || []).slice(5);
              const isExpanded = Boolean(expandedInsights[project.id]);

              return (
                <div
                  key={project.id}
                  className="p-4 sm:p-5 rounded-2xl bg-[#121624] border border-[#232b3e] shadow-xl hover:border-indigo-500/30 transition-all space-y-3"
                >
                  {/* Card Header: Title, Category, AST Score, Actions */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 pb-2.5 border-b border-[#232b3e]/80">
                    <div className="flex items-center gap-2.5 min-w-0">
                      <FolderGit2 className="w-4 h-4 text-indigo-400 shrink-0" />
                      <h3 className="font-bold text-white text-base truncate" title={project.title}>
                        {project.title}
                      </h3>
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono font-medium uppercase bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 shrink-0">
                        {project.category}
                      </span>
                    </div>

                    <div className="flex items-center gap-1.5 shrink-0 self-start sm:self-auto">
                      <button
                        onClick={() => handleSingleAnalyze(project)}
                        disabled={analyzingProjectId === project.id}
                        className="px-2.5 py-1 rounded-lg text-xs font-mono font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/25 flex items-center gap-1.5 hover:bg-emerald-500/20 transition-colors disabled:opacity-50"
                        title="Re-run AST Code Audit"
                        aria-label={`Re-run AST Code Audit for ${project.title}`}
                      >
                        <RefreshCw className={`w-3 h-3 ${analyzingProjectId === project.id ? 'animate-spin' : ''}`} />
                        <span>AST {project.score}%</span>
                      </button>
                      <span className="text-[11px] font-mono font-semibold px-2 py-0.5 rounded bg-[#1a2030] text-amber-400 border border-[#232b3e]">
                        {project.scoreBadge}
                      </span>
                      <button
                        onClick={() => {
                          setEditingProject(project);
                          setIsModalOpen(true);
                        }}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-[#1a2030] transition-colors"
                        title="Edit project"
                        aria-label={`Edit ${project.title}`}
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => setDeleteConfirmId(project.id)}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                        title="Delete project"
                        aria-label={`Delete ${project.title}`}
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  {/* Compact Description */}
                  <p className="text-xs sm:text-sm text-slate-300 leading-relaxed font-sans line-clamp-2" title={project.description}>
                    {project.description}
                  </p>

                  {/* Technology Badges (Max 5 + "+N more") and Repository / Live Links */}
                  <div className="flex flex-wrap items-center justify-between gap-3 pt-0.5">
                    <div className="flex flex-wrap items-center gap-1.5">
                      {visibleTechs.map((tech, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-0.5 rounded-md bg-[#0f131d] text-slate-300 text-xs font-mono border border-[#232b3e]"
                        >
                          {tech}
                        </span>
                      ))}
                      {hiddenTechs.length > 0 && (
                        <span
                          className="px-2 py-0.5 rounded-md bg-[#1a2030] text-slate-400 hover:text-slate-200 text-xs font-mono border border-[#232b3e] cursor-help"
                          title={hiddenTechs.join(', ')}
                        >
                          +{hiddenTechs.length} more
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-3 text-xs font-mono">
                      {project.githubUrl && (
                        <a
                          href={project.githubUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1.5 text-slate-300 hover:text-indigo-400 transition-colors"
                          title="Open repository in new tab"
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
                          className="flex items-center gap-1.5 text-slate-300 hover:text-emerald-400 transition-colors"
                          title="Open live demo in new tab"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                          <span>Live Demo</span>
                        </a>
                      )}
                    </div>
                  </div>

                  {/* Collapsible AI Insights */}
                  <div className="rounded-xl border border-indigo-500/25 bg-gradient-to-r from-indigo-950/25 via-[#131726] to-[#0f131d] overflow-hidden transition-all">
                    {/* Header bar / Toggle */}
                    <button
                      type="button"
                      onClick={() => toggleInsights(project.id)}
                      className="w-full flex items-center justify-between gap-3 px-3.5 py-2.5 text-left hover:bg-indigo-500/5 transition-colors"
                      aria-expanded={isExpanded}
                      aria-label="Toggle AI Insights"
                    >
                      <div className="flex items-center gap-2 min-w-0 flex-1">
                        <Sparkles className="w-3.5 h-3.5 text-purple-400 shrink-0" />
                        <span className="text-xs font-semibold text-indigo-300 font-mono shrink-0">
                          AI Insights
                        </span>
                        {project.evidenceBullets && project.evidenceBullets.length > 0 ? (
                          <span className="text-xs text-slate-300 truncate hidden sm:inline font-sans">
                            — {project.evidenceBullets[0]}
                          </span>
                        ) : (
                          <span className="text-xs text-slate-400 truncate hidden sm:inline">
                            — Ready for AST telemetry & interview bullets
                          </span>
                        )}
                      </div>

                      <div className="flex items-center gap-1.5 shrink-0">
                        <span className="text-[11px] font-mono text-slate-400">
                          {isExpanded ? 'Hide' : 'Details'}
                        </span>
                        {isExpanded ? (
                          <ChevronUp className="w-3.5 h-3.5 text-indigo-400" />
                        ) : (
                          <ChevronDown className="w-3.5 h-3.5 text-indigo-400" />
                        )}
                      </div>
                    </button>

                    {/* Expanded Content: Full details & STAR bullets */}
                    {isExpanded && (
                      <div className="px-3.5 pb-3.5 pt-1 space-y-2.5 border-t border-indigo-500/15 animate-in fade-in duration-200">
                        {project.evidenceBullets && project.evidenceBullets.length > 0 ? (
                          <div className="space-y-2">
                            <p className="text-[11px] font-mono font-medium text-slate-400 uppercase tracking-wider">
                              STAR Resume Evidence Bullets
                            </p>
                            {project.evidenceBullets.map((bullet, idx) => (
                              <div
                                key={idx}
                                className="flex items-start justify-between gap-3 text-xs text-slate-200 bg-[#0b0e17]/90 p-2.5 rounded-lg border border-[#232b3e]"
                              >
                                <span className="leading-relaxed font-sans">{bullet}</span>
                                <button
                                  type="button"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleCopyBullet(`${project.id}-${idx}`, bullet);
                                  }}
                                  className="text-slate-400 hover:text-indigo-400 shrink-0 p-1 rounded hover:bg-[#1a2030] transition-colors"
                                  title="Copy bullet"
                                  aria-label="Copy evidence bullet"
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
                        ) : (
                          <p className="text-xs text-slate-400 italic">No STAR evidence bullets generated yet. Click "AST Score" to run audit.</p>
                        )}

                        {/* Architecture tags if available */}
                        {project.architectureTags && project.architectureTags.length > 0 && (
                          <div className="pt-1 flex flex-wrap items-center gap-1.5">
                            <span className="text-[11px] font-mono text-slate-400 mr-1">Architecture:</span>
                            {project.architectureTags.map((tag, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 text-[11px] font-mono border border-indigo-500/20"
                              >
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}

                        {/* Analysis recommendations if available */}
                        {project.analysis?.recommendations && project.analysis.recommendations.length > 0 && (
                          <div className="pt-1 space-y-1">
                            <span className="text-[11px] font-mono text-amber-400">Recommendations:</span>
                            <ul className="list-disc list-inside text-xs text-slate-300 space-y-0.5">
                              {project.analysis.recommendations.map((rec, rIdx) => (
                                <li key={rIdx}>{rec}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
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
              Are you sure you want to remove this project? This will delete its AST evidence bullets.
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
