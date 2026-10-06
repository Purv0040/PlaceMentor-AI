import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Target, Map, User } from 'lucide-react';
import { useApp } from '../../context/AppContext';

export const MobileNavigation = () => {
  const { closeSidebar } = useApp();

  const quickNav = [
    { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { label: 'Skill Gaps', path: '/skill-gaps', icon: Target },
    { label: 'Roadmap', path: '/roadmap', icon: Map },
    { label: 'Profile', path: '/profile', icon: User },
  ];

  return (
    <nav className="lg:hidden fixed bottom-0 left-0 right-0 z-40 bg-[#0f131d]/95 backdrop-blur-xl border-t border-[#232b3e] px-2 py-2 safe-bottom shadow-2xl">
      <div className="flex items-center justify-around max-w-lg mx-auto">
        {quickNav.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={closeSidebar}
              className={({ isActive }) =>
                `flex flex-col items-center gap-1 py-1 px-3.5 rounded-xl transition-all ${
                  isActive
                    ? 'text-indigo-400 font-semibold bg-indigo-500/10'
                    : 'text-slate-400 hover:text-slate-200'
                }`
              }
            >
              <Icon className="w-5 h-5" />
              <span className="text-[10px] font-medium tracking-wide">{item.label}</span>
            </NavLink>
          );
        })}
      </div>
    </nav>
  );
};
