import React, { useState, useEffect } from 'react';
import { X, FolderPlus, Save, AlertCircle } from 'lucide-react';

export const ProjectModal = ({ isOpen, onClose, onSave, projectToEdit }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'Full Stack',
    technologies: '',
    githubUrl: '',
    liveUrl: '',
    architectureTags: '',
  });
  const [error, setError] = useState('');

  useEffect(() => {
    if (projectToEdit) {
      setFormData({
        title: projectToEdit.title || '',
        description: projectToEdit.description || '',
        category: projectToEdit.category || 'Full Stack',
        technologies: Array.isArray(projectToEdit.technologies) ? projectToEdit.technologies.join(', ') : (projectToEdit.technologies || ''),
        githubUrl: projectToEdit.githubUrl || '',
        liveUrl: projectToEdit.liveUrl || '',
        architectureTags: Array.isArray(projectToEdit.architectureTags) ? projectToEdit.architectureTags.join(', ') : (projectToEdit.architectureTags || ''),
      });
    } else {
      setFormData({
        title: '',
        description: '',
        category: 'Full Stack',
        technologies: '',
        githubUrl: '',
        liveUrl: '',
        architectureTags: '',
      });
    }
    setError('');
  }, [projectToEdit, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.title.trim() || !formData.description.trim()) {
      setError('Project title and description are required.');
      return;
    }

    const techArray = formData.technologies
      .split(',')
      .map((t) => t.trim())
      .filter((t) => t.length > 0);

    const archArray = formData.architectureTags
      .split(',')
      .map((a) => a.trim())
      .filter((a) => a.length > 0);

    const projectData = {
      id: projectToEdit ? projectToEdit.id : `proj-${Date.now()}`,
      title: formData.title.trim(),
      description: formData.description.trim(),
      category: formData.category,
      technologies: techArray.length > 0 ? techArray : ['React', 'Node.js'],
      githubUrl: formData.githubUrl.trim(),
      liveUrl: formData.liveUrl.trim(),
      score: projectToEdit ? projectToEdit.score : 88,
      scoreBadge: projectToEdit ? projectToEdit.scoreBadge : 'Production Grade',
      complexityScore: projectToEdit ? projectToEdit.complexityScore : 85,
      architectureTags: archArray.length > 0 ? archArray : ['REST API', 'Docker'],
      evidenceBullets: projectToEdit
        ? projectToEdit.evidenceBullets
        : [
            `Engineered ${formData.title} with high code modularity and clean architectural patterns.`,
            `Integrated ${techArray[0] || 'core technologies'} delivering responsive throughput.`
          ],
      updatedAt: 'Just now'
    };

    onSave(projectData);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-in fade-in duration-200">
      <div className="relative w-full max-w-xl bg-[#121624] border border-[#232b3e] rounded-2xl shadow-2xl overflow-hidden p-6 max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-[#232b3e]">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
              <FolderPlus className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-lg text-white">
                {projectToEdit ? 'Edit Project Audit' : 'Add New Project'}
              </h3>
              <p className="text-xs text-slate-400">Project Intelligence AST Audit</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-[#1a2133] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="mt-4 space-y-4 overflow-y-auto pr-1 flex-1">
          {error && (
            <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Project Title *
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="e.g. Distributed Event Bus & Pub-Sub Broker"
              className="w-full px-3.5 py-2 rounded-xl bg-[#0b0e17] border border-[#232b3e] text-white text-sm focus:outline-none focus:border-indigo-500 transition-colors"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Category / Domain
            </label>
            <select
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              className="w-full px-3.5 py-2 rounded-xl bg-[#0b0e17] border border-[#232b3e] text-white text-sm focus:outline-none focus:border-indigo-500 transition-colors"
            >
              <option value="Full Stack / AI">Full Stack / AI</option>
              <option value="Backend / Systems">Backend / Systems</option>
              <option value="Systems Programming">Systems Programming</option>
              <option value="Full Stack">Full Stack</option>
              <option value="AI / ML">AI / ML</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Description *
            </label>
            <textarea
              rows="3"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Summarize architectural goals, scale, and problem solved..."
              className="w-full px-3.5 py-2 rounded-xl bg-[#0b0e17] border border-[#232b3e] text-white text-sm focus:outline-none focus:border-indigo-500 transition-colors resize-none"
              required
            ></textarea>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Technologies (comma separated)
            </label>
            <input
              type="text"
              value={formData.technologies}
              onChange={(e) => setFormData({ ...formData, technologies: e.target.value })}
              placeholder="React, Node.js, Docker, PostgreSQL, Redis"
              className="w-full px-3.5 py-2 rounded-xl bg-[#0b0e17] border border-[#232b3e] text-white text-sm focus:outline-none focus:border-indigo-500 transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Architecture Tags (comma separated)
            </label>
            <input
              type="text"
              value={formData.architectureTags}
              onChange={(e) => setFormData({ ...formData, architectureTags: e.target.value })}
              placeholder="Microservices, Pub-Sub, REST API, WebSockets"
              className="w-full px-3.5 py-2 rounded-xl bg-[#0b0e17] border border-[#232b3e] text-white text-sm focus:outline-none focus:border-indigo-500 transition-colors"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                GitHub Repository URL
              </label>
              <input
                type="url"
                value={formData.githubUrl}
                onChange={(e) => setFormData({ ...formData, githubUrl: e.target.value })}
                placeholder="https://github.com/user/repo"
                className="w-full px-3.5 py-2 rounded-xl bg-[#0b0e17] border border-[#232b3e] text-white text-sm focus:outline-none focus:border-indigo-500 transition-colors"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Live Demo URL (Optional)
              </label>
              <input
                type="url"
                value={formData.liveUrl}
                onChange={(e) => setFormData({ ...formData, liveUrl: e.target.value })}
                placeholder="https://myproject.demo.app"
                className="w-full px-3.5 py-2 rounded-xl bg-[#0b0e17] border border-[#232b3e] text-white text-sm focus:outline-none focus:border-indigo-500 transition-colors"
              />
            </div>
          </div>

          {/* Buttons */}
          <div className="pt-4 flex items-center justify-end gap-3 border-t border-[#232b3e]">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-sm font-medium text-slate-400 hover:text-white hover:bg-[#1a2133] transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 rounded-xl text-sm font-semibold bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white transition-all shadow-md shadow-indigo-600/25 flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              <span>{projectToEdit ? 'Update Project' : 'Save Project'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
