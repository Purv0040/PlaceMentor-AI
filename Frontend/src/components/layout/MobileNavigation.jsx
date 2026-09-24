import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Target, Map, Mic, User } from 'lucide-react';
import { useApp } from '../../context/AppContext';

export const MobileNavigation = () => {
  const { closeSidebar } = useApp();

  const quickNav = [
    { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { label: 'Skill Gaps', path: '/skill-gaps', icon: Target },
    { label: 'Roadmap', path: '/roadmap', icon: Map },
    { label: 'AI Mock', path: '/mock-interview', icon: Mic },
    { label: 'Profile', path: '/profile', icon: User },
  ];

  return (
    <div className="lg:hidden fixed bottom-0 left-0 right-0 z-40 bg-[#0f131d]/95 backdrop-blur-lg border-t border-[#232b3e] px-2 py-1.5 shadow-2xl">
      <div className="flex items-center justify-around">
        {quickNav.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={closeSidebar}
              className={({ isActive }) =>
                `flex flex-col items-center gap-1 py-1 px-3 rounded-xl transition-colors ${
                  isActive ? 'text-indigo-400 font-semibold' : 'text-slate-400 hover:text-slate-200'
                }`
              }
            >
              <Icon className="w-5 h-5" />
              <span className="text-[10px] font-medium">{item.label}</span>
            </NavLink>
          );
        })}
      </div>
    </div>
  );
};
