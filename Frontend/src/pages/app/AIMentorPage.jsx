import React, { useState, useEffect, useRef } from 'react';
import { useUser } from '../../context/UserContext';
import { useOnboarding } from '../../context/OnboardingContext';
import { usePlanning } from '../../context/PlanningContext';
import { mentorService } from '../../services/mentorService';

import { MentorHeader } from '../../components/mentor/MentorHeader';
import { MentorMessage } from '../../components/mentor/MentorMessage';
import { MentorInputDock } from '../../components/mentor/MentorInputDock';
import { MentorHistorySidebar } from '../../components/mentor/MentorHistorySidebar';
import { MentorQuickPrompts } from '../../components/mentor/MentorQuickPrompts';

export const AIMentorPage = () => {
  const { user } = useUser();
  const { onboardingData } = useOnboarding();
  const planningState = usePlanning();

  // Consistent unique identifier for current authenticated or guest user
  const currentUserId = user?.id || user?._id || user?.email || 'student_candidate';

  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isVoiceActive, setIsVoiceActive] = useState(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState(true);
  const [activePersona, setActivePersona] = useState('tech');

  const messagesEndRef = useRef(null);

  // Build normalized context object aggregating active application data
  const mentorContext = mentorService.buildMentorContext({
    user,
    onboardingData,
    planningState
  });

  // Factory to create a clean initial session for the current user
  const createDefaultSession = (context, persona = 'tech') => {
    const defaultSessionId = `session-${currentUserId}-${Date.now()}`;
    return {
      id: defaultSessionId,
      title: 'Technical Preparation',
      persona: persona,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      messages: mentorService.getInitialGreeting(context, persona)
    };
  };

  // Load chat sessions list from user-scoped storage
  const [sessions, setSessions] = useState(() => {
    const stored = mentorService.getStoredSessions(currentUserId);
    if (stored && stored.length > 0) return stored;
    return [createDefaultSession(mentorContext, 'tech')];
  });

  // Active session ID
  const [activeSessionId, setActiveSessionId] = useState(() => {
    return sessions[0]?.id || `session-${currentUserId}-${Date.now()}`;
  });

  // Dynamic user-wise synchronization: when user changes, isolate and load that user's chat history
  useEffect(() => {
    let isCancelled = false;

    const loadUserHistory = async () => {
      // 1. Synchronously retrieve user-scoped cached sessions
      const userStored = mentorService.getStoredSessions(currentUserId);
      if (userStored && userStored.length > 0) {
        if (!isCancelled) {
          setSessions(userStored);
          setActiveSessionId(userStored[0].id);
        }
      } else {
        const fresh = [createDefaultSession(mentorContext, activePersona)];
        if (!isCancelled) {
          setSessions(fresh);
          setActiveSessionId(fresh[0].id);
          mentorService.saveStoredSessions(fresh, currentUserId);
        }
      }

      // 2. Fetch conversations from backend for this authenticated user
      try {
        const backendConvs = await mentorService.getConversations();
        if (isCancelled) return;
        if (Array.isArray(backendConvs) && backendConvs.length > 0) {
          const currentLocal = mentorService.getStoredSessions(currentUserId);
          const merged = await Promise.all(
            backendConvs.map(async (bc) => {
              const bId = bc.conversation_id || bc.id || bc._id;
              const matchingLocal = currentLocal.find((s) => s.backendConversationId === bId || s.id === bId);
              if (matchingLocal && matchingLocal.messages?.length > 1) {
                return {
                  ...matchingLocal,
                  title: bc.title || matchingLocal.title,
                  updatedAt: bc.updated_at || matchingLocal.updatedAt
                };
              }

              let msgs = [];
              try {
                const detail = await mentorService.getConversationDetail(bId);
                if (detail && Array.isArray(detail.messages) && detail.messages.length > 0) {
                  msgs = detail.messages.map((m, idx) => ({
                    id: m.message_id || `msg-${bId}-${idx}`,
                    sender: m.role === 'user' ? 'user' : 'ai',
                    role: m.role || (m.sender === 'user' ? 'user' : 'assistant'),
                    text: m.text || m.content || m.message || '',
                    timestamp: m.created_at
                      ? new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                      : new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                  }));
                }
              } catch (e) {}

              if (!msgs || msgs.length === 0) {
                msgs = mentorService.getInitialGreeting(mentorContext, activePersona);
              }

              return {
                id: bId,
                backendConversationId: bId,
                title: bc.title || 'Placement Session',
                persona: activePersona,
                createdAt: bc.created_at || new Date().toISOString(),
                updatedAt: bc.updated_at || new Date().toISOString(),
                messages: msgs
              };
            })
          );

          if (!isCancelled && merged.length > 0) {
            setSessions(merged);
            mentorService.saveStoredSessions(merged, currentUserId);
            if (!merged.some((s) => s.id === activeSessionId)) {
              setActiveSessionId(merged[0].id);
            }
          }
        }
      } catch (err) {
        console.warn('Backend conversations sync skipped, using user-scoped storage:', err);
      }
    };

    loadUserHistory();

    return () => {
      isCancelled = true;
    };
  }, [currentUserId]);

  // Find active session object
  const currentSession = sessions.find((s) => s.id === activeSessionId) || sessions[0];

  // Active messages derived from current session
  const messages = currentSession?.messages || [];

  // Persist sessions whenever they change for the current user
  useEffect(() => {
    if (sessions && sessions.length > 0) {
      mentorService.saveStoredSessions(sessions, currentUserId);
      if (currentSession?.messages) {
        mentorService.saveChat(currentSession.messages, currentUserId);
      }
    }
  }, [sessions, activeSessionId, currentUserId]);

  // Sync active persona when session changes
  useEffect(() => {
    if (currentSession?.persona && currentSession.persona !== activePersona) {
      setActivePersona(currentSession.persona);
    }
  }, [activeSessionId]);

  // Auto-scroll to bottom of conversation timeline
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Handle Ctrl+N keyboard shortcut for new chat
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'n') {
        e.preventDefault();
        handleNewChat();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activePersona, currentUserId]);

  // Create a brand new chat session for current user
  const handleNewChat = async () => {
    const newSessionId = `session-${currentUserId}-${Date.now()}`;
    const newSession = {
      id: newSessionId,
      title: 'New Chat',
      persona: activePersona,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      messages: mentorService.getInitialGreeting(mentorContext, activePersona)
    };

    setSessions((prev) => [newSession, ...prev]);
    setActiveSessionId(newSessionId);
    setInput('');

    // If authenticated, also create on backend in background
    try {
      const res = await mentorService.createConversation('New Chat');
      if (res && (res.conversation_id || res.id)) {
        const bConvId = res.conversation_id || res.id;
        setSessions((prev) =>
          prev.map((s) =>
            s.id === newSessionId ? { ...s, backendConversationId: bConvId } : s
          )
        );
      }
    } catch (e) {}
  };

  // Select an existing conversation session
  const handleSelectSession = (sessionId) => {
    setActiveSessionId(sessionId);
    // On small screens, auto-close the drawer on selection
    if (window.innerWidth < 1024) {
      setIsHistoryOpen(false);
    }
  };

  // Delete a session
  const handleDeleteSession = async (sessionId) => {
    const sessionToDelete = sessions.find((s) => s.id === sessionId);
    const backendId = sessionToDelete?.backendConversationId || (sessionId.startsWith('session-') ? null : sessionId);
    if (backendId) {
      try {
        await mentorService.archiveConversation(backendId);
      } catch (e) {}
    }

    if (sessions.length <= 1) {
      // If deleting the only session, reset it to a fresh chat for this user
      const freshSession = createDefaultSession(mentorContext, activePersona);
      setSessions([freshSession]);
      setActiveSessionId(freshSession.id);
      mentorService.saveStoredSessions([freshSession], currentUserId);
      return;
    }

    const updated = sessions.filter((s) => s.id !== sessionId);
    setSessions(updated);
    mentorService.saveStoredSessions(updated, currentUserId);
    if (activeSessionId === sessionId) {
      setActiveSessionId(updated[0].id);
    }
  };

  // Rename a session title
  const handleRenameSession = (sessionId, newTitle) => {
    setSessions((prev) => {
      const updated = prev.map((s) => (s.id === sessionId ? { ...s, title: newTitle, updatedAt: new Date().toISOString() } : s));
      mentorService.saveStoredSessions(updated, currentUserId);
      return updated;
    });
  };

  // Change mode / persona
  const handleSelectPersona = (personaId) => {
    setActivePersona(personaId);
    // Update active session persona
    setSessions((prev) =>
      prev.map((s) =>
        s.id === activeSessionId
          ? {
              ...s,
              persona: personaId,
              updatedAt: new Date().toISOString()
            }
          : s
      )
    );
  };

  // Send message
  const handleSendMessage = async (textToSend = input) => {
    const queryText = typeof textToSend === 'string' ? textToSend.trim() : input.trim();
    if (!queryText || isLoading) return;

    const userMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      role: 'user',
      text: queryText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    // Auto-derive title if currently "New Chat" or "Untitled Session"
    let updatedTitle = currentSession?.title;
    if (!currentSession || currentSession.title === 'New Chat' || currentSession.title === 'Untitled Session') {
      updatedTitle = queryText.slice(0, 32) + (queryText.length > 32 ? '...' : '');
    }

    const updatedMessages = [...messages, userMessage];

    // Optimistically update session messages
    setSessions((prev) =>
      prev.map((s) =>
        s.id === activeSessionId
          ? {
              ...s,
              title: updatedTitle,
              messages: updatedMessages,
              updatedAt: new Date().toISOString()
            }
          : s
      )
    );

    setInput('');
    setIsLoading(true);

    try {
      const historyPayload = updatedMessages.slice(-6).map((m) => ({
        role: m.role || (m.sender === 'user' ? 'user' : 'assistant'),
        content: m.text || m.content || ''
      }));

      const activeBackendConvId = currentSession?.backendConversationId || (activeSessionId?.startsWith('session-') ? null : activeSessionId);

      const response = await mentorService.generateMentorResponse(
        queryText,
        mentorContext,
        activeBackendConvId,
        historyPayload,
        activePersona
      );

      const assistantMessage = {
        id: `ai-${Date.now()}`,
        sender: 'ai',
        role: 'assistant',
        timestamp: response.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        verified: response.verified === true,
        text: response.text || response.response,
        codeSnippet: response.codeSnippet || null,
        svgDiagram: response.svgDiagram || false
      };

      setSessions((prev) =>
        prev.map((s) =>
          s.id === activeSessionId
            ? {
                ...s,
                backendConversationId: response.conversation_id || s.backendConversationId,
                messages: [...s.messages, assistantMessage],
                updatedAt: new Date().toISOString()
              }
            : s
        )
      );
    } catch (error) {
      console.error('Failed to generate mentor response', error);
      const errorMessage = {
        id: `err-${Date.now()}`,
        sender: 'ai',
        role: 'assistant',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        verified: false,
        text: "I couldn't generate a response right now due to a network interruption. Please try asking again."
      };
      setSessions((prev) =>
        prev.map((s) =>
          s.id === activeSessionId
            ? {
                ...s,
                messages: [...s.messages, errorMessage],
                updatedAt: new Date().toISOString()
              }
            : s
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearCurrentChat = () => {
    if (window.confirm('Are you sure you want to clear the messages in this chat?')) {
      const resetGreeting = mentorService.getInitialGreeting(mentorContext, activePersona);
      setSessions((prev) =>
        prev.map((s) =>
          s.id === activeSessionId
            ? {
                ...s,
                messages: resetGreeting,
                updatedAt: new Date().toISOString()
              }
            : s
        )
      );
    }
  };

  const handleAttachCode = () => {
    setInput((prev) => prev + (prev ? '\n' : '') + '```cpp\n// Paste C++ or Python code snippet here\n```');
  };

  const handleToggleVoice = () => {
    setIsVoiceActive((prev) => !prev);
    if (!isVoiceActive) {
      setTimeout(() => {
        setIsVoiceActive(false);
        setInput("Explain Kahn's Topological Sort algorithm step by step");
      }, 2500);
    }
  };

  return (
    <div className="w-full flex flex-col text-slate-100">
      {/* Background Glow */}
      <div className="relative w-full">
        <div className="absolute -top-20 -left-10 w-96 h-96 bg-purple-600/5 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute top-10 right-0 w-80 h-80 bg-indigo-600/5 rounded-full blur-3xl pointer-events-none" />

        {/* Page Top Header Bar */}
        <MentorHeader
          isHistoryOpen={isHistoryOpen}
          onToggleHistory={() => setIsHistoryOpen((prev) => !prev)}
          activePersona={activePersona}
          onNewChat={handleNewChat}
          candidateName={mentorContext?.user?.name || user?.name || ''}
        />

        {/* Main Body Layout: History Panel + Chat Space - Equal Height and Bottom Baseline */}
        <div className="w-full flex items-stretch gap-4 pt-4 pb-4 h-[calc(100vh-140px)] min-h-[580px]">
          {/* ChatGPT-style History Sidebar */}
          {isHistoryOpen && (
            <div className="hidden lg:block shrink-0 h-full">
              <div className="rounded-2xl border border-[#232838] overflow-hidden shadow-xl h-full flex flex-col">
                <MentorHistorySidebar
                  isOpen={isHistoryOpen}
                  onClose={() => setIsHistoryOpen(false)}
                  sessions={sessions}
                  activeSessionId={activeSessionId}
                  onSelectSession={handleSelectSession}
                  onNewChat={handleNewChat}
                  onDeleteSession={handleDeleteSession}
                  onRenameSession={handleRenameSession}
                  candidateName={mentorContext?.user?.name || user?.name || ''}
                />
              </div>
            </div>
          )}

          {/* Mobile slide-over drawer */}
          <div className="lg:hidden">
            <MentorHistorySidebar
              isOpen={isHistoryOpen}
              onClose={() => setIsHistoryOpen(false)}
              sessions={sessions}
              activeSessionId={activeSessionId}
              onSelectSession={handleSelectSession}
              onNewChat={handleNewChat}
              onDeleteSession={handleDeleteSession}
              onRenameSession={handleRenameSession}
              candidateName={mentorContext?.user?.name || user?.name || ''}
            />
          </div>

          {/* Central Chat Workspace */}
          <div className="flex-1 flex flex-col min-w-0 h-full">
            {/* Chat Container Box */}
            <div className="flex flex-col rounded-2xl bg-[#141824] border border-[#232838] shadow-xl p-4 md:p-5 gap-3 h-full">
              {/* Top Sub-Bar: Active Session Title */}
              <div className="flex items-center gap-2 pb-2 border-b border-[#1c2233] shrink-0 min-w-0">
                <span className="material-symbols-outlined text-purple-400 text-sm shrink-0">chat_bubble</span>
                <span className="text-xs font-semibold text-slate-200 truncate">
                  {currentSession?.title || 'Active Chat'}
                </span>
              </div>

              {/* Chat Timeline Stream */}
              <div className="flex-1 overflow-y-auto pr-1 flex flex-col gap-4 min-h-0 custom-scrollbar">
                {messages.map((msg) => (
                  <MentorMessage
                    key={msg.id}
                    message={msg}
                    userAvatar={user?.avatarUrl}
                  />
                ))}
                <div ref={messagesEndRef} />
              </div>

              {/* Quick Prompt Suggestions */}
              {messages.length <= 1 && (
                <div className="shrink-0">
                  <MentorQuickPrompts
                    onSelectPrompt={(prompt) => handleSendMessage(prompt)}
                    disabled={isLoading}
                  />
                </div>
              )}

              {/* Clean Input Dock */}
              <div className="shrink-0">
                <MentorInputDock
                  input={input}
                  setInput={setInput}
                  onSend={() => handleSendMessage()}
                  isLoading={isLoading}
                  onAttachCode={handleAttachCode}
                  isVoiceActive={isVoiceActive}
                  onToggleVoice={handleToggleVoice}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
