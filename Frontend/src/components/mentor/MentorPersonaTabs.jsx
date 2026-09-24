import React from 'react';

export const MentorPersonaTabs = ({ activePersona, onSelectPersona }) => {
  const personas = [
    {
      id: 'tech',
      icon: 'terminal',
      title: 'SDE Technical Interviewer',
      subtitle: '(Google/Amazon)',
      fillIcon: true
    },
    {
      id: 'dsa',
      icon: 'psychology_alt',
      title: 'Socratic DSA Tutor',
      subtitle: '(Zero Spoilers)'
    },
    {
      id: 'story',
      icon: 'record_voice_over',
      title: 'Storytelling & STAR Coach'
    },
    {
      id: 'strat',
      icon: 'military_tech',
      title: 'Placement Strategist & Stamina'
    }
  ];

  return (
    <div className="flex flex-wrap items-center gap-1.5 p-1 rounded-xl bg-[#0a0e18] border border-[#1c1f2a] shadow-inner mb-4">
      {personas.map((p) => {
        const isActive = activePersona === p.id;
        return (
          <button
            key={p.id}
            type="button"
            onClick={() => onSelectPersona(p.id)}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
              isActive
                ? 'bg-[#262a35] text-white shadow-sm border border-purple-500/30 font-semibold'
                : 'text-slate-400 hover:text-slate-200 hover:bg-[#171b26]'
            }`}
          >
            <span
              className={`material-symbols-outlined text-base ${
                isActive ? 'text-purple-400' : 'text-slate-400'
              }`}
              style={p.fillIcon && isActive ? { fontVariationSettings: "'FILL' 1" } : {}}
            >
              {p.icon}
            </span>
            <span>
              {p.title}{' '}
              {p.subtitle && (
                <span className={`text-[10px] font-mono ${isActive ? 'text-purple-300' : 'text-slate-500'}`}>
                  {p.subtitle}
                </span>
              )}
            </span>
          </button>
        );
      })}
    </div>
  );
};
