import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export const MentorMessage = ({ message, onOptionClick, userAvatar }) => {
  const navigate = useNavigate();
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user' || message.sender === 'user';

  const handleCopy = (code) => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Helper to render basic markdown bold/code/list formatting safely
  const formatText = (content) => {
    if (!content) return null;

    return content.split('\n\n').map((paragraph, pIdx) => {
      const lines = paragraph.split('\n');
      return (
        <div key={pIdx} className="space-y-1 my-1">
          {lines.map((line, lIdx) => {
            let formattedLine = line;

            // Handle list items
            const isBullet = line.trim().startsWith('- ') || line.trim().startsWith('• ');
            const isNumbered = /^\d+\.\s/.test(line.trim());

            if (isBullet) {
              formattedLine = line.trim().replace(/^[-•]\s*/, '');
            }

            // Convert **bold** and `code`
            const parts = formattedLine.split(/(\*\*.*?\*\*|`.*?`)/g);

            const renderedParts = parts.map((part, idx) => {
              if (part.startsWith('**') && part.endsWith('**')) {
                return <strong key={idx} className="font-semibold text-white">{part.slice(2, -2)}</strong>;
              }
              if (part.startsWith('`') && part.endsWith('`')) {
                return (
                  <code key={idx} className="font-mono text-xs text-indigo-300 bg-[#0a0e18] px-1.5 py-0.5 rounded border border-[#232b3e]">
                    {part.slice(1, -1)}
                  </code>
                );
              }
              return part;
            });

            if (isBullet) {
              return (
                <div key={lIdx} className="flex items-start gap-2 pl-2">
                  <span className="text-purple-400 mt-1">•</span>
                  <span>{renderedParts}</span>
                </div>
              );
            }

            if (isNumbered) {
              return (
                <div key={lIdx} className="pl-1">
                  {renderedParts}
                </div>
              );
            }

            return <p key={lIdx}>{renderedParts}</p>;
          })}
        </div>
      );
    });
  };

  if (isUser) {
    return (
      <div className="flex items-start justify-end gap-3">
        <div className="flex flex-col items-end gap-1 max-w-2xl">
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-mono text-slate-400">{message.timestamp || 'Just now'}</span>
            <span className="text-xs font-medium text-slate-200">You</span>
          </div>
          <div className="p-3.5 rounded-2xl bg-indigo-600 text-white text-xs md:text-sm leading-relaxed shadow-md rounded-tr-none">
            <p>{message.text || message.content}</p>
          </div>
          <span className="text-[10px] font-mono text-emerald-400 flex items-center gap-1">
            <span className="material-symbols-outlined text-xs">done_all</span>
            Delivered with student context vector
          </span>
        </div>
        <div className="w-8 h-8 rounded-xl bg-[#1c1f2a] border border-[#262a35] overflow-hidden shrink-0 flex items-center justify-center">
          {userAvatar ? (
            <img src={userAvatar} alt="Candidate" className="w-full h-full object-cover" />
          ) : (
            <span className="material-symbols-outlined text-indigo-400 text-base">person</span>
          )}
        </div>
      </div>
    );
  }

  // Assistant Message
  return (
    <div className="flex items-start gap-3">
      <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-purple-900/60 to-indigo-900/60 border border-purple-500/30 flex items-center justify-center text-purple-300 shadow-md shrink-0">
        <span className="material-symbols-outlined text-lg" style={{ fontVariationSettings: "'FILL' 1" }}>
          smart_toy
        </span>
      </div>

      <div className="flex flex-col gap-2 flex-grow max-w-3xl">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs font-semibold text-white">Staff Mentor</span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-500/10 text-purple-300 border border-purple-500/20 uppercase font-medium">
            {message.persona === 'dsa' ? 'Socratic DSA Mode' : message.persona === 'story' ? 'STAR Coach Mode' : message.persona === 'strat' ? 'Strategist Mode' : 'Technical Mode'}
          </span>
          <span className="text-[11px] font-mono text-slate-400">{message.timestamp || 'Just now'}</span>
          {message.verified && (
            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Verified Solution
            </span>
          )}
        </div>

        <div className="p-4 rounded-2xl bg-[#1c1f2a] border border-[#262a35] text-slate-200 text-xs md:text-sm leading-relaxed shadow-sm space-y-3 rounded-tl-none">
          <div>{formatText(message.text || message.content)}</div>

          {/* Optional Visual SVG Graph Diagram */}
          {message.svgDiagram && (
            <div className="p-3 rounded-xl bg-[#0a0e18] border border-[#232b3e] flex flex-col gap-2 my-2">
              <div className="flex items-center justify-between text-[11px] font-mono text-slate-400">
                <span className="uppercase text-purple-300 flex items-center gap-1">
                  <span className="material-symbols-outlined text-sm">schema</span>
                  Visualizing Cycle State Tracking
                </span>
                <span>DFS Back-edge to Gray Ancestor</span>
              </div>
              <div className="w-full flex justify-center py-2 overflow-x-auto">
                <svg className="w-full max-w-lg h-auto min-w-[320px]" viewBox="0 0 540 120">
                  <defs>
                    <marker id="arrow" markerHeight="6" markerWidth="6" orient="auto-start-reverse" refX="8" refY="5" viewBox="0 0 10 10">
                      <path d="M 0 1 L 9 5 L 0 9 z" fill="#908fa0"></path>
                    </marker>
                    <marker id="arrow-error" markerHeight="6" markerWidth="6" orient="auto-start-reverse" refX="8" refY="5" viewBox="0 0 10 10">
                      <path d="M 0 1 L 9 5 L 0 9 z" fill="#ffb4ab"></path>
                    </marker>
                  </defs>
                  <line markerEnd="url(#arrow)" stroke="#908fa0" strokeWidth="2" x1="80" x2="180" y1="60" y2="60"></line>
                  <line markerEnd="url(#arrow)" stroke="#908fa0" strokeWidth="2" x1="220" x2="320" y1="60" y2="60"></line>
                  <line markerEnd="url(#arrow)" stroke="#908fa0" strokeWidth="2" x1="360" x2="460" y1="60" y2="60"></line>
                  <path d="M 470 45 C 440 -15, 240 -15, 210 45" fill="none" markerEnd="url(#arrow-error)" stroke="#ffb4ab" strokeDasharray="4,4" strokeWidth="2.5"></path>
                  <circle cx="60" cy="60" fill="#1c1f2a" r="20" stroke="#4edea3" strokeWidth="2"></circle>
                  <text fill="#dfe2f1" fontFamily="JetBrains Mono" fontSize="12" fontWeight="600" textAnchor="middle" x="60" y="65">v[0]</text>
                  <text fill="#4edea3" fontFamily="Inter" fontSize="10" textAnchor="middle" x="60" y="98">Black (done)</text>
                  <circle cx="200" cy="60" fill="#313540" r="20" stroke="#ffb4ab" strokeWidth="2.5"></circle>
                  <text fill="#ffb4ab" fontFamily="JetBrains Mono" fontSize="12" fontWeight="700" textAnchor="middle" x="200" y="65">v[1]</text>
                  <text fill="#ffb4ab" fontFamily="Inter" fontSize="10" textAnchor="middle" x="200" y="98">Gray (in-stack)</text>
                  <circle cx="340" cy="60" fill="#313540" r="20" stroke="#c0c1ff" strokeWidth="2"></circle>
                  <text fill="#dfe2f1" fontFamily="JetBrains Mono" fontSize="12" fontWeight="600" textAnchor="middle" x="340" y="65">v[2]</text>
                  <text fill="#c0c1ff" fontFamily="Inter" fontSize="10" textAnchor="middle" x="340" y="98">Processing</text>
                  <circle cx="480" cy="60" fill="#313540" r="20" stroke="#ffb4ab" strokeWidth="2.5"></circle>
                  <text fill="#ffb4ab" fontFamily="JetBrains Mono" fontSize="12" fontWeight="700" textAnchor="middle" x="480" y="65">v[3]</text>
                  <text fill="#ffb4ab" fontFamily="Inter" fontSize="10" textAnchor="middle" x="480" y="98">Detected Loop</text>
                </svg>
              </div>
            </div>
          )}

          {/* Code Snippet Box */}
          {message.codeSnippet && (
            <div className="rounded-xl bg-[#0a0e18] border border-[#232b3e] overflow-hidden my-2">
              <div className="flex items-center justify-between px-3 py-1.5 bg-[#171b26] text-slate-400 font-mono text-[11px] border-b border-[#232b3e]">
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-500/80"></span>
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-500/80"></span>
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/80"></span>
                  <span className="ml-2 text-slate-200 font-semibold">{message.codeSnippet.filename || 'code_snippet.cpp'}</span>
                </div>
                <button
                  type="button"
                  onClick={() => handleCopy(message.codeSnippet.code)}
                  className="flex items-center gap-1 hover:text-white px-2 py-0.5 rounded bg-[#0a0e18] hover:bg-[#1c1f2a] transition-all text-slate-300"
                >
                  <span className="material-symbols-outlined text-xs">content_copy</span>
                  <span>{copied ? 'Copied!' : 'Copy Code'}</span>
                </button>
              </div>
              <pre className="p-3.5 overflow-x-auto font-mono text-xs text-indigo-200 leading-relaxed select-text">
                <code>{message.codeSnippet.code}</code>
              </pre>
            </div>
          )}

          {/* Interactive Checkpoint Banner */}
          {message.checkpoint && (
            <div className="p-3 rounded-xl bg-[#171b26] border border-purple-500/30 flex flex-col md:flex-row items-center justify-between gap-3 my-2">
              <div className="flex items-center gap-2.5">
                <span className="material-symbols-outlined text-purple-400 text-xl">help_center</span>
                <div>
                  <span className="text-xs font-semibold text-white">{message.checkpoint.title || 'Interactive Checkpoint:'}</span>
                  <p className="text-xs text-slate-300">{message.checkpoint.subtitle}</p>
                </div>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                {message.checkpoint.options?.map((opt, oIdx) => (
                  <button
                    key={oIdx}
                    type="button"
                    onClick={() => onOptionClick && onOptionClick(opt.prompt || opt.label)}
                    className={`px-3 py-1.5 rounded-lg text-xs transition-all ${
                      oIdx === 1
                        ? 'bg-indigo-600 hover:bg-indigo-500 text-white font-medium shadow-md'
                        : 'bg-[#262a35] hover:bg-[#313540] text-slate-200'
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons for Route Navigation */}
          {message.actions && message.actions.length > 0 && (
            <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-[#262a35] mt-3">
              <span className="text-[11px] font-mono text-slate-400 mr-1">Recommended Actions:</span>
              {message.actions.map((act, aIdx) => (
                <button
                  key={aIdx}
                  type="button"
                  onClick={() => navigate(act.route)}
                  className="px-3 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 hover:text-indigo-200 border border-indigo-500/30 text-xs font-medium transition-all flex items-center gap-1.5 shadow-sm"
                >
                  <span className="material-symbols-outlined text-sm">open_in_new</span>
                  <span>{act.label}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
