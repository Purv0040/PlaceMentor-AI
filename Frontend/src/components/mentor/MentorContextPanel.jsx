import React from 'react';
import { useNavigate } from 'react-router-dom';

export const MentorContextPanel = ({ mentorContext, tasks = [], onToggleTask }) => {
  const navigate = useNavigate();

  // Active problem from context or fallback to active LC submission
  const activeProblem = {
    title: "Course Schedule II",
    number: "#210",
    difficulty: "Medium",
    topic: "Graphs / Topological Sort",
    patterns: ["Topological Sort", "Kahn's BFS", "DAG Verification"],
    timeComplexity: "O(V + E)",
    spaceComplexity: "O(V + E)",
    score: "94%"
  };

  // Today's pending tasks: dynamic from planning state or mentorContext
  const displayTasks = (tasks && tasks.length > 0)
    ? tasks.slice(0, 3)
    : (mentorContext?.todayTasks?.pendingTaskList || []).slice(0, 3);

  const pendingCount = (tasks && tasks.length > 0)
    ? tasks.filter(t => !t.completed && t.status !== 'completed').length
    : (mentorContext?.todayTasks?.remaining ?? 2);

  return (
    <aside className="xl:col-span-4 flex flex-col gap-4">
      {/* 1. Active Problem & Submission Feedback (Combined Compact Card) */}
      <div className="flex flex-col p-4 rounded-2xl bg-[#141824] border border-[#232838] shadow-md gap-3">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-purple-400 text-lg">code_blocks</span>
            <span className="text-xs font-semibold text-white">Active Problem</span>
          </div>
          <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-[10px] font-mono font-semibold border border-emerald-500/20">
            {activeProblem.difficulty} {activeProblem.number}
          </span>
        </div>

        {/* Problem Title & Patterns */}
        <div>
          <h3 className="text-sm font-bold text-white">{activeProblem.title}</h3>
          <div className="flex flex-wrap gap-1.5 mt-2">
            {activeProblem.patterns.map((ptn, idx) => (
              <span
                key={idx}
                className="px-2 py-0.5 rounded-md bg-[#191e2e] text-slate-300 text-[10px] font-mono border border-[#252b3d]"
              >
                {ptn}
              </span>
            ))}
          </div>
        </div>

        {/* Compact Submission Telemetry */}
        <div className="pt-2.5 border-t border-[#1f2433] flex flex-col gap-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400 text-[11px] font-medium flex items-center gap-1">
              <span className="material-symbols-outlined text-sm text-indigo-400">speed</span>
              Complexity &amp; Quality
            </span>
            <span className="text-[10px] font-mono text-purple-300 font-bold px-1.5 py-0.5 rounded bg-purple-500/10 border border-purple-500/20">
              {activeProblem.score} Score
            </span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-center text-xs">
            <div className="px-2.5 py-1.5 rounded-lg bg-[#191e2e] border border-[#252b3d]">
              <span className="text-[10px] text-slate-400 block font-mono">Time Complexity</span>
              <span className="text-xs font-semibold font-mono text-emerald-400">{activeProblem.timeComplexity}</span>
            </div>
            <div className="px-2.5 py-1.5 rounded-lg bg-[#191e2e] border border-[#252b3d]">
              <span className="text-[10px] text-slate-400 block font-mono">Space Complexity</span>
              <span className="text-xs font-semibold font-mono text-purple-300">{activeProblem.spaceComplexity}</span>
            </div>
          </div>

          {/* Quick checks */}
          <div className="flex items-center justify-between text-[11px] text-slate-300 px-0.5 pt-1">
            <span className="flex items-center gap-1 text-emerald-400">
              <span className="material-symbols-outlined text-xs">check_circle</span>
              Cycle Check: PASS
            </span>
            <span className="flex items-center gap-1 text-emerald-400">
              <span className="material-symbols-outlined text-xs">check_circle</span>
              Graph In-degree: PASS
            </span>
          </div>
        </div>
      </div>

      {/* 2. Today's Tasks (Dynamic & Interactive Card) */}
      <div className="flex flex-col p-4 rounded-2xl bg-[#141824] border border-[#232838] shadow-md gap-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-purple-400 text-lg">checklist</span>
            <span className="text-xs font-semibold text-white">Today's Tasks</span>
          </div>
          <span className="px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-300 text-[10px] font-mono font-medium border border-purple-500/20">
            {pendingCount} Pending
          </span>
        </div>

        {/* Tasks List */}
        <div className="flex flex-col gap-2">
          {displayTasks.length > 0 ? (
            displayTasks.map((task) => {
              const isDone = task.completed || task.status === 'completed';
              return (
                <div
                  key={task.id}
                  onClick={() => onToggleTask && onToggleTask(task.id)}
                  className={`flex items-start gap-2.5 p-2 rounded-xl border transition-all cursor-pointer ${
                    isDone
                      ? 'bg-[#121622]/50 border-[#1f2433] opacity-60'
                      : 'bg-[#191e2e] hover:bg-[#1f2538] border-[#252b3d]'
                  }`}
                >
                  <button
                    type="button"
                    className={`mt-0.5 w-4 h-4 rounded border flex items-center justify-center shrink-0 transition-colors ${
                      isDone
                        ? 'bg-purple-600 border-purple-500 text-white'
                        : 'border-slate-500 hover:border-purple-400'
                    }`}
                  >
                    {isDone && <span className="material-symbols-outlined text-xs">check</span>}
                  </button>

                  <div className="flex flex-col min-w-0 flex-1">
                    <span
                      className={`text-xs font-medium truncate ${
                        isDone ? 'line-through text-slate-500' : 'text-slate-200'
                      }`}
                      title={task.title}
                    >
                      {task.title}
                    </span>
                    <div className="flex items-center gap-2 mt-0.5 text-[10px] text-slate-400 font-mono">
                      {task.category && (
                        <span className="text-purple-300">{task.category}</span>
                      )}
                      {task.duration && (
                        <>
                          <span>•</span>
                          <span>{task.duration}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="p-3 text-center text-xs text-slate-400 bg-[#191e2e] rounded-xl border border-[#252b3d]">
              All scheduled tasks completed for today!
            </div>
          )}
        </div>

        {/* Bottom Link to Full Tasks */}
        <button
          type="button"
          onClick={() => navigate('/tasks')}
          className="text-center text-[11px] font-medium text-purple-400 hover:text-purple-300 transition-colors pt-1"
        >
          Manage All Tasks &rarr;
        </button>
      </div>

      {/* 3. Useful Quick Actions (Compact Pill Bar) */}
      <div className="flex flex-col p-3 rounded-2xl bg-[#141824] border border-[#232838] shadow-md gap-2">
        <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 px-1">
          Quick Actions
        </span>
        <div className="grid grid-cols-3 gap-1.5">
          <button
            type="button"
            onClick={() => navigate('/roadmap')}
            className="flex flex-col items-center justify-center p-2 rounded-xl bg-[#191e2e] hover:bg-purple-600/15 hover:border-purple-500/30 text-slate-300 hover:text-white border border-[#252b3d] transition-all text-center gap-1 group"
          >
            <span className="material-symbols-outlined text-base text-purple-400 group-hover:scale-110 transition-transform">
              route
            </span>
            <span className="text-[11px] font-medium leading-tight">Roadmap</span>
          </button>

          <button
            type="button"
            onClick={() => navigate('/skill-gaps')}
            className="flex flex-col items-center justify-center p-2 rounded-xl bg-[#191e2e] hover:bg-purple-600/15 hover:border-purple-500/30 text-slate-300 hover:text-white border border-[#252b3d] transition-all text-center gap-1 group"
          >
            <span className="material-symbols-outlined text-base text-indigo-400 group-hover:scale-110 transition-transform">
              radar
            </span>
            <span className="text-[11px] font-medium leading-tight">Skill Gaps</span>
          </button>

          <button
            type="button"
            onClick={() => navigate('/mock-interview')}
            className="flex flex-col items-center justify-center p-2 rounded-xl bg-[#191e2e] hover:bg-purple-600/15 hover:border-purple-500/30 text-slate-300 hover:text-white border border-[#252b3d] transition-all text-center gap-1 group"
          >
            <span className="material-symbols-outlined text-base text-emerald-400 group-hover:scale-110 transition-transform">
              videocam
            </span>
            <span className="text-[11px] font-medium leading-tight">Mock Interview</span>
          </button>
        </div>
      </div>
    </aside>
  );
};
