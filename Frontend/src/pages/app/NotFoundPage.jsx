import React from 'react';
import { NavLink } from 'react-router-dom';
import { AlertTriangle, Home, ArrowLeft } from 'lucide-react';

export const NotFoundPage = () => {
  return (
    <div className="min-h-screen bg-[#0b0e17] text-white flex items-center justify-center p-6 text-center">
      <div className="max-w-md space-y-6">
        <div className="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center mx-auto text-amber-400">
          <AlertTriangle className="w-8 h-8" />
        </div>

        <div className="space-y-2">
          <h1 className="text-4xl font-extrabold font-mono text-white">404</h1>
          <h2 className="text-xl font-bold">Page Not Found</h2>
          <p className="text-xs text-slate-400 leading-relaxed">
            The telemetry path or route you requested does not exist in PlaceMentor AI.
          </p>
        </div>

        <div className="flex justify-center gap-3">
          <NavLink
            to="/dashboard"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition-colors"
          >
            <Home className="w-4 h-4" /> Go to Dashboard
          </NavLink>
          <NavLink
            to="/"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#121624] border border-[#232b3e] text-slate-300 hover:text-white text-xs font-semibold"
          >
            Landing Page
          </NavLink>
        </div>
      </div>
    </div>
  );
};
