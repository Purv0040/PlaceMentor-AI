import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  Github,
  Code2,
  FolderKanban,
  Gauge,
  Target,
  Map,
  CheckSquare,
  TrendingUp,
  Mic,
  MessageCircle,
  Sparkles,
  Trophy,
  User,
  Settings,
  X
} from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { useUser } from '../../context/UserContext';

export const Sidebar = () => {
  const { sidebarOpen, closeSidebar } = useApp();
  const { user } = useUser();

  const navGroups = [
    {
      title: 'Main',
      items: [
        { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard }
      ]
    },
    {
      title: 'Preparation',
      items: [
        { label: 'Resume Intelligence', path: '/resume', icon: FileText },
        { label: 'GitHub Intelligence', path: '/github', icon: Github },
        { label: 'LeetCode Analytics', path: '/leetcode', icon: Code2 },
        { label: 'Projects Audit', path: '/projects', icon: FolderKanban }
      ]
    },
    {
      title: 'Intelligence',
      items: [
        { label: 'Placement Readiness', path: '/placement-readiness', icon: Gauge },
        { label: 'Skill Gaps', path: '/skill-gaps', icon: Target }
      ]
    },
    {
      title: 'Planning',
      items: [
        { label: '90-Day Roadmap', path: '/roadmap', icon: Map },
        { label: "Today's Tasks", path: '/tasks', icon: CheckSquare },
        { label: 'Progress Telemetry', path: '/progress', icon: TrendingUp }
      ]
    },
    {
      title: 'Practice',
      items: [
        { label: 'AI Mock Interview', path: '/mock-interview', icon: Mic },
        { label: 'Communication Lab', path: '/communication', icon: MessageCircle }
      ]
    },
    {
      title: 'AI Copilot',
      items: [
        { label: 'AI Placement Mentor', path: '/ai-mentor', icon: Sparkles, badge: 'AI' }
      ]
    },
    {
      title: 'Personal',
      items: [
        { label: 'Achievements', path: '/achievements', icon: Trophy },
        { label: 'Profile', path: '/profile', icon: User },
        { label: 'Settings', path: '/settings', icon: Settings }
      ]
    }
  ];

  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {sidebarOpen && (
        <div
          onClick={closeSidebar}
          className="fixed inset-0 z-40 bg-black/75 backdrop-blur-sm lg:hidden transition-opacity"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 bg-[#0f131d] border-r border-[#232b3e] flex flex-col transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="h-16 px-5 border-b border-[#232b3e] flex items-center justify-between shrink-0">
          <NavLink to="/dashboard" onClick={closeSidebar} className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-600/30 group-hover:scale-105 transition-transform">
              <Sparkles className="w-4.5 h-4.5 text-white" />
            </div>
            <div>
              <div className="font-bold text-base text-white tracking-wide flex items-center gap-1.5">
                PlaceMentor <span className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-400 font-mono font-semibold">AI</span>
              </div>
              <p className="text-[10px] text-slate-400 font-mono">Placement Copilot</p>
            </div>
          </NavLink>
          <button
            onClick={closeSidebar}
            className="lg:hidden p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/60"
            aria-label="Close Sidebar"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation Groups */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-4">
          {navGroups.map((group) => (
            <div key={group.title} className="space-y-1">
              <h4 className="px-3 text-[10px] font-mono font-semibold uppercase tracking-wider text-slate-500">
                {group.title}
              </h4>
              {group.items.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    onClick={closeSidebar}
                    className={({ isActive }) =>
                      `flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all ${
                        isActive
                          ? 'bg-gradient-to-r from-indigo-600/90 to-indigo-700/80 text-white font-semibold shadow-md shadow-indigo-600/20 border border-indigo-500/30'
                          : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/40'
                      }`
                    }
                  >
                    <Icon className="w-4 h-4 shrink-0" />
                    <span className="flex-1 truncate">{item.label}</span>
                    {item.badge && (
                      <span className="px-1.5 py-0.5 text-[10px] font-bold font-mono rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
                        {item.badge}
                      </span>
                    )}
                  </NavLink>
                );
              })}
            </div>
          ))}
        </nav>

        {/* Footer User Info */}
        <div className="p-3 border-t border-[#232b3e] bg-[#0b0e17] shrink-0">
          <div className="p-2.5 rounded-xl bg-[#121624] border border-[#232b3e] flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center font-bold text-xs text-indigo-400 font-mono">
              {user?.name ? user.name.split(' ').map(n=>n[0]).join('') : 'AP'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-white truncate">{user?.name || 'Alex Patel'}</p>
              <p className="text-[10px] text-slate-400 truncate">{user?.targetRole || 'Backend Developer'}</p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
