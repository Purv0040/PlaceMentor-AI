import React from 'react';
import { NavLink } from 'react-router-dom';
import { Menu, Bell, Search, Sparkles } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { UserMenuDropdown } from '../common/UserMenuDropdown';
import { dashboardData } from '../../data/dashboardData';

export const Header = () => {
  const { toggleSidebar, activeNotificationCount } = useApp();

  return (
    <header className="h-16 bg-[#0f131d]/90 backdrop-blur-md border-b border-[#232b3e] sticky top-0 z-30 px-4 lg:px-6 flex items-center justify-between">
      {/* Left: Mobile Sidebar Toggle & Search Bar */}
      <div className="flex items-center gap-3">
        <button
          onClick={toggleSidebar}
          className="lg:hidden p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800/60 border border-[#232b3e]"
          aria-label="Open Navigation Sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="relative hidden md:block w-64 lg:w-80">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search LC problems, roadmaps, DSA topics..."
            className="w-full pl-9 pr-4 py-1.5 text-xs rounded-xl bg-[#121624] border border-[#232b3e] text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
          />
        </div>
      </div>

      {/* Right: Telemetry Pill, Notifications & User Dropdown */}
      <div className="flex items-center gap-3">
        {/* Readiness Score Pill */}
        <NavLink
          to="/placement-readiness"
          className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-xs hover:border-indigo-500/40 transition-colors"
        >
          <Sparkles className="w-4 h-4 text-indigo-400" />
          <span className="text-slate-300 font-medium">Readiness:</span>
          <span className="font-bold text-indigo-400 font-mono">{dashboardData.readinessScore} / 100</span>
        </NavLink>

        {/* Notifications */}
        <button
          className="relative p-2 rounded-xl bg-[#121624] border border-[#232b3e] text-slate-400 hover:text-white hover:border-slate-700 transition-colors"
          aria-label="Notifications"
        >
          <Bell className="w-4 h-4" />
          {activeNotificationCount > 0 && (
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
          )}
        </button>

        {/* User Menu Dropdown */}
        <UserMenuDropdown />
      </div>
    </header>
  );
};
