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
  Check
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
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 bg-surface-container-low p-6 rounded-2xl border border-outline-variant/60 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <h1 className="text-2xl font-bold text-on-surface tracking-tight">AI Mock Interview Studio</h1>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-secondary-container/40 text-secondary text-xs font-mono border border-secondary/30">
              <Zap className="w-3.5 h-3.5 text-secondary" />
              Telemetry v4.2 · Real-Time Adaptive Engine
            </span>
          </div>
          <p className="text-sm text-on-surface-variant max-w-2xl">
            Practice realistic multi-stage technical and system design interviews, receive instant AI feedback, and calibrate readiness for Tier-1 companies.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start lg:self-center shrink-0">
          <button
            onClick={() => setIsSetupOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-surface-container-high hover:bg-surface-bright text-on-surface text-sm font-medium rounded-xl transition-all shadow-sm"
          >
            <Sliders className="w-4 h-4 text-primary" />
            <span>Settings</span>
          </button>
          <button
            onClick={() => setIsSetupOpen(true)}
            className="flex items-center gap-2 px-5 py-2 bg-primary text-on-primary hover:bg-primary-fixed-dim rounded-xl font-semibold text-sm transition-all shadow-md"
          >
            <Play className="w-4 h-4 fill-on-primary" />
            <span>Start Mock Interview</span>
          </button>
        </div>
      </div>

      {/* IDLE MODE VIEW */}
      {sessionState === 'idle' && (
        <div className="space-y-6">
          {/* Readiness Calibration Score Card */}
          <div className="p-6 rounded-2xl bg-surface-container-low border border-outline-variant/60 space-y-4 shadow-sm">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-outline-variant/40">
              <div>
                <span className="text-xs font-mono uppercase text-secondary tracking-wider block">Candidate Interview Calibration</span>
                <h3 className="text-lg font-bold text-on-surface">Target Role: {user?.targetRole || 'Backend SDE-1'}</h3>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-tertiary-container/30 text-tertiary border border-tertiary/30 self-start sm:self-auto">
                Calibration Score: 76/100 (+4% vs last week)
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
              <div className="p-4 rounded-xl bg-surface-container border border-outline-variant/40 space-y-1">
                <span className="text-on-surface-variant block">Technical Accuracy</span>
                <span className="text-xl font-bold text-on-surface">82%</span>
                <span className="text-[11px] text-tertiary block pt-0.5">High precision algorithm responses</span>
              </div>

              <div className="p-4 rounded-xl bg-surface-container border border-outline-variant/40 space-y-1">
                <span className="text-on-surface-variant block">Communication Articulation</span>
                <span className="text-xl font-bold text-on-surface">74%</span>
                <span className="text-[11px] text-secondary block pt-0.5">145 WPM optimal cadence</span>
              </div>

              <div className="p-4 rounded-xl bg-surface-container border border-outline-variant/40 space-y-1">
                <span className="text-on-surface-variant block">STAR Structure Compliance</span>
                <span className="text-xl font-bold text-on-surface">78%</span>
                <span className="text-[11px] text-primary block pt-0.5">Requires quantified metrics</span>
              </div>
            </div>
          </div>

          {/* Targeted Modalities */}
          <div className="space-y-4">
            <h3 className="font-semibold text-on-surface text-lg">Targeted Interview Modalities</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div
                onClick={() => handleStartInterview({ modality: 'System Architecture & Design', difficulty: 'Hard', questionCount: 3, duration: '20 mins' })}
                className="p-5 rounded-2xl bg-surface-container-low border border-outline-variant/60 space-y-3 hover:border-primary/50 transition-all cursor-pointer shadow-sm"
              >
                <div className="p-2.5 rounded-xl bg-primary-container/20 text-primary border border-primary/30 w-fit">
                  <Layers className="w-5 h-5" />
                </div>
                <h4 className="font-bold text-on-surface text-base">System Architecture & Design</h4>
                <p className="text-xs text-on-surface-variant leading-relaxed">
                  Scalability, Caching (Redis), Pub-Sub Messaging, CAP theorem, and Database Sharding trade-offs.
                </p>
                <span className="text-xs font-semibold text-primary inline-flex items-center gap-1">
                  Launch Architecture Session <ArrowUpRight className="w-3.5 h-3.5" />
                </span>
              </div>

              <div
                onClick={() => handleStartInterview({ modality: 'Technical / DSA Drill', difficulty: 'Medium', questionCount: 3, duration: '15 mins' })}
                className="p-5 rounded-2xl bg-surface-container-low border border-outline-variant/60 space-y-3 hover:border-primary/50 transition-all cursor-pointer shadow-sm"
              >
                <div className="p-2.5 rounded-xl bg-tertiary-container/20 text-tertiary border border-tertiary/30 w-fit">
                  <Zap className="w-5 h-5" />
                </div>
                <h4 className="font-bold text-on-surface text-base">Technical / DSA Drill</h4>
                <p className="text-xs text-on-surface-variant leading-relaxed">
                  Topological Sort, 2D Dynamic Programming, Tree Traversals, and time/space complexity analysis.
                </p>
                <span className="text-xs font-semibold text-tertiary inline-flex items-center gap-1">
                  Launch DSA Session <ArrowUpRight className="w-3.5 h-3.5" />
                </span>
              </div>

              <div
                onClick={() => handleStartInterview({ modality: 'Behavioral & HR STAR Drill', difficulty: 'Medium', questionCount: 3, duration: '15 mins' })}
                className="p-5 rounded-2xl bg-surface-container-low border border-outline-variant/60 space-y-3 hover:border-primary/50 transition-all cursor-pointer shadow-sm"
              >
                <div className="p-2.5 rounded-xl bg-secondary-container/20 text-secondary border border-secondary/30 w-fit">
                  <Sparkles className="w-5 h-5" />
                </div>
                <h4 className="font-bold text-on-surface text-base">Behavioral STAR Drill</h4>
                <p className="text-xs text-on-surface-variant leading-relaxed">
                  Leadership principles, conflict resolution, technical disagreement, and project evidence.
                </p>
                <span className="text-xs font-semibold text-secondary inline-flex items-center gap-1">
                  Launch Behavioral Session <ArrowUpRight className="w-3.5 h-3.5" />
                </span>
              </div>
            </div>
          </div>

          {/* Interview Session History */}
          <div className="bg-surface-container-low p-6 rounded-2xl border border-outline-variant/60 space-y-4 shadow-sm">
            <div className="flex items-center justify-between pb-3 border-b border-outline-variant/50">
              <h3 className="font-semibold text-on-surface text-base flex items-center gap-2">
                <History className="w-5 h-5 text-primary" />
                Interview Practice History
              </h3>
              <span className="text-xs font-mono text-on-surface-variant">{history.length} Saved Sessions</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse font-mono text-xs">
                <thead>
                  <tr className="border-b border-outline-variant/40 text-[11px] uppercase text-on-surface-variant">
                    <th className="py-2.5 px-3">Date</th>
                    <th className="py-2.5 px-3">Modality / Type</th>
                    <th className="py-2.5 px-3">Difficulty</th>
                    <th className="py-2.5 px-3">Duration</th>
                    <th className="py-2.5 px-3">Score</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant/30">
                  {history.map((item) => (
                    <tr key={item.id} className="hover:bg-surface-container/50 transition-colors">
                      <td className="py-3 px-3 font-semibold text-on-surface">{item.date}</td>
                      <td className="py-3 px-3 text-on-surface-variant">{item.type}</td>
                      <td className="py-3 px-3">
                        <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-surface-container text-primary">
                          {item.difficulty}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-on-surface-variant">{item.durationText}</td>
                      <td className="py-3 px-3 font-bold text-tertiary">{item.score}%</td>
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
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-xl bg-surface-container-low border border-primary/40 font-mono text-xs shadow-sm">
            <div className="flex items-center gap-3">
              <span className="px-2.5 py-0.5 rounded-full bg-primary-container/20 text-primary font-bold border border-primary/30">
                Question {currentQuestionIdx + 1} of {questions.length}
              </span>
              <span className="text-on-surface font-semibold truncate max-w-[200px] sm:max-w-none">
                {sessionConfig?.modality || 'System Architecture'}
              </span>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1.5 text-secondary font-bold">
                <Clock className="w-4 h-4" />
                <span>Elapsed: {formatTimer(secondsElapsed)}</span>
              </div>
              <button
                onClick={() => setSessionState('idle')}
                className="text-error hover:underline text-xs"
              >
                Quit Session
              </button>
            </div>
          </div>

          {/* Question Prompt Card */}
          <div className="p-6 rounded-2xl bg-surface-container-low border border-outline-variant/60 space-y-4 shadow-sm">
            <div className="flex items-center justify-between pb-3 border-b border-outline-variant/40">
              <span className="text-xs font-mono font-semibold text-primary uppercase tracking-wider">
                Topic: {currentQ.topic}
              </span>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono text-on-surface-variant">Target Time: {currentQ.targetDuration}</span>
                <button
                  onClick={() => setShowHint(!showHint)}
                  className="px-2.5 py-1 rounded-lg bg-surface-container text-xs font-medium text-secondary hover:bg-surface-container-high border border-secondary/30 transition-colors flex items-center gap-1"
                >
                  <HelpCircle className="w-3.5 h-3.5" />
                  <span>{showHint ? 'Hide Hint' : 'Show Hint'}</span>
                </button>
              </div>
            </div>

            <h3 className="text-lg font-bold text-on-surface leading-relaxed">{currentQ.question}</h3>

            {showHint && (
              <div className="p-3.5 rounded-xl bg-secondary-container/15 border border-secondary/30 text-xs text-on-surface-variant font-sans space-y-1 animate-in fade-in">
                <span className="font-semibold text-secondary font-mono block">Copilot Hint:</span>
                <p>{currentQ.hint}</p>
              </div>
            )}

            {/* Answer Input Area */}
            <div className="space-y-2 pt-2">
              <div className="flex items-center justify-between text-xs font-mono text-on-surface-variant">
                <span>Type or outline your architectural response below:</span>
                <span>Word Count: {wordCount} words</span>
              </div>
              <textarea
                rows="8"
                value={answerText}
                onChange={(e) => setAnswerText(e.target.value)}
                placeholder="Structure your answer (e.g. 1. High Level Architecture, 2. Redis Caching Invalidation, 3. Trade-offs & Bottlenecks)..."
                className="w-full p-4 rounded-xl bg-surface-container border border-outline-variant text-on-surface text-sm focus:outline-none focus:border-primary transition-colors resize-none leading-relaxed font-sans"
              ></textarea>
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-outline-variant/40">
              <button
                onClick={handleSubmitAnswer}
                disabled={!answerText.trim()}
                className="px-6 py-2.5 rounded-xl text-sm font-semibold bg-primary text-on-primary hover:bg-primary-fixed-dim transition-all shadow-md disabled:opacity-50 flex items-center gap-2"
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
        <div className="p-12 text-center rounded-2xl bg-surface-container-low border border-primary/40 space-y-4 shadow-xl my-8">
          <RefreshCw className="w-10 h-10 text-primary animate-spin mx-auto" />
          <h3 className="text-lg font-bold text-on-surface">Evaluating Technical & Architectural Response...</h3>
          <p className="text-xs text-on-surface-variant font-mono">
            Telemetry v4.2 AI Evaluator inspecting technical accuracy, trade-offs, and STAR structure...
          </p>
        </div>
      )}

      {/* RESULTS EVALUATION VIEW */}
      {sessionState === 'results' && evalResult && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-surface-container-low border border-outline-variant/60 space-y-6 shadow-sm">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-outline-variant/40">
              <div>
                <span className="text-xs font-mono uppercase text-tertiary tracking-wider block">AI Evaluation Complete</span>
                <h3 className="text-xl font-bold text-on-surface">Mock Interview Diagnostic Results</h3>
              </div>
              <div className="flex items-center gap-2">
                <span className="px-3 py-1 rounded-full text-sm font-mono font-bold bg-tertiary-container/30 text-tertiary border border-tertiary/30">
                  Overall Score: {evalResult.score}/100
                </span>
              </div>
            </div>

            {/* Sub-score cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
              <div className="p-4 rounded-xl bg-surface-container border border-outline-variant/40 space-y-1">
                <span className="text-on-surface-variant block">Technical Accuracy</span>
                <span className="text-2xl font-bold text-on-surface">{evalResult.technicalAccuracy}%</span>
              </div>
              <div className="p-4 rounded-xl bg-surface-container border border-outline-variant/40 space-y-1">
                <span className="text-on-surface-variant block">Communication Clarity</span>
                <span className="text-2xl font-bold text-on-surface">{evalResult.communicationClarity}%</span>
              </div>
              <div className="p-4 rounded-xl bg-surface-container border border-outline-variant/40 space-y-1">
                <span className="text-on-surface-variant block">Answer Structure</span>
                <span className="text-2xl font-bold text-on-surface">{evalResult.answerStructure}%</span>
              </div>
            </div>

            {/* AI Feedback Rationale */}
            <div className="p-4 rounded-xl bg-primary-container/10 border border-primary/30 space-y-2">
              <span className="text-xs font-mono uppercase font-semibold text-primary flex items-center gap-1">
                <Sparkles className="w-4 h-4" />
                AI Evaluator Feedback:
              </span>
              <p className="text-sm text-on-surface font-sans leading-relaxed">{evalResult.aiFeedback}</p>
            </div>

            {/* Strengths & Weaknesses */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="p-4 rounded-xl bg-surface-container border border-outline-variant/40 space-y-2">
                <span className="font-semibold text-tertiary font-mono flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4" />
                  Key Strengths
                </span>
                <ul className="space-y-1.5 text-on-surface-variant font-sans">
                  {evalResult.strengths.map((str, idx) => (
                    <li key={idx} className="flex items-start gap-1.5">
                      <span className="text-tertiary">•</span> {str}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="p-4 rounded-xl bg-surface-container border border-outline-variant/40 space-y-2">
                <span className="font-semibold text-secondary font-mono flex items-center gap-1.5">
                  <AlertCircle className="w-4 h-4" />
                  Areas for Improvement
                </span>
                <ul className="space-y-1.5 text-on-surface-variant font-sans">
                  {evalResult.weaknesses.map((wk, idx) => (
                    <li key={idx} className="flex items-start gap-1.5">
                      <span className="text-secondary">•</span> {wk}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="pt-4 flex flex-wrap items-center justify-between gap-3 border-t border-outline-variant/40">
              <button
                onClick={() => setSessionState('idle')}
                className="px-4 py-2 rounded-xl text-xs font-medium text-on-surface-variant hover:text-on-surface hover:bg-surface-container"
              >
                Back to Interview Dashboard
              </button>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => navigate('/skill-gaps')}
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-surface-container-high hover:bg-surface-bright text-on-surface"
                >
                  Analyze Skill Gaps
                </button>
                <button
                  onClick={() => handleStartInterview(sessionConfig || { modality: 'System Architecture & Design' })}
                  className="px-5 py-2 rounded-xl text-xs font-semibold bg-primary text-on-primary hover:bg-primary-fixed-dim transition-all shadow-md flex items-center gap-1.5"
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
