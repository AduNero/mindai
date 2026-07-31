import { AnimatePresence, motion } from "framer-motion";
import { FormEvent, KeyboardEvent, MouseEvent, useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { chatApi } from "@/api";
import { FullPageSpinner } from "@/components/common/Spinner";
import { DownloadIcon, PlusIcon, SearchIcon, SendIcon, SparkleIcon, TrashIcon } from "@/components/common/icons";
import { useToast } from "@/context/ToastContext";
import type { ChatMessage, ChatSession } from "@/types";
import { cn } from "@/utils/cn";

const SUGGESTED_PROMPTS = [
  "I've been feeling anxious lately",
  "Tips for better sleep",
  "How can I manage exam stress?",
  "I just want to talk",
];

/**
 * AI companion chat. Messages are sent to the backend
 * (POST /chat/sessions/:id/send/), which persists the user's message,
 * generates a reply via apps.chat.services.llm (an OpenAI-API-compatible
 * provider — NVIDIA NIM by default), and returns both.
 */
export default function AIChatPage() {
  const { showToast } = useToast();
  const [loading, setLoading] = useState(true);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [activeTitle, setActiveTitle] = useState("");
  const [draft, setDraft] = useState("");
  const [search, setSearch] = useState("");
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const loadSessions = async () => {
    const { data } = await chatApi.listSessions();
    setSessions(data.results);
    return data.results;
  };

  useEffect(() => {
    loadSessions()
      .then((results) => {
        if (results.length > 0) selectSession(results[0].id);
      })
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }, [draft]);

  const selectSession = async (id: string) => {
    setActiveId(id);
    const { data } = await chatApi.getSession(id);
    setMessages(data.messages);
    setActiveTitle(data.title);
  };

  const handleNewSession = async () => {
    const { data } = await chatApi.createSession("New conversation");
    setSessions((prev) => [data, ...prev]);
    setActiveId(data.id);
    setMessages([]);
    setActiveTitle(data.title);
    setDraft("");
    textareaRef.current?.focus();
  };

  const handleDeleteSession = async (e: MouseEvent, id: string) => {
    e.stopPropagation();
    if (!window.confirm("Delete this conversation? This can't be undone.")) return;
    await chatApi.deleteSession(id);
    const remaining = sessions.filter((s) => s.id !== id);
    setSessions(remaining);
    if (activeId === id) {
      if (remaining.length > 0) {
        selectSession(remaining[0].id);
      } else {
        setActiveId(null);
        setMessages([]);
        setActiveTitle("");
      }
    }
  };

  const sendContent = async (content: string) => {
    if (!content.trim() || sending) return;

    let sessionId = activeId;
    if (!sessionId) {
      const { data } = await chatApi.createSession("New conversation");
      setSessions((prev) => [data, ...prev]);
      sessionId = data.id;
      setActiveId(sessionId);
    }

    setDraft("");
    setSending(true);
    try {
      const { data } = await chatApi.sendMessage(sessionId, content);
      setMessages((prev) => [...prev, data.user_message, ...(data.assistant_message ? [data.assistant_message] : [])]);
      if (data.error) {
        showToast("The AI companion is temporarily unavailable — your message was saved.", "error");
      }
      const refreshed = await chatApi.getSession(sessionId);
      setActiveTitle(refreshed.data.title);
      setSessions((prev) =>
        prev.map((s) => (s.id === sessionId ? { ...s, title: refreshed.data.title, message_count: refreshed.data.message_count } : s)),
      );
    } catch {
      setDraft(content);
      showToast("Couldn't send your message — please try again.", "error");
    } finally {
      setSending(false);
    }
  };

  const handleSend = async (e: FormEvent) => {
    e.preventDefault();
    await sendContent(draft);
  };

  const handleComposerKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendContent(draft);
    }
  };

  const handleExport = async () => {
    if (!activeId) return;
    const { data } = await chatApi.exportSessionAsText(activeId);
    const url = URL.createObjectURL(data);
    const link = document.createElement("a");
    link.href = url;
    link.download = `chat-${activeId}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleSearch = async (value: string) => {
    setSearch(value);
    if (!value) {
      await loadSessions();
      return;
    }
    const { data } = await chatApi.search(value);
    const ids = new Set(data.map((r) => r.session_id));
    setSessions((prev) => prev.filter((s) => ids.has(s.id)));
  };

  if (loading) return <FullPageSpinner />;

  return (
    <div className="grid h-[calc(100vh-8.5rem)] grid-cols-1 gap-4 overflow-hidden md:grid-cols-[300px_1fr]">
      {/* Sidebar */}
      <div className="card flex flex-col overflow-hidden !p-0">
        <div className="border-b border-gray-100 p-4 dark:border-gray-800">
          <div className="mb-3 flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 text-white">
              <SparkleIcon className="h-4 w-4" />
            </div>
            <h1 className="font-semibold text-gray-900 dark:text-gray-100">AI Companion</h1>
          </div>
          <button
            onClick={handleNewSession}
            className="btn-primary w-full text-sm shadow-sm"
          >
            <PlusIcon className="h-4 w-4" />
            New conversation
          </button>
        </div>

        <div className="border-b border-gray-100 p-3 dark:border-gray-800">
          <div className="relative">
            <SearchIcon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <input
              className="input pl-9"
              placeholder="Search conversations..."
              value={search}
              onChange={(e) => handleSearch(e.target.value)}
            />
          </div>
        </div>

        <div className="flex-1 space-y-1 overflow-y-auto p-2">
          {sessions.length === 0 ? (
            <p className="px-3 py-6 text-center text-xs text-gray-400">No conversations yet — start one above.</p>
          ) : (
            sessions.map((s) => (
              <button
                key={s.id}
                onClick={() => selectSession(s.id)}
                className={cn(
                  "group flex w-full items-center justify-between gap-2 rounded-xl px-3 py-2.5 text-left text-sm transition-colors",
                  s.id === activeId
                    ? "bg-brand-50 font-medium text-brand-700 dark:bg-brand-950 dark:text-brand-300"
                    : "text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800",
                )}
              >
                <span className="truncate">{s.title || "New conversation"}</span>
                <TrashIcon
                  onClick={(e) => handleDeleteSession(e, s.id)}
                  className="h-3.5 w-3.5 shrink-0 text-gray-400 opacity-0 transition-opacity hover:text-red-500 group-hover:opacity-100"
                />
              </button>
            ))
          )}
        </div>
      </div>

      {/* Main pane */}
      <div className="card flex flex-col overflow-hidden !p-0">
        {!activeId ? (
          <div className="flex flex-1 flex-col items-center justify-center gap-6 px-6 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-500 to-brand-700 text-white shadow-lg shadow-brand-500/20">
              <SparkleIcon className="h-8 w-8" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">How are you feeling today?</h2>
              <p className="mt-1 max-w-sm text-sm text-gray-500 dark:text-gray-400">
                Talk to your AI companion — it's here to listen, not to judge. Not a substitute for professional care.
              </p>
            </div>
            <div className="flex flex-wrap justify-center gap-2">
              {SUGGESTED_PROMPTS.map((prompt) => (
                <button key={prompt} onClick={() => sendContent(prompt)} className="btn-outline text-xs">
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            <div className="flex items-center justify-between border-b border-gray-100 px-5 py-3.5 dark:border-gray-800">
              <div className="flex items-center gap-3 overflow-hidden">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 text-white">
                  <SparkleIcon className="h-4 w-4" />
                </div>
                <div className="overflow-hidden">
                  <h2 className="truncate font-semibold text-gray-900 dark:text-gray-100">{activeTitle || "New conversation"}</h2>
                  <p className="text-xs text-gray-400">AI companion &middot; always here to listen</p>
                </div>
              </div>
              <button onClick={handleExport} className="btn-outline shrink-0 text-xs" title="Export conversation">
                <DownloadIcon className="h-3.5 w-3.5" />
                Export
              </button>
            </div>

            <div className="flex-1 space-y-4 overflow-y-auto px-5 py-5">
              {messages.length === 0 && (
                <div className="flex flex-col items-center gap-4 py-10 text-center">
                  <p className="text-sm text-gray-400">No messages yet — say hello.</p>
                  <div className="flex flex-wrap justify-center gap-2">
                    {SUGGESTED_PROMPTS.map((prompt) => (
                      <button key={prompt} onClick={() => sendContent(prompt)} className="btn-outline text-xs">
                        {prompt}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              <AnimatePresence initial={false}>
                {messages.map((m) => (
                  <MessageBubble key={m.id} message={m} />
                ))}
                {sending && <TypingIndicator key="typing" />}
              </AnimatePresence>
              <div ref={bottomRef} />
            </div>

            <div className="border-t border-gray-100 p-4 dark:border-gray-800">
              <form onSubmit={handleSend} className="flex items-end gap-2">
                <textarea
                  ref={textareaRef}
                  rows={1}
                  className="input max-h-40 flex-1 resize-none py-2.5"
                  placeholder="Type a message... (Enter to send, Shift+Enter for a new line)"
                  value={draft}
                  onChange={(e) => setDraft(e.target.value)}
                  onKeyDown={handleComposerKeyDown}
                  disabled={sending}
                />
                <button
                  type="submit"
                  disabled={sending || !draft.trim()}
                  aria-label="Send message"
                  className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-600 text-white transition-colors hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  <SendIcon className="h-4 w-4" />
                </button>
              </form>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.sender === "user";
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={cn("flex items-end gap-2", isUser ? "justify-end" : "justify-start")}
    >
      {!isUser && (
        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-brand-500 to-brand-700 text-white">
          <SparkleIcon className="h-3.5 w-3.5" />
        </div>
      )}
      <div
        className={cn(
          "max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed",
          isUser
            ? "rounded-br-sm bg-brand-600 text-white"
            : "rounded-bl-sm bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100",
        )}
      >
        {isUser ? (
          <span className="whitespace-pre-wrap">{message.content}</span>
        ) : (
          <div className="markdown-content">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                ul: ({ children }) => <ul className="mb-2 list-disc space-y-1 pl-4 last:mb-0">{children}</ul>,
                ol: ({ children }) => <ol className="mb-2 list-decimal space-y-1 pl-4 last:mb-0">{children}</ol>,
                strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                a: ({ children, href }) => (
                  <a href={href} target="_blank" rel="noreferrer" className="text-brand-600 underline dark:text-brand-400">
                    {children}
                  </a>
                ),
                code: ({ children }) => (
                  <code className="rounded bg-black/10 px-1 py-0.5 text-xs dark:bg-white/10">{children}</code>
                ),
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </motion.div>
  );
}

function TypingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className="flex items-end gap-2"
    >
      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-brand-500 to-brand-700 text-white">
        <SparkleIcon className="h-3.5 w-3.5" />
      </div>
      <div className="flex items-center gap-1 rounded-2xl rounded-bl-sm bg-gray-100 px-4 py-3 dark:bg-gray-800">
        {[0, 1, 2].map((i) => (
          <motion.span
            key={i}
            className="h-1.5 w-1.5 rounded-full bg-gray-400 dark:bg-gray-500"
            animate={{ opacity: [0.3, 1, 0.3] }}
            transition={{ duration: 1, repeat: Infinity, delay: i * 0.15 }}
          />
        ))}
      </div>
    </motion.div>
  );
}
