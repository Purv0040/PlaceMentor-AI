import React, { useState } from 'react';

export const MentorHistorySidebar = ({
  isOpen,
  onClose,
  sessions = [],
  activeSessionId,
  onSelectSession,
  onNewChat,
  onDeleteSession,
  onRenameSession
}) => {
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  const handleStartRename = (e, session) => {
    e.stopPropagation();
    setEditingId(session.id);
    setEditTitle(session.title);
  };

  const handleSaveRename = (e, sessionId) => {
    e.stopPropagation();
    if (editTitle.trim()) {
      onRenameSession(sessionId, editTitle.trim());
    }
    setEditingId(null);
  };

  const handleCancelRename = (e) => {
    e.stopPropagation();
    setEditingId(null);
  };

  const filteredSessions = sessions.filter((s) =>
    (s.title || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <>
      {/* Mobile Backdrop overlay */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-30 lg:hidden"
        />
      )}

      {/* Slide-out Sidebar Panel */}
      <aside
        className={`fixed lg:static top-0 bottom-0 left-0 z-40 w-72 md:w-80 h-full bg-[#0d111c] border-r border-[#1f2433] flex flex-col transition-all duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0 lg:w-72'
        }`}
      >
        {/* Sidebar Header & New Chat Button */}
        <div className="p-3 border-b border-[#1f2433] flex flex-col gap-2.5 shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-purple-400 text-lg">history</span>
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-300">
                Chat History
              </span>
            </div>
            {/* Close button on mobile/desktop toggle */}
            <button
              type="button"
              onClick={onClose}
              className="lg:hidden p-1 rounded-lg text-slate-400 hover:text-white hover:bg-[#1a1f2e] transition-colors"
              title="Close history panel"
            >
              <span className="material-symbols-outlined text-sm">close</span>
            </button>
          </div>

          {/* New Chat Primary Action Button */}
          <button
            type="button"
            onClick={onNewChat}
            className="w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl bg-purple-600/15 hover:bg-purple-600 text-purple-300 hover:text-white border border-purple-500/30 hover:border-purple-500 font-medium text-xs shadow-sm transition-all group"
          >
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-base group-hover:rotate-90 transition-transform">
                add
              </span>
              <span>New Chat</span>
            </div>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#101422] border border-[#23293d] text-slate-400 group-hover:border-purple-400 group-hover:text-purple-200">
              Ctrl+N
            </span>
          </button>

          {/* Search Filter Input */}
          {sessions.length > 3 && (
            <div className="relative">
              <span className="material-symbols-outlined text-slate-500 text-sm absolute left-2.5 top-1/2 -translate-y-1/2">
                search
              </span>
              <input
                type="text"
                placeholder="Search chats..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-[#131826] border border-[#1f2638] rounded-lg pl-8 pr-2.5 py-1.5 text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-purple-500/50"
              />
            </div>
          )}
        </div>

        {/* Conversation List Stream with sleek scrollbar */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1 custom-scrollbar min-h-0">
          {filteredSessions.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-48 text-center px-4 text-slate-500 text-xs">
              <span className="material-symbols-outlined text-2xl mb-1 text-slate-600">
                chat_bubble_outline
              </span>
              <p>No chat history yet.</p>
              <p className="text-[11px] text-slate-600 mt-1">Start a conversation to save your sessions.</p>
            </div>
          ) : (
            filteredSessions.map((session) => {
              const isActive = session.id === activeSessionId;
              const isEditing = editingId === session.id;

              return (
                <div
                  key={session.id}
                  onClick={() => onSelectSession(session.id)}
                  className={`group relative flex items-center justify-between px-3 py-2.5 rounded-xl cursor-pointer text-xs transition-all ${
                    isActive
                      ? 'bg-[#1e2335] text-white border border-purple-500/30 shadow-md font-medium'
                      : 'text-slate-300 hover:text-white hover:bg-[#151928] border border-transparent'
                  }`}
                >
                  {isEditing ? (
                    <div className="flex items-center gap-1.5 w-full" onClick={(e) => e.stopPropagation()}>
                      <input
                        type="text"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') handleSaveRename(e, session.id);
                          if (e.key === 'Escape') handleCancelRename(e);
                        }}
                        autoFocus
                        className="flex-1 bg-[#0a0d15] border border-purple-500 text-white rounded px-2 py-1 text-xs focus:outline-none"
                      />
                      <button
                        type="button"
                        onClick={(e) => handleSaveRename(e, session.id)}
                        className="p-1 text-emerald-400 hover:text-emerald-300"
                        title="Save"
                      >
                        <span className="material-symbols-outlined text-sm">check</span>
                      </button>
                      <button
                        type="button"
                        onClick={handleCancelRename}
                        className="p-1 text-rose-400 hover:text-rose-300"
                        title="Cancel"
                      >
                        <span className="material-symbols-outlined text-sm">close</span>
                      </button>
                    </div>
                  ) : (
                    <>
                      <div className="flex items-center gap-2.5 min-w-0 pr-2">
                        <span
                          className={`material-symbols-outlined text-sm shrink-0 ${
                            isActive ? 'text-purple-400' : 'text-slate-500 group-hover:text-slate-300'
                          }`}
                        >
                          chat
                        </span>
                        <div className="flex flex-col min-w-0">
                          <span className="truncate text-xs font-normal" title={session.title}>
                            {session.title || 'Untitled Session'}
                          </span>
                          {session.updatedAt && (
                            <span className="text-[10px] text-slate-500 font-mono">
                              {new Date(session.updatedAt).toLocaleDateString([], {
                                month: 'short',
                                day: 'numeric'
                              })}
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Action buttons (Rename & Delete) */}
                      <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          type="button"
                          onClick={(e) => handleStartRename(e, session)}
                          className="p-1 rounded text-slate-400 hover:text-slate-200 hover:bg-[#20273a] transition-colors"
                          title="Rename chat"
                        >
                          <span className="material-symbols-outlined text-[13px]">edit</span>
                        </button>
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            onDeleteSession(session.id);
                          }}
                          className="p-1 rounded text-slate-400 hover:text-rose-400 hover:bg-[#20273a] transition-colors"
                          title="Delete chat"
                        >
                          <span className="material-symbols-outlined text-[13px]">delete</span>
                        </button>
                      </div>
                    </>
                  )}
                </div>
              );
            })
          )}
        </div>

        {/* Sidebar Footer info */}
        <div className="p-3 border-t border-[#1f2433] bg-[#0b0e17] flex items-center justify-between text-[11px] text-slate-500 shrink-0">
          <div className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            <span>AI Memory Active</span>
          </div>
          <span className="font-mono text-[10px]">{sessions.length} chats</span>
        </div>
      </aside>
    </>
  );
};
