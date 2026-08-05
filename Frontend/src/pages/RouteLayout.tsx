import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, ArrowRight } from 'lucide-react';

interface RouteLayoutProps {
  routeName: string;
  description?: string;
}

const routesList = [
  { path: '/', name: '/' },
  { path: '/auth', name: '/auth' },
  { path: '/onboarding/domain', name: '/onboarding/domain' },
  { path: '/onboarding/details', name: '/onboarding/details' },
  { path: '/onboarding/profiles', name: '/onboarding/profiles' },
  { path: '/report', name: '/report' },
];

export const RouteLayout: React.FC<RouteLayoutProps> = ({ routeName, description }) => {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 flex flex-col justify-center items-center p-6 antialiased">
      <div className="w-full max-w-2xl bg-white rounded-2xl shadow-sm border border-indigo-100 p-8 md:p-10 transition-all duration-200">
        <div className="flex items-center gap-2 mb-6">
          <div className="p-2.5 bg-indigo-50 rounded-xl text-indigo-600">
            <Sparkles className="w-6 h-6" />
          </div>
          <span className="text-sm font-semibold tracking-wide text-indigo-600 uppercase">
            PlaceMentor AI
          </span>
        </div>

        <h1 id="page-title" className="text-3xl md:text-4xl font-bold text-slate-900 tracking-tight mb-3">
          {routeName}
        </h1>

        <p className="text-slate-500 mb-8 text-base">
          {description || `Placeholder page for route ${routeName}`}
        </p>

        <div className="border-t border-slate-100 pt-6">
          <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4">
            Available Routes Directory
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {routesList.map((route) => {
              const isActive = route.name === routeName;
              return (
                <Link
                  key={route.path}
                  to={route.path}
                  className={`flex items-center justify-between p-3 rounded-xl text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'bg-slate-50 text-slate-700 hover:bg-indigo-50 hover:text-indigo-600'
                  }`}
                >
                  <span>{route.name}</span>
                  <ArrowRight className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
