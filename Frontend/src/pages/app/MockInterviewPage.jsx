import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { usePlanning } from '../../context/PlanningContext';
import { useUser } from '../../context/UserContext';
import { defaultQuestions, getDynamicQuestion, getStoredInterviewHistory, saveInterviewHistory } from '../../data/interviewData';
import { interviewService } from '../../services/interviewService';
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
  ArrowRight,
  History,
  RotateCcw,
  Send,
  Award,
  Layers,
  Sliders,
  Check,
  RefreshCw,
  Code,
  FileText,
  ChevronDown,
  ChevronUp,
  X,
  BookOpen,
  Info
} from 'lucide-react';

export const MockInterviewPage = () => {
  const navigate = useNavigate();
  const { user } = useUser();
  const { toggleTaskCompletion, toastNotification } = usePlanning();

  // Navigation states: 'idle' | 'active' | 'evaluating' | 'question_feedback' | 'results'
  const [sessionState, setSessionState] = useState('idle');
  const [isSetupOpen, setIsSetupOpen] = useState(false);
  const [sessionConfig, setSessionConfig] = useState(null);
  const [activeSession, setActiveSession] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [questionNumber, setQuestionNumber] = useState(1);
  const [totalQuestions, setTotalQuestions] = useState(5);
  const [answerText, setAnswerText] = useState('');
  const [showHint, setShowHint] = useState(false);
  const [secondsElapsed, setSecondsElapsed] = useState(0);

  // Per-question feedback and completed session records
  const [currentQuestionEval, setCurrentQuestionEval] = useState(null);
  const [nextQuestionPending, setNextQuestionPending] = useState(null);
  const [completedQuestionsList, setCompletedQuestionsList] = useState([]);
  const [finalSessionSummary, setFinalSessionSummary] = useState(null);
  const [expandedQuestionIdx, setExpandedQuestionIdx] = useState(null);

  // History & Detail Modal
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [selectedHistorySession, setSelectedHistorySession] = useState(null);
  const [historySessionQuestions, setHistorySessionQuestions] = useState([]);
  const [loadingHistoryDetails, setLoadingHistoryDetails] = useState(false);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setLoadingHistory(true);
    try {
      const apiHistory = await interviewService.getInterviewHistory();
      if (apiHistory && apiHistory.length > 0) {
        const formatted = apiHistory.map((item) => ({
          id: item.interview_id || item.id,
          date: item.created_at ? new Date(item.created_at).toLocaleDateString() : 'Recent',
          role: item.target_role || 'Backend Developer',
          type: item.interview_type ? item.interview_type.toUpperCase().replace(/_/g, ' ') : 'Technical',
          difficulty: item.difficulty || 'Medium',
          durationText: '15:00',
          score: item.overall_score || 75,
          status: item.status || 'Completed',
          rawData: item,
        }));
        setHistory(formatted);
      } else {
        setHistory(getStoredInterviewHistory());
      }
    } catch (e) {
      setHistory(getStoredInterviewHistory());
    } finally {
      setLoadingHistory(false);
    }
  };

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

  // Start interview session
  const handleStartInterview = async (config) => {
    setSessionConfig(config);
    setAnswerText('');
    setSecondsElapsed(0);
    setShowHint(false);
    setCurrentQuestionEval(null);
    setNextQuestionPending(null);
    setCompletedQuestionsList([]);
    setFinalSessionSummary(null);
    try {
      const targetDomain = config?.role || user?.targetRole || 'Full Stack Engineer';
      const res = await interviewService.startInterview({
        ...config,
        role: targetDomain,
      });
      if (res && res.interview_id) {
        setActiveSession(res);
        setTotalQuestions(res.total_questions || config.questionCount || 3);
        setQuestionNumber(res.current_question || 1);
        if (res.current_question_data) {
          setCurrentQuestion(res.current_question_data);
        } else {
          const dynamicQ = getDynamicQuestion(targetDomain, 1, []);
          setCurrentQuestion(dynamicQ);
        }
        setSessionState('active');
      } else {
        const dynamicQ = getDynamicQuestion(targetDomain, 1, []);
        setCurrentQuestion(dynamicQ);
        setQuestionNumber(1);
        setTotalQuestions(config.questionCount || 3);
        setSessionState('active');
      }
    } catch (e) {
      const targetDomain = config?.role || user?.targetRole || 'Full Stack Engineer';
      const dynamicQ = getDynamicQuestion(targetDomain, 1, []);
      setCurrentQuestion(dynamicQ);
      setQuestionNumber(1);
      setTotalQuestions(config.questionCount || 3);
      setSessionState('active');
    }
  };

  // Insert STAR Outline Template into answer
  const handleInsertTemplate = (type) => {
    if (type === 'star') {
      const template = `Situation:\n[Describe the context, project, or problem you faced]\n\nTask:\n[What was your specific responsibility or goal?]\n\nAction:\n[What concrete steps, architecture, or tools did you implement?]\n\nResult:\n[Quantifiable metrics, business impact, or key lessons learned]`;
      setAnswerText((prev) => prev ? `${prev}\n\n${template}` : template);
    } else if (type === 'system_design') {
      const template = `1. Functional & Non-Functional Requirements:\n- Scale: req/sec, latency target, data storage\n\n2. High-Level Architecture:\n- Client -> API Gateway -> Load Balancer -> Services -> Cache & DB\n\n3. Data Storage & Scaling Strategy:\n- Schema design, Indexing, Partitioning/Sharding\n\n4. Trade-offs, Bottlenecks & Edge Cases:\n- Cache invalidation, Failover, Rate limiting`;
      setAnswerText((prev) => prev ? `${prev}\n\n${template}` : template);
    }
  };

  // Submit answer for evaluation
  const handleSubmitAnswer = async () => {
    if (!answerText.trim()) return;
    const submittedAnswer = answerText.trim();
    setSessionState('evaluating');

    try {
      if (activeSession && activeSession.interview_id) {
        const res = await interviewService.submitAnswer(activeSession.interview_id, submittedAnswer);
        if (res) {
          const rawEval = res.evaluation || {};
          const formattedEval = {
            score: rawEval.score || 75,
            technicalAccuracy: rawEval.technical_accuracy || rawEval.correctness || 75,
            communicationClarity: rawEval.communication_quality || rawEval.clarity || 75,
            answerStructure: rawEval.clarity || rawEval.answer_structure || 75,
            aiFeedback: rawEval.ai_feedback || rawEval.feedback || "Good response addressing key points.",
            strengths: rawEval.strengths || ["Clearly articulated approach", "Used relevant terminology"],
            weaknesses: rawEval.weaknesses || ["Could elaborate on edge cases or metrics"],
            modelAnswer: rawEval.model_answer || rawEval.ideal_response || "Optimal answer highlights systematic problem decomposition and explicit architectural trade-offs.",
          };

          const completedQ = {
            questionNumber: questionNumber,
            question: currentQuestion.question,
            category: currentQuestion.category || currentQuestion.skill || 'Technical',
            answer: submittedAnswer,
            evaluation: formattedEval,
          };
          setCompletedQuestionsList((prev) => [...prev, completedQ]);
          setCurrentQuestionEval(formattedEval);

          if (res.status === 'in_progress' && res.next_question) {
            setNextQuestionPending(res.next_question);
            setSessionState('question_feedback');
            return;
          } else {
            // Completed final question
            setFinalSessionSummary(res.session_result || {
              overall_score: formattedEval.score,
              strengths: formattedEval.strengths,
              weaknesses: formattedEval.weaknesses,
            });
            setSessionState('results');
            fetchHistory();
            return;
          }
        }
      }

      // Local fallback evaluation with accurate multi-factor rubric
      const words = submittedAnswer.split(/\s+/).filter(Boolean);
      const wordCount = words.length;
      const lowerAns = submittedAnswer.toLowerCase();

      const techKeywords = ["redis", "cache", "sql", "api", "database", "latency", "throughput", "index", "sharding", "async", "event loop", "star", "trade-off", "performance"];
      const matchedKeywords = techKeywords.filter(k => lowerAns.includes(k));
      const hasNumbers = /\b\d+(\.\d+)?(ms|s|%|k|req|rps|gb|mb)?\b/.test(lowerAns);
      const hasStructure = /first|second|specifically|because|however|for example|trade-off|situation|task|action|result/.test(lowerAns);

      let techAccuracy = 50 + Math.min(40, matchedKeywords.length * 8);
      if (wordCount < 15) techAccuracy = Math.min(50, techAccuracy);

      let depthScore = 45;
      if (wordCount >= 90) depthScore = 90;
      else if (wordCount >= 50) depthScore = 78;
      else if (wordCount >= 25) depthScore = 65;

      let clarityScore = 55 + (hasStructure ? 20 : 0) + (hasNumbers ? 15 : 0);
      clarityScore = Math.min(95, clarityScore);

      const calculatedScore = wordCount < 8
        ? 30
        : Math.min(95, Math.max(35, Math.round((techAccuracy * 0.35) + (depthScore * 0.30) + (clarityScore * 0.35))));

      const fallbackEval = {
        score: calculatedScore,
        technicalAccuracy: Math.min(95, techAccuracy),
        communicationClarity: clarityScore,
        answerStructure: clarityScore,
        aiFeedback: calculatedScore >= 80
          ? `Solid technical explanation (${calculatedScore}/100) demonstrating clear engineering comprehension and vocabulary.`
          : calculatedScore >= 65
          ? `Good foundational response (${calculatedScore}/100). Adding concrete numerical metrics and edge cases will improve your score.`
          : `Needs expansion (${calculatedScore}/100). Elaborate on architectural mechanisms, concrete technologies, and trade-offs.`,
        strengths: matchedKeywords.length > 0
          ? [`Used relevant domain concepts: ${matchedKeywords.slice(0, 3).join(', ')}`, "Answered the core prompt directly"]
          : ["Submitted a direct initial response", "Clear sentence structure"],
        weaknesses: !hasNumbers
          ? ["Lacks quantitative benchmarks or system scale estimates (latency, req/s, cache hit %)", "Can cover failover edge cases"]
          : ["Elaborate on edge cases and failure recovery"],
        modelAnswer: "Focus on clear cause-and-effect reasoning with measurable outcomes and trade-offs.",
      };

      const fallbackCompletedQ = {
        questionNumber: questionNumber,
        question: currentQuestion.question,
        category: currentQuestion.category || 'Technical',
        answer: submittedAnswer,
        evaluation: fallbackEval,
      };
      setCompletedQuestionsList((prev) => [...prev, fallbackCompletedQ]);
      setCurrentQuestionEval(fallbackEval);

      if (questionNumber < totalQuestions) {
        const targetDomain = sessionConfig?.role || user?.targetRole || 'Full Stack Engineer';
        const nextQ = getDynamicQuestion(
          targetDomain,
          questionNumber + 1,
          [...completedQuestionsList, fallbackCompletedQ]
        );
        setNextQuestionPending(nextQ);
        setSessionState('question_feedback');
      } else {
        const allCompleted = [...completedQuestionsList, fallbackCompletedQ];
        const overallScore = Math.round(allCompleted.reduce((acc, q) => acc + (q.evaluation?.score || 70), 0) / allCompleted.length);
        setFinalSessionSummary({
          overall_score: overallScore,
          strengths: fallbackEval.strengths,
          weaknesses: fallbackEval.weaknesses,
        });
        setSessionState('results');
      }
    } catch (e) {
      // In case of error, transition gracefully
      setSessionState('results');
    }
  };

  // Move to next question after reviewing per-question feedback
  const handleProceedToNextQuestion = () => {
    if (nextQuestionPending) {
      setCurrentQuestion(nextQuestionPending);
      setQuestionNumber((prev) => prev + 1);
      setAnswerText('');
      setShowHint(false);
      setCurrentQuestionEval(null);
      setNextQuestionPending(null);
      setSessionState('active');
    } else {
      setSessionState('results');
      fetchHistory();
    }
  };

  // Open history detail view
  const handleOpenHistoryDetail = async (sessionItem) => {
    setSelectedHistorySession(sessionItem);
    setLoadingHistoryDetails(true);
    try {
      const questions = await interviewService.getInterviewQuestions(sessionItem.id);
      setHistorySessionQuestions(Array.isArray(questions) ? questions : []);
    } catch (e) {
      setHistorySessionQuestions([]);
    } finally {
      setLoadingHistoryDetails(false);
    }
  };

  const currentQ = currentQuestion || defaultQuestions[0];
  const wordCount = answerText.trim() ? answerText.trim().split(/\s+/).length : 0;

  // Calculate aggregated scores for final review
  const calculatedOverallScore = finalSessionSummary?.overall_score || (
    completedQuestionsList.length > 0
      ? Math.round(completedQuestionsList.reduce((acc, q) => acc + (q.evaluation?.score || 70), 0) / completedQuestionsList.length)
      : 78
  );

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 bg-gradient-to-r from-indigo-950/60 via-purple-950/40 to-[#121624] p-6 rounded-2xl border border-indigo-500/30 shadow-xl backdrop-blur-md">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">AI Mock Interview Studio</h1>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 text-xs font-mono border border-cyan-500/30">
              <Zap className="w-3.5 h-3.5 text-cyan-400" />
              Role-Grounded Question Drill
            </span>
          </div>
          <p className="text-sm text-slate-300 max-w-2xl">
            Simulate realistic multi-stage technical and system design interviews, receive instant AI feedback per answer, and review comprehensive question-by-question scorecards.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start lg:self-center shrink-0">
          <button
            onClick={() => setIsSetupOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-[#1a2133] hover:bg-[#232b3e] text-white text-sm font-medium rounded-xl border border-[#232b3e] transition-all shadow-sm"
          >
            <Sliders className="w-4 h-4 text-indigo-400" />
            <span>Customize Setup</span>
          </button>
          <button
            onClick={() => setIsSetupOpen(true)}
            className="flex items-center gap-2 px-5 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white rounded-xl font-semibold text-sm transition-all shadow-md shadow-indigo-600/25"
          >
            <Play className="w-4 h-4 fill-white" />
            <span>Start Practice</span>
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
                <span className="text-xs font-mono uppercase text-amber-400 tracking-wider block">Candidate Calibration</span>
                <h3 className="text-lg font-bold text-white">Target Role: {user?.targetRole || 'Backend SDE-1'}</h3>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 self-start sm:self-auto">
                Ready to Practice: Full Pipeline Active
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
              <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-1">
                <span className="text-slate-400 block">Structured Answering</span>
                <span className="text-xl font-bold text-white">STAR Method</span>
                <span className="text-[11px] text-emerald-400 block pt-0.5">Built-in templates for rapid framing</span>
              </div>

              <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-1">
                <span className="text-slate-400 block">Instant Diagnostics</span>
                <span className="text-xl font-bold text-white">Per-Question</span>
                <span className="text-[11px] text-amber-400 block pt-0.5">Immediate scoring after every submit</span>
              </div>

              <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-1">
                <span className="text-slate-400 block">Complete Record</span>
                <span className="text-xl font-bold text-white">Audit Trail</span>
                <span className="text-[11px] text-indigo-400 block pt-0.5">Click any past session to inspect QA</span>
              </div>
            </div>
          </div>

          {/* Targeted Modalities */}
          <div className="space-y-4">
            <h3 className="font-semibold text-white text-lg">Targeted Interview Modalities</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div
                onClick={() => handleStartInterview({ modality: 'system_design', difficulty: 'hard', questionCount: 3 })}
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
                onClick={() => handleStartInterview({ modality: 'dsa', difficulty: 'medium', questionCount: 3 })}
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
                onClick={() => handleStartInterview({ modality: 'behavioral', difficulty: 'medium', questionCount: 3 })}
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
                    <th className="py-2.5 px-3 text-right">Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1e2638]">
                  {history.map((item, idx) => (
                    <tr
                      key={item.id || idx}
                      onClick={() => handleOpenHistoryDetail(item)}
                      className="hover:bg-[#1a2133] transition-colors cursor-pointer"
                    >
                      <td className="py-3 px-3 font-semibold text-white">{item.date}</td>
                      <td className="py-3 px-3 text-slate-300">{item.type}</td>
                      <td className="py-3 px-3">
                        <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
                          {item.difficulty}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-slate-400">{item.durationText || '15:00'}</td>
                      <td className="py-3 px-3 font-bold text-emerald-400">{item.score}%</td>
                      <td className="py-3 px-3 text-right">
                        <span className="text-xs text-indigo-400 hover:text-indigo-300 font-sans">
                          Inspect &rarr;
                        </span>
                      </td>
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
          {/* Question Stepper & Progress Tracker */}
          <div className="bg-[#121624] p-4 rounded-xl border border-[#232b3e] shadow-lg space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs font-mono">
              <div className="flex items-center gap-2">
                <span className="font-bold text-indigo-400">SESSION PROGRESS:</span>
                <span className="text-white">Question {questionNumber} of {totalQuestions}</span>
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

            {/* Step Indicators */}
            <div className="grid grid-cols-3 sm:grid-cols-5 gap-2 pt-1">
              {Array.from({ length: totalQuestions }).map((_, idx) => {
                const stepNum = idx + 1;
                const isCompleted = stepNum < questionNumber;
                const isCurrent = stepNum === questionNumber;

                return (
                  <div
                    key={idx}
                    className={`p-2 rounded-lg border text-center transition-all ${
                      isCurrent
                        ? 'bg-indigo-600/20 border-indigo-500 text-indigo-300 font-bold'
                        : isCompleted
                        ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                        : 'bg-[#0b0e17] border-[#1e2638] text-slate-500'
                    }`}
                  >
                    <div className="flex items-center justify-center gap-1 text-[11px] font-mono">
                      {isCompleted ? <Check className="w-3.5 h-3.5" /> : null}
                      <span>Q{stepNum}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Question Prompt Card */}
          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-lg">
            <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-[#232b3e]">
              <span className="text-xs font-mono font-semibold text-indigo-400 uppercase tracking-wider">
                Focus / Skill: {currentQ.skill || currentQ.category || currentQ.topic || 'Core Technical'}
              </span>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono text-slate-400">Difficulty: {currentQ.difficulty || 'Medium'}</span>
                {currentQ.hint && (
                  <button
                    onClick={() => setShowHint(!showHint)}
                    className="px-2.5 py-1 rounded-lg bg-[#1a2133] text-xs font-medium text-amber-400 hover:bg-[#232b3e] border border-amber-500/30 transition-colors flex items-center gap-1"
                  >
                    <HelpCircle className="w-3.5 h-3.5" />
                    <span>{showHint ? 'Hide Hint' : 'Show Copilot Hint'}</span>
                  </button>
                )}
              </div>
            </div>

            <h3 className="text-lg font-bold text-white leading-relaxed">{currentQ.question}</h3>

            {currentQ.expected_focus && (
              <p className="text-xs text-slate-400 font-mono">
                <strong className="text-slate-300">Expected Focus:</strong> {currentQ.expected_focus}
              </p>
            )}

            {showHint && currentQ.hint && (
              <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-xs text-amber-200 font-sans space-y-1 animate-in fade-in">
                <span className="font-semibold text-amber-400 font-mono block">Interviewer Hint:</span>
                <p>{currentQ.hint}</p>
              </div>
            )}

            {/* Answer Input Area & Helper Buttons */}
            <div className="space-y-2 pt-2">
              <div className="flex flex-wrap items-center justify-between gap-2 text-xs font-mono text-slate-400">
                <div className="flex items-center gap-2">
                  <span>Type your response below:</span>
                  <div className="flex items-center gap-1.5">
                    <button
                      type="button"
                      onClick={() => handleInsertTemplate('star')}
                      className="px-2 py-0.5 rounded bg-[#1a2133] hover:bg-[#232b3e] text-indigo-300 border border-[#232b3e] transition-colors flex items-center gap-1"
                    >
                      <FileText className="w-3 h-3" />
                      <span>Insert STAR Outline</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => handleInsertTemplate('system_design')}
                      className="px-2 py-0.5 rounded bg-[#1a2133] hover:bg-[#232b3e] text-indigo-300 border border-[#232b3e] transition-colors flex items-center gap-1"
                    >
                      <Code className="w-3 h-3" />
                      <span>Design Blueprint</span>
                    </button>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <span className={wordCount < 30 ? 'text-amber-400' : 'text-emerald-400'}>
                    Word Count: {wordCount} words {wordCount < 30 && '(Aim for 40+ for detail)'}
                  </span>
                </div>
              </div>

              <textarea
                rows="9"
                value={answerText}
                onChange={(e) => setAnswerText(e.target.value)}
                placeholder="Structure your answer clearly. Highlight specific design patterns, trade-offs, architecture decisions, or real project experiences..."
                className="w-full p-4 rounded-xl bg-[#0b0e17] border border-[#232b3e] text-white focus:outline-none focus:border-indigo-500 transition-colors resize-none leading-relaxed font-sans text-sm"
              ></textarea>
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-[#232b3e]">
              <span className="text-xs text-slate-500 font-mono">
                Pressing submit triggers real-time telemetry scoring & instant feedback
              </span>
              <button
                onClick={handleSubmitAnswer}
                disabled={!answerText.trim()}
                className="px-6 py-2.5 rounded-xl text-sm font-semibold bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white transition-all shadow-md shadow-indigo-600/25 disabled:opacity-50 flex items-center gap-2"
              >
                <Send className="w-4 h-4" />
                <span>Submit Answer for Evaluation</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* EVALUATING LOADING STATE */}
      {sessionState === 'evaluating' && (
        <div className="p-12 text-center rounded-2xl bg-[#121624] border border-indigo-500/40 space-y-4 shadow-xl my-8">
          <RefreshCw className="w-10 h-10 text-indigo-400 animate-spin mx-auto" />
          <h3 className="text-lg font-bold text-white">Analyzing Response Quality...</h3>
          <p className="text-xs text-slate-400 font-mono">
            PlaceMentor AI evaluating technical accuracy, communication clarity, and structural trade-offs...
          </p>
        </div>
      )}

      {/* PER-QUESTION INTERMEDIATE FEEDBACK VIEW */}
      {sessionState === 'question_feedback' && currentQuestionEval && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-[#121624] border border-indigo-500/40 space-y-6 shadow-xl">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#232b3e]">
              <div>
                <span className="text-xs font-mono uppercase text-emerald-400 tracking-wider block">
                  Question {questionNumber} Evaluated
                </span>
                <h3 className="text-xl font-bold text-white">Question Scorecard & Feedback</h3>
              </div>
              <div className="flex items-center gap-2">
                <span className="px-3.5 py-1 rounded-full text-base font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  Question Score: {currentQuestionEval.score}/100
                </span>
              </div>
            </div>

            {/* Score Metric Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
              <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-1">
                <span className="text-slate-400 block">Technical Accuracy</span>
                <span className="text-2xl font-bold text-white">{currentQuestionEval.technicalAccuracy}%</span>
              </div>
              <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-1">
                <span className="text-slate-400 block">Communication Quality</span>
                <span className="text-2xl font-bold text-white">{currentQuestionEval.communicationClarity}%</span>
              </div>
              <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-1">
                <span className="text-slate-400 block">Answer Structure</span>
                <span className="text-2xl font-bold text-white">{currentQuestionEval.answerStructure}%</span>
              </div>
            </div>

            {/* AI Evaluator Feedback */}
            <div className="p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/30 space-y-2">
              <span className="text-xs font-mono uppercase font-semibold text-indigo-400 flex items-center gap-1">
                <Sparkles className="w-4 h-4" />
                Interviewer Assessment:
              </span>
              <p className="text-sm text-slate-200 leading-relaxed">{currentQuestionEval.aiFeedback}</p>
            </div>

            {/* Strengths & Weaknesses */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-2">
                <span className="font-semibold text-emerald-400 font-mono flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4" />
                  What You Did Well
                </span>
                <ul className="space-y-1 text-slate-300">
                  {(currentQuestionEval.strengths || []).map((s, idx) => (
                    <li key={idx} className="flex items-start gap-1.5">
                      <span className="text-emerald-400">•</span> {s}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-2">
                <span className="font-semibold text-amber-400 font-mono flex items-center gap-1.5">
                  <AlertCircle className="w-4 h-4" />
                  Points to Improve
                </span>
                <ul className="space-y-1 text-slate-300">
                  {(currentQuestionEval.weaknesses || []).map((w, idx) => (
                    <li key={idx} className="flex items-start gap-1.5">
                      <span className="text-amber-400">•</span> {w}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="pt-4 flex items-center justify-between border-t border-[#232b3e]">
              <span className="text-xs font-mono text-slate-400">
                Ready for the next challenge? Question {questionNumber + 1} of {totalQuestions}
              </span>
              <button
                onClick={handleProceedToNextQuestion}
                className="px-6 py-2.5 rounded-xl text-sm font-semibold bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white transition-all shadow-md shadow-indigo-600/25 flex items-center gap-2"
              >
                <span>Continue to Next Question</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* FINAL COMPREHENSIVE DIAGNOSTIC RESULTS VIEW */}
      {sessionState === 'results' && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-6 shadow-lg">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#232b3e]">
              <div>
                <span className="text-xs font-mono uppercase text-emerald-400 tracking-wider block">
                  Interview Session Complete
                </span>
                <h3 className="text-2xl font-bold text-white">Full Performance Diagnostic Report</h3>
              </div>
              <div className="flex items-center gap-2">
                <span className="px-4 py-1.5 rounded-full text-lg font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  Final Score: {calculatedOverallScore}/100
                </span>
              </div>
            </div>

            {/* Summary Banner */}
            <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] flex flex-col md:flex-row md:items-center justify-between gap-4 font-mono text-xs">
              <div>
                <span className="text-slate-400 block">Total Questions Completed</span>
                <span className="text-base font-bold text-white">
                  {completedQuestionsList.length > 0 ? completedQuestionsList.length : totalQuestions} Questions
                </span>
              </div>
              <div>
                <span className="text-slate-400 block">Session Duration</span>
                <span className="text-base font-bold text-amber-400">{formatTimer(secondsElapsed)}</span>
              </div>
              <div>
                <span className="text-slate-400 block">Candidate Target</span>
                <span className="text-base font-bold text-indigo-400">{user?.targetRole || 'Backend SDE-1'}</span>
              </div>
            </div>

            {/* Question-by-Question Accordion Breakdown */}
            <div className="space-y-3">
              <h4 className="text-sm font-mono font-bold uppercase text-slate-300 flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-indigo-400" />
                Question-by-Question Analysis
              </h4>

              {completedQuestionsList.map((item, idx) => {
                const isExpanded = expandedQuestionIdx === idx;
                const score = item.evaluation?.score || 75;

                return (
                  <div key={idx} className="rounded-xl border border-[#232b3e] bg-[#0b0e17] overflow-hidden">
                    <button
                      onClick={() => setExpandedQuestionIdx(isExpanded ? null : idx)}
                      className="w-full p-4 flex items-center justify-between text-left hover:bg-[#121624] transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <span className="px-2 py-0.5 rounded text-xs font-mono font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                          Q{item.questionNumber || idx + 1}
                        </span>
                        <span className="font-semibold text-white text-sm line-clamp-1">{item.question}</span>
                      </div>
                      <div className="flex items-center gap-3 shrink-0">
                        <span className="text-xs font-mono font-bold text-emerald-400">{score}%</span>
                        {isExpanded ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
                      </div>
                    </button>

                    {isExpanded && (
                      <div className="p-4 border-t border-[#1e2638] space-y-3 bg-[#121624]/60 text-xs">
                        <div>
                          <span className="font-mono text-slate-400 block font-semibold mb-1">Your Submitted Answer:</span>
                          <div className="p-3 rounded-lg bg-[#0b0e17] border border-[#1e2638] text-slate-200 whitespace-pre-wrap font-sans">
                            {item.answer}
                          </div>
                        </div>

                        <div>
                          <span className="font-mono text-indigo-400 block font-semibold mb-1">AI Evaluator Feedback:</span>
                          <p className="text-slate-300 font-sans leading-relaxed">{item.evaluation?.aiFeedback}</p>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                          <div className="p-3 rounded-lg bg-[#0b0e17] border border-[#1e2638]">
                            <span className="font-semibold text-emerald-400 font-mono block mb-1">Strengths</span>
                            <ul className="space-y-1 text-slate-300">
                              {(item.evaluation?.strengths || []).map((st, sidx) => (
                                <li key={sidx}>• {st}</li>
                              ))}
                            </ul>
                          </div>

                          <div className="p-3 rounded-lg bg-[#0b0e17] border border-[#1e2638]">
                            <span className="font-semibold text-amber-400 font-mono block mb-1">Areas for Growth</span>
                            <ul className="space-y-1 text-slate-300">
                              {(item.evaluation?.weaknesses || []).map((wk, widx) => (
                                <li key={widx}>• {wk}</li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
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
                  onClick={() => handleStartInterview(sessionConfig || { modality: 'technical', questionCount: 3 })}
                  className="px-5 py-2 rounded-xl text-xs font-semibold bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white transition-all shadow-md shadow-indigo-600/25 flex items-center gap-1.5"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>Practice Another Session</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* SESSION DETAILS MODAL FOR HISTORICAL SESSIONS */}
      {selectedHistorySession && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-in fade-in duration-200">
          <div className="relative w-full max-w-2xl bg-[#121624] border border-[#232b3e] rounded-2xl shadow-2xl overflow-hidden p-6 max-h-[85vh] flex flex-col">
            <div className="flex items-center justify-between pb-4 border-b border-[#232b3e]">
              <div>
                <h3 className="font-semibold text-lg text-white">Historical Session Transcript</h3>
                <p className="text-xs text-slate-400 font-mono">
                  {selectedHistorySession.role} · {selectedHistorySession.type} · Score: {selectedHistorySession.score}%
                </p>
              </div>
              <button
                onClick={() => setSelectedHistorySession(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-[#1a2133] transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto space-y-4 py-4 pr-1">
              {loadingHistoryDetails ? (
                <div className="text-center py-8 space-y-2">
                  <RefreshCw className="w-6 h-6 text-indigo-400 animate-spin mx-auto" />
                  <p className="text-xs text-slate-400 font-mono">Loading question transcript...</p>
                </div>
              ) : historySessionQuestions.length > 0 ? (
                historySessionQuestions.map((q, idx) => (
                  <div key={idx} className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-2 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-bold text-indigo-400">Question {q.question_number || idx + 1}</span>
                      <span className="font-mono text-emerald-400 font-bold">
                        Score: {q.evaluation?.score || 75}%
                      </span>
                    </div>
                    <p className="text-white font-semibold text-sm">{q.question}</p>
                    {q.answer && (
                      <div className="p-2.5 rounded bg-[#121624] border border-[#232b3e] text-slate-300 whitespace-pre-wrap font-sans">
                        {q.answer}
                      </div>
                    )}
                    {q.evaluation?.ai_feedback && (
                      <p className="text-slate-400 italic">Feedback: {q.evaluation.ai_feedback}</p>
                    )}
                  </div>
                ))
              ) : (
                <div className="p-6 text-center text-slate-400 font-mono text-xs">
                  Session record saved ({selectedHistorySession.date}). Full question breakdown is available for sessions run on this instance.
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-[#232b3e] flex items-center justify-end">
              <button
                onClick={() => setSelectedHistorySession(null)}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-[#1a2133] hover:bg-[#232b3e] text-white"
              >
                Close
              </button>
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
