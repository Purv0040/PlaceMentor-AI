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
        <div className="fixed bottom-10 right-6 z-50 flex items-center gap-2 px-4 py-3 bg-surface-container-highest border border-primary/40 text-on-surface rounded-xl shadow-2xl font-mono text-xs animate-in slide-in-from-bottom duration-200">
          <CheckCircle2 className="w-4 h-4 text-primary shrink-0" />
          <span>{toastNotification}</span>
        </div>
      )}

      {/* Header Banner */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 bg-surface-container-low p-6 rounded-2xl border border-outline-variant/60 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <h1 className="text-2xl font-bold text-on-surface tracking-tight">Today's Action Plan</h1>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-secondary-container/40 text-secondary text-xs font-mono border border-secondary/30">
              <Zap className="w-3.5 h-3.5 text-secondary" />
              Day {roadmap.currentDay} Execution Matrix
            </span>
          </div>
          <p className="text-sm text-on-surface-variant max-w-2xl">
            Prioritized daily engineering drills synchronized across your DSA accuracy, system architecture, and resume telemetry.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start lg:self-center shrink-0">
          <button
            onClick={() => navigate('/roadmap')}
            className="flex items-center gap-1.5 px-4 py-2 bg-primary text-on-primary hover:bg-primary-fixed-dim text-sm font-semibold rounded-xl transition-all shadow-md"
          >
            <span>View 90-Day Roadmap</span>
            <ArrowUpRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Completion Summary Bar */}
      <div className="p-6 rounded-2xl bg-surface-container-low border border-outline-variant/60 space-y-4 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <span className="text-xs font-mono uppercase text-on-surface-variant tracking-wider block">Today's Progress</span>
            <h3 className="text-lg font-bold text-on-surface">
              {completedCount} of {totalCount} Tasks Completed ({completionPercent}%)
            </h3>
          </div>
          <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-tertiary-container/30 text-tertiary border border-tertiary/30 self-start sm:self-auto">
            Sprint 5 · Day {roadmap.currentDay}
          </span>
        </div>

        <div className="w-full bg-surface-container rounded-full h-3 overflow-hidden border border-outline-variant/40">
          <div
            className="bg-tertiary h-full transition-all duration-500"
            style={{ width: `${completionPercent}%` }}
          ></div>
        </div>

        <div className="flex flex-wrap items-center justify-between text-xs font-mono text-on-surface-variant pt-1">
          <span>Active Tasks: {totalCount - completedCount}</span>
          <span>Target Duration: ~3.5 Hours Total</span>
          <span>Status: {completionPercent === 100 ? 'All Tasks Completed 🎉' : 'In Progress'}</span>
        </div>
      </div>

      {/* Category Filter Pills */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <h3 className="font-semibold text-on-surface text-lg flex items-center gap-2">
            <ListTodo className="w-5 h-5 text-primary" />
            Task Execution Matrix
          </h3>

          <div className="flex flex-wrap items-center gap-1.5 text-xs font-mono">
            {['All', 'DSA', 'System Design', 'Projects', 'Resume', 'LeetCode'].map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`px-3.5 py-1.5 rounded-xl border transition-all ${
                  activeCategory === cat
                    ? 'bg-primary text-on-primary border-primary font-semibold shadow-sm'
                    : 'bg-surface-container text-on-surface-variant border-outline-variant/60 hover:text-on-surface'
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
            <div className="p-8 text-center rounded-2xl bg-surface-container-low border border-dashed border-outline-variant text-on-surface-variant text-xs">
              No tasks found for category "{activeCategory}".
            </div>
          ) : (
            filteredTasks.map((task) => (
              <div
                key={task.id}
                className={`p-4 rounded-2xl border transition-all ${
                  task.completed
                    ? 'bg-surface-container-low/50 border-outline-variant/40 opacity-75'
                    : 'bg-surface-container-low border-outline-variant/60 hover:border-primary/40'
                } flex items-center justify-between gap-4 shadow-sm`}
              >
                <div className="flex items-start gap-3.5 flex-1 min-w-0">
                  <button
                    type="button"
                    onClick={() => toggleTaskCompletion(task.id)}
                    className="mt-0.5 shrink-0 text-on-surface-variant hover:text-primary transition-colors"
                  >
                    <CheckCircle2
                      className={`w-5 h-5 ${
                        task.completed ? 'text-tertiary fill-tertiary/20' : 'text-outline'
                      }`}
                    />
                  </button>

                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                      <span className="text-[10px] font-mono uppercase font-semibold px-2 py-0.5 rounded bg-primary-container/20 text-primary border border-primary/30">
                        {task.category}
                      </span>
                      <span className="text-[10px] font-mono text-on-surface-variant flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5" /> {task.duration}
                      </span>
                      <span
                        className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded font-bold ${
                          task.priority === 'High'
                            ? 'bg-secondary-container/30 text-secondary'
                            : 'bg-surface-container-high text-on-surface-variant'
                        }`}
                      >
                        {task.priority} Priority
                      </span>
                    </div>

                    <p className={`text-sm font-semibold ${task.completed ? 'line-through text-on-surface-variant' : 'text-on-surface'}`}>
                      {task.title}
                    </p>

                    {task.description && (
                      <p className="text-xs text-on-surface-variant mt-1 leading-relaxed">{task.description}</p>
                    )}
                  </div>
                </div>

                <button
                  onClick={() => navigate(task.route)}
                  className="p-2.5 rounded-xl bg-surface-container text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high border border-outline-variant/50 transition-colors shrink-0"
                  title="Open Module Page"
                >
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* AI Advice Banner */}
      <div className="p-6 rounded-2xl bg-surface-container-low border border-outline-variant/60 space-y-4 shadow-sm">
        <h3 className="font-semibold text-on-surface text-base flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-secondary" />
          Copilot Execution Advice
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-surface-container border border-outline-variant/50 space-y-2">
            <h4 className="font-semibold text-sm text-on-surface">Track Completion Analytics</h4>
            <p className="text-xs text-on-surface-variant leading-relaxed">
              Every completed task automatically updates your active 24-day streak and overall readiness progress.
            </p>
            <button
              onClick={() => navigate('/progress')}
              className="text-xs font-semibold text-primary hover:underline inline-flex items-center gap-1 pt-1"
            >
              <span>View Progress Telemetry</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="p-4 rounded-xl bg-surface-container border border-outline-variant/50 space-y-2">
            <h4 className="font-semibold text-sm text-on-surface">Review 90-Day Curriculum</h4>
            <p className="text-xs text-on-surface-variant leading-relaxed">
              Inspect upcoming Day 35–40 milestones in Sprint 5 of your adaptive roadmap.
            </p>
            <button
              onClick={() => navigate('/roadmap')}
              className="text-xs font-semibold text-primary hover:underline inline-flex items-center gap-1 pt-1"
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
