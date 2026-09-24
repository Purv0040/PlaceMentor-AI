import React, { useRef, useEffect } from 'react';

export const MentorInputDock = ({
  input,
  setInput,
  onSend,
  isLoading,
  onClearChat,
  onAttachCode,
  isVoiceActive,
  onToggleVoice
}) => {
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend(e);
    }
  };

  return (
    <div className="relative flex flex-col rounded-xl bg-[#0a0e18] border border-[#232b3e] shadow-xl p-3 gap-2.5">
      {/* Loading Bar / Typing Indicator */}
      {isLoading && (
        <div className="flex items-center gap-2 px-2 py-1 text-xs text-purple-300 font-mono animate-pulse">
          <span className="material-symbols-outlined text-sm text-purple-400">auto_awesome</span>
          <span>AI Placement Copilot is thinking...</span>
        </div>
      )}

      <textarea
        ref={textareaRef}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={isLoading}
        placeholder="Ask your mentor anything (paste code, ask design tradeoffs, or request interview hints)..."
        rows={2}
        className="w-full bg-transparent text-white placeholder:text-slate-500 text-xs md:text-sm focus:outline-none resize-none px-1"
      />

      <div className="flex items-center justify-between pt-1 border-t border-[#1c1f2a]">
        <div className="flex items-center gap-1.5 flex-wrap">
          <button
            type="button"
            onClick={onAttachCode}
            disabled={isLoading}
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-[#171b26] hover:bg-[#262a35] text-slate-300 hover:text-white text-xs transition-colors border border-[#262a35]"
            title="Attach Code, LeetCode URL, or System Schema"
          >
            <span className="material-symbols-outlined text-sm">attach_file</span>
            <span className="hidden sm:inline">Attach Code</span>
          </button>

          <button
            type="button"
            onClick={onToggleVoice}
            disabled={isLoading}
            className={`flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs transition-colors border ${
              isVoiceActive
                ? 'bg-rose-500/20 text-rose-300 border-rose-500/40 animate-pulse'
                : 'bg-[#171b26] hover:bg-[#262a35] text-slate-300 hover:text-white border-[#262a35]'
            }`}
          >
            <span className="material-symbols-outlined text-sm text-emerald-400">mic</span>
            <span className="hidden sm:inline">{isVoiceActive ? 'Listening...' : 'Voice Query'}</span>
          </button>

          <button
            type="button"
            onClick={onClearChat}
            disabled={isLoading}
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-[#171b26] hover:bg-[#262a35] text-slate-400 hover:text-rose-400 text-xs transition-colors border border-[#262a35]"
            title="Clear Chat History"
          >
            <span className="material-symbols-outlined text-sm">delete_sweep</span>
            <span className="hidden md:inline">Clear Chat</span>
          </button>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-[10px] font-mono text-slate-500 hidden sm:inline">
            Press Enter to send (Shift+Enter for newline)
          </span>
          <button
            type="button"
            onClick={onSend}
            disabled={isLoading || !input.trim()}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 text-white text-xs font-semibold shadow-lg hover:shadow-purple-500/25 transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-40 disabled:scale-100 disabled:cursor-not-allowed"
          >
            <span className="material-symbols-outlined text-base">send</span>
            <span>Ask Copilot</span>
          </button>
        </div>
      </div>
    </div>
  );
};
