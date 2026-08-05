import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, ArrowRight, ShieldCheck, Target, TrendingUp } from 'lucide-react';

export const Home: React.FC = () => {
  return (
    <div className="relative min-h-screen bg-slate-50 text-slate-900 flex flex-col justify-between antialiased selection:bg-indigo-500 selection:text-white">
      {/* Background Decorative Accents */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-indigo-200/40 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-indigo-300/30 rounded-full blur-3xl" />
      </div>

      {/* Top-Right Action Buttons Only - No Navbar */}
      <div className="absolute top-4 right-4 sm:top-8 sm:right-8 z-10 flex items-center gap-2 sm:gap-3">
        <Link
          id="student-login-btn"
          to="/auth"
          className="px-3 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm font-medium text-indigo-600 bg-white border border-indigo-200 rounded-xl hover:bg-indigo-50 hover:border-indigo-300 transition-all shadow-xs"
        >
          Student Login
        </Link>
        <Link
          id="register-btn"
          to="/auth"
          className="px-3 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm font-medium text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 transition-all shadow-sm hover:shadow-indigo-200"
        >
          Register
        </Link>
      </div>

      {/* Main Centered Hero Section */}
      <main className="relative flex-1 flex flex-col items-center justify-center text-center px-6 py-16 max-w-4xl mx-auto w-full">
        {/* Brand Chip */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-100/70 text-indigo-700 border border-indigo-200/60 text-xs font-semibold uppercase tracking-wider mb-6">
          <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
          <span>PlaceMentor AI</span>
        </div>

        {/* Hero Title - App Name */}
        <h1 id="hero-title" className="text-4xl sm:text-5xl md:text-6xl font-extrabold text-slate-900 tracking-tight leading-[1.15] mb-4">
          Placement Readiness Analyzer
        </h1>

        {/* One-Line Tagline */}
        <p id="hero-tagline" className="text-lg sm:text-xl md:text-2xl font-medium text-indigo-600 max-w-2xl mb-6 leading-snug">
          Evaluate your career readiness, bridge skill gaps, and land your dream role.
        </p>

        {/* Short Description */}
        <p id="hero-description" className="text-base sm:text-lg text-slate-600 max-w-2xl leading-relaxed mb-10">
          An AI-powered assessment suite designed for students. Analyze your resume, technical proficiency, and domain suitability to generate a comprehensive placement performance report.
        </p>

        {/* Primary Call to Action */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 w-full sm:w-auto">
          <Link
            id="get-started-btn"
            to="/auth"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-7 py-3.5 text-base font-semibold text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 transition-all shadow-md hover:shadow-indigo-200"
          >
            <span>Get Started</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        {/* Key Highlights */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mt-16 pt-12 border-t border-slate-200/80 w-full text-left">
          <div className="flex items-start gap-3 p-3 rounded-xl">
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg shrink-0">
              <Target className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-900">Domain Match</h3>
              <p className="text-xs text-slate-500 mt-0.5">Benchmark skills against real industry hiring criteria.</p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-3 rounded-xl">
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg shrink-0">
              <TrendingUp className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-900">Gap Analysis</h3>
              <p className="text-xs text-slate-500 mt-0.5">Identify weak spots in technical & soft skills instantly.</p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-3 rounded-xl">
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg shrink-0">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-900">Readiness Score</h3>
              <p className="text-xs text-slate-500 mt-0.5">Get a verified score & tailored report for interviews.</p>
            </div>
          </div>
        </div>
      </main>

      {/* Simple Footer */}
      <footer className="py-6 text-center text-xs text-slate-400">
        © {new Date().getFullYear()} PlaceMentor AI. All rights reserved.
      </footer>
    </div>
  );
};

export default Home;
