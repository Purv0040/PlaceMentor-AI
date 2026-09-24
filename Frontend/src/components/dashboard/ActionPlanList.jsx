import React from 'react';
import { NavLink } from 'react-router-dom';
import { CheckCircle2, Clock, ArrowRight } from 'lucide-react';
import { usePlanning } from '../../context/PlanningContext';

export const ActionPlanList = () => {
  const { tasks, toggleTaskCompletion } = usePlanning();

  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <div
          key={task.id}
          className={`p-3.5 rounded-xl border transition-all ${
            task.completed
              ? 'bg-[#0f131d]/60 border-[#232b3e]/60 opacity-60'
              : 'bg-[#0f131d] border-[#232b3e] hover:border-indigo-500/40'
          } flex items-center justify-between gap-3`}
        >
          <div className="flex items-start gap-3 flex-1 min-w-0">
            <button
              type="button"
              onClick={() => toggleTaskCompletion(task.id)}
              className="mt-0.5 shrink-0 text-slate-500 hover:text-indigo-400 transition-colors"
              aria-label={`Toggle task completion: ${task.title}`}
            >
              <CheckCircle2
                className={`w-4 h-4 ${task.completed ? 'text-emerald-400 fill-emerald-400/20' : 'text-slate-600'}`}
              />
            </button>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2 mb-0.5">
                <span className="text-[10px] font-mono uppercase font-semibold px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-400">
                  {task.category}
                </span>
                <span className="text-[10px] text-slate-500 flex items-center gap-1 font-mono">
                  <Clock className="w-3 h-3" /> {task.duration}
                </span>
              </div>
              <p className={`text-xs font-semibold ${task.completed ? 'line-through text-slate-500' : 'text-slate-200'}`}>
                {task.title}
              </p>
            </div>
          </div>

          <NavLink
            to={task.route}
            className="p-1.5 rounded-lg bg-[#121624] border border-[#232b3e] text-slate-400 hover:text-white hover:border-slate-700 transition-colors shrink-0"
            title="Start Drill"
          >
            <ArrowRight className="w-3.5 h-3.5" />
          </NavLink>
        </div>
      ))}
    </div>
  );
};
