import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { usePlanning } from '../../context/PlanningContext';
import { useUser } from '../../context/UserContext';
import { defaultQuestions, getStoredInterviewHistory, saveInterviewHistory } from '../../data/interviewData';
import { aiService } from '../../services/aiService';
import { InterviewSetupModal } from '../../components/practice/InterviewSetupModal';
import {
  Zap,
  Play,
  Clock,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Sparkles,
  ArrowUpRight,
  History,
  RotateCcw,
  Send,
  Award,
  Layers,
  Sliders,
  Check,
  RefreshCw
} from 'lucide-react';

export const MockInterviewPage = () => {
  const navigate = useNavigate();
  const { user } = useUser();
  const { toggleTaskCompletion, toastNotification } = usePlanning();

  const [sessionState, setSessionState] = useState('idle'); // 'idle' | 'active' | 'evaluating' | 'results'
  const [isSetupOpen, setIsSetupOpen] = useState(false);
  const [sessionConfig, setSessionConfig] = useState(null);
  const [questions, setQuestions] = useState(defaultQuestions);
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);
  const [answerText, setAnswerText] = useState('');
  const [showHint, setShowHint] = useState(false);
  const [secondsElapsed, setSecondsElapsed] = useState(0);
  const [evalResult, setEvalResult] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    setHistory(getStoredInterviewHistory());
  }, []);

  // Timer effect for active session
  useEffect(() => {
    let interval = null;
    if (sessionState === 'active') {
      interval = setInterval(() => {
        setSecondsElapsed((prev) => prev + 1);
      }, 1000);
    } else {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [sessionState]);

  const formatTimer = (totalSeconds) => {
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleStartInterview = (config) => {
    setSessionConfig(config);
    setCurrentQuestionIdx(0);
    setAnswerText('');
    setSecondsElapsed(0);
    setShowHint(false);
    setSessionState('active');
  };

  const handleSubmitAnswer = async () => {
    if (!answerText.trim()) return;
    setSessionState('evaluating');

    const currentQ = questions[currentQuestionIdx];
    const evaluation = await aiService.evaluateInterviewAnswer(currentQ, answerText);
    setEvalResult(evaluation);

    // Add to history
    const newRecord = {
      id: `session-${Date.now()}`,
      date: 'Just now',
      role: sessionConfig?.role || 'Backend SDE-1',
      type: sessionConfig?.modality || 'System Architecture & Design',
      difficulty: sessionConfig?.difficulty || 'Medium',
      questionCount: sessionConfig?.questionCount || 1,
      durationText: formatTimer(secondsElapsed),
      score: evaluation.score,
      status: 'Completed',
      strengths: evaluation.strengths,
      weaknesses: evaluation.weaknesses
    };

    const updatedHistory = [newRecord, ...history];
    setHistory(updatedHistory);
    saveInterviewHistory(updatedHistory);

    setSessionState('results');
  };

  const currentQ = questions[currentQuestionIdx] || questions[0];
  const wordCount = answerText.trim() ? answerText.trim().split(/\s+/).length : 0;

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 bg-gradient-to-r from-indigo-950/60 via-purple-950/40 to-[#121624] p-6 rounded-2xl border border-indigo-500/30 shadow-xl backdrop-blur-md">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">AI Mock Interview Studio</h1>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 text-xs font-mono border border-cyan-500/30">
              <Zap className="w-3.5 h-3.5 text-cyan-400" />
              Telemetry v4.2 · Real-Time Adaptive Engine
            </span>
          </div>
          <p className="text-sm text-slate-300 max-w-2xl">
            Practice realistic multi-stage technical and system design interviews, receive instant AI feedback, and calibrate readiness for Tier-1 companies.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start lg:self-center shrink-0">
          <button
            onClick={() => setIsSetupOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-[#1a2133] hover:bg-[#232b3e] text-white text-sm font-medium rounded-xl border border-[#232b3e] transition-all shadow-sm"
          >
            <Sliders className="w-4 h-4 text-indigo-400" />
            <span>Settings</span>
          </button>
          <button
            onClick={() => setIsSetupOpen(true)}
            className="flex items-center gap-2 px-5 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white rounded-xl font-semibold text-sm transition-all shadow-md shadow-indigo-600/25"
          >
            <Play className="w-4 h-4 fill-white" />
            <span>Start Mock Interview</span>
          </button>
        </div>
      </div>

      {/* IDLE MODE VIEW */}
      {sessionState === 'idle' && (
        <div className="space-y-6">
          {/* Readiness Calibration Score Card */}
          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-lg">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#232b3e]">
              <div>
                <span className="text-xs font-mono uppercase text-amber-400 tracking-wider block">Candidate Interview Calibration</span>
                <h3 className="text-lg font-bold text-white">Target Role: {user?.targetRole || 'Backend SDE-1'}</h3>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 self-start sm:self-auto">
                Calibration Score: 76/100 (+4% vs last week)
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
              <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-1">
                <span className="text-slate-400 block">Technical Accuracy</span>
                <span className="text-xl font-bold text-white">82%</span>
                <span className="text-[11px] text-emerald-400 block pt-0.5">High precision algorithm responses</span>
              </div>

              <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-1">
                <span className="text-slate-400 block">Communication Articulation</span>
                <span className="text-xl font-bold text-white">74%</span>
                <span className="text-[11px] text-amber-400 block pt-0.5">145 WPM optimal cadence</span>
              </div>

              <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-1">
                <span className="text-slate-400 block">STAR Structure Compliance</span>
                <span className="text-xl font-bold text-white">78%</span>
                <span className="text-[11px] text-indigo-400 block pt-0.5">Requires quantified metrics</span>
              </div>
            </div>
          </div>

          {/* Targeted Modalities */}
          <div className="space-y-4">
            <h3 className="font-semibold text-white text-lg">Targeted Interview Modalities</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div
                onClick={() => handleStartInterview({ modality: 'System Architecture & Design', difficulty: 'Hard', questionCount: 3, duration: '20 mins' })}
                className="p-5 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-3 hover:border-indigo-500/50 transition-all cursor-pointer shadow-lg group"
              >
                <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 w-fit">
                  <Layers className="w-5 h-5" />
                </div>
                <h4 className="font-bold text-white text-base group-hover:text-indigo-300 transition-colors">System Architecture & Design</h4>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Scalability, Caching (Redis), Pub-Sub Messaging, CAP theorem, and Database Sharding trade-offs.
                </p>
                <span className="text-xs font-semibold text-indigo-400 group-hover:text-indigo-300 inline-flex items-center gap-1">
                  Launch Architecture Session <ArrowUpRight className="w-3.5 h-3.5" />
                </span>
              </div>

              <div
                onClick={() => handleStartInterview({ modality: 'Technical / DSA Drill', difficulty: 'Medium', questionCount: 3, duration: '15 mins' })}
                className="p-5 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-3 hover:border-emerald-500/50 transition-all cursor-pointer shadow-lg group"
              >
                <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 w-fit">
                  <Zap className="w-5 h-5" />
                </div>
                <h4 className="font-bold text-white text-base group-hover:text-emerald-300 transition-colors">Technical / DSA Drill</h4>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Topological Sort, 2D Dynamic Programming, Tree Traversals, and time/space complexity analysis.
                </p>
                <span className="text-xs font-semibold text-emerald-400 group-hover:text-emerald-300 inline-flex items-center gap-1">
                  Launch DSA Session <ArrowUpRight className="w-3.5 h-3.5" />
                </span>
              </div>

              <div
                onClick={() => handleStartInterview({ modality: 'Behavioral & HR STAR Drill', difficulty: 'Medium', questionCount: 3, duration: '15 mins' })}
                className="p-5 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-3 hover:border-purple-500/50 transition-all cursor-pointer shadow-lg group"
              >
                <div className="p-2.5 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20 w-fit">
                  <Sparkles className="w-5 h-5" />
                </div>
                <h4 className="font-bold text-white text-base group-hover:text-purple-300 transition-colors">Behavioral STAR Drill</h4>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Leadership principles, conflict resolution, technical disagreement, and project evidence.
                </p>
                <span className="text-xs font-semibold text-purple-400 group-hover:text-purple-300 inline-flex items-center gap-1">
                  Launch Behavioral Session <ArrowUpRight className="w-3.5 h-3.5" />
                </span>
              </div>
            </div>
          </div>

          {/* Interview Session History */}
          <div className="bg-[#121624] p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-lg">
            <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
              <h3 className="font-semibold text-white text-base flex items-center gap-2">
                <History className="w-5 h-5 text-indigo-400" />
                Interview Practice History
              </h3>
              <span className="text-xs font-mono text-slate-400">{history.length} Saved Sessions</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse font-mono text-xs">
                <thead>
                  <tr className="border-b border-[#232b3e] text-[11px] uppercase text-slate-400">
                    <th className="py-2.5 px-3">Date</th>
                    <th className="py-2.5 px-3">Modality / Type</th>
                    <th className="py-2.5 px-3">Difficulty</th>
                    <th className="py-2.5 px-3">Duration</th>
                    <th className="py-2.5 px-3">Score</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1e2638]">
                  {history.map((item) => (
                    <tr key={item.id} className="hover:bg-[#1a2133] transition-colors">
                      <td className="py-3 px-3 font-semibold text-white">{item.date}</td>
                      <td className="py-3 px-3 text-slate-300">{item.type}</td>
                      <td className="py-3 px-3">
                        <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
                          {item.difficulty}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-slate-400">{item.durationText}</td>
                      <td className="py-3 px-3 font-bold text-emerald-400">{item.score}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ACTIVE INTERVIEW SESSION MODE */}
      {sessionState === 'active' && (
        <div className="space-y-6">
          {/* Active Session Header Bar */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-xl bg-[#121624] border border-indigo-500/40 font-mono text-xs shadow-lg">
            <div className="flex items-center gap-3">
              <span className="px-2.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 font-bold border border-indigo-500/30">
                Question {currentQuestionIdx + 1} of {questions.length}
              </span>
              <span className="text-white font-semibold truncate max-w-[200px] sm:max-w-none">
                {sessionConfig?.modality || 'System Architecture'}
              </span>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1.5 text-amber-400 font-bold">
                <Clock className="w-4 h-4" />
                <span>Elapsed: {formatTimer(secondsElapsed)}</span>
              </div>
              <button
                onClick={() => setSessionState('idle')}
                className="text-rose-400 hover:underline text-xs"
              >
                Quit Session
              </button>
            </div>
          </div>

          {/* Question Prompt Card */}
          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-lg">
            <div className="flex items-center justify-between pb-3 border-b border-[#232b3e]">
              <span className="text-xs font-mono font-semibold text-indigo-400 uppercase tracking-wider">
                Topic: {currentQ.topic}
              </span>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono text-slate-400">Target Time: {currentQ.targetDuration}</span>
                <button
                  onClick={() => setShowHint(!showHint)}
                  className="px-2.5 py-1 rounded-lg bg-[#1a2133] text-xs font-medium text-amber-400 hover:bg-[#232b3e] border border-amber-500/30 transition-colors flex items-center gap-1"
                >
                  <HelpCircle className="w-3.5 h-3.5" />
                  <span>{showHint ? 'Hide Hint' : 'Show Hint'}</span>
                </button>
              </div>
            </div>

            <h3 className="text-lg font-bold text-white leading-relaxed">{currentQ.question}</h3>

            {showHint && (
              <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-xs text-amber-200 font-sans space-y-1 animate-in fade-in">
                <span className="font-semibold text-amber-400 font-mono block">Copilot Hint:</span>
                <p>{currentQ.hint}</p>
              </div>
            )}

            {/* Answer Input Area */}
            <div className="space-y-2 pt-2">
              <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                <span>Type or outline your architectural response below:</span>
                <span>Word Count: {wordCount} words</span>
              </div>
              <textarea
                rows="8"
                value={answerText}
                onChange={(e) => setAnswerText(e.target.value)}
                placeholder="Structure your answer (e.g. 1. High Level Architecture, 2. Redis Caching Invalidation, 3. Trade-offs & Bottlenecks)..."
                className="w-full p-4 rounded-xl bg-[#0b0e17] border border-[#232b3e] text-white focus:outline-none focus:border-indigo-500 transition-colors resize-none leading-relaxed font-sans"
              ></textarea>
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-[#232b3e]">
              <button
                onClick={handleSubmitAnswer}
                disabled={!answerText.trim()}
                className="px-6 py-2.5 rounded-xl text-sm font-semibold bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white transition-all shadow-md shadow-indigo-600/25 disabled:opacity-50 flex items-center gap-2"
              >
                <Send className="w-4 h-4" />
                <span>Submit Answer & Evaluate</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* EVALUATING LOADING STATE */}
      {sessionState === 'evaluating' && (
        <div className="p-12 text-center rounded-2xl bg-[#121624] border border-indigo-500/40 space-y-4 shadow-xl my-8">
          <RefreshCw className="w-10 h-10 text-indigo-400 animate-spin mx-auto" />
          <h3 className="text-lg font-bold text-white">Evaluating Technical & Architectural Response...</h3>
          <p className="text-xs text-slate-400 font-mono">
            Telemetry v4.2 AI Evaluator inspecting technical accuracy, trade-offs, and STAR structure...
          </p>
        </div>
      )}

      {/* RESULTS EVALUATION VIEW */}
      {sessionState === 'results' && evalResult && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-6 shadow-lg">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#232b3e]">
              <div>
                <span className="text-xs font-mono uppercase text-emerald-400 tracking-wider block">AI Evaluation Complete</span>
                <h3 className="text-xl font-bold text-white">Mock Interview Diagnostic Results</h3>
              </div>
              <div className="flex items-center gap-2">
                <span className="px-3 py-1 rounded-full text-sm font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  Overall Score: {evalResult.score}/100
                </span>
              </div>
            </div>

            {/* Sub-score cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
              <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-1">
                <span className="text-slate-400 block">Technical Accuracy</span>
                <span className="text-2xl font-bold text-white">{evalResult.technicalAccuracy}%</span>
              </div>
              <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-1">
                <span className="text-slate-400 block">Communication Clarity</span>
                <span className="text-2xl font-bold text-white">{evalResult.communicationClarity}%</span>
              </div>
              <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-1">
                <span className="text-slate-400 block">Answer Structure</span>
                <span className="text-2xl font-bold text-white">{evalResult.answerStructure}%</span>
              </div>
            </div>

            {/* AI Feedback Rationale */}
            <div className="p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/30 space-y-2">
              <span className="text-xs font-mono uppercase font-semibold text-indigo-400 flex items-center gap-1">
                <Sparkles className="w-4 h-4" />
                AI Evaluator Feedback:
              </span>
              <p className="text-sm text-slate-200 font-sans leading-relaxed">{evalResult.aiFeedback}</p>
            </div>

            {/* Strengths & Weaknesses */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-2">
                <span className="font-semibold text-emerald-400 font-mono flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4" />
                  Key Strengths
                </span>
                <ul className="space-y-1.5 text-slate-300 font-sans">
                  {evalResult.strengths.map((str, idx) => (
                    <li key={idx} className="flex items-start gap-1.5">
                      <span className="text-emerald-400">•</span> {str}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-2">
                <span className="font-semibold text-amber-400 font-mono flex items-center gap-1.5">
                  <AlertCircle className="w-4 h-4" />
                  Areas for Improvement
                </span>
                <ul className="space-y-1.5 text-slate-300 font-sans">
                  {evalResult.weaknesses.map((wk, idx) => (
                    <li key={idx} className="flex items-start gap-1.5">
                      <span className="text-amber-400">•</span> {wk}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="pt-4 flex flex-wrap items-center justify-between gap-3 border-t border-[#232b3e]">
              <button
                onClick={() => setSessionState('idle')}
                className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-[#1a2133]"
              >
                Back to Interview Dashboard
              </button>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => navigate('/skill-gaps')}
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-[#1a2133] hover:bg-[#232b3e] text-white border border-[#232b3e]"
                >
                  Analyze Skill Gaps
                </button>
                <button
                  onClick={() => handleStartInterview(sessionConfig || { modality: 'System Architecture & Design' })}
                  className="px-5 py-2 rounded-xl text-xs font-semibold bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white transition-all shadow-md shadow-indigo-600/25 flex items-center gap-1.5"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>Start New Session</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Setup Modal */}
      <InterviewSetupModal
        isOpen={isSetupOpen}
        onClose={() => setIsSetupOpen(false)}
        onStartInterview={handleStartInterview}
      />
    </div>
  );
};
