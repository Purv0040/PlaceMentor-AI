import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';
import { dashboardData } from '../../data/dashboardData';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="p-3 rounded-xl bg-[#121624] border border-[#232b3e] shadow-xl text-xs space-y-1">
        <p className="font-bold text-white">{label} Telemetry Baseline</p>
        <p className="text-indigo-400 font-mono">Overall Readiness: {payload[0].value}%</p>
        <p className="text-purple-400 font-mono">DSA Accuracy: {payload[1].value}%</p>
        <p className="text-emerald-400 font-mono">System Design: {payload[2].value}%</p>
      </div>
    );
  }
  return null;
};

export const TelemetryChart = () => {
  return (
    <div className="w-full h-64 sm:h-72">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={dashboardData.weeklyTelemetryCurve} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="colorReadiness" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
              <stop offset="95%" stopColor="#6366f1" stopOpacity={0.0} />
            </linearGradient>
            <linearGradient id="colorDsa" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#a855f7" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#a855f7" stopOpacity={0.0} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="#232b3e" vertical={false} />
          <XAxis dataKey="week" stroke="#908fa0" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis stroke="#908fa0" tick={{ fontSize: 11 }} domain={[40, 100]} axisLine={false} tickLine={false} />
          <Tooltip content={<CustomTooltip />} />

          <Area
            type="monotone"
            dataKey="readiness"
            stroke="#6366f1"
            strokeWidth={3}
            fillOpacity={1}
            fill="url(#colorReadiness)"
            name="Readiness Score"
          />
          <Area
            type="monotone"
            dataKey="dsa"
            stroke="#a855f7"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorDsa)"
            name="DSA Accuracy"
          />
          <Area
            type="monotone"
            dataKey="sysDesign"
            stroke="#10b981"
            strokeWidth={2}
            strokeDasharray="4 4"
            fill="none"
            name="System Design"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};
