import React from 'react';

export const AchievementFilterTabs = ({
  activeCategory,
  onSelectCategory,
  searchQuery,
  onSearchChange,
  unlockedCount,
  totalCount
}) => {
  const categories = [
    { id: 'all', label: 'All Badges' },
    { id: 'Consistency', label: 'Consistency' },
    { id: 'DSA & Code', label: 'DSA & Code' },
    { id: 'System Design', label: 'System Design' },
    { id: 'Milestones', label: 'Milestones' },
    { id: 'Interview & STAR', label: 'Interview & STAR' }
  ];

  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pt-2">
      {/* Category Tabs */}
      <div className="flex flex-wrap items-center gap-1.5 p-1 rounded-xl bg-[#0a0e18] border border-[#232b3e]">
        {categories.map((cat) => {
          const isActive = activeCategory === cat.id;
          return (
            <button
              key={cat.id}
              type="button"
              onClick={() => onSelectCategory(cat.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                isActive
                  ? 'bg-indigo-600 text-white font-semibold shadow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-[#1c1f2a]'
              }`}
            >
              {cat.label}
            </button>
          );
        })}
      </div>

      {/* Search Input */}
      <div className="relative w-full md:w-64">
        <span className="material-symbols-outlined absolute left-3 top-2.5 text-slate-400 text-base">
          search
        </span>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Filter achievements..."
          className="w-full pl-9 pr-3 py-2 bg-[#171b26] border border-[#262a35] rounded-xl text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
        />
      </div>
    </div>
  );
};
