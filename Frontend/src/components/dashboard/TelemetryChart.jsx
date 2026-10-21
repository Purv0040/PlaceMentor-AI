import React, { useState, useMemo } from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';
import { LineChart, Calendar, AlertCircle } from 'lucide-react';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="p-3 rounded-xl bg-[#0f131d] border border-[#232b3e] shadow-2xl text-xs space-y-1.5 min-w-[160px]">
        <div className="flex items-center justify-between gap-2 border-b border-[#232b3e] pb-1.5">
          <span className="font-semibold text-white">{data.name}</span>
          {data.dateRange && (
            <span className="text-[10px] text-slate-400 font-mono">{data.dateRange}</span>
          )}
        </div>
        <div className="flex items-center justify-between text-indigo-400 font-mono">
          <span>Completion:</span>
          <strong>{data.percentage}%</strong>
        </div>
        {typeof data.completed === 'number' && typeof data.total === 'number' && (
          <div className="flex items-center justify-between text-slate-400 text-[11px]">
            <span>Tasks:</span>
            <span className="text-slate-200">{data.completed} / {data.total}</span>
          </div>
        )}
        {data.readiness !== undefined && (
          <div className="flex items-center justify-between text-purple-400 font-mono">
            <span>Readiness:</span>
            <strong>{data.readiness}%</strong>
          </div>
        )}
      </div>
    );
  }
  return null;
};

export const TelemetryChart = ({ progressData, readinessHistory = [], loading = false }) => {
  const [timeRange, setTimeRange] = useState('7D');

  const formatShortDate = (dateStr) => {
    if (!dateStr) return '';
    try {
      const parts = dateStr.slice(0, 10).split('-');
      if (parts.length === 3) {
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const m = parseInt(parts[1], 10) - 1;
        const d = parseInt(parts[2], 10);
        return `${monthNames[m]} ${d}`;
      }
      return dateStr.slice(5);
    } catch {
      return dateStr;
    }
  };

  const chartData = useMemo(() => {
    if (!progressData) return [];

    const daily = Array.isArray(progressData.daily_completion) ? progressData.daily_completion : [];
    const weekly = Array.isArray(progressData.weekly_completion) ? progressData.weekly_completion : [];

    if (timeRange === '7D') {
      // Last 7 days from daily_completion or available slice
      const slice7 = daily.slice(0, 7);
      return slice7.map((item) => ({
        name: formatShortDate(item.date),
        date: item.date,
        completed: item.completed || 0,
        total: item.total || 0,
        percentage: Math.round(item.percentage || 0),
      }));
    }

    if (timeRange === '30D') {
      // Up to 30 days from daily_completion
      const slice30 = daily.slice(0, 30);
      return slice30.map((item) => ({
        name: formatShortDate(item.date),
        date: item.date,
        completed: item.completed || 0,
        total: item.total || 0,
        percentage: Math.round(item.percentage || 0),
      }));
    }

    if (timeRange === '90D') {
      // Roadmap weekly completion breakdown
      return weekly.map((item) => ({
        name: `W${item.week}`,
        dateRange: `${formatShortDate(item.start_date)} - ${formatShortDate(item.end_date)}`,
        completed: item.completed || 0,
        total: item.total || 0,
        percentage: Math.round(item.percentage || 0),
      }));
    }

    return [];
  }, [progressData, timeRange]);

  const hasData = chartData && chartData.length > 0;

  return (
    <div className="w-full flex flex-col justify-between h-full">
      {/* Range Filter Controls */}
      <div className="flex items-center justify-between gap-2 mb-3">
        <span className="text-xs text-slate-400 flex items-center gap-1.5 font-medium">
          <Calendar className="w-3.5 h-3.5 text-indigo-400" />
          <span>Timeline View</span>
        </span>
        <div className="inline-flex items-center p-0.5 rounded-lg bg-[#0f131d] border border-[#232b3e] text-[11px]">
          <button
            type="button"
            onClick={() => setTimeRange('7D')}
            className={`px-2 py-0.5 rounded-md transition-colors ${
              timeRange === '7D'
                ? 'bg-indigo-600 text-white font-semibold'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            7 Days
          </button>
          <button
            type="button"
            onClick={() => setTimeRange('30D')}
            className={`px-2 py-0.5 rounded-md transition-colors ${
              timeRange === '30D'
                ? 'bg-indigo-600 text-white font-semibold'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            30 Days
          </button>
          <button
            type="button"
            onClick={() => setTimeRange('90D')}
            className={`px-2 py-0.5 rounded-md transition-colors ${
              timeRange === '90D'
                ? 'bg-indigo-600 text-white font-semibold'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Roadmap Weeks
          </button>
        </div>
      </div>

      {/* Chart Canvas or Empty State */}
      {loading ? (
        <div className="h-44 w-full flex items-center justify-center bg-[#0f131d]/40 rounded-xl border border-[#232b3e] animate-pulse">
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <LineChart className="w-4 h-4 animate-spin text-indigo-400" />
            <span>Loading telemetry...</span>
          </div>
        </div>
      ) : hasData ? (
        <div className="w-full h-44 sm:h-48 pt-1">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 8, right: 8, left: -22, bottom: 0 }}>
              <defs>
                <linearGradient id="dashboardProgressGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.45} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0.0} />
                </linearGradient>
              </defs>

              <CartesianGrid strokeDasharray="3 3" stroke="#1f2738" vertical={false} />
              <XAxis
                dataKey="name"
                stroke="#64748b"
                tick={{ fontSize: 10 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                stroke="#64748b"
                tick={{ fontSize: 10 }}
                domain={[0, 100]}
                ticks={[0, 25, 50, 75, 100]}
                unit="%"
                axisLine={false}
                tickLine={false}
              />
              <Tooltip content={<CustomTooltip />} />

              <Area
                type="monotone"
                dataKey="percentage"
                stroke="#6366f1"
                strokeWidth={2.5}
                fillOpacity={1}
                fill="url(#dashboardProgressGrad)"
                dot={{ r: 3, fill: '#6366f1', strokeWidth: 0 }}
                activeDot={{ r: 5, fill: '#818cf8', stroke: '#121624', strokeWidth: 2 }}
                name="Task Completion"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="h-44 w-full flex flex-col items-center justify-center text-center p-4 rounded-xl bg-[#0f131d]/50 border border-dashed border-[#232b3e]">
          <AlertCircle className="w-6 h-6 text-slate-600 mb-1.5" />
          <p className="text-xs font-semibold text-slate-300">No activity history recorded</p>
          <p className="text-[11px] text-slate-500 mt-0.5 max-w-xs">
            Complete daily roadmap tasks to view live progress telemetry and sprint momentum.
          </p>
        </div>
      )}

      {/* Footer Subtext */}
      <div className="mt-3 pt-2.5 border-t border-[#232b3e]/60 flex items-center justify-between text-[11px] text-slate-400">
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-indigo-500" />
          <span>Real task completion from saved roadmap</span>
        </span>
        <span className="font-mono text-slate-400">
          {progressData?.completion_percentage != null
            ? `${progressData.completion_percentage}% Total`
            : ''}
        </span>
      </div>
    </div>
  );
};
