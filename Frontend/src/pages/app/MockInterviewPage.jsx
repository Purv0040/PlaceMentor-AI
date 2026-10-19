import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/UserContext';
<<<<<<< HEAD
import { defaultQuestions, getDynamicQuestion, getStoredInterviewHistory, saveInterviewHistory } from '../../data/interviewData';
=======
import { defaultQuestions } from '../../data/interviewData';
>>>>>>> f5f3d0fa4107f7c6729cfe2cb922a1872ad02460
import { interviewService } from '../../services/interviewService';
import { InterviewSetupModal } from '../../components/practice/InterviewSetupModal';
import {
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
  Code2,
  RefreshCw,
  Eye,
  X,
  ChevronRight,
  FileText,
  Lightbulb,
  Check,
<<<<<<< HEAD
  RefreshCw,
  Code,
  FileText,
  ChevronDown,
  ChevronUp,
  X,
  BookOpen,
  Info
=======
  Target,
  Terminal,
  Trash2,
>>>>>>> f5f3d0fa4107f7c6729cfe2cb922a1872ad02460
} from 'lucide-react';

/**
 * Returns role-tailored interview tracks dynamically matched to the student's target role.
 */
export function getRoleModalityCards(targetRole = '') {
  const r = (targetRole || '').toLowerCase();

  // AWS / DevOps & Cloud Engineer Track
  if (r.includes('devops') || r.includes('cloud') || r.includes('aws') || r.includes('infrastructure') || r.includes('sre')) {
    return [
      {
        id: 'cloud_devops',
        modality: 'technical',
        title: 'Cloud & Infrastructure Automation',
        icon: 'terminal',
        badge: 'DevOps & SRE Track',
        description: 'CI/CD Pipelines (GitHub Actions/Jenkins), Linux & Shell scripting, Docker, Kubernetes cluster ops, and Terraform IaC.',
        questionRange: '1–5 Questions',
        actionLabel: 'Start DevOps Drill',
        accentColor: 'emerald',
      },
      {
        id: 'cloud_architecture',
        modality: 'system_design',
        title: 'Cloud Architecture & Resilience',
        icon: 'layers',
        badge: 'Multi-Region Cloud Scale',
        description: 'Multi-Region AWS Architectures, High Availability, Auto-Scaling, ECS/EKS, S3 & RDS/DynamoDB, and Disaster Recovery.',
        questionRange: '1–5 Questions',
        actionLabel: 'Start Architecture',
        accentColor: 'indigo',
      },
      {
        id: 'devops_behavioral',
        modality: 'behavioral',
        title: 'Incident & On-Call Leadership (STAR)',
        icon: 'award',
        badge: 'Production Reliability',
        description: 'Production outages (SEV-1), blameless post-mortems, on-call escalations, and cross-functional SLA/SLO defense.',
        questionRange: '1–5 Questions',
        actionLabel: 'Start Behavioral',
        accentColor: 'purple',
      },
    ];
  }

  // Cybersecurity Track
  if (r.includes('security') || r.includes('cyber')) {
    return [
      {
        id: 'security_drill',
        modality: 'technical',
        title: 'Threat & Vulnerability Analysis',
        icon: 'terminal',
        badge: 'SecOps & Penetration',
        description: 'OWASP Top 10 vulnerabilities, penetration testing, cryptography, Wireshark packet triage, and Linux security internals.',
        questionRange: '1–5 Questions',
        actionLabel: 'Start Security Drill',
        accentColor: 'emerald',
      },
      {
        id: 'security_architecture',
        modality: 'system_design',
        title: 'Security Architecture & Zero Trust',
        icon: 'layers',
        badge: 'Enterprise Defense',
        description: 'IAM least privilege, network segmentation, SIEM/SOC event correlation, threat modeling, and PKI infrastructure design.',
        questionRange: '1–5 Questions',
        actionLabel: 'Start Architecture',
        accentColor: 'indigo',
      },
      {
        id: 'security_incident',
        modality: 'behavioral',
        title: 'Incident Response & Crisis (STAR)',
        icon: 'award',
        badge: 'Breach Containment',
        description: 'Active breach containment, forensic triage, compliance audit defense, and cross-team security remediation under pressure.',
        questionRange: '1–5 Questions',
        actionLabel: 'Start Behavioral',
        accentColor: 'purple',
      },
    ];
  }

  // AI / ML Engineer Track
  if (r.includes('ai') || r.includes('ml') || r.includes('machine learning')) {
    return [
      {
        id: 'ml_drill',
        modality: 'technical',
        title: 'ML Foundations & Algorithm Drill',
        icon: 'code',
        badge: 'Deep Learning & Math',
        description: 'PyTorch/TensorFlow, gradient descent optimization, loss functions, Transformer attention, and model evaluation metrics.',
        questionRange: '1–5 Questions',
        actionLabel: 'Start ML Drill',
        accentColor: 'emerald',
      },
      {
        id: 'ml_sys_design',
        modality: 'system_design',
        title: 'ML System Design & MLOps',
        icon: 'layers',
        badge: 'High-Throughput Inference',
        description: 'End-to-end ML training & inference pipelines, vector databases (Chroma/FAISS), embedding retrieval, and GPU scaling.',
        questionRange: '1–5 Questions',
        actionLabel: 'Start Architecture',
        accentColor: 'indigo',
      },
      {
        id: 'ml_leadership',
        modality: 'behavioral',
        title: 'AI Leadership & Ethics (STAR)',
        icon: 'award',
        badge: 'Model Governance',
        description: 'Model drift mitigation, research-to-production transitions, technical trade-offs, and ethical AI deployment.',
        questionRange: '1–5 Questions',
        actionLabel: 'Start Behavioral',
        accentColor: 'purple',
      },
    ];
  }

  // Data Roles Track
  if (r.includes('data')) {
    return [
      {
        id: 'data_drill',
        modality: 'technical',
        title: 'Data & SQL Analytics Drill',
        icon: 'code',
        badge: 'Query & Transforms',
        description: 'Complex SQL window functions, aggregations, Pandas transformations, statistical hypothesis testing, and query profiling.',
        questionRange: '1–5 Questions',
        actionLabel: 'Start Data Drill',
        accentColor: 'emerald',
      },
      {
        id: 'data_architecture',
        modality: 'system_design',
        title: 'Data Architecture & Pipelines',
        icon: 'layers',
        badge: 'Data Warehousing & Streaming',
        description: 'Batch & streaming ETL/ELT pipelines, Snowflake/BigQuery warehousing, Kafka message streams, and data lake partitioning.',
        questionRange: '1–5 Questions',
        actionLabel: 'Start Architecture',
        accentColor: 'indigo',
      },
      {
        id: 'data_behavioral',
        modality: 'behavioral',
        title: 'Stakeholder & Metric Alignment (STAR)',
        icon: 'award',
        badge: 'Cross-functional Insights',
        description: 'Metric discrepancies, executive presentations, KPI trade-offs, and quantified business impact stories.',
        questionRange: '1–5 Questions',
        actionLabel: 'Start Behavioral',
        accentColor: 'purple',
      },
    ];
  }

  // Standard SDE / Full Stack / Backend Track:
  return [
    {
      id: 'dsa_drill',
      modality: 'dsa',
      title: 'Technical & DSA Drill',
      icon: 'code',
      badge: 'Algorithms & LeetCode',
      description: 'Topological Sort, 2D Dynamic Programming, Tree Traversals, complexity trade-offs, and algorithm defense.',
      questionRange: '1–5 Questions',
      actionLabel: 'Start DSA',
      accentColor: 'emerald',
    },
    {
      id: 'system_architecture',
      modality: 'system_design',
      title: 'System Architecture & Design',
      icon: 'layers',
      badge: 'Distributed Scale',
      description: 'Scalability, Caching (Redis), Message Brokering (Kafka), Database Sharding, and CAP theorem trade-offs.',
      questionRange: '1–5 Questions',
      actionLabel: 'Start Architecture',
      accentColor: 'indigo',
    },
    {
      id: 'behavioral_star',
      modality: 'behavioral',
      title: 'Behavioral & Leadership (STAR)',
      icon: 'award',
      badge: 'Tier-1 STAR Competencies',
      description: 'Production outages, technical disagreements, cross-functional ownership, and quantified impact stories.',
      questionRange: '1–5 Questions',
      actionLabel: 'Start Behavioral',
      accentColor: 'purple',
    },
  ];
}

