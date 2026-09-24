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
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 bg-surface-container-low p-6 rounded-2xl border border-outline-variant/60 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <h1 className="text-2xl font-bold text-on-surface tracking-tight">Communication Readiness Lab</h1>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-secondary-container/40 text-secondary text-xs font-mono border border-secondary/30">
              <Zap className="w-3.5 h-3.5 text-secondary" />
              TELEMETRY V4.2 · SPEECH & ARTICULATION ENGINE
            </span>
          </div>
          <p className="text-sm text-on-surface-variant max-w-2xl">
            Calibrate speaking pace (WPM), technical vocabulary density, verbal clarity, and filler word frequency for Tier-1 engineering interviews.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start lg:self-center shrink-0">
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-tertiary-container/20 text-tertiary text-xs font-mono border border-tertiary/30">
            <Mic className="w-4 h-4 text-tertiary" />
            AI Coach Active
          </span>
          <button
            onClick={() => navigate('/mock-interview')}
            className="flex items-center gap-1.5 px-4 py-2 bg-primary text-on-primary hover:bg-primary-fixed-dim text-sm font-semibold rounded-xl transition-all shadow-md"
          >
            <span>Practice Mock Interview</span>
            <ArrowUpRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Communication Score Hero Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Readiness Score Card */}
        <div className="bg-surface-container-low p-6 rounded-2xl border border-outline-variant/60 space-y-6 flex flex-col justify-between shadow-sm">
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-mono uppercase tracking-wider text-on-surface-variant">Diagnostic Matrix</span>
              <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-secondary-container/40 text-secondary border border-secondary/30">
                +7% vs Day 1
              </span>
            </div>

            <div className="py-4 text-center">
              <div className="inline-flex flex-col items-center justify-center w-36 h-36 rounded-full border-4 border-secondary/30 bg-surface-container/60 shadow-[0_0_24px_rgba(221,183,255,0.2)]">
                <span className="text-4xl font-black text-on-surface tracking-tight">78</span>
                <span className="text-[11px] font-mono text-secondary font-semibold">/ 100 Index</span>
              </div>
            </div>

            <div className="text-center space-y-1">
              <p className="text-sm font-semibold text-on-surface">Good Technical Articulation</p>
              <p className="text-xs text-on-surface-variant">Optimal interview cadence (140-150 WPM)</p>
            </div>
          </div>

          <div className="pt-4 border-t border-outline-variant/50 flex items-center justify-between text-xs font-mono">
            <span className="text-on-surface-variant font-medium">Engine Telemetry</span>
            <span className="text-tertiary font-bold">Speech Verified</span>
          </div>
        </div>

        {/* 4 Diagnostic Metrics Grid */}
        <div className="lg:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Metric 1: Verbal Clarity */}
          <div className="p-5 bg-surface-container-low rounded-2xl border border-outline-variant/60 space-y-2 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono uppercase text-on-surface-variant">Verbal Clarity</span>
              <span className="text-xs font-mono font-bold text-tertiary">82% Score</span>
            </div>
            <span className="text-2xl font-bold text-on-surface">High Precision</span>
            <p className="text-xs text-on-surface-variant">Clear structural transitions between points</p>
          </div>

          {/* Metric 2: Speaking Pace */}
          <div className="p-5 bg-surface-container-low rounded-2xl border border-outline-variant/60 space-y-2 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono uppercase text-on-surface-variant">Speaking Pace</span>
              <span className="text-xs font-mono font-bold text-primary">145 WPM</span>
            </div>
            <span className="text-2xl font-bold text-on-surface">Optimal Cadence</span>
            <p className="text-xs text-on-surface-variant">Ideal target range: 140–150 WPM</p>
          </div>

          {/* Metric 3: Pitch Stability */}
          <div className="p-5 bg-surface-container-low rounded-2xl border border-outline-variant/60 space-y-2 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono uppercase text-on-surface-variant">Pitch Stability</span>
              <span className="text-xs font-mono font-bold text-secondary">74% Score</span>
            </div>
            <span className="text-2xl font-bold text-on-surface">Confident Tone</span>
            <p className="text-xs text-on-surface-variant">Steady pitch modulation during STAR narrative</p>
          </div>

          {/* Metric 4: Filler Words */}
          <div className="p-5 bg-surface-container-low rounded-2xl border border-outline-variant/60 space-y-2 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono uppercase text-on-surface-variant">Filler Words Frequency</span>
              <span className="text-xs font-mono font-bold text-tertiary">2 / min</span>
            </div>
            <span className="text-2xl font-bold text-on-surface">Low Frequency</span>
            <p className="text-xs text-on-surface-variant">Target: &lt; 3 filler words per minute</p>
          </div>
        </div>
      </div>

      {/* Interactive Practice Prompt Studio */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-on-surface text-lg flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-primary" />
            Articulation Practice Prompts
          </h3>
          <span className="text-xs font-mono text-on-surface-variant">Select Prompt Category</span>
        </div>

        {/* Prompt Selection Tabs */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 border-b border-outline-variant/50">
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
                  ? 'bg-primary text-on-primary shadow-sm'
                  : 'bg-surface-container text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high'
              }`}
            >
              {p.title}
            </button>
          ))}
        </div>

        {/* Active Prompt Card & Input Studio */}
        <div className="p-6 rounded-2xl bg-surface-container-low border border-outline-variant/60 space-y-4 shadow-sm">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-outline-variant/40">
            <span className="text-xs font-mono uppercase font-semibold text-secondary">
              Category: {currentPrompt.category}
            </span>
            <span className="text-xs font-mono text-on-surface-variant">Target Pace: {currentPrompt.targetWpm} WPM</span>
          </div>

          <h4 className="text-base font-bold text-on-surface leading-relaxed">{currentPrompt.promptText}</h4>

          <div className="space-y-2">
            <span className="text-xs font-mono uppercase text-on-surface-variant block">Suggested Keywords to Include:</span>
            <div className="flex flex-wrap gap-1.5">
              {currentPrompt.suggestedKeywords.map((kw, idx) => (
                <span key={idx} className="px-2.5 py-0.5 rounded bg-surface-container text-on-surface text-xs font-mono border border-outline-variant/40">
                  {kw}
                </span>
              ))}
            </div>
          </div>

          <div className="space-y-2 pt-2">
            <div className="flex items-center justify-between text-xs font-mono text-on-surface-variant">
              <span>Type your response or speech transcription below:</span>
              <span>Word Count: {wordCount} words</span>
            </div>
            <textarea
              rows="6"
              value={responseText}
              onChange={(e) => setResponseText(e.target.value)}
              placeholder="Structure your response clearly with STAR or technical breakdown..."
              className="w-full p-4 rounded-xl bg-surface-container border border-outline-variant text-on-surface text-sm focus:outline-none focus:border-primary transition-colors resize-none font-sans leading-relaxed"
            ></textarea>
          </div>

          <div className="flex items-center justify-end gap-3 pt-3 border-t border-outline-variant/40">
            <button
              onClick={handleEvaluate}
              disabled={!responseText.trim() || isEvaluating}
              className="px-6 py-2.5 rounded-xl text-sm font-semibold bg-primary text-on-primary hover:bg-primary-fixed-dim transition-all shadow-md disabled:opacity-50 flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
              <span>{isEvaluating ? 'Analyzing Speech...' : 'Analyze Articulation'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Evaluation Results Card */}
      {evalResult && (
        <div className="p-6 rounded-2xl bg-surface-container-low border border-outline-variant/60 space-y-6 shadow-sm animate-in fade-in">
          <div className="flex items-center justify-between pb-3 border-b border-outline-variant/40">
            <h3 className="text-lg font-bold text-on-surface flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-secondary" />
              AI Articulation Diagnostic Evaluation
            </h3>
            <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-tertiary-container/30 text-tertiary border border-tertiary/30">
              Overall Score: {evalResult.overallScore}/100
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs font-mono">
            <div className="p-3.5 rounded-xl bg-surface-container border border-outline-variant/40 space-y-1">
              <span className="text-on-surface-variant block">Verbal Clarity</span>
              <span className="text-xl font-bold text-on-surface">{evalResult.verbalClarity}%</span>
            </div>
            <div className="p-3.5 rounded-xl bg-surface-container border border-outline-variant/40 space-y-1">
              <span className="text-on-surface-variant block">Speaking Pace</span>
              <span className="text-xl font-bold text-on-surface">{evalResult.wpm} WPM</span>
            </div>
            <div className="p-3.5 rounded-xl bg-surface-container border border-outline-variant/40 space-y-1">
              <span className="text-on-surface-variant block">Pitch Stability</span>
              <span className="text-xl font-bold text-on-surface">{evalResult.pitchStability}%</span>
            </div>
            <div className="p-3.5 rounded-xl bg-surface-container border border-outline-variant/40 space-y-1">
              <span className="text-on-surface-variant block">Filler Words</span>
              <span className="text-xl font-bold text-tertiary">{evalResult.fillerWordsCount} detected</span>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-primary-container/10 border border-primary/30 text-xs text-on-surface font-sans space-y-1">
            <span className="font-semibold text-primary font-mono block">Coaching Rationale:</span>
            <p>{evalResult.feedback}</p>
          </div>
        </div>
      )}

      {/* Practice History List */}
      <div className="bg-surface-container-low p-6 rounded-2xl border border-outline-variant/60 space-y-4 shadow-sm">
        <div className="flex items-center justify-between pb-3 border-b border-outline-variant/50">
          <h3 className="font-semibold text-on-surface text-base flex items-center gap-2">
            <History className="w-5 h-5 text-primary" />
            Communication Practice History
          </h3>
          <span className="text-xs font-mono text-on-surface-variant">{history.length} Saved Sessions</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse font-mono text-xs">
            <thead>
              <tr className="border-b border-outline-variant/40 text-[11px] uppercase text-on-surface-variant">
                <th className="py-2.5 px-3">Date</th>
                <th className="py-2.5 px-3">Prompt Title</th>
                <th className="py-2.5 px-3">Verbal Clarity</th>
                <th className="py-2.5 px-3">Pace (WPM)</th>
                <th className="py-2.5 px-3">Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/30">
              {history.map((item) => (
                <tr key={item.id} className="hover:bg-surface-container/50 transition-colors">
                  <td className="py-3 px-3 font-semibold text-on-surface">{item.date}</td>
                  <td className="py-3 px-3 text-on-surface-variant">{item.title}</td>
                  <td className="py-3 px-3 text-tertiary">{item.verbalClarity}%</td>
                  <td className="py-3 px-3 text-on-surface-variant">{item.wpm} WPM</td>
                  <td className="py-3 px-3 font-bold text-tertiary">{item.score}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
