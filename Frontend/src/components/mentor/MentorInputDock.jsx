import React, { useRef, useEffect } from 'react';

export const MentorInputDock = ({
  input,
  setInput,
  onSend,
  isLoading,
  onAttachCode,
  isVoiceActive,
  onToggleVoice
}) => {
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 140)}px`;
    }
  }, [input]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend(e);
    }
  };

  return (
    <div className="relative flex flex-col rounded-2xl bg-[#121622] border border-[#222838] focus-within:border-purple-500/50 focus-within:ring-1 focus-within:ring-purple-500/20 shadow-xl p-3 gap-2.5 transition-all">
      {/* Loading Indicator */}
      {isLoading && (
        <div className="flex items-center gap-2 px-2 py-1 text-xs text-purple-300 font-mono animate-pulse">
          <span className="material-symbols-outlined text-sm text-purple-400">auto_awesome</span>
          <span>Placement Copilot is thinking...</span>
        </div>
      )}

      {/* Main Textarea */}
      <textarea
        ref={textareaRef}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={isLoading}
        placeholder="Ask your AI Mentor anything..."
        rows={2}
        className="w-full bg-transparent text-white placeholder:text-slate-500 text-xs md:text-sm focus:outline-none resize-none px-1 leading-relaxed"
      />

      {/* Input Action Controls - All buttons neatly aligned to the right side */}
      <div className="flex items-center justify-end pt-2 border-t border-[#1e2333] gap-2 flex-wrap">
        {/* Attach Code */}
        <button
          type="button"
          onClick={onAttachCode}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#191e2e] hover:bg-purple-600/15 hover:text-purple-300 hover:border-purple-500/30 text-slate-300 text-xs font-medium transition-all border border-[#252b3d] disabled:opacity-50 cursor-pointer"
          title="Insert code snippet template"
        >
          <span className="material-symbols-outlined text-sm text-purple-400">code</span>
          <span>Attach Code</span>
        </button>

        {/* Voice Input */}
        <button
          type="button"
          onClick={onToggleVoice}
          disabled={isLoading}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all border cursor-pointer ${
            isVoiceActive
              ? 'bg-rose-500/20 text-rose-300 border-rose-500/40 animate-pulse'
              : 'bg-[#191e2e] hover:bg-purple-600/15 hover:text-purple-300 hover:border-purple-500/30 text-slate-300 border-[#252b3d]'
          }`}
          title="Dictate query via voice"
        >
          <span className={`material-symbols-outlined text-sm ${isVoiceActive ? 'text-rose-400' : 'text-emerald-400'}`}>
            mic
          </span>
          <span>{isVoiceActive ? 'Listening...' : 'Voice Input'}</span>
        </button>

        {/* Send Button */}
        <button
          type="button"
          onClick={onSend}
          disabled={isLoading || !input.trim()}
          className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold shadow-lg hover:shadow-purple-500/25 transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-40 disabled:scale-100 disabled:cursor-not-allowed cursor-pointer"
        >
          <span>Ask Mentor</span>
          <span className="material-symbols-outlined text-sm">send</span>
        </button>
      </div>
    </div>
  );
};
