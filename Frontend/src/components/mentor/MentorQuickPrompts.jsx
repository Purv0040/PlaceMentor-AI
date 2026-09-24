import React from 'react';

export const MentorQuickPrompts = ({ onSelectPrompt, disabled }) => {
  const prompts = [
    {
      icon: 'tips_and_updates',
      iconColor: 'text-purple-400',
      label: "What should I work on today?",
      promptText: "What should I work on today?"
    },
    {
      icon: 'radar',
      iconColor: 'text-rose-400',
      label: "Analyze my skill gaps",
      promptText: "What are my biggest weaknesses and skill gaps?"
    },
    {
      icon: 'description',
      iconColor: 'text-indigo-400',
      label: "How can I improve my resume?",
      promptText: "How can I improve my resume for Tier-1 ATS screening?"
    },
    {
      icon: 'verified',
      iconColor: 'text-emerald-400',
      label: "Am I interview ready?",
      promptText: "Am I interview ready? Give me an overall readiness analysis."
    },
    {
      icon: 'memory',
      iconColor: 'text-amber-400',
      label: "Explain Kahn's algorithm",
      promptText: "Explain Kahn's Topological Sort algorithm step by step"
    },
    {
      icon: 'groups',
      iconColor: 'text-sky-400',
      label: "Run mock: Conflict with a Teammate",
      promptText: "Run a 10-minute mock: Conflict with a Teammate"
    }
  ];

  return (
    <div className="flex flex-col gap-1.5 pt-2">
      <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
        Suggested Next Prompts For Today:
      </span>
      <div className="flex flex-wrap items-center gap-2">
        {prompts.map((p, idx) => (
          <button
            key={idx}
            type="button"
            disabled={disabled}
            onClick={() => onSelectPrompt(p.promptText)}
            className="px-3 py-1.5 rounded-lg bg-[#1c1f2a] hover:bg-[#262a35] text-slate-300 hover:text-white font-sans text-xs shadow-sm transition-all flex items-center gap-1.5 border border-[#262a35] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span className={`material-symbols-outlined text-sm ${p.iconColor}`}>
              {p.icon}
            </span>
            <span>{p.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};
