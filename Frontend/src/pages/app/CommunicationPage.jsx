import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { defaultCommunicationPrompts, getStoredCommunicationHistory, saveCommunicationHistory } from '../../data/communicationData';
import { aiService } from '../../services/aiService';
import {
  Zap,
  Mic,
  MessageSquare,
  Sparkles,
  ArrowUpRight,
  History,
  Send,
  CheckCircle2,
  AlertCircle,
  Volume2,
  TrendingUp,
  RotateCcw,
  Activity
} from 'lucide-react';

export const CommunicationPage = () => {
  const navigate = useNavigate();
  const [prompts, setPrompts] = useState(defaultCommunicationPrompts);
  const [activePromptIdx, setActivePromptIdx] = useState(0);
  const [responseText, setResponseText] = useState('');
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [evalResult, setEvalResult] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    setHistory(getStoredCommunicationHistory());
  }, []);

  const currentPrompt = prompts[activePromptIdx] || prompts[0];
  const wordCount = responseText.trim() ? responseText.trim().split(/\s+/).length : 0;

  const handleEvaluate = async () => {
    if (!responseText.trim()) return;
    setIsEvaluating(true);

    const evaluation = await aiService.evaluateCommunicationResponse(currentPrompt, responseText);
    setEvalResult(evaluation);
    setIsEvaluating(false);

    // Add to history
    const newRecord = {
      id: `comm-${Date.now()}`,
      date: 'Just now',
      title: currentPrompt.title,
      score: evaluation.overallScore,
      verbalClarity: evaluation.verbalClarity,
      wpm: evaluation.wpm,
      pitchStability: evaluation.pitchStability,
      fillerWordsCount: evaluation.fillerWordsCount,
      feedback: evaluation.feedback
    };

    const updatedHistory = [newRecord, ...history];
    setHistory(updatedHistory);
    saveCommunicationHistory(updatedHistory);
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 bg-gradient-to-r from-indigo-950/60 via-purple-950/40 to-[#121624] p-6 rounded-2xl border border-indigo-500/30 shadow-xl backdrop-blur-md">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">Communication Readiness Lab</h1>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 text-xs font-mono border border-cyan-500/30">
              <Zap className="w-3.5 h-3.5 text-cyan-400" />
              TELEMETRY V4.2 · SPEECH & ARTICULATION ENGINE
            </span>
          </div>
          <p className="text-sm text-slate-300 max-w-2xl">
            Calibrate speaking pace (WPM), technical vocabulary density, verbal clarity, and filler word frequency for Tier-1 engineering interviews.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start lg:self-center shrink-0">
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-500/10 text-emerald-400 text-xs font-mono border border-emerald-500/30">
            <Mic className="w-4 h-4 text-emerald-400" />
            AI Coach Active
          </span>
          <button
            onClick={() => navigate('/mock-interview')}
            className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-sm font-semibold rounded-xl transition-all shadow-md shadow-indigo-600/25"
          >
            <span>Practice Mock Interview</span>
            <ArrowUpRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Communication Score Hero Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Readiness Score Card */}
        <div className="bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-6 flex flex-col justify-between shadow-lg">
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-mono uppercase tracking-wider text-slate-400">Diagnostic Matrix</span>
              <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-purple-500/10 text-purple-400 border border-purple-500/30">
                +7% vs Day 1
              </span>
            </div>

            <div className="py-4 text-center">
              <div className="inline-flex flex-col items-center justify-center w-36 h-36 rounded-full border-4 border-purple-500/30 bg-[#0b0e17] shadow-[0_0_24px_rgba(168,85,247,0.25)]">
                <span className="text-4xl font-black text-white tracking-tight">78</span>
                <span className="text-[11px] font-mono text-purple-400 font-semibold">/ 100 Index</span>
              </div>
            </div>

            <div className="text-center space-y-1">
              <p className="text-sm font-semibold text-white">Good Technical Articulation</p>
              <p className="text-xs text-slate-400">Optimal interview cadence (140-150 WPM)</p>
            </div>
          </div>

          <div className="pt-4 border-t border-[#232b3e] flex items-center justify-between text-xs font-mono">
            <span className="text-slate-400 font-medium">Engine Telemetry</span>
            <span className="text-emerald-400 font-bold">Speech Verified</span>
          </div>
        </div>

        {/* 4 Diagnostic Metrics Grid */}
        <div className="lg:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Metric 1: Verbal Clarity */}
          <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] space-y-2 shadow-lg">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono uppercase text-slate-400">Verbal Clarity</span>
              <span className="text-xs font-mono font-bold text-emerald-400">82% Score</span>
            </div>
            <span className="text-2xl font-bold text-white">High Precision</span>
            <p className="text-xs text-slate-400">Clear structural transitions between points</p>
          </div>

          {/* Metric 2: Speaking Pace */}
          <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] space-y-2 shadow-lg">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono uppercase text-slate-400">Speaking Pace</span>
              <span className="text-xs font-mono font-bold text-indigo-400">145 WPM</span>
            </div>
            <span className="text-2xl font-bold text-white">Optimal Cadence</span>
            <p className="text-xs text-slate-400">Ideal target range: 140–150 WPM</p>
          </div>

          {/* Metric 3: Pitch Stability */}
          <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] space-y-2 shadow-lg">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono uppercase text-slate-400">Pitch Stability</span>
              <span className="text-xs font-mono font-bold text-purple-400">74% Score</span>
            </div>
            <span className="text-2xl font-bold text-white">Confident Tone</span>
            <p className="text-xs text-slate-400">Steady pitch modulation during STAR narrative</p>
          </div>

          {/* Metric 4: Filler Words */}
          <div className="p-5 bg-[#121624] rounded-2xl border border-[#232b3e] space-y-2 shadow-lg">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono uppercase text-slate-400">Filler Words Frequency</span>
              <span className="text-xs font-mono font-bold text-amber-400">2 / min</span>
            </div>
            <span className="text-2xl font-bold text-white">Low Frequency</span>
            <p className="text-xs text-slate-400">Target: &lt; 3 filler words per minute</p>
          </div>
        </div>
      </div>

      {/* Interactive Practice Prompt Studio */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-white text-lg flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-indigo-400" />
            Articulation Practice Prompts
          </h3>
          <span className="text-xs font-mono text-slate-400">Select Prompt Category</span>
        </div>

        {/* Prompt Selection Tabs */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 border-b border-[#232b3e]">
          {prompts.map((p, idx) => (
            <button
              key={p.id}
              onClick={() => {
                setActivePromptIdx(idx);
                setResponseText('');
                setEvalResult(null);
              }}
              className={`px-4 py-2 rounded-xl text-xs font-mono font-semibold transition-all whitespace-nowrap ${
                activePromptIdx === idx
                  ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-md'
                  : 'bg-[#1a2133] text-slate-400 hover:text-white hover:bg-[#232b3e] border border-[#232b3e]'
              }`}
            >
              {p.title}
            </button>
          ))}
        </div>

        {/* Active Prompt Card & Input Studio */}
        <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-lg">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-[#232b3e]">
            <span className="text-xs font-mono uppercase font-semibold text-purple-400">
              Category: {currentPrompt.category}
            </span>
            <span className="text-xs font-mono text-slate-400">Target Pace: {currentPrompt.targetWpm} WPM</span>
          </div>

          <h4 className="text-base font-bold text-white leading-relaxed">{currentPrompt.promptText}</h4>

          <div className="space-y-2">
            <span className="text-xs font-mono uppercase text-slate-400 block">Suggested Keywords to Include:</span>
            <div className="flex flex-wrap gap-1.5">
              {currentPrompt.suggestedKeywords.map((kw, idx) => (
                <span key={idx} className="px-2.5 py-0.5 rounded bg-[#1a2133] text-indigo-300 text-xs font-mono border border-indigo-500/20">
                  {kw}
                </span>
              ))}
            </div>
          </div>

          <div className="space-y-2 pt-2">
            <div className="flex items-center justify-between text-xs font-mono text-slate-400">
              <span>Type your response or speech transcription below:</span>
              <span>Word Count: {wordCount} words</span>
            </div>
            <textarea
              rows="6"
              value={responseText}
              onChange={(e) => setResponseText(e.target.value)}
              placeholder="Structure your response clearly with STAR or technical breakdown..."
              className="w-full p-4 rounded-xl bg-[#0b0e17] border border-[#232b3e] text-white focus:outline-none focus:border-indigo-500 transition-colors resize-none font-sans leading-relaxed"
            ></textarea>
          </div>

          <div className="flex items-center justify-end gap-3 pt-3 border-t border-[#232b3e]">
            <button
              onClick={handleEvaluate}
              disabled={!responseText.trim() || isEvaluating}
              className="px-6 py-2.5 rounded-xl text-sm font-semibold bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white transition-all shadow-md shadow-indigo-600/25 disabled:opacity-50 flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
              <span>{isEvaluating ? 'Analyzing Speech...' : 'Analyze Articulation'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Evaluation Results Card */}
      {evalResult && (
        <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-6 shadow-lg animate-in fade-in">
          <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-purple-400" />
              AI Articulation Diagnostic Evaluation
            </h3>
            <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              Overall Score: {evalResult.overallScore}/100
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs font-mono">
            <div className="p-3.5 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-1">
              <span className="text-slate-400 block">Verbal Clarity</span>
              <span className="text-xl font-bold text-white">{evalResult.verbalClarity}%</span>
            </div>
            <div className="p-3.5 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-1">
              <span className="text-slate-400 block">Speaking Pace</span>
              <span className="text-xl font-bold text-white">{evalResult.wpm} WPM</span>
            </div>
            <div className="p-3.5 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-1">
              <span className="text-slate-400 block">Pitch Stability</span>
              <span className="text-xl font-bold text-white">{evalResult.pitchStability}%</span>
            </div>
            <div className="p-3.5 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-1">
              <span className="text-slate-400 block">Filler Words</span>
              <span className="text-xl font-bold text-amber-400">{evalResult.fillerWordsCount} detected</span>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-xs text-slate-200 font-sans space-y-1">
            <span className="font-semibold text-indigo-400 font-mono block">Coaching Rationale:</span>
            <p>{evalResult.feedback}</p>
          </div>
        </div>
      )}

      {/* Practice History List */}
      <div className="bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-lg">
        <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
          <h3 className="font-semibold text-white text-base flex items-center gap-2">
            <History className="w-5 h-5 text-indigo-400" />
            Communication Practice History
          </h3>
          <span className="text-xs font-mono text-slate-400">{history.length} Saved Sessions</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse font-mono text-xs">
            <thead>
              <tr className="border-b border-[#232b3e] text-[11px] uppercase text-slate-400">
                <th className="py-2.5 px-3">Date</th>
                <th className="py-2.5 px-3">Prompt Title</th>
                <th className="py-2.5 px-3">Verbal Clarity</th>
                <th className="py-2.5 px-3">Pace (WPM)</th>
                <th className="py-2.5 px-3">Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1e2638]">
              {history.map((item) => (
                <tr key={item.id} className="hover:bg-[#1a2133] transition-colors">
                  <td className="py-3 px-3 font-semibold text-white">{item.date}</td>
                  <td className="py-3 px-3 text-slate-300">{item.title}</td>
                  <td className="py-3 px-3 text-emerald-400">{item.verbalClarity}%</td>
                  <td className="py-3 px-3 text-slate-400">{item.wpm} WPM</td>
                  <td className="py-3 px-3 font-bold text-emerald-400">{item.score}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
