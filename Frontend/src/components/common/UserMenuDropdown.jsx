import React, { useState, useRef, useEffect } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { User, Settings, LogOut, ChevronDown, Sparkles } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useUser } from '../../context/UserContext';

export const UserMenuDropdown = () => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);
  const navigate = useNavigate();
  const { logout } = useAuth();
  const { user } = useUser();

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    setIsOpen(false);
    await logout();
    navigate('/login', { replace: true });
  };

  const initials = user?.name
    ? user.name.split(' ').map((n) => n[0]).join('').toUpperCase()
    : 'AP';

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 p-1.5 rounded-xl hover:bg-[#121624] border border-transparent hover:border-[#232b3e] transition-all"
        aria-label="User profile menu"
      >
        <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center font-bold text-xs text-white shadow-sm border border-indigo-400/30 font-mono">
          {initials}
        </div>
        <div className="hidden md:block text-left">
          <p className="text-xs font-semibold text-white leading-tight">{user?.name || 'Alex Patel'}</p>
          <p className="text-[10px] text-slate-400 font-mono leading-tight">{user?.college || 'CSPIT'}</p>
        </div>
        <ChevronDown className={`w-3.5 h-3.5 text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-56 rounded-2xl bg-[#121624] border border-[#232b3e] shadow-2xl py-2 z-50 animate-fadeIn space-y-1">
          <div className="px-4 py-2 border-b border-[#232b3e]">
            <p className="text-xs font-bold text-white">{user?.name || 'Alex Patel'}</p>
            <p className="text-[11px] text-indigo-400 font-mono">{user?.targetRole || 'Backend Developer'}</p>
          </div>

          <NavLink
            to="/profile"
            onClick={() => setIsOpen(false)}
            className="flex items-center gap-2.5 px-4 py-2 text-xs text-slate-300 hover:text-white hover:bg-[#1a2030] transition-colors"
          >
            <User className="w-4 h-4 text-slate-400" />
            <span>Candidate Profile</span>
          </NavLink>

          <NavLink
            to="/settings"
            onClick={() => setIsOpen(false)}
            className="flex items-center gap-2.5 px-4 py-2 text-xs text-slate-300 hover:text-white hover:bg-[#1a2030] transition-colors"
          >
            <Settings className="w-4 h-4 text-slate-400" />
            <span>System & AI Settings</span>
          </NavLink>

          <div className="border-t border-[#232b3e] pt-1 mt-1">
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-2.5 px-4 py-2 text-xs text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 transition-colors text-left"
            >
              <LogOut className="w-4 h-4" />
              <span>Log Out</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
