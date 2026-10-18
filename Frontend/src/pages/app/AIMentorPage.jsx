import React, { useState, useEffect, useRef } from 'react';
import { useUser } from '../../context/UserContext';
import { useOnboarding } from '../../context/OnboardingContext';
import { usePlanning } from '../../context/PlanningContext';
import { mentorService } from '../../services/mentorService';

import { MentorHeader } from '../../components/mentor/MentorHeader';
import { MentorMessage } from '../../components/mentor/MentorMessage';
import { MentorInputDock } from '../../components/mentor/MentorInputDock';

export const AIMentorPage = () => {
  const { user } = useUser();
  const { onboardingData } = useOnboarding();
  const planningState = usePlanning();

  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isVoiceActive, setIsVoiceActive] = useState(false);
  
  const messagesEndRef = useRef(null);

  // Build normalized context object aggregating active application data
  const mentorContext = mentorService.buildMentorContext({
    user,
    onboardingData,
    planningState
  });

  // Active backend conversation ID for conversational memory
  const [conversationId, setConversationId] = useState(() => {
    return localStorage.getItem('placementMentorActiveConvId') || null;
  });

  // Load chat history from localStorage or fallback to initial contextual greeting
  const [messages, setMessages] = useState(() => {
    const saved = mentorService.getStoredChat();
    if (saved && saved.length > 0) return saved;
    return mentorService.getInitialGreeting(mentorContext);
  });

  // Save chat history to localStorage whenever messages update
  useEffect(() => {
    mentorService.saveChat(messages);
  }, [messages]);

  // Auto-scroll to bottom of conversation timeline
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

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

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const historyPayload = messages.slice(-6).map((m) => ({
        role: m.role || (m.sender === 'user' ? 'user' : 'assistant'),
        content: m.text || m.content || ''
      }));

      const response = await mentorService.generateMentorResponse(
        queryText,
        mentorContext,
        conversationId,
        historyPayload
      );

      if (response.conversation_id && response.conversation_id !== conversationId) {
        setConversationId(response.conversation_id);
        localStorage.setItem('placementMentorActiveConvId', response.conversation_id);
      }

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

      setMessages((prev) => [...prev, assistantMessage]);
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
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    if (window.confirm("Are you sure you want to clear the conversation history?")) {
      mentorService.clearChat();
      localStorage.removeItem('placementMentorActiveConvId');
      setConversationId(null);
      const resetGreeting = mentorService.getInitialGreeting(mentorContext);
      setMessages(resetGreeting);
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
        <MentorHeader />

        {/* Main Chat Workspace */}
        <div className="w-full max-w-5xl mx-auto flex flex-col gap-4 pb-10 pt-4">
          <div className="flex flex-col rounded-2xl bg-[#141824] border border-[#232838] shadow-xl p-4 md:p-6 gap-4">
            {/* Top Action Bar */}
            <div className="flex items-center justify-end">
              <button
                type="button"
                onClick={handleClearChat}
                className="flex items-center gap-1.5 text-xs font-medium text-slate-400 hover:text-rose-400 px-2.5 py-1 rounded-lg hover:bg-[#191e2e] transition-colors"
                title="Clear conversation history"
              >
                <span className="material-symbols-outlined text-sm">delete_sweep</span>
                <span>Clear Chat</span>
              </button>
            </div>

            {/* Chat Timeline Stream */}
            <div className="flex flex-col gap-4 min-h-[460px] max-h-[620px] overflow-y-auto pr-1">
              {messages.map((msg) => (
                <MentorMessage
                  key={msg.id}
                  message={msg}
                  userAvatar={user?.avatarUrl}
                />
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Suggested Prompts (Shown only at conversation start) */}
            {messages.length <= 1 && (
              <div className="flex flex-wrap items-center gap-2 pt-1 pb-1">
                <span className="text-xs text-slate-400 font-medium mr-1 flex items-center gap-1">
                  <span className="material-symbols-outlined text-sm text-purple-400">tips_and_updates</span>
                  Suggested:
                </span>
                {[
                  "Help me learn DSA",
                  "Practice a technical interview",
                  "Help me plan my preparation"
                ].map((suggestion, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleSendMessage(suggestion)}
                    disabled={isLoading}
                    className="px-3 py-1.5 rounded-xl bg-[#181d2c] hover:bg-purple-600/20 text-slate-200 hover:text-purple-300 border border-[#252b3e] hover:border-purple-500/40 text-xs font-medium transition-all shadow-sm flex items-center gap-1.5 group disabled:opacity-50"
                  >
                    <span>{suggestion}</span>
                    <span className="material-symbols-outlined text-xs text-purple-400 group-hover:translate-x-0.5 transition-transform">
                      arrow_forward
                    </span>
                  </button>
                ))}
              </div>
            )}

            {/* Clean Input Dock */}
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
  );
};
