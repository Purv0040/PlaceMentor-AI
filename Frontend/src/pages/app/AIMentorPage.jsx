import React, { useState, useEffect, useRef } from 'react';
import { useUser } from '../../context/UserContext';
import { useOnboarding } from '../../context/OnboardingContext';
import { usePlanning } from '../../context/PlanningContext';
import { mentorService } from '../../services/mentorService';

import { MentorHeader } from '../../components/mentor/MentorHeader';
import { MentorPersonaTabs } from '../../components/mentor/MentorPersonaTabs';
import { MentorMessage } from '../../components/mentor/MentorMessage';
import { MentorQuickPrompts } from '../../components/mentor/MentorQuickPrompts';
import { MentorInputDock } from '../../components/mentor/MentorInputDock';
import { MentorContextPanel } from '../../components/mentor/MentorContextPanel';

export const AIMentorPage = () => {
  const { user } = useUser();
  const { onboardingData } = useOnboarding();
  const planningState = usePlanning();

  const [activePersona, setActivePersona] = useState('tech');
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
      const response = await mentorService.generateMentorResponse(
        queryText,
        mentorContext,
        activePersona
      );

      const assistantMessage = {
        id: `ai-${Date.now()}`,
        sender: 'ai',
        role: 'assistant',
        persona: activePersona,
        timestamp: response.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        verified: response.verified ?? true,
        text: response.text || response.response,
        codeSnippet: response.codeSnippet || null,
        svgDiagram: response.svgDiagram || false,
        checkpoint: response.checkpoint || null,
        actions: response.actions || null
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to generate mentor response', error);
      const errorMessage = {
        id: `err-${Date.now()}`,
        sender: 'ai',
        role: 'assistant',
        persona: activePersona,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        verified: false,
        text: "I couldn't generate a response right now due to a network interruption. Please try asking again.",
        actions: [
          { label: "View Skill Gaps", route: "/skill-gaps" },
          { label: "View Today's Tasks", route: "/tasks" }
        ]
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    mentorService.clearChat();
    const resetGreeting = mentorService.getInitialGreeting(mentorContext);
    setMessages(resetGreeting);
  };

  const handleSelectPrompt = (promptText) => {
    handleSendMessage(promptText);
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
    <div className="w-full min-h-[calc(100vh-5rem)] bg-[#0f131d] text-slate-100 flex flex-col">
      {/* Background Gradient Orbs */}
      <div className="relative w-full overflow-hidden">
        <div className="absolute -top-32 -left-20 w-96 h-96 bg-purple-900/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute top-20 right-0 w-80 h-80 bg-indigo-900/10 rounded-full blur-3xl pointer-events-none" />

        {/* Page Top Header Bar */}
        <MentorHeader mentorContext={mentorContext} />

        {/* Persona Mode Selector Tabs */}
        <MentorPersonaTabs
          activePersona={activePersona}
          onSelectPersona={setActivePersona}
        />

        {/* Main Workspace Split Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start pb-10">
          {/* Left & Center Workspace Area (8 Columns on Desktop) */}
          <section className="xl:col-span-8 flex flex-col gap-4">
            <div className="flex flex-col rounded-2xl bg-[#171b26] border border-[#262a35] shadow-xl p-4 md:p-6 gap-5">
              {/* Conversation Session Indicator Ribbon */}
              <div className="flex items-center justify-between px-3.5 py-1.5 rounded-lg bg-[#1c1f2a] border border-[#262a35] shadow-sm">
                <div className="flex items-center gap-2 text-[11px] font-mono text-slate-400">
                  <span className="inline-block w-2 h-2 rounded-full bg-emerald-400"></span>
                  <span>
                    LIVE MENTOR SESSION ID: <strong className="text-white font-semibold">#SDE-REV-210-DAG</strong>
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono text-purple-300 bg-purple-500/10 border border-purple-500/20 px-2 py-0.5 rounded">
                    Latency 180ms
                  </span>
                  <button
                    type="button"
                    onClick={handleClearChat}
                    className="text-slate-400 hover:text-rose-400 p-1 rounded hover:bg-[#262a35] transition-colors"
                    title="Clear Conversation History"
                  >
                    <span className="material-symbols-outlined text-base">delete_sweep</span>
                  </button>
                </div>
              </div>

              {/* Chat Timeline Stream */}
              <div className="flex flex-col gap-5 min-h-[380px] max-h-[600px] overflow-y-auto pr-1">
                {messages.map((msg) => (
                  <MentorMessage
                    key={msg.id}
                    message={msg}
                    onOptionClick={handleSendMessage}
                    userAvatar={user?.avatarUrl}
                  />
                ))}
                <div ref={messagesEndRef} />
              </div>

              {/* Quick Suggestion Prompts */}
              <MentorQuickPrompts
                onSelectPrompt={handleSelectPrompt}
                disabled={isLoading}
              />

              {/* Input Dock */}
              <MentorInputDock
                input={input}
                setInput={setInput}
                onSend={() => handleSendMessage()}
                isLoading={isLoading}
                onClearChat={handleClearChat}
                onAttachCode={handleAttachCode}
                isVoiceActive={isVoiceActive}
                onToggleVoice={handleToggleVoice}
              />
            </div>
          </section>

          {/* Right-Hand AI Diagnostics & Copilot Panel (4 Columns on Desktop) */}
          <MentorContextPanel mentorContext={mentorContext} />
        </div>
      </div>
    </div>
  );
};
