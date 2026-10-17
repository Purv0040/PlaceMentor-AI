import React from 'react';

export const MentorPersonaTabs = ({ activePersona, onSelectPersona }) => {
  const personas = [
    {
      id: 'tech',
      icon: 'terminal',
      title: 'Technical Interviewer'
    },
    {
      id: 'dsa',
      icon: 'psychology_alt',
      title: 'DSA Tutor'
    },
    {
      id: 'story',
      icon: 'record_voice_over',
      title: 'STAR Coach'
    },
    {
      id: 'strat',
      icon: 'military_tech',
      title: 'Placement Strategist'
    }
  ];

  return (
    <div className="flex flex-wrap items-center gap-1.5 p-1 rounded-xl bg-[#121622] border border-[#202535] my-4 shadow-inner">
      {personas.map((p) => {
        const isActive = activePersona === p.id;
        return (
          <button
            key={p.id}
            type="button"
            onClick={() => onSelectPersona(p.id)}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
              isActive
                ? 'bg-purple-500/15 text-white border border-purple-500/35 font-semibold shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-[#1a1f30]'
            }`}
          >
            <span
              className={`material-symbols-outlined text-base ${
                isActive ? 'text-purple-400' : 'text-slate-400'
              }`}
            >
              {p.icon}
            </span>
            <span>{p.title}</span>
          </button>
        );
      })}
    </div>
  );
};
