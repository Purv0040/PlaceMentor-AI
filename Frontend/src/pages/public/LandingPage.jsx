import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  Sparkles,
  ArrowRight,
  Zap,
  ShieldCheck,
  CheckCircle2,
  FileText,
  Github,
  Code2,
  FolderGit2,
  Target,
  Map,
  Video,
  MessageSquare,
  Bot,
  Activity
} from 'lucide-react';

export const LandingPage = () => {
  return (
    <div className="space-y-24 py-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      {/* 1. HERO SECTION */}
      <section id="hero" className="text-center space-y-8 pt-8">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-xs font-mono text-indigo-400">
          <Sparkles className="w-3.5 h-3.5" />
          <span>AI-Powered Placement Preparation Copilot</span>
        </div>

        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold text-white tracking-tight leading-tight max-w-5xl mx-auto">
          Your AI Copilot for <br />
          <span
            className="bg-gradient-to-r from-indigo-400 via-purple-400 to-emerald-400 bg-clip-text text-transparent inline-block"
            style={{ WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}
          >
            Placement Preparation
          </span>
        </h1>

        <p className="max-w-2xl mx-auto text-slate-400 text-sm sm:text-base leading-relaxed">
          Connect your GitHub, LeetCode, Resume, and Coding activity into a unified AI Copilot that dynamically adapts your 90-day placement roadmap.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
          <NavLink
            to="/signup"
            className="px-6 py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs sm:text-sm shadow-xl shadow-indigo-600/30 flex items-center gap-2 transition-all transform hover:-translate-y-0.5 border border-indigo-400/30"
          >
            Start Free Placement Onboarding <ArrowRight className="w-4 h-4" />
          </NavLink>
          <NavLink
            to="/dashboard"
            className="px-6 py-3.5 rounded-xl bg-[#121624] hover:bg-[#1a2030] border border-[#232b3e] text-slate-300 hover:text-white font-semibold text-xs sm:text-sm transition-all shadow-md"
          >
            Explore Demo Dashboard
          </NavLink>
        </div>

        {/* Hero Feature Badges */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-12 text-left">
          <div className="p-4 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-2 hover:border-indigo-500/40 transition-colors">
            <ShieldCheck className="w-5 h-5 text-indigo-400" />
            <p className="font-bold text-xs text-white">7-Vector Audit</p>
            <p className="text-[11px] text-slate-400">Multi-domain baseline evaluation</p>
          </div>
          <div className="p-4 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-2 hover:border-purple-500/40 transition-colors">
            <Zap className="w-5 h-5 text-purple-400" />
            <p className="font-bold text-xs text-white">90-Day Dynamic Roadmap</p>
            <p className="text-[11px] text-slate-400">Telemetry-driven daily study plan</p>
          </div>
          <div className="p-4 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-2 hover:border-emerald-500/40 transition-colors">
            <Bot className="w-5 h-5 text-emerald-400" />
            <p className="font-bold text-xs text-white">Socratic AI Mentor</p>
            <p className="text-[11px] text-slate-400">Targeted probing & code hints</p>
          </div>
          <div className="p-4 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-2 hover:border-amber-500/40 transition-colors">
            <Activity className="w-5 h-5 text-amber-400" />
            <p className="font-bold text-xs text-white">Real-Time Telemetry</p>
            <p className="text-[11px] text-slate-400">GitHub & LeetCode sync</p>
          </div>
        </div>
      </section>

      {/* 2. THE PLACEMENT PARADOX SECTION */}
      <section id="architecture" className="space-y-8">
        <div className="text-center space-y-3">
          <span className="text-[11px] font-mono uppercase tracking-wider text-indigo-400 font-semibold px-2.5 py-1 rounded bg-indigo-500/10 border border-indigo-500/20">
            The Core Challenge
          </span>
          <h2 className="text-3xl sm:text-4xl font-bold text-white">The Placement Paradox</h2>
          <p className="text-xs sm:text-sm text-slate-400 max-w-xl mx-auto">
            Traditional preparation relies on static sheets and blind problem solving. PlaceMentor AI bridges the gap with continuous telemetry analysis.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="p-6 rounded-2xl bg-[#121624] border border-rose-500/20 space-y-4">
            <div className="w-8 h-8 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400 font-bold text-xs">
              ✕
            </div>
            <h3 className="text-lg font-bold text-white">Traditional Static Preparation</h3>
            <ul className="space-y-2.5 text-xs text-slate-400">
              <li className="flex items-start gap-2">
                <span className="text-rose-400 mt-0.5">•</span>
                <span>Fixed problem lists ignoring candidate-specific weak spots.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-rose-400 mt-0.5">•</span>
                <span>No visibility into real GitHub repository code quality or architecture.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-rose-400 mt-0.5">•</span>
                <span>Generic ATS resume tips without role-targeted metric extraction.</span>
              </li>
            </ul>
          </div>

          <div className="p-6 rounded-2xl bg-gradient-to-tr from-[#121624] via-[#1a2030] to-indigo-950/20 border border-indigo-500/30 space-y-4">
            <div className="w-8 h-8 rounded-xl bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400 font-bold text-xs">
              ✓
            </div>
            <h3 className="text-lg font-bold text-white">PlaceMentor AI Copilot</h3>
            <ul className="space-y-2.5 text-xs text-slate-200">
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                <span>Dynamic 90-day roadmap that automatically shifts when topics are mastered.</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                <span>Deep GitHub & LeetCode telemetry auditing commit frequency and DSA speed.</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                <span>Socratic AI mentor guiding mock interviews and technical drills.</span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* 3. CONTEXTUAL TELEMETRY ENGINE */}
      <section className="p-8 sm:p-12 rounded-3xl bg-[#121624] border border-[#232b3e] space-y-8 shadow-xl">
        <div className="text-center space-y-3">
          <span className="text-[11px] font-mono uppercase tracking-wider text-purple-400 font-semibold px-2.5 py-1 rounded bg-purple-500/10 border border-purple-500/20">
            4-Step Intelligence Cycle
          </span>
          <h2 className="text-3xl sm:text-4xl font-bold text-white">Contextual Telemetry Engine</h2>
          <p className="text-xs sm:text-sm text-slate-400 max-w-xl mx-auto">
            Our multi-vector engine continuously ingests your preparation data to calculate your placement readiness.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="p-5 rounded-2xl bg-[#0f131d] border border-[#232b3e] space-y-3">
            <span className="text-xs font-mono font-bold text-indigo-400">Step 01</span>
            <h4 className="font-bold text-white text-sm">Candidate Telemetry</h4>
            <p className="text-xs text-slate-400">Syncs GitHub commits, LeetCode submissions, and uploaded resume text.</p>
          </div>
          <div className="p-5 rounded-2xl bg-[#0f131d] border border-[#232b3e] space-y-3">
            <span className="text-xs font-mono font-bold text-purple-400">Step 02</span>
            <h4 className="font-bold text-white text-sm">Multi-Vector Synthesis</h4>
            <p className="text-xs text-slate-400">Calculates your 7-vector score baseline against Tier-1 SDE company standards.</p>
          </div>
          <div className="p-5 rounded-2xl bg-[#0f131d] border border-[#232b3e] space-y-3">
            <span className="text-xs font-mono font-bold text-emerald-400">Step 03</span>
            <h4 className="font-bold text-white text-sm">Dynamic Planning</h4>
            <p className="text-xs text-slate-400">Generates adaptive daily tasks calibrated for your target placement drive.</p>
          </div>
          <div className="p-5 rounded-2xl bg-[#0f131d] border border-[#232b3e] space-y-3">
            <span className="text-xs font-mono font-bold text-amber-400">Step 04</span>
            <h4 className="font-bold text-white text-sm">Continuous Polish</h4>
            <p className="text-xs text-slate-400">Socratic mock drills refine verbal communication and live coding speed.</p>
          </div>
        </div>
      </section>

      {/* 4. COMPLETE PLATFORM SUITE */}
      <section id="features" className="space-y-8">
        <div className="text-center space-y-3">
          <span className="text-[11px] font-mono uppercase tracking-wider text-emerald-400 font-semibold px-2.5 py-1 rounded bg-emerald-500/10 border border-emerald-500/20">
            Full Feature Matrix
          </span>
          <h2 className="text-3xl sm:text-4xl font-bold text-white">Complete Platform Suite</h2>
          <p className="text-xs sm:text-sm text-slate-400 max-w-xl mx-auto">
            Everything required to transform candidate preparation into verifiable company offer readiness.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-3 hover:border-indigo-500/40 transition-colors">
            <FileText className="w-6 h-6 text-indigo-400" />
            <h4 className="font-bold text-white text-base">Resume Intelligence</h4>
            <p className="text-xs text-slate-400">ATS scoring, keyword alignment, and metric bullet point enhancement.</p>
          </div>

          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-3 hover:border-slate-500 transition-colors">
            <Github className="w-6 h-6 text-white" />
            <h4 className="font-bold text-white text-base">GitHub Intelligence</h4>
            <p className="text-xs text-slate-400">Commit frequency tracking, repo diversity, and architecture complexity audit.</p>
          </div>

          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-3 hover:border-amber-500/40 transition-colors">
            <Code2 className="w-6 h-6 text-amber-400" />
            <h4 className="font-bold text-white text-base">LeetCode Intelligence</h4>
            <p className="text-xs text-slate-400">DSA topic accuracy, problem solving speed telemetry, and pattern radar.</p>
          </div>

          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-3 hover:border-indigo-500/40 transition-colors">
            <FolderGit2 className="w-6 h-6 text-indigo-400" />
            <h4 className="font-bold text-white text-base">Project Intelligence</h4>
            <p className="text-xs text-slate-400">System design depth audit, API structure analysis, and code quality scoring.</p>
          </div>

          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-3 hover:border-rose-500/40 transition-colors">
            <Target className="w-6 h-6 text-rose-400" />
            <h4 className="font-bold text-white text-base">Skill Gap Analyzer</h4>
            <p className="text-xs text-slate-400">Candidate vs Required Benchmark matrix with priority remediation cards.</p>
          </div>

          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-3 hover:border-purple-500/40 transition-colors">
            <Map className="w-6 h-6 text-purple-400" />
            <h4 className="font-bold text-white text-base">90-Day AI Roadmap</h4>
            <p className="text-xs text-slate-400">Dynamic 3-phase curriculum with telemetry-driven missed day recovery.</p>
          </div>

          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-3 hover:border-emerald-500/40 transition-colors">
            <Video className="w-6 h-6 text-emerald-400" />
            <h4 className="font-bold text-white text-base">AI Mock Interview</h4>
            <p className="text-xs text-slate-400">Targeted technical and behavioral simulations with real-time feedback.</p>
          </div>

          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-3 hover:border-purple-500/40 transition-colors">
            <MessageSquare className="w-6 h-6 text-purple-400" />
            <h4 className="font-bold text-white text-base">Communication Coach</h4>
            <p className="text-xs text-slate-400">Verbal clarity, speaking pace (WPM), and technical explanation scoring.</p>
          </div>

          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-3 hover:border-indigo-500/40 transition-colors">
            <Bot className="w-6 h-6 text-indigo-400" />
            <h4 className="font-bold text-white text-base">AI Placement Mentor</h4>
            <p className="text-xs text-slate-400">Socratic conversational mentor providing code hints and conceptual drills.</p>
          </div>
        </div>
      </section>

      {/* 5. STREAMLINED ONBOARDING FLOW */}
      <section id="how-it-works" className="space-y-8">
        <div className="text-center space-y-3">
          <span className="text-[11px] font-mono uppercase tracking-wider text-indigo-400 font-semibold px-2.5 py-1 rounded bg-indigo-500/10 border border-indigo-500/20">
            Simple 4-Step Start
          </span>
          <h2 className="text-3xl sm:text-4xl font-bold text-white">Streamlined Onboarding Flow</h2>
          <p className="text-xs sm:text-sm text-slate-400 max-w-xl mx-auto">
            Get your personalized AI placement profile and initial 90-day roadmap in under 3 minutes.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-3">
            <div className="w-7 h-7 rounded-lg bg-indigo-600/20 border border-indigo-500/30 text-indigo-400 font-mono font-bold text-xs flex items-center justify-center">
              1
            </div>
            <h4 className="font-bold text-white text-sm">Build Your Profile</h4>
            <p className="text-xs text-slate-400">Input academic details, target role, and preferred company tier.</p>
          </div>

          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-3">
            <div className="w-7 h-7 rounded-lg bg-indigo-600/20 border border-indigo-500/30 text-indigo-400 font-mono font-bold text-xs flex items-center justify-center">
              2
            </div>
            <h4 className="font-bold text-white text-sm">Connect Accounts</h4>
            <p className="text-xs text-slate-400">Link GitHub handle and LeetCode profile for automated telemetry sync.</p>
          </div>

          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-3">
            <div className="w-7 h-7 rounded-lg bg-indigo-600/20 border border-indigo-500/30 text-indigo-400 font-mono font-bold text-xs flex items-center justify-center">
              3
            </div>
            <h4 className="font-bold text-white text-sm">AI Baseline Audit</h4>
            <p className="text-xs text-slate-400">Copilot synthesizes your 7-vector score and high-priority skill gaps.</p>
          </div>

          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-3">
            <div className="w-7 h-7 rounded-lg bg-indigo-600/20 border border-indigo-500/30 text-indigo-400 font-mono font-bold text-xs flex items-center justify-center">
              4
            </div>
            <h4 className="font-bold text-white text-sm">Execute Roadmap</h4>
            <p className="text-xs text-slate-400">Follow dynamic daily tasks and complete Socratic interview drills.</p>
          </div>
        </div>
      </section>

      {/* 6. FAQ & EXPECTATIONS */}
      <section id="faq" className="space-y-8">
        <div className="text-center space-y-3">
          <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 font-semibold px-2.5 py-1 rounded bg-slate-800 border border-slate-700">
            Clarity & Expectations
          </span>
          <h2 className="text-3xl sm:text-4xl font-bold text-white">Frequently Asked Questions</h2>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-2">
            <h4 className="font-bold text-white text-sm">How does the 7-vector score work?</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              It evaluates performance across DSA, System Design, Projects, GitHub Telemetry, LeetCode Solves, Mock Interviews, and Communication.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-2">
            <h4 className="font-bold text-white text-sm">Do I need to connect GitHub to use the platform?</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Connecting GitHub provides rich telemetry for code quality and commit cadence, but you can also start with manual profile inputs.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-2">
            <h4 className="font-bold text-white text-sm">What happens if I miss a few days of my roadmap?</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              The telemetry engine automatically re-balances your upcoming schedule and schedules recovery tasks without overwhelming your daily prep time.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-2">
            <h4 className="font-bold text-white text-sm">Is PlaceMentor AI tailored for specific roles?</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Yes, benchmarks adapt specifically for Backend Developer, Full Stack Engineer, AI/ML Engineer, and Frontend Developer candidate profiles.
            </p>
          </div>
        </div>
      </section>

      {/* 7. BOTTOM CTA */}
      <section className="p-8 sm:p-12 rounded-3xl bg-gradient-to-tr from-indigo-900/40 via-purple-900/30 to-[#121624] border border-indigo-500/30 text-center space-y-6 shadow-2xl">
        <h2 className="text-3xl sm:text-4xl font-extrabold text-white">
          Start building your placement readiness today.
        </h2>
        <p className="text-xs sm:text-sm text-slate-300 max-w-lg mx-auto leading-relaxed">
          Join candidates leveraging telemetry-driven AI roadmaps to secure Tier-1 product company offers.
        </p>
        <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
          <NavLink
            to="/signup"
            className="px-6 py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs sm:text-sm shadow-xl shadow-indigo-600/30 flex items-center gap-2 transition-all border border-indigo-400/30"
          >
            Create Account & Start Onboarding <ArrowRight className="w-4 h-4" />
          </NavLink>
          <NavLink
            to="/login"
            className="px-6 py-3.5 rounded-xl bg-[#121624] hover:bg-[#1a2030] border border-[#232b3e] text-slate-300 hover:text-white font-semibold text-xs sm:text-sm transition-all"
          >
            Log In
          </NavLink>
        </div>
      </section>
    </div>
  );
};
