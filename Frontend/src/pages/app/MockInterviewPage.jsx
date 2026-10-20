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
  const [questionsList, setQuestionsList] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [questionNumber, setQuestionNumber] = useState(1);
  const [totalQuestions, setTotalQuestions] = useState(3);
  const [answersMap, setAnswersMap] = useState({});
  const [showHint, setShowHint] = useState(false);
  const [secondsElapsed, setSecondsElapsed] = useState(0);

  // Synchronize answerText for the currently active question
  const answerText = answersMap[questionNumber] || '';
  const setAnswerText = (valOrUpdater) => {
    setAnswersMap((prev) => {
      const prevVal = prev[questionNumber] || '';
      const nextVal = typeof valOrUpdater === 'function' ? valOrUpdater(prevVal) : valOrUpdater;
      return { ...prev, [questionNumber]: nextVal };
    });
  };

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

  // Ensure questionsList is populated if session becomes active without it
  useEffect(() => {
    if (sessionState === 'active' && questionsList.length === 0) {
      const targetDomain = sessionConfig?.role || user?.targetRole || 'Full Stack Engineer';
      const modality = sessionConfig?.modality || 'System Architecture & Design';
      const difficulty = sessionConfig?.difficulty || 'Medium';
      const initialList = [];
      for (let i = 1; i <= totalQuestions; i++) {
        initialList.push(getDynamicQuestion(targetDomain, i, initialList, modality, difficulty));
      }
      setQuestionsList(initialList);
      if (!currentQuestion) {
        setCurrentQuestion(initialList[0]);
      }
    }
  }, [sessionState, questionsList.length, totalQuestions, sessionConfig]);

  // Start interview session
  const handleStartInterview = async (config) => {
    setSessionConfig(config);
    setAnswersMap({});
    setSecondsElapsed(0);
    setShowHint(false);
    setCurrentQuestionEval(null);
    setNextQuestionPending(null);
    setCompletedQuestionsList([]);
    setFinalSessionSummary(null);

    const qCount = config.questionCount || 3;
    setTotalQuestions(qCount);
    setQuestionNumber(1);

    const targetDomain = config?.role || user?.targetRole || 'Full Stack Engineer';
    const modality = config?.modality || 'System Architecture & Design';
    const difficulty = config?.difficulty || 'Medium';

    // Pre-generate all questions for this session so candidate can click Q1, Q2, Q3 immediately
    const generatedList = [];
    for (let i = 1; i <= qCount; i++) {
      const q = getDynamicQuestion(targetDomain, i, generatedList, modality, difficulty);
      generatedList.push(q);
    }
    setQuestionsList(generatedList);
    setCurrentQuestion(generatedList[0]);

    try {
      const res = await interviewService.startInterview({
        ...config,
        role: targetDomain,
        question_count: qCount,
      });
      if (res && res.interview_id) {
        setActiveSession(res);
        if (res.current_question_data) {
          generatedList[0] = {
            ...generatedList[0],
            ...res.current_question_data,
            question: res.current_question_data.question || generatedList[0].question,
          };
          setQuestionsList([...generatedList]);
          setCurrentQuestion(generatedList[0]);
        }
      }
    } catch (e) {
      console.warn("Backend startInterview error, using dynamic generated questions:", e);
    }
    setSessionState('active');
  };

  // Select question from stepper pill or navigation button
  const handleSelectQuestion = (stepNum) => {
    if (stepNum < 1 || stepNum > totalQuestions) return;
    setQuestionNumber(stepNum);
    setShowHint(false);
    if (questionsList[stepNum - 1]) {
      setCurrentQuestion(questionsList[stepNum - 1]);
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

  // Strict non-answer detection (e.g. "NA", "i donot know", "idk", "pass", "skip", etc.)
  const isNonAnswer = (text) => {
    if (!text) return true;
    const trimmed = text.trim();
    const cleaned = trimmed.toLowerCase().replace(/[^\w\s]/g, ' ').replace(/\s+/g, ' ').trim();
    const compact = cleaned.replace(/\s+/g, '');

    const nonAnswerExact = new Set([
      'na', 'n a', 'none', 'nil', 'null', 'nothing', 'no', 'nope', 'idk', 'dunno',
      'pass', 'skip', 'next', 'dont know', 'dontknow', 'donot know', 'donotknow',
      'do not know', 'no idea', 'noidea', 'no clue', 'noclue', 'not sure', 'notsure',
      'not known', 'notknown', 'unknown', 'cant answer', 'cannot answer', 'unable to answer',
      'no answer', 'no response', 'idont know', 'i dont know', 'i donot know', 'i do not know',
      'i have no idea', 'i have no clue', 'not aware', 'dont remember', 'do not remember'
    ]);

    if (nonAnswerExact.has(cleaned) || nonAnswerExact.has(compact) || nonAnswerExact.has(trimmed.toLowerCase())) {
      return true;
    }

    if (compact.length <= 3) {
      return true;
    }

    const words = cleaned.split(' ').filter(Boolean);
    if (words.length <= 12) {
      const phrases = [
        'dont know', 'donot know', 'do not know', 'no idea', 'no clue',
        'not sure', 'not familiar', 'havent learned', 'havent studied',
        'cant answer', 'cannot answer', 'skip this', 'pass this',
        'no knowledge', 'zero knowledge', 'forgot this', 'dont remember'
      ];
      if (phrases.some((p) => cleaned.includes(p))) {
        return true;
      }
    }

    if (/^(.)\1{3,}$/.test(compact) || /^(asdf|qwer|zxcv|1234|abcd)+$/i.test(compact)) {
      return true;
    }

    return false;
  };

  // Evaluation rubric helper for evaluating question responses
  const evaluateAnswerRubric = (questionObj, submittedAnswer) => {
    const rawTrimmed = (submittedAnswer || '').trim();

    // 1. Non-answer check: Award strictly 0 points
    if (isNonAnswer(rawTrimmed)) {
      return {
        score: 0,
        technicalAccuracy: 0,
        communicationClarity: 0,
        answerStructure: 0,
        aiFeedback: `No answer provided (0/100). The candidate answered "${rawTrimmed.slice(0, 40)}" and did not attempt the technical prompt.`,
        strengths: [
          "Acknowledged knowledge gap honestly instead of fabricating incorrect information."
        ],
        weaknesses: [
          "Did not attempt the technical question or demonstrate foundational knowledge.",
          "Lacks familiarity with the required domain concept."
        ],
        improvementSuggestions: [
          "Review core technical concepts, architecture mechanisms, and industry use-cases for this topic.",
          "In technical interviews, try to reason from first principles or discuss related technologies rather than passing completely."
        ],
        modelAnswer: questionObj?.hint || questionObj?.expected_focus || "Optimal response explains core principles, architecture mechanisms, and concrete system trade-offs.",
      };
    }

    const words = rawTrimmed.split(/\s+/).filter(Boolean);
    const wordCount = words.length;
    const lowerAns = rawTrimmed.toLowerCase();

    const isBehavioral = String(questionObj?.modality || questionObj?.category || '').toLowerCase().includes('behavioral') ||
      String(questionObj?.modality || questionObj?.category || '').toLowerCase().includes('star');

    const isDsa = String(questionObj?.modality || questionObj?.category || '').toLowerCase().includes('dsa') ||
      String(questionObj?.modality || questionObj?.category || '').toLowerCase().includes('algo');

    const techKeywords = isBehavioral
      ? [
          "situation", "task", "action", "result", "metric", "stakeholder", "resolved", "conflict",
          "priority", "impact", "negotiated", "deadline", "team", "outage", "diagnose", "leadership",
          "trade-off", "responsibility", "communication", "collaborate", "deliverable", "accountability"
        ]
      : isDsa
      ? [
          "complexity", "o(n)", "o(1)", "o(log n)", "hash", "tree", "graph", "queue", "stack",
          "dynamic programming", "sliding window", "pointer", "binary search", "traversal", "recursion",
          "array", "dag", "matrix", "attention", "vector", "time complexity", "space complexity"
        ]
      : [
          "redis", "cache", "caching", "sql", "nosql", "postgres", "mongodb", "api", "database",
          "latency", "throughput", "index", "indexing", "sharding", "async", "await", "event loop",
          "star", "trade-off", "performance", "quantization", "kv cache", "flashattention",
          "attention", "transformer", "gpu", "memory", "vllm", "kubernetes", "docker",
          "microservices", "load balancer", "acid", "security", "jwt", "concurrency", "http",
          "rest", "graphql", "grpc", "ci/cd", "observability", "batching", "fp4", "int8", "rag"
        ];
    const matchedKeywords = techKeywords.filter((k) => lowerAns.includes(k));
    const hasNumbers = /\b\d+(\.\d+)?(ms|s|%|k|req|rps|gb|mb)?\b/.test(lowerAns);
    const hasStructure = /first|second|specifically|because|however|for example|trade-off|situation|task|action|result/.test(lowerAns);

    // 2. Trivial response check (< 6 words with 0 keywords)
    if (wordCount < 6 && matchedKeywords.length === 0) {
      return {
        score: 5,
        technicalAccuracy: 5,
        communicationClarity: 10,
        answerStructure: 5,
        aiFeedback: `Insufficient response (5/100). The submission contains no relevant technical explanation or domain terminology for this question.`,
        strengths: ["Submitted a brief response."],
        weaknesses: ["Answer lacks technical depth, reasoning, and domain terminology."],
        improvementSuggestions: [
          "Provide a thorough technical answer covering definitions, architecture, and trade-offs."
        ],
        modelAnswer: questionObj?.hint || questionObj?.expected_focus || "Optimal answer explains core principles, architecture mechanisms, and concrete system trade-offs.",
      };
    }

    // 3. Genuine response scoring
    let techAccuracy = Math.min(95, 25 + matchedKeywords.length * 12);
    if (wordCount < 15) techAccuracy = Math.min(40, techAccuracy);

    let depthScore = 25;
    if (wordCount >= 90) depthScore = 92;
    else if (wordCount >= 50) depthScore = 78;
    else if (wordCount >= 25) depthScore = 65;
    else if (wordCount >= 15) depthScore = 45;

    let clarityScore = 35 + (hasStructure ? 30 : 0) + (hasNumbers ? 20 : 0);
    clarityScore = Math.min(95, clarityScore);

    const calculatedScore = Math.min(
      96,
      Math.max(10, Math.round((techAccuracy * 0.40) + (depthScore * 0.30) + (clarityScore * 0.30)))
    );

    return {
      score: calculatedScore,
      technicalAccuracy: Math.min(96, techAccuracy),
      communicationClarity: clarityScore,
      answerStructure: clarityScore,
      aiFeedback: calculatedScore >= 80
        ? `Solid technical explanation (${calculatedScore}/100) demonstrating clear engineering comprehension and vocabulary.`
        : calculatedScore >= 60
        ? `Good foundational response (${calculatedScore}/100). Adding concrete numerical metrics and edge cases will improve your score.`
        : `Needs expansion (${calculatedScore}/100). Elaborate on architectural mechanisms, concrete technologies, and trade-offs.`,
      strengths: matchedKeywords.length > 0
        ? [`Used relevant domain concepts: ${matchedKeywords.slice(0, 3).join(', ')}`, "Answered prompt with technical reasoning"]
        : ["Submitted an initial explanation", "Sentence structure is readable"],
      weaknesses: !hasNumbers
        ? ["Lacks quantitative benchmarks or system scale estimates (latency, req/s, cache hit %)", "Can cover failover edge cases"]
        : ["Elaborate on edge cases and failure recovery"],
      modelAnswer: questionObj?.hint || questionObj?.expected_focus || "Focus on clear cause-and-effect reasoning with measurable outcomes and trade-offs.",
    };
  };

  // Submit all answers for comprehensive evaluation
  const handleSubmitAllAnswers = async () => {
    // Safety check: ensure all questions have answers
    const unanswered = [];
    for (let i = 1; i <= totalQuestions; i++) {
      if (!(answersMap[i] || '').trim()) {
        unanswered.push(i);
      }
    }
    if (unanswered.length > 0) return;

    setSessionState('evaluating');

    try {
      const completedList = [];

      for (let i = 1; i <= totalQuestions; i++) {
        const qObj = questionsList[i - 1] || currentQuestion || defaultQuestions[0];
        const submittedAnswer = (answersMap[i] || '').trim();

        let formattedEval = null;

        // If explicitly non-answer (NA, i donot know, etc.), enforce 0 evaluation
        if (isNonAnswer(submittedAnswer)) {
          formattedEval = evaluateAnswerRubric(qObj, submittedAnswer);
        } else if (activeSession && activeSession.interview_id) {
          try {
            const res = await interviewService.submitAnswer(activeSession.interview_id, submittedAnswer);
            if (res && res.evaluation) {
              const rawEval = res.evaluation;
              formattedEval = {
                score: typeof rawEval.score === 'number' ? rawEval.score : 75,
                technicalAccuracy: typeof (rawEval.technical_accuracy ?? rawEval.correctness) === 'number'
                  ? (rawEval.technical_accuracy ?? rawEval.correctness)
                  : 75,
                communicationClarity: typeof (rawEval.communication_quality ?? rawEval.clarity) === 'number'
                  ? (rawEval.communication_quality ?? rawEval.clarity)
                  : 75,
                answerStructure: typeof (rawEval.clarity ?? rawEval.answer_structure) === 'number'
                  ? (rawEval.clarity ?? rawEval.answer_structure)
                  : 75,
                aiFeedback: rawEval.ai_feedback || rawEval.feedback || "Good response addressing key points.",
                strengths: rawEval.strengths || ["Clearly articulated approach", "Used relevant terminology"],
                weaknesses: rawEval.weaknesses || ["Could elaborate on edge cases or metrics"],
                modelAnswer: rawEval.model_answer || rawEval.ideal_response || "Optimal answer highlights systematic problem decomposition and explicit architectural trade-offs.",
              };
            }
          } catch (e) {
            console.warn(`Backend submit for question ${i} failed, using local rubric fallback:`, e);
          }
        }

        if (!formattedEval) {
          formattedEval = evaluateAnswerRubric(qObj, submittedAnswer);
        }

        completedList.push({
          questionNumber: i,
          question: qObj.question,
          category: qObj.category || qObj.skill || 'Technical',
          answer: submittedAnswer,
          evaluation: formattedEval,
        });
      }

      setCompletedQuestionsList(completedList);

      const overallScore = Math.round(
        completedList.reduce((acc, q) => acc + (typeof q.evaluation?.score === 'number' ? q.evaluation.score : 0), 0) / completedList.length
      );

      const allStrengths = Array.from(new Set(completedList.flatMap(q => q.evaluation?.strengths || []))).slice(0, 4);
      const allWeaknesses = Array.from(new Set(completedList.flatMap(q => q.evaluation?.weaknesses || []))).slice(0, 4);

      setFinalSessionSummary({
        overall_score: overallScore,
        strengths: allStrengths.length > 0 ? allStrengths : ["Demonstrated technical attempt", "Systematic reasoning"],
        weaknesses: allWeaknesses.length > 0 ? allWeaknesses : ["Elaborate on production metrics and failure modes"],
      });

      const targetDomain = sessionConfig?.role || user?.targetRole || 'Full Stack Engineer';
      const historyItem = {
        id: activeSession?.interview_id || `session-${Date.now()}`,
        date: new Date().toLocaleDateString(),
        role: targetDomain,
        type: (sessionConfig?.modality || 'Technical Drill').toUpperCase(),
        difficulty: sessionConfig?.difficulty || 'Medium',
        questionCount: totalQuestions,
        durationText: formatTimer(secondsElapsed),
        score: overallScore,
        status: overallScore >= 60 ? 'Completed' : 'Needs Practice',
        strengths: allStrengths,
        weaknesses: allWeaknesses,
        questions: completedList,
      };

      const updatedHistory = [historyItem, ...getStoredInterviewHistory()];
      saveInterviewHistory(updatedHistory);
      setHistory(updatedHistory);

      if (toggleTaskCompletion) {
        toggleTaskCompletion('mock_interview');
      }
      if (toastNotification) {
        toastNotification('Mock interview submitted and evaluated successfully!');
      }

      setSessionState('results');
    } catch (e) {
      console.error("Submission failed:", e);
      setSessionState('results');
    }
  };

  // Legacy single answer submit alias
  const handleSubmitAnswer = handleSubmitAllAnswers;

  // Move to next question after reviewing per-question feedback
  const handleProceedToNextQuestion = () => {
    if (nextQuestionPending) {
      setCurrentQuestion(nextQuestionPending);
      setQuestionNumber((prev) => prev + 1);
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

  const currentQ = questionsList[questionNumber - 1] || currentQuestion || defaultQuestions[0];
  const wordCount = answerText.trim() ? answerText.trim().split(/\s+/).length : 0;

  // Calculate answer progress across all session questions
  const answeredCount = Array.from({ length: totalQuestions }).filter((_, idx) => {
    const stepNum = idx + 1;
    return (answersMap[stepNum] || '').trim().length > 0;
  }).length;

  const allAnswered = totalQuestions > 0 && answeredCount === totalQuestions;

  const unAnsweredQuestions = Array.from({ length: totalQuestions })
    .map((_, idx) => idx + 1)
    .filter((stepNum) => !(answersMap[stepNum] || '').trim().length);

  // Calculate aggregated scores for final review
  const calculatedOverallScore = typeof finalSessionSummary?.overall_score === 'number'
    ? finalSessionSummary.overall_score
    : (
      completedQuestionsList.length > 0
        ? Math.round(completedQuestionsList.reduce((acc, q) => acc + (typeof q.evaluation?.score === 'number' ? q.evaluation.score : 0), 0) / completedQuestionsList.length)
        : 0
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
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-bold text-indigo-400">SESSION PROGRESS:</span>
                <span className="text-white">Question {questionNumber} of {totalQuestions}</span>
                <span className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/30 text-[11px] font-sans font-medium">
                  {sessionConfig?.modality || 'System Architecture & Design'}
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

            {/* Step Indicators - Clickable Q1, Q2, Q3 pills with real-time answer status */}
            <div className="grid grid-cols-3 sm:grid-cols-5 gap-2.5 pt-1">
              {Array.from({ length: totalQuestions }).map((_, idx) => {
                const stepNum = idx + 1;
                const isCurrent = stepNum === questionNumber;
                const hasAnswer = (answersMap[stepNum] || '').trim().length > 0;

                return (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleSelectQuestion(stepNum)}
                    className={`p-2.5 rounded-xl border text-center transition-all cursor-pointer select-none flex items-center justify-center gap-1.5 ${
                      isCurrent
                        ? 'bg-indigo-600/30 border-indigo-500 text-white font-bold ring-2 ring-indigo-500/50 shadow-md'
                        : hasAnswer
                        ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-400 hover:bg-emerald-500/20'
                        : 'bg-[#0b0e17] border-[#1e2638] text-slate-400 hover:border-slate-500 hover:text-slate-200'
                    }`}
                  >
                    {hasAnswer && <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />}
                    <span className="text-xs font-mono font-semibold">Q{stepNum}</span>
                    {hasAnswer ? (
                      <span className="text-[10px] text-emerald-400 font-sans hidden sm:inline">(Answered)</span>
                    ) : (
                      <span className="text-[10px] text-slate-500 font-sans hidden sm:inline">(Empty)</span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Question Prompt Card */}
          <div className="p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-lg">
            <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-[#232b3e]">
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded bg-purple-500/10 text-purple-300 border border-purple-500/20 text-[10px] font-mono uppercase tracking-wider">
                  {currentQ.modality || sessionConfig?.modality || 'System Architecture'}
                </span>
                <span className="text-xs font-mono font-semibold text-indigo-400 uppercase tracking-wider">
                  Focus: {currentQ.skill || currentQ.category || currentQ.topic || 'Core Technical'}
                </span>
              </div>
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

            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-3 border-t border-[#232b3e]">
              <div className="flex items-center gap-2 text-xs font-mono">
                {allAnswered ? (
                  <span className="flex items-center gap-1.5 text-emerald-400 font-semibold">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span>All {totalQuestions} questions answered. Submit is now enabled!</span>
                  </span>
                ) : (
                  <span className="flex items-center gap-1.5 text-amber-400">
                    <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
                    <span>
                      Write answers for all questions to enable submit ({answeredCount}/{totalQuestions} written — missing: {unAnsweredQuestions.map(n => `Q${n}`).join(', ')})
                    </span>
                  </span>
                )}
              </div>

              <div className="flex items-center gap-2 shrink-0">
                {questionNumber > 1 && (
                  <button
                    type="button"
                    onClick={() => handleSelectQuestion(questionNumber - 1)}
                    className="px-3.5 py-2 rounded-xl text-xs font-mono text-slate-300 hover:text-white bg-[#1a2133] hover:bg-[#232b3e] border border-[#232b3e] transition-colors"
                  >
                    ← Q{questionNumber - 1}
                  </button>
                )}

                {questionNumber < totalQuestions && (
                  <button
                    type="button"
                    onClick={() => handleSelectQuestion(questionNumber + 1)}
                    className="px-3.5 py-2 rounded-xl text-xs font-mono text-indigo-300 hover:text-white bg-[#1a2133] hover:bg-[#232b3e] border border-indigo-500/30 transition-colors"
                  >
                    Q{questionNumber + 1} →
                  </button>
                )}

                <button
                  type="button"
                  onClick={handleSubmitAllAnswers}
                  disabled={!allAnswered}
                  className={`px-5 py-2.5 rounded-xl text-sm font-semibold transition-all flex items-center gap-2 shadow-md ${
                    allAnswered
                      ? 'bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white shadow-indigo-600/30 cursor-pointer animate-pulse'
                      : 'bg-[#1a2133] border border-[#232b3e] text-slate-500 cursor-not-allowed opacity-50'
                  }`}
                  title={!allAnswered ? `Please write answers for ${unAnsweredQuestions.map(n => `Q${n}`).join(', ')} before submitting` : 'Submit all answers for evaluation'}
                >
                  <Send className="w-4 h-4" />
                  <span>Submit Answer for Evaluation</span>
                </button>
              </div>
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
                <span className={`px-3.5 py-1 rounded-full text-base font-mono font-bold border ${
                  (currentQuestionEval.score ?? 0) >= 70
                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                    : (currentQuestionEval.score ?? 0) >= 40
                    ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                    : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                }`}>
                  Question Score: {currentQuestionEval.score ?? 0}/100
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
                <span className={`px-4 py-1.5 rounded-full text-lg font-mono font-bold border ${
                  calculatedOverallScore >= 70
                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                    : calculatedOverallScore >= 40
                    ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                    : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                }`}>
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
                const score = typeof item.evaluation?.score === 'number' ? item.evaluation.score : 0;
                const scoreColor = score >= 70 ? 'text-emerald-400' : score >= 40 ? 'text-amber-400' : 'text-rose-400';

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
                        <span className={`text-xs font-mono font-bold ${scoreColor}`}>{score}%</span>
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
