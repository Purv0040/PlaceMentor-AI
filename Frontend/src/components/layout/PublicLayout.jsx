import React from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { Sparkles, ArrowRight } from 'lucide-react';

export const PublicLayout = () => {
  const location = useLocation();
  const isLanding = location.pathname === '/';

  return (
    <div className="min-h-screen bg-[#0b0e17] text-slate-100 flex flex-col font-sans antialiased selection:bg-indigo-500/30 selection:text-white">
      {/* Top Header Navbar */}
      <header className="h-16 border-b border-[#232b3e] bg-[#0f131d]/90 backdrop-blur-md sticky top-0 z-40 px-4 sm:px-8 flex items-center justify-between">
        <NavLink to="/" className="flex items-center gap-2.5 group">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-600/30 group-hover:scale-105 transition-transform">
            <Sparkles className="w-4.5 h-4.5 text-white" />
          </div>
          <div className="font-bold text-base text-white tracking-wide flex items-center gap-1.5">
            PlaceMentor <span className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-400 font-mono font-semibold">AI</span>
          </div>
        </NavLink>

        {/* Anchor Links for Landing page */}
        {isLanding && (
          <nav className="hidden md:flex items-center gap-6 text-xs text-slate-400 font-medium">
            <a href="#hero" className="hover:text-white transition-colors">Overview</a>
            <a href="#architecture" className="hover:text-white transition-colors">Architecture</a>
            <a href="#features" className="hover:text-white transition-colors">Suite</a>
            <a href="#how-it-works" className="hover:text-white transition-colors">Workflow</a>
            <a href="#faq" className="hover:text-white transition-colors">FAQ</a>
          </nav>
        )}

        {/* Right CTA Actions */}
        <div className="flex items-center gap-3">
          <NavLink
            to="/login"
            className="px-3.5 py-2 text-xs font-semibold text-slate-300 hover:text-white transition-colors"
          >
            Log In
          </NavLink>
          <NavLink
            to="/signup"
            className="px-4 py-2 text-xs font-semibold rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/30 transition-all flex items-center gap-1.5"
          >
            Get Started <ArrowRight className="w-3.5 h-3.5" />
          </NavLink>
        </div>
      </header>

      {/* Main Page Area */}
      <main className="flex-1">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="py-8 border-t border-[#232b3e] bg-[#0b0e17] text-center text-xs text-slate-500 font-mono">
        <div className="max-w-6xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            </div>
            <span className="font-sans font-bold text-slate-300">PlaceMentor AI</span>
          </div>
          <p>© 2026 PlaceMentor AI — Contextual Placement Telemetry Engine</p>
          <div className="flex items-center gap-4 text-[11px] text-slate-400">
            <NavLink to="/login" className="hover:text-slate-200">Sign In</NavLink>
            <NavLink to="/signup" className="hover:text-slate-200">Register</NavLink>
            <NavLink to="/dashboard" className="hover:text-slate-200">Demo App</NavLink>
          </div>
        </div>
      </footer>
    </div>
  );
};