export const MockInterviewPage = () => {
  const navigate = useNavigate();
  const { user } = useUser();

<<<<<<< HEAD
  // Navigation states: 'idle' | 'active' | 'evaluating' | 'question_feedback' | 'results'
=======
  // Active student's target role from profile context
  const targetRole = user?.targetRole || user?.career?.targetRole || 'Full Stack Engineer';

  // Dynamic modalities adapted to user's target role
  const modalityCards = useMemo(() => getRoleModalityCards(targetRole), [targetRole]);

  // Session State: 'idle' | 'active' | 'evaluating' | 'question_feedback' | 'results'
>>>>>>> f5f3d0fa4107f7c6729cfe2cb922a1872ad02460
  const [sessionState, setSessionState] = useState('idle');
  const [isSetupOpen, setIsSetupOpen] = useState(false);
  const [setupInitialConfig, setSetupInitialConfig] = useState(null);

  // Active Session Data
  const [sessionConfig, setSessionConfig] = useState(null);
  const [activeSession, setActiveSession] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [questionNumber, setQuestionNumber] = useState(1);
  const [totalQuestions, setTotalQuestions] = useState(3);
  const [answerText, setAnswerText] = useState('');
  const [showHint, setShowHint] = useState(false);
  const [secondsElapsed, setSecondsElapsed] = useState(0);
<<<<<<< HEAD

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
=======
  const [singleQuestionFeedback, setSingleQuestionFeedback] = useState(null);
  const [nextQuestionCache, setNextQuestionCache] = useState(null);

  // Completed Session Result
  const [evalResult, setEvalResult] = useState(null);

  // History & Reporting State
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [selectedReport, setSelectedReport] = useState(null);
  const [reportQuestions, setReportQuestions] = useState([]);
  const [loadingReportDetails, setLoadingReportDetails] = useState(false);
>>>>>>> f5f3d0fa4107f7c6729cfe2cb922a1872ad02460

  // Confirmation dialog for ending session
  const [confirmQuitOpen, setConfirmQuitOpen] = useState(false);

  // Fetch real interview history from backend API
  const fetchHistory = useCallback(async () => {
    setLoadingHistory(true);
    try {
      const apiHistory = await interviewService.getInterviewHistory();
<<<<<<< HEAD
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
=======
      if (Array.isArray(apiHistory) && apiHistory.length > 0) {
        const formatted = apiHistory.map((item) => {
          const isCompleted = item.status === 'completed' || (item.overall_score !== null && item.overall_score !== undefined);
          return {
            id: item.interview_id || item.id,
            date: item.created_at || item.started_at
              ? new Date(item.created_at || item.started_at).toLocaleDateString(undefined, {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric',
                })
              : 'Recent',
            role: item.target_role || targetRole,
            type: formatModalityLabel(item.interview_type || 'technical'),
            rawType: item.interview_type || 'technical',
            difficulty: item.difficulty || 'medium',
            currentQuestionNum: item.current_question || 1,
            totalQuestions: item.total_questions || 3,
            durationText: item.completed_at && item.started_at
              ? `${Math.max(1, Math.round((new Date(item.completed_at) - new Date(item.started_at)) / 60000))} mins`
              : isCompleted
              ? `${item.total_questions || 3} questions`
              : `In Progress · ${item.total_questions || 3} Qs`,
            score: isCompleted ? (item.overall_score ?? (item.evaluation?.overall_score ?? null)) : null,
            status: isCompleted ? 'completed' : 'active',
            categoryScores: item.category_scores || item.evaluation?.category_scores || {},
            strengths: item.evaluation?.strengths || item.strengths || [],
            weaknesses: item.evaluation?.weaknesses || item.weaknesses || [],
            recommendations: item.evaluation?.recommendations || item.recommendations || [],
            evaluation: item.evaluation || null,
          };
        });
>>>>>>> f5f3d0fa4107f7c6729cfe2cb922a1872ad02460
        setHistory(formatted);
      } else {
        setHistory([]);
      }
    } catch (e) {
      setHistory([]);
    } finally {
      setLoadingHistory(false);
    }
  }, [targetRole]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  // Timer for active interview
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

  // Keyboard accessibility for ESC key to close modal dialogs
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        if (selectedReport) setSelectedReport(null);
        if (confirmQuitOpen) setConfirmQuitOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedReport, confirmQuitOpen]);

  const formatTimer = (totalSeconds) => {
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

<<<<<<< HEAD
  // Start interview session
=======
  // Helper to format modality labels
  function formatModalityLabel(modality = '') {
    const clean = modality.toLowerCase();
    if (clean.includes('dsa') || clean === 'coding') return 'Technical / DSA';
    if (clean.includes('system') || clean.includes('design') || clean === 'architecture') return 'System Design';
    if (clean.includes('behavioral') || clean.includes('star') || clean === 'hr') return 'Behavioral / STAR';
    return 'Full Technical Mock';
  }

  // Calculate dynamic calibration metrics from real saved completed sessions
  const calibrationMetrics = useMemo(() => {
    const completedSessions = history.filter((s) => s.status === 'completed' && s.score !== null && s.score !== undefined);
    const inProgressSessions = history.filter((s) => s.status === 'active');

    if (completedSessions.length === 0) {
      return {
        hasData: false,
        totalSessions: history.length,
        completedCount: 0,
        inProgressCount: inProgressSessions.length,
        latestInProgress: inProgressSessions[0] || null,
        averageScore: null,
        avgTechnical: null,
        avgStructure: null,
        statusLabel: inProgressSessions.length > 0 ? 'Sessions In Progress' : 'Not Assessed',
      };
    }

    const totalScore = completedSessions.reduce((acc, curr) => acc + curr.score, 0);
    const avgScore = Math.round(totalScore / completedSessions.length);

    // Calculate subcategory averages if available
    let techSum = 0;
    let techCount = 0;
    let structSum = 0;
    let structCount = 0;

    completedSessions.forEach((s) => {
      const cats = s.categoryScores || {};
      const techVal = cats.Technical || cats.technical || cats.core;
      if (typeof techVal === 'number') {
        techSum += techVal;
        techCount++;
      }
      const structVal = cats.Structure || cats.structure || cats.Communication || cats.communication;
      if (typeof structVal === 'number') {
        structSum += structVal;
        structCount++;
      }
    });

    const avgTech = techCount > 0 ? Math.round(techSum / techCount) : avgScore;
    const avgStruct = structCount > 0 ? Math.round(structSum / structCount) : Math.max(50, avgScore - 4);

    return {
      hasData: true,
      totalSessions: completedSessions.length,
      completedCount: completedSessions.length,
      inProgressCount: inProgressSessions.length,
      latestInProgress: inProgressSessions[0] || null,
      averageScore: avgScore,
      avgTechnical: avgTech,
      avgStructure: avgStruct,
      statusLabel: avgScore >= 80 ? 'Interview Ready' : avgScore >= 65 ? 'Solid Baseline' : 'Needs Practice',
    };
  }, [history]);

  // Handle Launching Setup from Header or Modality Card
  const handleOpenSetupWithModality = (preselectedModality) => {
    setSetupInitialConfig({
      role: targetRole,
      modality: preselectedModality || 'technical',
      difficulty: 'medium',
      questionCount: 3,
    });
    setIsSetupOpen(true);
  };

  // Start Interview Flow
>>>>>>> f5f3d0fa4107f7c6729cfe2cb922a1872ad02460
  const handleStartInterview = async (config) => {
    setSessionConfig(config);
    setAnswerText('');
    setSecondsElapsed(0);
    setShowHint(false);
<<<<<<< HEAD
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
=======
    setSingleQuestionFeedback(null);
    setNextQuestionCache(null);
    setErrorMessage(null);
    setSessionState('evaluating');

    try {
      const res = await interviewService.startInterview(config);
      if (res && (res.interview_id || res.id)) {
        const interviewId = res.interview_id || res.id;
        setActiveSession({ ...res, interview_id: interviewId });
>>>>>>> f5f3d0fa4107f7c6729cfe2cb922a1872ad02460
        setTotalQuestions(res.total_questions || config.questionCount || 3);
        setQuestionNumber(res.current_question || 1);

        if (res.current_question_data) {
          setCurrentQuestion(res.current_question_data);
        } else {
<<<<<<< HEAD
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
=======
          // Fetch current question explicitly if not in payload
          const currentData = await interviewService.getCurrentQuestion(interviewId);
          if (currentData && currentData.question) {
            setCurrentQuestion(currentData.question);
          } else {
            setCurrentQuestion(defaultQuestions[0]);
          }
        }
        setSessionState('active');
      } else {
        // Fallback to local structured question if API unauthenticated
        setCurrentQuestion(defaultQuestions[0]);
        setQuestionNumber(1);
        setTotalQuestions(config.questionCount || 3);
        setActiveSession({ interview_id: `local_${Date.now()}` });
        setSessionState('active');
      }
    } catch (e) {
      setErrorMessage(e.message || 'Could not start interview session. Operating in local drill mode.');
      setCurrentQuestion(defaultQuestions[0]);
      setQuestionNumber(1);
      setTotalQuestions(config.questionCount || 3);
      setActiveSession({ interview_id: `local_${Date.now()}` });
>>>>>>> f5f3d0fa4107f7c6729cfe2cb922a1872ad02460
      setSessionState('active');
    }
  };

<<<<<<< HEAD
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
=======
  // Submit Answer to Current Question
  const handleSubmitAnswer = async () => {
    const trimmed = answerText.trim();
    if (!trimmed) return;

>>>>>>> f5f3d0fa4107f7c6729cfe2cb922a1872ad02460
    setSessionState('evaluating');
    setErrorMessage(null);

    try {
<<<<<<< HEAD
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
=======
      if (activeSession && activeSession.interview_id && !activeSession.interview_id.startsWith('local_')) {
        const res = await interviewService.submitAnswer(activeSession.interview_id, trimmed);
        if (res) {
          const evaluation = res.evaluation || {};
          const isLast = res.is_last_question || (questionNumber >= totalQuestions);

          if (isLast) {
            // Finalize entire interview
            const finalSummary = res.session_result || (await interviewService.completeInterview(activeSession.interview_id));
            const formattedResult = {
              overallScore: finalSummary?.overall_score ?? (evaluation.score || 75),
              technicalAccuracy: evaluation.technical_accuracy ?? (evaluation.correctness ?? 75),
              communicationClarity: evaluation.communication_quality ?? (evaluation.clarity ?? 75),
              answerStructure: evaluation.clarity ?? 75,
              feedback: finalSummary?.overall_feedback || evaluation.ai_feedback || 'Completed role interview evaluation.',
              strengths: finalSummary?.strengths?.length > 0 ? finalSummary.strengths : (evaluation.strengths || ['Demonstrated good technical concepts']),
              weaknesses: finalSummary?.weaknesses?.length > 0 ? finalSummary.weaknesses : (evaluation.weaknesses || ['Include more specific trade-offs and metrics']),
              recommendations: finalSummary?.recommendations || evaluation.improvement_suggestions || [],
              categoryScores: finalSummary?.category_scores || { Technical: 75, Communication: 75 },
            };
            setEvalResult(formattedResult);
>>>>>>> f5f3d0fa4107f7c6729cfe2cb922a1872ad02460
            setSessionState('results');
            fetchHistory();
            return;
          } else {
            // Intermediate question: show question feedback step
            setSingleQuestionFeedback({
              score: evaluation.score || 75,
              feedback: evaluation.ai_feedback || 'Answer recorded and evaluated.',
              strengths: evaluation.strengths || [],
              weaknesses: evaluation.weaknesses || [],
              suggestions: evaluation.improvement_suggestions || [],
            });
            setNextQuestionCache(res.next_question);
            setSessionState('question_feedback');
            return;
          }
        }
      }

<<<<<<< HEAD
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
=======
      // Offline / Local Simulation fallback
      const wordCount = trimmed.split(/\s+/).length;
      const calcScore = Math.min(92, Math.max(55, 65 + Math.min(25, Math.floor(wordCount / 4))));
      const isLastLocal = questionNumber >= totalQuestions;

      if (isLastLocal) {
        setEvalResult({
          overallScore: calcScore,
          technicalAccuracy: calcScore,
          communicationClarity: Math.max(50, calcScore - 4),
          answerStructure: calcScore,
          feedback: `Good technical answer covering core concepts for target role ${targetRole}.`,
          strengths: ['Identified primary architecture components', 'Clear structured response format'],
          weaknesses: ['Add concrete quantitative metrics and latency trade-offs'],
          recommendations: ['Practice STAR structured bullet points when answering scenario questions'],
          categoryScores: { Technical: calcScore, Communication: calcScore },
        });
        setSessionState('results');
      } else {
        setSingleQuestionFeedback({
          score: calcScore,
          feedback: 'Solid response articulation with relevant technical keywords.',
          strengths: ['Clear logical transitions'],
          weaknesses: ['Elaborate with specific benchmark numbers'],
          suggestions: ['State time/space complexity or performance boundaries'],
        });
        setNextQuestionCache(defaultQuestions[questionNumber % defaultQuestions.length]);
        setSessionState('question_feedback');
      }
    } catch (e) {
      setErrorMessage(e.message || 'Error evaluating answer. You may proceed to the next question or retry.');
      setSessionState('active');
    }
  };

  // Move to Next Question
  const handleProceedToNextQuestion = () => {
    if (nextQuestionCache) {
      setCurrentQuestion(nextQuestionCache);
    } else {
      setCurrentQuestion(defaultQuestions[questionNumber % defaultQuestions.length]);
    }
    setQuestionNumber((prev) => prev + 1);
    setAnswerText('');
    setShowHint(false);
    setSingleQuestionFeedback(null);
    setNextQuestionCache(null);
    setSessionState('active');
  };

  // End Session Early
  const handleEndSessionEarly = async () => {
    setConfirmQuitOpen(false);
    if (activeSession && activeSession.interview_id && !activeSession.interview_id.startsWith('local_')) {
      setSessionState('evaluating');
      try {
        const finalRes = await interviewService.completeInterview(activeSession.interview_id);
        if (finalRes) {
          setEvalResult({
            overallScore: finalRes.overall_score || 70,
            technicalAccuracy: finalRes.category_scores?.Technical || 70,
            communicationClarity: finalRes.category_scores?.Communication || 70,
            answerStructure: 70,
            feedback: 'Session ended early by candidate. Evaluated questions answered up to this point.',
            strengths: finalRes.strengths || ['Completed initial questions'],
            weaknesses: finalRes.weaknesses || ['Session ended before completing all planned questions'],
            recommendations: finalRes.recommendations || ['Complete full length drills to build interview endurance'],
            categoryScores: finalRes.category_scores || {},
          });
          setSessionState('results');
          fetchHistory();
          return;
        }
      } catch (e) {}
    }
    setSessionState('idle');
  };

  // Resume Active Interview Flow
  const handleResumeInterview = async (sessionItem) => {
    if (!sessionItem || !sessionItem.id) return;
    if (selectedReport) setSelectedReport(null);
    setErrorMessage(null);
    setSessionState('evaluating');

    try {
      const res = await interviewService.getCurrentQuestion(sessionItem.id);
      if (res && res.session) {
        const sess = res.session;
        setActiveSession({ ...sess, interview_id: sess.interview_id || sessionItem.id });
        setTotalQuestions(sess.total_questions || sessionItem.totalQuestions || 3);
        setQuestionNumber(sess.current_question || sessionItem.currentQuestionNum || 1);
        setSessionConfig({
          role: sess.target_role || sessionItem.role || targetRole,
          modality: sess.interview_type || sessionItem.rawType || 'technical',
          difficulty: sess.difficulty || sessionItem.difficulty || 'medium',
          questionCount: sess.total_questions || sessionItem.totalQuestions || 3,
        });

        if (res.question) {
          setCurrentQuestion(res.question);
        } else {
          setCurrentQuestion(defaultQuestions[0]);
        }

        if (sess.started_at) {
          const elapsed = Math.max(0, Math.floor((Date.now() - new Date(sess.started_at).getTime()) / 1000));
          setSecondsElapsed(elapsed < 7200 ? elapsed : 0);
        } else {
          setSecondsElapsed(0);
        }

        setAnswerText('');
        setShowHint(false);
        setSingleQuestionFeedback(null);
        setNextQuestionCache(null);
        setSessionState('active');
      } else {
        throw new Error('Could not fetch active question for this session.');
      }
    } catch (err) {
      setErrorMessage(err.message || 'Failed to resume session. Please try again.');
      setSessionState('idle');
    }
  };

  // Complete Session Early from Report Modal
  const handleCompleteSessionEarlyFromReport = async (sessionItem) => {
    if (!sessionItem || !sessionItem.id) return;
    setLoadingReportDetails(true);
    try {
      const compRes = await interviewService.completeInterview(sessionItem.id);
      if (compRes) {
        await fetchHistory();
        setSelectedReport((prev) => ({
          ...prev,
          status: 'completed',
          score: compRes.overall_score || 75,
          durationText: `${compRes.total_questions || 3} questions`,
          categoryScores: compRes.category_scores || {},
          strengths: compRes.strengths || [],
          weaknesses: compRes.weaknesses || [],
          recommendations: compRes.recommendations || [],
        }));
        const qList = await interviewService.getSessionQuestions(sessionItem.id);
        if (Array.isArray(qList)) {
          setReportQuestions(qList);
        }
      }
    } catch (err) {
      setErrorMessage(err.message || 'Could not complete session early.');
    } finally {
      setLoadingReportDetails(false);
    }
  };

  // Delete / Discard Interview Session
  const handleDeleteInterview = async (interviewId) => {
    if (!interviewId) return;
    if (!window.confirm('Are you sure you want to delete this interview session? This action cannot be undone.')) {
      return;
    }
    try {
      await interviewService.deleteInterview(interviewId);
      if (selectedReport && (selectedReport.id === interviewId || selectedReport.interview_id === interviewId)) {
        setSelectedReport(null);
      }
      fetchHistory();
    } catch (err) {
      setErrorMessage(err.message || 'Failed to delete interview session.');
    }
  };

  // View Report Action: Fetch full question details for session
  const handleViewReport = async (sessionItem) => {
    setSelectedReport(sessionItem);
    setReportQuestions([]);
    setLoadingReportDetails(true);

    try {
      if (sessionItem.id) {
        const questions = await interviewService.getSessionQuestions(sessionItem.id);
        if (Array.isArray(questions)) {
          setReportQuestions(questions);
        }
      }
    } catch (e) {
      // Questions remain empty, report modal shows session-level evaluation
    } finally {
      setLoadingReportDetails(false);
    }
  };

>>>>>>> f5f3d0fa4107f7c6729cfe2cb922a1872ad02460
  const wordCount = answerText.trim() ? answerText.trim().split(/\s+/).length : 0;
  const currentQ = currentQuestion || defaultQuestions[0];

  // Calculate aggregated scores for final review
  const calculatedOverallScore = finalSessionSummary?.overall_score || (
    completedQuestionsList.length > 0
      ? Math.round(completedQuestionsList.reduce((acc, q) => acc + (q.evaluation?.score || 70), 0) / completedQuestionsList.length)
      : 78
  );

  return (
<<<<<<< HEAD
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
=======
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* 1. Header: Simplified Title, Target Role, and One Prominent Action */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 p-5 sm:p-6 bg-[#121624] rounded-2xl border border-[#232b3e] shadow-lg">
        <div className="space-y-1">
          <div className="flex flex-wrap items-center gap-2.5">
            <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
              AI Mock Interview Studio
            </h1>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <Target className="w-3.5 h-3.5" />
              Target Role: <strong className="text-white font-semibold ml-0.5">{targetRole}</strong>
            </span>
          </div>
          <p className="text-xs sm:text-sm text-slate-400 max-w-2xl">
            Interactive, role-calibrated technical, system design, and behavioral mock interviews with step-by-step AI evaluation.
>>>>>>> f5f3d0fa4107f7c6729cfe2cb922a1872ad02460
          </p>
        </div>

        <div className="shrink-0 flex items-center gap-3">
          <button
<<<<<<< HEAD
            onClick={() => setIsSetupOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-[#1a2133] hover:bg-[#232b3e] text-white text-sm font-medium rounded-xl border border-[#232b3e] transition-all shadow-sm"
          >
            <Sliders className="w-4 h-4 text-indigo-400" />
            <span>Customize Setup</span>
          </button>
          <button
            onClick={() => setIsSetupOpen(true)}
            className="flex items-center gap-2 px-5 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white rounded-xl font-semibold text-sm transition-all shadow-md shadow-indigo-600/25"
=======
            onClick={() => handleOpenSetupWithModality('technical')}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs sm:text-sm font-semibold rounded-xl transition-all shadow-md shadow-indigo-600/20 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            aria-label="Start Mock Interview Session"
>>>>>>> f5f3d0fa4107f7c6729cfe2cb922a1872ad02460
          >
            <Play className="w-4 h-4 fill-white" />
            <span>Start Practice</span>
          </button>
        </div>
      </div>

      {/* Inline Global Error Alert */}
      {errorMessage && (
        <div
          role="alert"
          className="flex items-center justify-between p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs sm:text-sm"
        >
          <div className="flex items-center gap-2.5">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{errorMessage}</span>
          </div>
          <button
            onClick={() => setErrorMessage(null)}
            className="text-rose-400 hover:text-rose-200 transition-colors p-1"
            aria-label="Dismiss error notification"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* =========================================================================
          VIEW 1: IDLE DASHBOARD (Calibration Metrics, Modality Cards, History)
          ========================================================================= */}
      {sessionState === 'idle' && (
        <div className="space-y-6 animate-in fade-in duration-200">
          {/* Dynamic Calibration Score Panel */}
          <div className="p-5 sm:p-6 rounded-2xl bg-[#121624] border border-[#232b3e] shadow-lg space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#1e2638]">
              <div>
<<<<<<< HEAD
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
=======
                <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400 block">
                  Interview Readiness Calibration
                </span>
                <h2 className="text-base sm:text-lg font-bold text-white mt-0.5">
                  Performance Benchmarks · {targetRole}
                </h2>
              </div>

              <div className="flex items-center gap-2 self-start sm:self-auto">
                <span className="px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                  {loadingHistory
                    ? 'Loading...'
                    : calibrationMetrics.hasData
                    ? `${calibrationMetrics.completedCount} ${calibrationMetrics.completedCount === 1 ? 'Interview Completed' : 'Interviews Completed'}`
                    : calibrationMetrics.inProgressCount > 0
                    ? `${calibrationMetrics.inProgressCount} In Progress`
                    : '0 Completed Sessions'}
                </span>
              </div>
            </div>

            {loadingHistory ? (
              <div className="py-6 text-center space-y-2">
                <div className="w-6 h-6 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin mx-auto" />
                <p className="text-xs text-slate-400">Loading interview calibration metrics...</p>
              </div>
            ) : !calibrationMetrics.hasData ? (
              calibrationMetrics.inProgressCount > 0 ? (
                <div className="p-5 rounded-xl bg-[#0b0e17] border border-amber-500/20 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
                      <p className="text-sm font-semibold text-white">
                        {calibrationMetrics.inProgressCount} Interview Session{calibrationMetrics.inProgressCount > 1 ? 's' : ''} In Progress
                      </p>
                    </div>
                    <p className="text-xs text-slate-400 max-w-xl">
                      You have active sessions started for <strong className="text-slate-200">{targetRole}</strong>. Resume now to complete questions and unlock your role readiness calibration.
                    </p>
                  </div>
                  <button
                    onClick={() => handleResumeInterview(calibrationMetrics.latestInProgress)}
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-md shadow-emerald-600/20 transition-all self-start sm:self-auto shrink-0"
                  >
                    <Play className="w-3.5 h-3.5 fill-current" />
                    <span>Resume Active Session</span>
                  </button>
                </div>
              ) : (
                <div className="p-5 rounded-xl bg-[#0b0e17] border border-[#1e2638] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <p className="text-sm font-semibold text-white">No completed interviews yet</p>
                    <p className="text-xs text-slate-400 max-w-xl">
                      Launch a mock interview session to benchmark your technical accuracy, problem-solving depth, and answer structure for {targetRole}.
                    </p>
                  </div>
                  <button
                    onClick={() => handleOpenSetupWithModality('technical')}
                    className="px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-colors self-start sm:self-auto shrink-0"
                  >
                    Configure First Drill
                  </button>
                </div>
              )
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
                <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-1">
                  <span className="text-xs text-slate-400 block font-medium">Overall Calibration</span>
                  <div className="flex items-baseline gap-2">
                    <span className="text-2xl font-bold text-white">{calibrationMetrics.averageScore}</span>
                    <span className="text-xs text-indigo-400 font-medium">/ 100</span>
                  </div>
                  <span className="text-[11px] text-emerald-400 font-medium block">
                    {calibrationMetrics.statusLabel}
                  </span>
                </div>

                <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-1">
                  <span className="text-xs text-slate-400 block font-medium">Technical Accuracy</span>
                  <div className="flex items-baseline gap-2">
                    <span className="text-2xl font-bold text-white">{calibrationMetrics.avgTechnical}%</span>
                  </div>
                  <span className="text-[11px] text-slate-400 font-medium block">
                    Conceptual precision across drills
                  </span>
                </div>

                <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-1">
                  <span className="text-xs text-slate-400 block font-medium">Answer Structure</span>
                  <div className="flex items-baseline gap-2">
                    <span className="text-2xl font-bold text-white">{calibrationMetrics.avgStructure}%</span>
                  </div>
                  <span className="text-[11px] text-slate-400 font-medium block">
                    Logical breakdown & clarity
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* 3 Core Accessible Interview Modes - Dynamically tailored to target role */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="font-semibold text-white text-base">Select Interview Modality</h2>
                <p className="text-xs text-slate-400">Choose a focused track calibrated for {targetRole}</p>
              </div>
              <span className="text-xs font-medium text-indigo-400 bg-indigo-500/10 px-2.5 py-1 rounded-full border border-indigo-500/20">
                Tailored for {targetRole}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {modalityCards.map((card) => {
                const IconComponent =
                  card.icon === 'terminal' ? Terminal :
                  card.icon === 'layers' ? Layers :
                  card.icon === 'award' ? Award : Code2;

                const isEmerald = card.accentColor === 'emerald';
                const isPurple = card.accentColor === 'purple';

                return (
                  <div
                    key={card.id}
                    onClick={() => handleOpenSetupWithModality(card.modality)}
                    className={`p-5 rounded-2xl bg-[#121624] border border-[#232b3e] ${
                      isEmerald
                        ? 'hover:border-emerald-500/40'
                        : isPurple
                        ? 'hover:border-purple-500/40'
                        : 'hover:border-indigo-500/40'
                    } transition-all cursor-pointer shadow-lg space-y-3 group`}
                  >
                    <div className="flex items-center justify-between">
                      <div
                        className={`p-2.5 rounded-xl ${
                          isEmerald
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : isPurple
                            ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20'
                            : 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                        } w-fit`}
                      >
                        <IconComponent className="w-5 h-5" />
                      </div>
                      <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 px-2 py-0.5 rounded bg-[#1a2133] border border-[#232b3e]">
                        {card.badge}
                      </span>
                    </div>

                    <div>
                      <h3
                        className={`font-bold text-white text-base ${
                          isEmerald
                            ? 'group-hover:text-emerald-300'
                            : isPurple
                            ? 'group-hover:text-purple-300'
                            : 'group-hover:text-indigo-300'
                        } transition-colors`}
                      >
                        {card.title}
                      </h3>
                      <p className="text-xs text-slate-400 leading-relaxed mt-1">
                        {card.description}
                      </p>
                    </div>

                    <div className="pt-2 border-t border-[#1e2638] flex items-center justify-between text-xs">
                      <span className="text-slate-500">{card.questionRange}</span>
                      <span
                        className={`${
                          isEmerald
                            ? 'text-emerald-400 group-hover:text-emerald-300'
                            : isPurple
                            ? 'text-purple-400 group-hover:text-purple-300'
                            : 'text-indigo-400 group-hover:text-indigo-300'
                        } font-semibold inline-flex items-center gap-1`}
                      >
                        {card.actionLabel} <ArrowUpRight className="w-3.5 h-3.5" />
                      </span>
                    </div>
                  </div>
                );
              })}
>>>>>>> f5f3d0fa4107f7c6729cfe2cb922a1872ad02460
            </div>
          </div>

          {/* Compact Interview History Table */}
          <div className="bg-[#121624] p-5 sm:p-6 rounded-2xl border border-[#232b3e] space-y-4 shadow-lg">
            <div className="flex items-center justify-between pb-3 border-b border-[#1e2638]">
              <div className="flex items-center gap-2">
                <History className="w-5 h-5 text-indigo-400" />
                <h3 className="font-semibold text-white text-base">
                  Interview Practice History
                </h3>
              </div>
              <span className="text-xs text-slate-400 font-medium">
                {loadingHistory ? 'Loading...' : `${history.length} Saved ${history.length === 1 ? 'Session' : 'Sessions'}`}
              </span>
            </div>

<<<<<<< HEAD
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
=======
            {loadingHistory ? (
              <div className="py-8 text-center space-y-2">
                <div className="w-6 h-6 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin mx-auto" />
                <p className="text-xs text-slate-400">Loading saved interviews...</p>
              </div>
            ) : history.length === 0 ? (
              <div className="py-10 text-center space-y-3">
                <div className="w-12 h-12 rounded-full bg-[#1a2133] border border-[#232b3e] flex items-center justify-center mx-auto text-slate-500">
                  <FileText className="w-5 h-5" />
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium text-white">No interview history recorded yet</p>
                  <p className="text-xs text-slate-400 max-w-sm mx-auto">
                    Completed mock interview sessions will appear here with scores, duration, and question-by-question evaluations.
                  </p>
                </div>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="border-b border-[#1e2638] text-[11px] uppercase tracking-wider text-slate-400">
                      <th className="py-3 px-3">Date</th>
                      <th className="py-3 px-3">Role</th>
                      <th className="py-3 px-3">Modality</th>
                      <th className="py-3 px-3">Difficulty</th>
                      <th className="py-3 px-3">Duration</th>
                      <th className="py-3 px-3">Score</th>
                      <th className="py-3 px-3 text-right">Action</th>
>>>>>>> f5f3d0fa4107f7c6729cfe2cb922a1872ad02460
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#1e2638]">
                    {history.map((item, idx) => (
                      <tr key={item.id || idx} className="hover:bg-[#1a2133]/60 transition-colors">
                        <td className="py-3 px-3 font-medium text-white whitespace-nowrap">
                          {item.date}
                        </td>
                        <td className="py-3 px-3 text-slate-300 max-w-[160px] truncate" title={item.role}>
                          {item.role}
                        </td>
                        <td className="py-3 px-3 text-slate-300 whitespace-nowrap">
                          {item.type}
                        </td>
                        <td className="py-3 px-3 whitespace-nowrap">
                          <span className="px-2 py-0.5 rounded text-[10px] uppercase font-semibold bg-[#1a2133] text-indigo-300 border border-[#232b3e]">
                            {item.difficulty}
                          </span>
                        </td>
                        <td className="py-3 px-3 text-slate-400 whitespace-nowrap">
                          {item.durationText}
                        </td>
                        <td className="py-3 px-3 whitespace-nowrap">
                          {item.status === 'completed' && item.score !== null ? (
                            <span
                              className={`inline-block px-2.5 py-0.5 rounded-full text-[11px] font-bold ${
                                item.score >= 80
                                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                  : item.score >= 65
                                  ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                                  : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                              }`}
                            >
                              {item.score}%
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                              <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
                              In Progress (Q{item.currentQuestionNum}/{item.totalQuestions})
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-3 text-right whitespace-nowrap">
                          <div className="inline-flex items-center justify-end gap-2">
                            {item.status === 'active' ? (
                              <>
                                <button
                                  onClick={() => handleResumeInterview(item)}
                                  className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold text-emerald-400 hover:text-emerald-300 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 transition-all shadow-sm"
                                  aria-label={`Resume session from ${item.date}`}
                                >
                                  <Play className="w-3.5 h-3.5 fill-current" />
                                  <span>Resume</span>
                                </button>
                                <button
                                  onClick={() => handleViewReport(item)}
                                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium text-slate-300 hover:text-white bg-[#1a2133] hover:bg-[#232b3e] border border-[#232b3e] transition-colors"
                                  title="Session Details / Finalize"
                                >
                                  <Eye className="w-3.5 h-3.5" />
                                  <span>Details</span>
                                </button>
                                <button
                                  onClick={() => handleDeleteInterview(item.id)}
                                  className="p-1 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                                  title="Discard Session"
                                  aria-label="Discard session"
                                >
                                  <Trash2 className="w-3.5 h-3.5" />
                                </button>
                              </>
                            ) : (
                              <>
                                <button
                                  onClick={() => handleViewReport(item)}
                                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium text-indigo-400 hover:text-indigo-300 bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/20 transition-colors"
                                  aria-label={`View report for session on ${item.date}`}
                                >
                                  <Eye className="w-3.5 h-3.5" />
                                  <span>View Report</span>
                                </button>
                                <button
                                  onClick={() => handleDeleteInterview(item.id)}
                                  className="p-1 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                                  title="Delete Session"
                                  aria-label="Delete session"
                                >
                                  <Trash2 className="w-3.5 h-3.5" />
                                </button>
                              </>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* =========================================================================
          VIEW 2: ACTIVE INTERVIEW SESSION MODE (One question at a time)
          ========================================================================= */}
      {sessionState === 'active' && (
<<<<<<< HEAD
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
=======
        <div className="space-y-5 animate-in fade-in duration-200">
          {/* Active Session Status Bar */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-2xl bg-[#121624] border border-[#232b3e] shadow-lg text-xs">
            <div className="flex flex-wrap items-center gap-2.5">
              <span className="px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 font-bold border border-indigo-500/20">
                Question {questionNumber} of {totalQuestions}
              </span>
              <span className="text-white font-semibold uppercase tracking-wider">
                {currentQ.category || sessionConfig?.modality || 'Technical Interview'}
              </span>
              <span className="text-slate-500">·</span>
              <span className="text-slate-400">
                Difficulty: <strong className="text-slate-200 capitalize">{currentQ.difficulty || sessionConfig?.difficulty || 'Medium'}</strong>
              </span>
            </div>

            <div className="flex items-center gap-4 self-start sm:self-auto">
              <div className="flex items-center gap-1.5 text-amber-400 font-mono font-bold">
                <Clock className="w-4 h-4" />
                <span>Elapsed: {formatTimer(secondsElapsed)}</span>
              </div>
              <button
                type="button"
                onClick={() => setConfirmQuitOpen(true)}
                className="text-rose-400 hover:text-rose-300 text-xs font-medium transition-colors"
              >
                End Session
              </button>
            </div>
          </div>

          {/* Question Box */}
          <div className="p-5 sm:p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-lg">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-[#1e2638]">
              <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">
                Core Topic / Skill: {currentQ.skill || currentQ.topic || 'Engineering Architecture'}
              </span>
              {currentQ.hint && (
                <button
                  type="button"
                  onClick={() => setShowHint(!showHint)}
                  className="px-2.5 py-1 rounded-lg bg-[#1a2133] text-xs font-medium text-amber-400 hover:bg-[#232b3e] border border-amber-500/20 transition-colors flex items-center gap-1.5 self-start sm:self-auto"
                >
                  <HelpCircle className="w-3.5 h-3.5" />
                  <span>{showHint ? 'Hide Hint' : 'Show Hint'}</span>
                </button>
              )}
>>>>>>> f5f3d0fa4107f7c6729cfe2cb922a1872ad02460
            </div>

            <h2 className="text-base sm:text-lg font-bold text-white leading-relaxed">
              {currentQ.question}
            </h2>

            {currentQ.expected_focus && (
              <p className="text-xs text-slate-400 font-mono">
                <strong className="text-slate-300">Expected Focus:</strong> {currentQ.expected_focus}
              </p>
            )}

            {showHint && currentQ.hint && (
<<<<<<< HEAD
              <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-xs text-amber-200 font-sans space-y-1 animate-in fade-in">
                <span className="font-semibold text-amber-400 font-mono block">Interviewer Hint:</span>
                <p>{currentQ.hint}</p>
=======
              <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-200 space-y-1 animate-in fade-in">
                <span className="font-semibold text-amber-400 block flex items-center gap-1.5">
                  <Lightbulb className="w-3.5 h-3.5" /> Interviewer Hint:
                </span>
                <p className="leading-relaxed">{currentQ.hint}</p>
>>>>>>> f5f3d0fa4107f7c6729cfe2cb922a1872ad02460
              </div>
            )}

            {/* Answer Input Area & Helper Buttons */}
            <div className="space-y-2 pt-2">
<<<<<<< HEAD
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
=======
              <div className="flex flex-col sm:flex-row sm:items-center justify-between text-xs text-slate-400 gap-1">
                <label htmlFor="interview-answer-input" className="font-medium text-slate-300">
                  Your Answer &amp; Solution Explanation:
                </label>
                <div className="flex items-center gap-2 text-slate-400">
                  <span className={wordCount > 0 ? 'text-white font-medium' : 'text-slate-500'}>
                    Word Count: {wordCount} words
                  </span>
                  <span className="text-slate-500">·</span>
                  <span>Char Count: {answerText.length}</span>
>>>>>>> f5f3d0fa4107f7c6729cfe2cb922a1872ad02460
                </div>
              </div>

              <textarea
<<<<<<< HEAD
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
=======
                id="interview-answer-input"
                rows={8}
                value={answerText}
                onChange={(e) => setAnswerText(e.target.value)}
                placeholder="Structure your answer clearly (e.g. 1. High-Level Design / Situation, 2. Technical Decisions & Trade-offs, 3. Concrete Metrics or Outcomes)..."
                className="w-full p-4 rounded-xl bg-[#0b0e17] border border-[#232b3e] text-white text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors resize-none leading-relaxed"
                aria-label="Interview Answer Input"
              />
            </div>

            {/* Action Bar */}
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pt-3 border-t border-[#1e2638]">
>>>>>>> f5f3d0fa4107f7c6729cfe2cb922a1872ad02460
              <button
                type="button"
                onClick={() => setConfirmQuitOpen(true)}
                className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white bg-[#1a2133] hover:bg-[#232b3e] border border-[#232b3e] transition-colors"
              >
                Quit / End Early
              </button>

              <button
                type="button"
                onClick={handleSubmitAnswer}
                disabled={!answerText.trim()}
                className="px-6 py-2.5 rounded-xl text-xs sm:text-sm font-semibold bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white transition-all shadow-md shadow-indigo-600/25 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <Send className="w-4 h-4" />
<<<<<<< HEAD
                <span>Submit Answer for Evaluation</span>
=======
                <span>Submit Answer</span>
>>>>>>> f5f3d0fa4107f7c6729cfe2cb922a1872ad02460
              </button>
            </div>
          </div>
        </div>
      )}

<<<<<<< HEAD
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
=======
      {/* =========================================================================
          VIEW 3: INTERMEDIATE QUESTION FEEDBACK (Between questions)
          ========================================================================= */}
      {sessionState === 'question_feedback' && singleQuestionFeedback && (
        <div className="p-5 sm:p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-5 shadow-lg animate-in fade-in duration-200">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#1e2638]">
            <div>
              <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400 block">
                Question {questionNumber} Evaluated
              </span>
              <h2 className="text-base sm:text-lg font-bold text-white mt-0.5">
                AI Feedback for Question {questionNumber} of {totalQuestions}
              </h2>
            </div>
            <span
              className={`px-3 py-1 rounded-full text-xs font-bold border self-start sm:self-auto ${
                singleQuestionFeedback.score >= 80
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                  : singleQuestionFeedback.score >= 65
                  ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                  : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
              }`}
            >
              Score: {singleQuestionFeedback.score}/100
            </span>
          </div>

          {/* AI Feedback */}
          <div className="p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-xs sm:text-sm text-slate-200 space-y-1">
            <span className="font-semibold text-indigo-300 block flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5" /> Evaluator Assessment
            </span>
            <p className="leading-relaxed">{singleQuestionFeedback.feedback}</p>
          </div>

          {/* Strengths & Weaknesses */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-2">
              <span className="font-semibold text-emerald-400 block flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Strengths
              </span>
              <ul className="space-y-1.5 text-slate-300">
                {singleQuestionFeedback.strengths?.length > 0 ? (
                  singleQuestionFeedback.strengths.map((str, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0" />
                      <span>{str}</span>
                    </li>
                  ))
                ) : (
                  <li className="text-slate-500">Core technical concepts addressed.</li>
                )}
              </ul>
            </div>

            <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-2">
              <span className="font-semibold text-amber-400 block flex items-center gap-1.5">
                <AlertCircle className="w-4 h-4 text-amber-400" /> Opportunities for Improvement
              </span>
              <ul className="space-y-1.5 text-slate-300">
                {singleQuestionFeedback.weaknesses?.length > 0 ? (
                  singleQuestionFeedback.weaknesses.map((w, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 shrink-0" />
                      <span>{w}</span>
                    </li>
                  ))
                ) : (
                  <li className="text-slate-500">No major gaps identified.</li>
                )}
              </ul>
            </div>
          </div>

          {/* Action to proceed */}
          <div className="pt-3 flex items-center justify-between border-t border-[#1e2638]">
            <button
              type="button"
              onClick={() => setConfirmQuitOpen(true)}
              className="text-xs text-slate-400 hover:text-white"
            >
              End Session Early
            </button>

            <button
              type="button"
              onClick={handleProceedToNextQuestion}
              className="px-6 py-2.5 rounded-xl text-xs sm:text-sm font-semibold bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white transition-all shadow-md shadow-indigo-600/25 flex items-center gap-2"
            >
              <span>Next Question ({questionNumber + 1} of {totalQuestions})</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* =========================================================================
          VIEW 4: EVALUATING LOADING STATE
          ========================================================================= */}
      {sessionState === 'evaluating' && (
        <div className="p-10 sm:p-14 text-center rounded-2xl bg-[#121624] border border-[#232b3e] space-y-4 shadow-xl">
          <RefreshCw className="w-8 h-8 text-indigo-400 animate-spin mx-auto" />
          <div className="space-y-1">
            <h3 className="text-base sm:text-lg font-bold text-white">
              Evaluating Response with AI...
            </h3>
            <p className="text-xs text-slate-400">
              Assessing technical accuracy, algorithmic reasoning, and structural clarity against {targetRole} standards.
            </p>
          </div>
        </div>
      )}

      {/* =========================================================================
          VIEW 5: POST-INTERVIEW DIAGNOSTIC RESULTS
          ========================================================================= */}
      {sessionState === 'results' && evalResult && (
        <div className="p-5 sm:p-6 rounded-2xl bg-[#121624] border border-[#232b3e] space-y-6 shadow-xl animate-in fade-in duration-300">
          {/* Results Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#1e2638]">
            <div>
              <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400 block">
                Mock Interview Complete
              </span>
              <h2 className="text-lg sm:text-xl font-bold text-white mt-0.5">
                Session Diagnostic &amp; Performance Breakdown
              </h2>
              <span className="text-xs text-slate-400 block mt-0.5">
                Calibrated for {targetRole}
              </span>
            </div>

            <div className="flex items-center gap-3 self-start sm:self-auto">
              <span
                className={`px-4 py-1.5 rounded-full text-sm font-bold border ${
                  evalResult.overallScore >= 80
                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                    : evalResult.overallScore >= 65
                    ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                    : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                }`}
>>>>>>> f5f3d0fa4107f7c6729cfe2cb922a1872ad02460
              >
                Overall Score: {evalResult.overallScore} / 100
              </span>
            </div>
          </div>

          {/* Category Evaluation Sub-Scores */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
            <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-1">
              <span className="text-xs font-medium text-slate-400 block">Technical Accuracy</span>
              <span className="text-2xl font-bold text-white">{evalResult.technicalAccuracy}%</span>
              <span className="text-[11px] text-slate-500 block">Correctness &amp; reasoning depth</span>
            </div>

            <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-1">
              <span className="text-xs font-medium text-slate-400 block">Answer Structure</span>
              <span className="text-2xl font-bold text-white">{evalResult.answerStructure}%</span>
              <span className="text-[11px] text-slate-500 block">Logical coherence &amp; flow</span>
            </div>

            <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-1">
              <span className="text-xs font-medium text-slate-400 block">Communication &amp; Delivery</span>
              <span className="text-2xl font-bold text-white">{evalResult.communicationClarity}%</span>
              <span className="text-[11px] text-slate-500 block">Articulation &amp; concise explanation</span>
            </div>
          </div>

          {/* AI Evaluator Feedback */}
          {evalResult.feedback && (
            <div className="p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-xs sm:text-sm text-slate-200 space-y-1">
              <span className="font-semibold text-indigo-300 block flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5" /> Evaluator Summary Assessment
              </span>
              <p className="leading-relaxed">{evalResult.feedback}</p>
            </div>
          )}

          {/* Strengths & Improvements */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-2.5">
              <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                Demonstrated Strengths
              </span>
              <ul className="space-y-1.5 text-slate-300">
                {evalResult.strengths?.length > 0 ? (
                  evalResult.strengths.map((str, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0" />
                      <span className="leading-relaxed">{str}</span>
                    </li>
                  ))
                ) : (
                  <li className="text-slate-500">Core concepts addressed.</li>
                )}
              </ul>
            </div>

            <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-2.5">
              <span className="text-xs font-semibold uppercase tracking-wider text-amber-400 flex items-center gap-1.5">
                <AlertCircle className="w-4 h-4 text-amber-400" />
                Specific Areas for Improvement
              </span>
              <ul className="space-y-1.5 text-slate-300">
                {evalResult.weaknesses?.length > 0 ? (
                  evalResult.weaknesses.map((w, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 shrink-0" />
                      <span className="leading-relaxed">{w}</span>
                    </li>
                  ))
                ) : (
                  <li className="text-slate-500">No major critical gaps identified.</li>
                )}
              </ul>
            </div>
          </div>

          {/* Actionable Next Steps */}
          {evalResult.recommendations?.length > 0 && (
            <div className="p-4 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-2.5">
              <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
                <Lightbulb className="w-4 h-4 text-indigo-400" />
                Actionable Next Steps &amp; Recommendations
              </span>
              <ul className="space-y-2 text-xs text-slate-300">
                {evalResult.recommendations.map((rec, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-indigo-400 font-mono font-bold shrink-0">{idx + 1}.</span>
                    <span className="leading-relaxed">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Actions Footer */}
          <div className="pt-4 flex flex-wrap items-center justify-between gap-3 border-t border-[#1e2638]">
            <button
              onClick={() => {
                setSessionState('idle');
                fetchHistory();
              }}
              className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white bg-[#1a2133] hover:bg-[#232b3e] border border-[#232b3e] transition-colors"
            >
              Back to Dashboard
            </button>

            <div className="flex items-center gap-3">
              <button
                onClick={() => navigate('/skill-gaps')}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-[#1a2133] hover:bg-[#232b3e] text-white border border-[#232b3e] transition-colors"
              >
                Analyze Skill Gaps
              </button>
              <button
                onClick={() => handleOpenSetupWithModality(sessionConfig?.modality || 'technical')}
                className="px-5 py-2 rounded-xl text-xs sm:text-sm font-semibold bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white transition-all shadow-md shadow-indigo-600/25 flex items-center gap-1.5"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Start New Session</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          VIEW REPORT MODAL DIALOG
          ========================================================================= */}
      {selectedReport && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-report-title"
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in"
          onClick={() => setSelectedReport(null)}
        >
          <div
            className="bg-[#121624] border border-[#232b3e] rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-2xl p-5 sm:p-6 space-y-5"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-start justify-between gap-3 pb-3 border-b border-[#1e2638]">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400">
                    Interview Session Report
                  </span>
                  {selectedReport.status === 'active' && (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                      <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
                      In Progress (Q{selectedReport.currentQuestionNum}/{selectedReport.totalQuestions})
                    </span>
                  )}
                </div>
                <h3 id="modal-report-title" className="text-base sm:text-lg font-bold text-white mt-1">
                  {selectedReport.type} · {selectedReport.role}
                </h3>
                <span className="text-xs text-slate-400 mt-0.5 block">
                  Started on {selectedReport.date} · Difficulty: <strong className="capitalize text-slate-300">{selectedReport.difficulty}</strong>
                </span>
              </div>
              <button
                onClick={() => setSelectedReport(null)}
                className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-[#1a2133] transition-colors"
                aria-label="Close session report"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* In-Progress Notification Banner */}
            {selectedReport.status === 'active' && (
              <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-300 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
                  <span>
                    This interview is actively in progress. You can resume answering or finalize it early to compute your score.
                  </span>
                </div>
                <button
                  onClick={() => handleResumeInterview(selectedReport)}
                  className="px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold flex items-center gap-1.5 shadow-sm self-start sm:self-auto shrink-0"
                >
<<<<<<< HEAD
                  Analyze Skill Gaps
                </button>
                <button
                  onClick={() => handleStartInterview(sessionConfig || { modality: 'technical', questionCount: 3 })}
                  className="px-5 py-2 rounded-xl text-xs font-semibold bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white transition-all shadow-md shadow-indigo-600/25 flex items-center gap-1.5"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>Practice Another Session</span>
=======
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Resume Now</span>
>>>>>>> f5f3d0fa4107f7c6729cfe2cb922a1872ad02460
                </button>
              </div>
            )}

            {/* Score Strip */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-[#0b0e17] border border-[#1e2638]">
                <span className="text-slate-400 block text-[11px]">Overall Score</span>
                <span className="text-xl font-bold text-white">
                  {selectedReport.score !== null ? `${selectedReport.score}/100` : 'In Progress'}
                </span>
              </div>
              <div className="p-3 rounded-xl bg-[#0b0e17] border border-[#1e2638]">
                <span className="text-slate-400 block text-[11px]">
                  {selectedReport.status === 'active' ? 'Questions Answered' : 'Technical Accuracy'}
                </span>
                <span className="text-xl font-bold text-emerald-400">
                  {selectedReport.status === 'active'
                    ? `${reportQuestions.filter((q) => q.answer).length} / ${selectedReport.totalQuestions}`
                    : `${selectedReport.categoryScores?.Technical || selectedReport.categoryScores?.technical || selectedReport.score || 75}%`}
                </span>
              </div>
              <div className="col-span-2 sm:col-span-1 p-3 rounded-xl bg-[#0b0e17] border border-[#1e2638]">
                <span className="text-slate-400 block text-[11px]">Duration / Status</span>
                <span className="text-xl font-bold text-indigo-400">
                  {selectedReport.status === 'active' ? 'Active' : selectedReport.durationText}
                </span>
              </div>
            </div>

            {/* Strengths & Weaknesses if present in session record */}
            {(selectedReport.strengths?.length > 0 || selectedReport.weaknesses?.length > 0) && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                {selectedReport.strengths?.length > 0 && (
                  <div className="p-3.5 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-2">
                    <span className="font-semibold text-emerald-400 block flex items-center gap-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Key Strengths
                    </span>
                    <ul className="space-y-1 text-slate-300">
                      {selectedReport.strengths.map((s, i) => (
                        <li key={i} className="flex items-start gap-1.5">
                          <span className="w-1 h-1 rounded-full bg-emerald-400 mt-1.5 shrink-0" />
                          <span>{s}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {selectedReport.weaknesses?.length > 0 && (
                  <div className="p-3.5 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-2">
                    <span className="font-semibold text-amber-400 block flex items-center gap-1.5">
                      <AlertCircle className="w-3.5 h-3.5" /> Areas for Improvement
                    </span>
                    <ul className="space-y-1 text-slate-300">
                      {selectedReport.weaknesses.map((w, i) => (
                        <li key={i} className="flex items-start gap-1.5">
                          <span className="w-1 h-1 rounded-full bg-amber-400 mt-1.5 shrink-0" />
                          <span>{w}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Question Breakdown List */}
            <div className="space-y-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 block">
                Session Question Breakdown:
              </span>

              {loadingReportDetails ? (
                <div className="py-4 text-center space-y-2">
                  <div className="w-5 h-5 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin mx-auto" />
                  <p className="text-xs text-slate-400">Loading submitted questions and answers...</p>
                </div>
              ) : reportQuestions.length === 0 ? (
                <p className="text-xs text-slate-500 italic p-3 bg-[#0b0e17] rounded-xl border border-[#1e2638]">
                  Detailed Q&amp;A history was not recorded for this session.
                </p>
              ) : (
                <div className="space-y-3">
                  {reportQuestions.map((q, idx) => (
                    <div key={q.question_id || idx} className="p-3.5 rounded-xl bg-[#0b0e17] border border-[#1e2638] space-y-2 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-indigo-400">
                          Q{q.question_number || idx + 1}: {q.skill || q.category || 'Topic'}
                        </span>
                        {q.evaluation?.score !== undefined ? (
                          <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-indigo-500/10 text-indigo-300">
                            {q.evaluation.score}%
                          </span>
                        ) : (
                          <span className="text-[10px] text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded">
                            Pending Candidate Answer
                          </span>
                        )}
                      </div>

                      <p className="font-medium text-white">{q.question}</p>

                      {q.answer ? (
                        <div className="p-2.5 rounded-lg bg-[#121624] border border-[#1e2638] text-slate-300 text-[11px] leading-relaxed">
                          <span className="font-semibold text-slate-400 block mb-0.5">Your Response:</span>
                          {q.answer}
                        </div>
                      ) : (
                        <p className="text-[11px] text-slate-500 italic">No answer submitted yet for this question.</p>
                      )}

                      {q.evaluation?.ai_feedback && (
                        <p className="text-[11px] text-slate-400 italic">
                          Feedback: {q.evaluation.ai_feedback}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-[#1e2638]">
              {selectedReport.status === 'active' ? (
                <>
                  <button
                    onClick={() => handleCompleteSessionEarlyFromReport(selectedReport)}
                    className="px-3.5 py-2 rounded-xl text-xs font-medium text-amber-300 hover:text-white bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/20 transition-colors flex items-center gap-1.5"
                  >
                    <Check className="w-3.5 h-3.5" />
                    <span>Finalize &amp; Score Early</span>
                  </button>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleResumeInterview(selectedReport)}
                      className="px-4 py-2 rounded-xl text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition-colors flex items-center gap-1.5 shadow-sm"
                    >
                      <Play className="w-3.5 h-3.5 fill-current" />
                      <span>Resume Interview</span>
                    </button>
                    <button
                      onClick={() => setSelectedReport(null)}
                      className="px-3.5 py-2 rounded-xl text-xs font-medium bg-[#1a2133] hover:bg-[#232b3e] text-slate-300 hover:text-white border border-[#232b3e] transition-colors"
                    >
                      Close
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <button
                    onClick={() => {
                      const preModality = selectedReport.rawType || 'technical';
                      setSelectedReport(null);
                      handleOpenSetupWithModality(preModality);
                    }}
                    className="px-3.5 py-2 rounded-xl text-xs font-medium text-indigo-400 hover:text-white bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/20 transition-colors"
                  >
                    Re-practice This Modality
                  </button>

                  <button
                    onClick={() => setSelectedReport(null)}
                    className="px-4 py-2 rounded-xl text-xs font-semibold bg-[#1a2133] hover:bg-[#232b3e] text-white border border-[#232b3e] transition-colors"
                  >
                    Close Report
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          CONFIRM QUIT SESSION MODAL
          ========================================================================= */}
      {confirmQuitOpen && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in"
          onClick={() => setConfirmQuitOpen(false)}
        >
          <div
            className="bg-[#121624] border border-[#232b3e] rounded-2xl w-full max-w-sm p-5 space-y-4 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
                <AlertCircle className="w-5 h-5" />
              </div>
              <h3 className="font-semibold text-white text-base">End Interview Session?</h3>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Are you sure you want to quit? Unsubmitted answers in the current question will not be evaluated.
            </p>
            <div className="flex items-center justify-end gap-2.5 pt-2">
              <button
                type="button"
                onClick={() => setConfirmQuitOpen(false)}
                className="px-3.5 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white bg-[#1a2133] border border-[#232b3e]"
              >
                Continue Interview
              </button>
              <button
                type="button"
                onClick={handleEndSessionEarly}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-rose-600 hover:bg-rose-500 text-white transition-colors"
              >
                End &amp; Exit
              </button>
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
        initialConfig={setupInitialConfig}
      />
    </div>
  );
};
