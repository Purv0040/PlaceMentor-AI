import React, { useState } from 'react';
import { X, Play, Sliders, Target, ShieldCheck } from 'lucide-react';
import { useUser } from '../../context/UserContext';

export const InterviewSetupModal = ({ isOpen, onClose, onStartInterview }) => {
  const { user } = useUser();
  const defaultRole = user?.targetRole || user?.career?.targetRole || 'Backend SDE-1';

  const [config, setConfig] = useState({
    role: defaultRole,
    modality: 'System Architecture & Design',
    difficulty: 'Medium',
    questionCount: 3,
    duration: '15 mins',
  });

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    onStartInterview(config);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-obsidian-950/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg bg-surface-container-high border border-outline-variant rounded-2xl shadow-2xl overflow-hidden p-6">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-outline-variant/50">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-primary-container/20 text-primary border border-primary/30">
              <Sliders className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-lg text-on-surface">Configure Mock Interview Session</h3>
              <p className="text-xs text-on-surface-variant">Telemetry V4.2 Adaptive AI Interviewer</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-on-surface-variant hover:text-on-surface hover:bg-surface-container transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-on-surface-variant uppercase tracking-wider mb-1">
              Target Candidate Role
            </label>
            <input
              type="text"
              value={config.role}
              onChange={(e) => setConfig({ ...config, role: e.target.value })}
              className="w-full px-3.5 py-2 rounded-xl bg-surface-container-low border border-outline-variant text-on-surface text-sm focus:outline-none focus:border-primary transition-colors"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-on-surface-variant uppercase tracking-wider mb-1">
              Interview Modality / Category
            </label>
            <select
              value={config.modality}
              onChange={(e) => setConfig({ ...config, modality: e.target.value })}
              className="w-full px-3.5 py-2 rounded-xl bg-surface-container-low border border-outline-variant text-on-surface text-sm focus:outline-none focus:border-primary transition-colors"
            >
              <option value="System Architecture & Design">System Architecture & Design</option>
              <option value="Technical / DSA Drill">Technical / DSA Drill</option>
              <option value="Behavioral & HR STAR Drill">Behavioral & HR STAR Drill</option>
              <option value="Full Tier-1 SDE Mock">Full Tier-1 SDE Mock (Combined)</option>
            </select>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant uppercase tracking-wider mb-1">
                Difficulty
              </label>
              <select
                value={config.difficulty}
                onChange={(e) => setConfig({ ...config, difficulty: e.target.value })}
                className="w-full px-3 py-2 rounded-xl bg-surface-container-low border border-outline-variant text-on-surface text-sm focus:outline-none focus:border-primary transition-colors"
              >
                <option value="Easy">Easy</option>
                <option value="Medium">Medium</option>
                <option value="Hard">Hard</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant uppercase tracking-wider mb-1">
                Questions
              </label>
              <select
                value={config.questionCount}
                onChange={(e) => setConfig({ ...config, questionCount: parseInt(e.target.value) })}
                className="w-full px-3 py-2 rounded-xl bg-surface-container-low border border-outline-variant text-on-surface text-sm focus:outline-none focus:border-primary transition-colors"
              >
                <option value={1}>1 Question</option>
                <option value={3}>3 Questions</option>
                <option value={5}>5 Questions</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant uppercase tracking-wider mb-1">
                Duration
              </label>
              <select
                value={config.duration}
                onChange={(e) => setConfig({ ...config, duration: e.target.value })}
                className="w-full px-3 py-2 rounded-xl bg-surface-container-low border border-outline-variant text-on-surface text-sm focus:outline-none focus:border-primary transition-colors"
              >
                <option value="10 mins">10 mins</option>
                <option value="15 mins">15 mins</option>
                <option value="30 mins">30 mins</option>
              </select>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="pt-4 flex items-center justify-end gap-3 border-t border-outline-variant/50">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-sm font-medium text-on-surface-variant hover:text-on-surface hover:bg-surface-container transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 rounded-xl text-sm font-semibold bg-primary text-on-primary hover:bg-primary-fixed-dim transition-all shadow-md flex items-center gap-2"
            >
              <Play className="w-4 h-4 fill-on-primary" />
              <span>Launch Mock Session</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
