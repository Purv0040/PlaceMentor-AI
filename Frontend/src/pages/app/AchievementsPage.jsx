import React, { useState } from 'react';
import { usePlanning } from '../../context/PlanningContext';
import { achievementService } from '../../services/achievementService';
import { AchievementHeader } from '../../components/achievements/AchievementHeader';
import { AchievementFilterTabs } from '../../components/achievements/AchievementFilterTabs';
import { AchievementCard } from '../../components/achievements/AchievementCard';

export const AchievementsPage = () => {
  const planningState = usePlanning();
  const [activeCategory, setActiveCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [isDailyClaimed, setIsDailyClaimed] = useState(() => achievementService.isDailyXpClaimed());

  // Derive achievements dynamically from real application context
  const achievements = achievementService.getAchievements(planningState);
  const stats = {
    ...achievementService.getStats(achievements),
    isDailyClaimed
  };

  const handleClaimDailyXp = () => {
    const success = achievementService.claimDailyXp();
    if (success) {
      setIsDailyClaimed(true);
      return true;
    }
    return false;
  };

  // Filter achievements by category and search query
  const filteredAchievements = achievements.filter((ach) => {
    const matchesCat = activeCategory === 'all' || ach.category === activeCategory;
    const matchesSearch =
      !searchQuery ||
      ach.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ach.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCat && matchesSearch;
  });

  const unlockedList = filteredAchievements.filter(a => a.unlocked);
  const lockedList = filteredAchievements.filter(a => !a.unlocked);

  return (
    <div className="w-full min-h-[calc(100vh-5rem)] bg-[#0f131d] text-slate-100 space-y-6 pb-12">
      {/* 1. Header & Level Progression Banner */}
      <AchievementHeader stats={stats} onClaimDailyXp={handleClaimDailyXp} />

      {/* 2. Category Filter & Search Bar */}
      <AchievementFilterTabs
        activeCategory={activeCategory}
        onSelectCategory={setActiveCategory}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        unlockedCount={stats.unlockedCount}
        totalCount={stats.totalCount}
      />

      {/* 3. Earned Achievements Grid */}
      <div className="space-y-4 pt-2">
        <div className="flex items-center justify-between border-b border-[#262a35] pb-2">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <span className="material-symbols-outlined text-emerald-400 text-lg">workspace_premium</span>
            Unlocked Competencies & Badges ({unlockedList.length})
          </h2>
          <span className="text-xs font-mono text-emerald-400 font-medium">Earned Milestones</span>
        </div>

        {unlockedList.length === 0 ? (
          <div className="p-8 text-center rounded-2xl bg-[#171b26] border border-[#262a35] text-slate-400 text-xs">
            No unlocked achievements found for the selected filter.
          </div>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {unlockedList.map((ach) => (
              <AchievementCard key={ach.id} achievement={ach} />
            ))}
          </div>
        )}
      </div>

      {/* 4. Locked Achievements Grid */}
      {lockedList.length > 0 && (
        <div className="space-y-4 pt-6">
          <div className="flex items-center justify-between border-b border-[#262a35] pb-2">
            <h2 className="text-base font-bold text-slate-300 flex items-center gap-2">
              <span className="material-symbols-outlined text-slate-400 text-lg">lock</span>
              Upcoming & Locked Thresholds ({lockedList.length})
            </h2>
            <span className="text-xs font-mono text-slate-400">Target Milestones</span>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {lockedList.map((ach) => (
              <AchievementCard key={ach.id} achievement={ach} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
