import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { usePlanning } from '../../context/PlanningContext';
import {
  Zap,
  CheckCircle2,
  Clock,
  ArrowRight,
  Filter,
  RefreshCw,
  Sparkles,
  ArrowUpRight,
  ListTodo,
  AlertCircle
} from 'lucide-react';

export const TasksPage = () => {
  const navigate = useNavigate();
  const { tasks, toggleTaskCompletion, roadmap, toastNotification } = usePlanning();
  const [activeCategory, setActiveCategory] = useState('All');

  const filteredTasks = activeCategory === 'All'
    ? tasks
    : tasks.filter((t) => t.category === activeCategory);

  const completedCount = tasks.filter((t) => t.completed).length;
  const totalCount = tasks.length;
  const completionPercent = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Toast Notification */}
      {toastNotification && (
        <div className="fixed bottom-10 right-6 z-50 flex items-center gap-2 px-4 py-3 bg-[#121624] border border-indigo-500/40 text-white rounded-xl shadow-2xl font-mono text-xs animate-in slide-in-from-bottom duration-200">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{toastNotification}</span>
        </div>
      )}

      {/* 1. HERO BANNER */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6 p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-indigo-950/60 via-purple-950/40 to-[#121624] border border-indigo-500/30 shadow-2xl">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-400 text-xs font-mono font-semibold border border-indigo-500/30">
              <Zap className="w-3.5 h-3.5 text-indigo-400" />
              Day {roadmap.currentDay} Execution Matrix
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">Today's Action Plan</h1>
          <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
            Prioritized daily engineering drills synchronized across your DSA accuracy, system architecture, and resume telemetry.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start lg:self-center shrink-0">
          <button
            onClick={() => navigate('/roadmap')}
            className="flex items-center gap-1.5 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs sm:text-sm font-semibold rounded-xl transition-all shadow-lg shadow-indigo-600/30 border border-indigo-400/30"
          >
            <span>View 90-Day Roadmap</span>
            <ArrowUpRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 2. COMPLETION SUMMARY BAR */}
      <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <span className="text-xs font-mono uppercase text-slate-400 font-semibold tracking-wider block">Today's Progress</span>
            <h3 className="text-lg font-bold text-white">
              {completedCount} of {totalCount} Tasks Completed ({completionPercent}%)
            </h3>
          </div>
          <span className="px-3 py-1.5 rounded-full text-xs font-mono font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 self-start sm:self-auto">
            Sprint 5 · Day {roadmap.currentDay}
          </span>
        </div>

        <div className="w-full bg-[#0f131d] rounded-full h-3 overflow-hidden border border-[#232b3e]">
          <div
            className="bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-400 h-full rounded-full transition-all duration-500 shadow-sm"
            style={{ width: `${completionPercent}%` }}
          ></div>
        </div>

        <div className="flex flex-wrap items-center justify-between text-xs font-mono text-slate-400 pt-1">
          <span>Active Tasks: {totalCount - completedCount}</span>
          <span>Target Duration: ~3.5 Hours Total</span>
          <span className="text-indigo-400 font-semibold">Status: {completionPercent === 100 ? 'All Tasks Completed 🎉' : 'In Progress'}</span>
        </div>
      </div>

      {/* 3. CATEGORY FILTER PILLS & TASK CARDS */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <h3 className="font-bold text-white text-lg flex items-center gap-2">
            <ListTodo className="w-5 h-5 text-indigo-400" />
            Task Execution Matrix
          </h3>

          <div className="flex flex-wrap items-center gap-1.5 text-xs font-mono">
            {['All', 'DSA', 'System Design', 'Projects', 'Resume', 'LeetCode'].map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`px-3.5 py-1.5 rounded-xl border transition-all ${
                  activeCategory === cat
                    ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white border-indigo-400/30 font-bold shadow-md'
                    : 'bg-[#121624] text-slate-400 border-[#232b3e] hover:text-white hover:bg-[#1a2030]'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Task Cards List */}
        <div className="grid grid-cols-1 gap-3">
          {filteredTasks.length === 0 ? (
            <div className="p-8 text-center rounded-2xl bg-[#121624] border border-dashed border-[#232b3e] text-slate-400 text-xs">
              No tasks found for category "{activeCategory}".
            </div>
          ) : (
            filteredTasks.map((task) => (
              <div
                key={task.id}
                className={`p-4 rounded-2xl border transition-all ${
                  task.completed
                    ? 'bg-[#0f131d]/60 border-[#232b3e] opacity-75'
                    : 'bg-[#121624] border-[#232b3e] hover:border-indigo-500/40'
                } flex items-center justify-between gap-4 shadow-xl`}
              >
                <div className="flex items-start gap-3.5 flex-1 min-w-0">
                  <button
                    type="button"
                    onClick={() => toggleTaskCompletion(task.id)}
                    className="mt-0.5 shrink-0 text-slate-400 hover:text-indigo-400 transition-colors"
                  >
                    <CheckCircle2
                      className={`w-5 h-5 ${
                        task.completed ? 'text-emerald-400 fill-emerald-500/20' : 'text-slate-500'
                      }`}
                    />
                  </button>

                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                      <span className="text-[10px] font-mono uppercase font-bold px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                        {task.category}
                      </span>
                      <span className="text-[10px] font-mono text-slate-400 flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5" /> {task.duration}
                      </span>
                      <span
                        className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded font-bold ${
                          task.priority === 'High'
                            ? 'bg-amber-500/20 text-amber-400'
                            : 'bg-[#1a2030] text-slate-400'
                        }`}
                      >
                        {task.priority} Priority
                      </span>
                    </div>

                    <p className={`text-xs sm:text-sm font-semibold ${task.completed ? 'line-through text-slate-400' : 'text-white'}`}>
                      {task.title}
                    </p>

                    {task.description && (
                      <p className="text-xs text-slate-300 mt-1 leading-relaxed">{task.description}</p>
                    )}
                  </div>
                </div>

                <button
                  onClick={() => navigate(task.route)}
                  className="p-2.5 rounded-xl bg-[#1a2030] text-slate-300 hover:text-white hover:bg-[#232b3e] border border-[#232b3e] transition-colors shrink-0"
                  title="Open Module Page"
                >
                  <ArrowRight className="w-4 h-4 text-indigo-400" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* 4. AI ADVICE BANNER */}
      <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-xl">
        <h3 className="font-bold text-white text-base flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-400" />
          Copilot Execution Advice
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-[#0f131d] border border-[#232b3e] space-y-2 hover:border-purple-500/40 transition-colors">
            <h4 className="font-bold text-sm text-white">Track Completion Analytics</h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              Every completed task automatically updates your active 24-day streak and overall readiness progress.
            </p>
            <button
              onClick={() => navigate('/progress')}
              className="text-xs font-bold text-indigo-400 hover:text-indigo-300 inline-flex items-center gap-1 pt-1"
            >
              <span>View Progress Telemetry</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="p-4 rounded-xl bg-[#0f131d] border border-[#232b3e] space-y-2 hover:border-purple-500/40 transition-colors">
            <h4 className="font-bold text-sm text-white">Review 90-Day Curriculum</h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              Inspect upcoming Day 35–40 milestones in Sprint 5 of your adaptive roadmap.
            </p>
            <button
              onClick={() => navigate('/roadmap')}
              className="text-xs font-bold text-indigo-400 hover:text-indigo-300 inline-flex items-center gap-1 pt-1"
            >
              <span>Go to 90-Day Roadmap</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
