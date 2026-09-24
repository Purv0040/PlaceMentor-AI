import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';

export const SettingsSection = ({ settings, onUpdateSettings, onResetAll }) => {
  const { logout } = useAuth();
  const [activeTab, setActiveTab] = useState('section-placement');
  const [showResetModal, setShowResetModal] = useState(false);
  const [passwordState, setPasswordState] = useState({ current: '', newPass: '', confirm: '' });
  const [passwordFeedback, setPasswordFeedback] = useState(null);

  const tabs = [
    { id: 'section-placement', label: 'Placement & Role Goals', icon: 'track_changes', badge: 'Active' },
    { id: 'section-telemetry', label: 'AI Personalization', icon: 'memory', badge: '7 active' },
    { id: 'section-mentor', label: 'Mentor Persona', icon: 'record_voice_over' },
    { id: 'section-notifications', label: 'Notifications & Cadence', icon: 'notifications_active' },
    { id: 'section-privacy', label: 'Privacy & Data Usage', icon: 'shield_person', badge: 'Strict' },
    { id: 'section-integrations', label: 'Connected Accounts', icon: 'hub', badge: '3 linked' },
    { id: 'section-security', label: 'Account & Security', icon: 'lock' },
    { id: 'section-danger', label: 'Danger Zone', icon: 'warning', danger: true }
  ];

  const handlePasswordChangeSubmit = (e) => {
    e.preventDefault();
    if (!passwordState.current || !passwordState.newPass) {
      setPasswordFeedback({ error: 'Please enter both current and new password.' });
      return;
    }
    if (passwordState.newPass !== passwordState.confirm) {
      setPasswordFeedback({ error: 'New passwords do not match.' });
      return;
    }
    setPasswordFeedback({ success: 'Frontend session credentials updated (Mock Mode).' });
    setPasswordState({ current: '', newPass: '', confirm: '' });
    setTimeout(() => setPasswordFeedback(null), 3000);
  };

  const handleConfirmReset = () => {
    onResetAll();
    setShowResetModal(false);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start pt-2">
      {/* LEFT COLUMN: Sticky Navigation Pills (3 cols) */}
      <div className="lg:col-span-3 lg:sticky lg:top-20 flex flex-col gap-4">
        <div className="flex flex-col bg-[#171b26] border border-[#262a35] rounded-2xl p-2 shadow-sm gap-1">
          <div className="px-3 py-1.5 flex items-center justify-between border-b border-[#262a35] mb-1">
            <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
              Configuration Modules
            </span>
            <span className="text-[10px] font-mono text-purple-300 bg-purple-500/10 px-1.5 py-0.2 rounded border border-purple-500/20">
              8 tabs
            </span>
          </div>

          {tabs.map((t) => {
            const isActive = activeTab === t.id;
            return (
              <button
                key={t.id}
                type="button"
                onClick={() => setActiveTab(t.id)}
                className={`flex items-center justify-between px-3 py-2 rounded-xl text-xs text-left transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-semibold shadow-md'
                    : t.danger
                    ? 'text-rose-400 hover:bg-rose-500/10'
                    : 'text-slate-400 hover:bg-[#1c1f2a] hover:text-white'
                }`}
              >
                <div className="flex items-center gap-2 min-w-0">
                  <span className="material-symbols-outlined text-base shrink-0">{t.icon}</span>
                  <span className="truncate">{t.label}</span>
                </div>
                {t.badge && (
                  <span
                    className={`text-[10px] font-mono px-1.5 py-0.2 rounded ${
                      isActive
                        ? 'bg-white/20 text-white'
                        : 'bg-[#0a0e18] text-indigo-300 border border-[#232b3e]'
                    }`}
                  >
                    {t.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* RIGHT COLUMN: Active Configuration Panel (9 cols) */}
      <div className="lg:col-span-9 flex flex-col gap-6">
        {/* 1. Placement & Role Goals */}
        {activeTab === 'section-placement' && (
          <div className="p-6 rounded-2xl bg-[#171b26] border border-[#262a35] shadow-lg space-y-4">
            <div className="flex items-center gap-2 border-b border-[#262a35] pb-3">
              <span className="material-symbols-outlined text-purple-400 text-lg">track_changes</span>
              <h3 className="font-bold text-base text-white">Placement & Role Targets</h3>
            </div>

            <div className="grid sm:grid-cols-2 gap-4 text-xs">
              <div className="space-y-1">
                <label className="text-[11px] text-slate-300">Target Career Role</label>
                <select
                  value={settings.placement.targetRole}
                  onChange={(e) =>
                    onUpdateSettings({
                      placement: { ...settings.placement, targetRole: e.target.value }
                    })
                  }
                  className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500"
                >
                  <option value="Backend Developer">Backend Developer</option>
                  <option value="Full Stack Developer">Full Stack Developer</option>
                  <option value="AI/ML Engineer">AI/ML Engineer</option>
                  <option value="Frontend Engineer">Frontend Engineer</option>
                  <option value="DevOps / Cloud Engineer">DevOps / Cloud Engineer</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-[11px] text-slate-300">Target Company Tier</label>
                <input
                  type="text"
                  value={settings.placement.companyTier}
                  onChange={(e) =>
                    onUpdateSettings({
                      placement: { ...settings.placement, companyTier: e.target.value }
                    })
                  }
                  className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[11px] text-slate-300">Target CTC Bracket</label>
                <input
                  type="text"
                  value={settings.placement.targetCtc}
                  onChange={(e) =>
                    onUpdateSettings({
                      placement: { ...settings.placement, targetCtc: e.target.value }
                    })
                  }
                  className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500 font-mono"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[11px] text-slate-300">Campus Placement Season</label>
                <input
                  type="text"
                  value={settings.placement.targetDrive}
                  onChange={(e) =>
                    onUpdateSettings({
                      placement: { ...settings.placement, targetDrive: e.target.value }
                    })
                  }
                  className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>
          </div>
        )}

        {/* 2. AI Personalization & Reasoning */}
        {activeTab === 'section-telemetry' && (
          <div className="p-6 rounded-2xl bg-[#171b26] border border-[#262a35] shadow-lg space-y-4">
            <div className="flex items-center gap-2 border-b border-[#262a35] pb-3">
              <span className="material-symbols-outlined text-indigo-400 text-lg">memory</span>
              <h3 className="font-bold text-base text-white">AI Personalization & Reasoning Parameters</h3>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3.5 rounded-xl bg-[#0a0e18] border border-[#232b3e] flex items-center justify-between">
                <div>
                  <p className="font-semibold text-white">Probing Question Density</p>
                  <p className="text-[11px] text-slate-400">Frequency of technical edge-case challenges in AI responses</p>
                </div>
                <span className="font-mono text-purple-300 font-semibold px-2.5 py-1 rounded bg-purple-500/10 border border-purple-500/20">
                  {settings.ai.probingDensity}
                </span>
              </div>

              <div className="p-3.5 rounded-xl bg-[#0a0e18] border border-[#232b3e] flex items-center justify-between">
                <div>
                  <p className="font-semibold text-white">Automated GitHub Commit Telemetry</p>
                  <p className="text-[11px] text-slate-400">Sync repo commit metrics every 6 hours</p>
                </div>
                <span className="font-mono text-emerald-400 font-semibold px-2.5 py-1 rounded bg-emerald-500/10 border border-emerald-500/20">
                  {settings.ai.autoCommitSync}
                </span>
              </div>

              <div className="p-3.5 rounded-xl bg-[#0a0e18] border border-[#232b3e] flex items-center justify-between">
                <div>
                  <p className="font-semibold text-white">Max Prompt Allocation</p>
                  <p className="text-[11px] text-slate-400">Token budget for sub-240ms live response latency</p>
                </div>
                <span className="font-mono text-indigo-300 font-semibold px-2.5 py-1 rounded bg-indigo-500/10 border border-indigo-500/20">
                  {settings.ai.maxPromptTokens} Tokens
                </span>
              </div>
            </div>
          </div>
        )}

        {/* 3. Mentor Persona Tuning */}
        {activeTab === 'section-mentor' && (
          <div className="p-6 rounded-2xl bg-[#171b26] border border-[#262a35] shadow-lg space-y-4">
            <div className="flex items-center gap-2 border-b border-[#262a35] pb-3">
              <span className="material-symbols-outlined text-purple-400 text-lg">record_voice_over</span>
              <h3 className="font-bold text-base text-white">AI Mentor Persona Calibration</h3>
            </div>

            <div className="grid sm:grid-cols-2 gap-4 text-xs">
              <div className="space-y-1">
                <label className="text-[11px] text-slate-300">Default Mentor Persona Mode</label>
                <select
                  value={settings.mentor.defaultPersona}
                  onChange={(e) =>
                    onUpdateSettings({
                      mentor: { ...settings.mentor, defaultPersona: e.target.value }
                    })
                  }
                  className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500"
                >
                  <option value="tech">SDE Technical Interviewer (Google/Amazon)</option>
                  <option value="dsa">Socratic DSA Tutor (Zero Spoilers)</option>
                  <option value="story">Storytelling & STAR Coach</option>
                  <option value="strat">Placement Strategist & Stamina</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-[11px] text-slate-300">Primary Code Language Format</label>
                <input
                  type="text"
                  value={settings.mentor.codeLanguagePreference}
                  onChange={(e) =>
                    onUpdateSettings({
                      mentor: { ...settings.mentor, codeLanguagePreference: e.target.value }
                    })
                  }
                  className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500 font-mono"
                />
              </div>
            </div>
          </div>
        )}

        {/* 4. Notifications & Cadence */}
        {activeTab === 'section-notifications' && (
          <div className="p-6 rounded-2xl bg-[#171b26] border border-[#262a35] shadow-lg space-y-4">
            <div className="flex items-center gap-2 border-b border-[#262a35] pb-3">
              <span className="material-symbols-outlined text-amber-400 text-lg">notifications_active</span>
              <h3 className="font-bold text-base text-white">Notifications & Cadence Settings</h3>
            </div>

            <div className="space-y-3 text-xs">
              {Object.entries({
                taskReminders: 'Daily Action Plan Task Reminders',
                achievementNotifications: 'Milestone & Badge Unlock Alerts',
                mentorNotifications: 'AI Copilot Insight Digest',
                weeklyProgressSummary: 'Weekly Executive Telemetry Report'
              }).map(([key, label]) => (
                <div key={key} className="p-3.5 rounded-xl bg-[#0a0e18] border border-[#232b3e] flex items-center justify-between">
                  <span className="font-semibold text-white">{label}</span>
                  <input
                    type="checkbox"
                    checked={settings.notifications[key] ?? true}
                    onChange={(e) =>
                      onUpdateSettings({
                        notifications: { ...settings.notifications, [key]: e.target.checked }
                      })
                    }
                    className="w-4 h-4 rounded accent-indigo-600 bg-[#1c1f2a] border-[#262a35] cursor-pointer"
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 5. Privacy & Data Usage */}
        {activeTab === 'section-privacy' && (
          <div className="p-6 rounded-2xl bg-[#171b26] border border-[#262a35] shadow-lg space-y-4">
            <div className="flex items-center gap-2 border-b border-[#262a35] pb-3">
              <span className="material-symbols-outlined text-emerald-400 text-lg">shield_person</span>
              <h3 className="font-bold text-base text-white">Privacy & Local Storage Controls</h3>
            </div>

            <div className="p-4 rounded-xl bg-[#0a0e18] border border-[#232b3e] space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-white">Local Application Telemetry Storage</span>
                <span className="font-mono text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10">Strict Local Only</span>
              </div>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                All candidate telemetry, roadmap tasks, and chat histories are stored client-side in browser memory. No private credentials or secrets are transmitted externally.
              </p>
            </div>
          </div>
        )}

        {/* 6. Connected Accounts */}
        {activeTab === 'section-integrations' && (
          <div className="p-6 rounded-2xl bg-[#171b26] border border-[#262a35] shadow-lg space-y-4">
            <div className="flex items-center gap-2 border-b border-[#262a35] pb-3">
              <span className="material-symbols-outlined text-indigo-400 text-lg">hub</span>
              <h3 className="font-bold text-base text-white">Connected Accounts & Integrations</h3>
            </div>

            <div className="grid sm:grid-cols-2 gap-3 text-xs">
              <div className="p-3.5 rounded-xl bg-[#0a0e18] border border-[#232b3e] flex items-center justify-between">
                <span className="font-semibold text-white">GitHub OAuth Sync</span>
                <span className="font-mono text-emerald-400 text-[11px] px-2 py-0.5 rounded bg-emerald-500/10">Connected</span>
              </div>
              <div className="p-3.5 rounded-xl bg-[#0a0e18] border border-[#232b3e] flex items-center justify-between">
                <span className="font-semibold text-white">LeetCode Profile Fetcher</span>
                <span className="font-mono text-emerald-400 text-[11px] px-2 py-0.5 rounded bg-emerald-500/10">Connected</span>
              </div>
            </div>
          </div>
        )}

        {/* 7. Account & Security */}
        {activeTab === 'section-security' && (
          <div className="p-6 rounded-2xl bg-[#171b26] border border-[#262a35] shadow-lg space-y-6">
            <div className="flex items-center gap-2 border-b border-[#262a35] pb-3">
              <span className="material-symbols-outlined text-indigo-400 text-lg">lock</span>
              <h3 className="font-bold text-base text-white">Account & Session Security</h3>
            </div>

            {/* Password Feedback */}
            {passwordFeedback && (
              <div
                className={`p-3 rounded-xl text-xs font-mono border ${
                  passwordFeedback.error
                    ? 'bg-rose-500/10 border-rose-500/30 text-rose-400'
                    : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                }`}
              >
                {passwordFeedback.error || passwordFeedback.success}
              </div>
            )}

            {/* Frontend Mock Change Password Form */}
            <form onSubmit={handlePasswordChangeSubmit} className="space-y-4 text-xs">
              <h4 className="font-semibold text-white">Change Account Password (Frontend Mock)</h4>
              <div className="grid sm:grid-cols-3 gap-3">
                <div className="space-y-1">
                  <label className="text-[11px] text-slate-300">Current Password</label>
                  <input
                    type="password"
                    value={passwordState.current}
                    onChange={(e) => setPasswordState({ ...passwordState, current: e.target.value })}
                    className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[11px] text-slate-300">New Password</label>
                  <input
                    type="password"
                    value={passwordState.newPass}
                    onChange={(e) => setPasswordState({ ...passwordState, newPass: e.target.value })}
                    className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[11px] text-slate-300">Confirm New Password</label>
                  <input
                    type="password"
                    value={passwordState.confirm}
                    onChange={(e) => setPasswordState({ ...passwordState, confirm: e.target.value })}
                    className="w-full px-3 py-2 bg-[#0a0e18] border border-[#232b3e] rounded-xl text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <button
                type="submit"
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold transition-colors shadow-md"
              >
                Update Password
              </button>
            </form>

            {/* Logout Session Action */}
            <div className="pt-4 border-t border-[#262a35] flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-white">Active Application Session</p>
                <p className="text-[11px] text-slate-400">Logout from current session using AuthContext</p>
              </div>
              <button
                type="button"
                onClick={logout}
                className="px-4 py-2 rounded-xl bg-rose-500/20 hover:bg-rose-600 text-rose-300 hover:text-white border border-rose-500/30 text-xs font-semibold transition-all shadow-sm"
              >
                Sign Out / Logout
              </button>
            </div>
          </div>
        )}

        {/* 8. Danger Zone */}
        {activeTab === 'section-danger' && (
          <div className="p-6 rounded-2xl bg-[#171b26] border border-rose-500/30 shadow-lg space-y-4">
            <div className="flex items-center gap-2 border-b border-rose-500/20 pb-3">
              <span className="material-symbols-outlined text-rose-400 text-lg">warning</span>
              <h3 className="font-bold text-base text-rose-400">Danger Zone</h3>
            </div>

            <div className="p-4 rounded-xl bg-rose-950/20 border border-rose-900/30 flex flex-col sm:flex-row sm:items-center justify-between gap-4 text-xs">
              <div>
                <p className="font-semibold text-rose-300">Reset System & Telemetry Data</p>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  Clears local settings and restores initial candidate configuration defaults.
                </p>
              </div>
              <button
                type="button"
                onClick={() => setShowResetModal(true)}
                className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-semibold shadow-md transition-all shrink-0"
              >
                Reset Telemetry
              </button>
            </div>
          </div>
        )}

        {/* Confirmation Modal */}
        {showResetModal && (
          <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="max-w-md w-full p-6 rounded-2xl bg-[#171b26] border border-rose-500/40 shadow-2xl space-y-4">
              <div className="flex items-center gap-3 text-rose-400">
                <span className="material-symbols-outlined text-2xl">warning</span>
                <h3 className="font-bold text-lg text-white">Confirm Reset Telemetry</h3>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                Are you sure you want to reset local settings? This will restore initial system defaults for role targets and persona configuration.
              </p>
              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowResetModal(false)}
                  className="px-4 py-2 rounded-xl bg-[#0a0e18] hover:bg-[#1c1f2a] text-slate-300 text-xs font-semibold border border-[#232b3e]"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleConfirmReset}
                  className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold shadow-md"
                >
                  Confirm Reset
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
