import { AnimatePresence, motion } from "framer-motion";
import { FormEvent, KeyboardEvent, MouseEvent, useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { chatApi } from "@/api";
import { FullPageSpinner } from "@/components/common/Spinner";
import {
  ArrowLeftIcon,
  ArrowRightIcon,
  ChatIcon,
  ClipboardIcon,
  DownloadIcon,
  HeartIcon,
  PlusIcon,
  SearchIcon,
  SendIcon,
  SparkleIcon,
  TrashIcon,
} from "@/components/common/icons";
import { useToast } from "@/context/ToastContext";
import type { ChatMessage, ChatSession } from "@/types";
import { cn } from "@/utils/cn";

const SUGGESTED_PROMPTS = [
  { text: "I've been feeling anxious lately", Icon: HeartIcon },
  { text: "Tips for better sleep", Icon: SparkleIcon },
  { text: "How can I manage exam stress?", Icon: ClipboardIcon },
  { text: "I just want to talk", Icon: ChatIcon },
];

/**
 * Friendly companion avatar — a small rounded character with glowing eyes,
 * reused everywhere the AI's "presence" shows up (empty state, message
 * bubbles, typing indicator) so it reads as one consistent character
 * rather than a generic icon-in-a-box.
 */
function CompanionMascot({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 64 64" className={className} fill="none" aria-hidden="true">
      <rect x="1" y="30" width="6" height="10" rx="3" className="fill-gray-200 dark:fill-gray-700" />
      <rect x="57" y="30" width="6" height="10" rx="3" className="fill-gray-200 dark:fill-gray-700" />
      <circle cx="32" cy="6" r="3" className="fill-brand-400" />
      <line x1="32" y1="9" x2="32" y2="14" stroke="currentColor" strokeOpacity="0.15" strokeWidth="2" />
      <rect
        x="10"
        y="12"
        width="44"
        height="38"
        rx="19"
        className="fill-gray-50 stroke-gray-200 dark:fill-gray-800 dark:stroke-gray-700"
        strokeWidth="1.5"
      />
      <rect x="22" y="26" width="6" height="12" rx="3" className="fill-brand-500" />
      <rect x="36" y="26" width="6" height="12" rx="3" className="fill-brand-500" />
      <rect
        x="20"
        y="52"
        width="24"
        height="12"
        rx="6"
        className="fill-gray-50 stroke-gray-200 dark:fill-gray-800 dark:stroke-gray-700"
        strokeWidth="1.5"
      />
    </svg>
  );
}

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
  // On mobile, the session list and the active chat share one screen —
  // only one is visible at a time. Defaults to the list (like any
  // messaging app), independent of `activeId`, so loading a session in
  // the background on first load doesn't jump straight past it.
  const [mobileShowChat, setMobileShowChat] = useState(false);
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
        if (results.length > 0) loadSessionMessages(results[0].id);
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

  const loadSessionMessages = async (id: string) => {
    setActiveId(id);
    const { data } = await chatApi.getSession(id);
    setMessages(data.messages);
    setActiveTitle(data.title);
  };

  const selectSession = async (id: string) => {
    await loadSessionMessages(id);
    setMobileShowChat(true);
  };

  const handleNewSession = async () => {
    const { data } = await chatApi.createSession("New conversation");
    setSessions((prev) => [data, ...prev]);
    setActiveId(data.id);
    setMessages([]);
    setActiveTitle(data.title);
    setDraft("");
    setMobileShowChat(true);
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
        // Not selectSession — deleting from the list shouldn't also jump
        // straight into a different chat out from under the user.
        loadSessionMessages(remaining[0].id);
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
    <div className="grid h-[calc(100dvh-8.5rem)] grid-cols-1 gap-4 overflow-hidden md:grid-cols-[300px_1fr]">
      {/* Sidebar — on mobile this and the chat pane below share one screen;
          only one shows at a time, switched via mobileShowChat. Both
          always render side by side from md upward. */}
      <div className={cn("card flex-col overflow-hidden !p-0", mobileShowChat ? "hidden md:flex" : "flex")}>
        <div className="border-b border-gray-100 p-4 dark:border-gray-800">
          <div className="mb-3 flex items-center gap-2">
            <CompanionMascot className="h-8 w-9" />
            <h1 className="font-semibold text-gray-900 dark:text-gray-100">AI Companion</h1>
          </div>
          <button onClick={handleNewSession} className="btn-primary w-full text-sm shadow-sm">
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
                  "group flex w-full items-center justify-between gap-2 rounded-2xl px-3 py-2.5 text-left text-sm transition-colors",
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
      <div className={cn("card flex-col overflow-hidden !p-0", mobileShowChat ? "flex" : "hidden md:flex")}>
        {!activeId ? (
          <div className="flex flex-1 items-center justify-center overflow-y-auto p-4 sm:p-6">
            <div className="w-full max-w-lg">
              <div className="rounded-3xl border border-gray-100 bg-gray-50 px-5 py-8 text-center dark:border-gray-800 dark:bg-gray-900/60 sm:px-8 sm:py-10">
                <CompanionMascot className="mx-auto h-16 w-[4.5rem]" />
                <h2 className="mt-4 text-2xl font-semibold text-gray-900 dark:text-gray-100">
                  Turn your thoughts into <span className="text-brand-600 dark:text-brand-400">clarity</span>.
                </h2>
                <p className="mx-auto mt-2 max-w-sm text-sm text-gray-500 dark:text-gray-400">
                  Your AI companion is here to listen — not to judge, and not a substitute for
                  professional care.
                </p>
              </div>

              <form
                onSubmit={handleSend}
                className="mt-3 rounded-3xl border border-gray-200 bg-white p-3 shadow-sm dark:border-gray-800 dark:bg-gray-900"
              >
                <textarea
                  rows={2}
                  className="w-full resize-none bg-transparent px-2 py-1 text-sm text-gray-900 placeholder-gray-400 outline-none dark:text-gray-100"
                  placeholder="What's on your mind?"
                  value={draft}
                  onChange={(e) => setDraft(e.target.value)}
                  onKeyDown={handleComposerKeyDown}
                />
                <div className="mt-1 flex items-center justify-between px-2">
                  <span className="text-xs text-gray-400">Enter to send</span>
                  <button
                    type="submit"
                    disabled={!draft.trim()}
                    aria-label="Send message"
                    className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-600 text-white transition-colors hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    <SendIcon className="h-4 w-4" />
                  </button>
                </div>
              </form>

              <div className="mt-6">
                <p className="mb-1 px-2 text-xs font-medium uppercase tracking-wide text-gray-400">
                  Suggested
                </p>
                <div className="space-y-0.5">
                  {SUGGESTED_PROMPTS.map(({ text, Icon }) => (
                    <button
                      key={text}
                      onClick={() => sendContent(text)}
                      className="group flex w-full items-center gap-3 rounded-2xl px-2 py-2.5 text-left text-sm transition-colors hover:bg-gray-50 dark:hover:bg-gray-800"
                    >
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-brand-50 text-brand-600 dark:bg-brand-950 dark:text-brand-300">
                        <Icon className="h-4 w-4" />
                      </div>
                      <span className="flex-1 text-gray-700 dark:text-gray-300">{text}</span>
                      <ArrowRightIcon className="h-4 w-4 -translate-x-1 text-gray-300 opacity-0 transition-all group-hover:translate-x-0 group-hover:opacity-100 dark:text-gray-600" />
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <>
            <div className="flex items-center justify-between border-b border-gray-100 px-3 py-3.5 sm:px-5 dark:border-gray-800">
              <div className="flex min-w-0 items-center gap-2 sm:gap-3">
                <button
                  onClick={() => setMobileShowChat(false)}
                  aria-label="Back to conversations"
                  className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-gray-500 hover:bg-gray-100 md:hidden dark:text-gray-400 dark:hover:bg-gray-800"
                >
                  <ArrowLeftIcon className="h-4 w-4" />
                </button>
                <CompanionMascot className="h-8 w-9 shrink-0" />
                <div className="min-w-0 overflow-hidden">
                  <h2 className="truncate font-semibold text-gray-900 dark:text-gray-100">{activeTitle || "New conversation"}</h2>
                  <p className="hidden text-xs text-gray-400 sm:block">AI companion &middot; always here to listen</p>
                </div>
              </div>
              <button onClick={handleExport} className="btn-outline shrink-0 text-xs" title="Export conversation">
                <DownloadIcon className="h-3.5 w-3.5" />
                <span className="hidden sm:inline">Export</span>
              </button>
            </div>

            <div className="flex-1 space-y-4 overflow-y-auto px-3 py-5 sm:px-5">
              {messages.length === 0 && (
                <div className="flex flex-col items-center gap-4 py-10 text-center">
                  <p className="text-sm text-gray-400">No messages yet — say hello.</p>
                  <div className="flex flex-wrap justify-center gap-2">
                    {SUGGESTED_PROMPTS.map(({ text }) => (
                      <button key={text} onClick={() => sendContent(text)} className="btn-outline text-xs">
                        {text}
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

            <div className="border-t border-gray-100 p-2 sm:p-4 dark:border-gray-800">
              <form
                onSubmit={handleSend}
                className="flex items-end gap-2 rounded-3xl border border-gray-200 bg-white p-2 pl-4 dark:border-gray-700 dark:bg-gray-900"
              >
                <textarea
                  ref={textareaRef}
                  rows={1}
                  className="max-h-40 flex-1 resize-none bg-transparent py-2 text-sm text-gray-900 placeholder-gray-400 outline-none dark:text-gray-100"
                  placeholder="Type a message..."
                  value={draft}
                  onChange={(e) => setDraft(e.target.value)}
                  onKeyDown={handleComposerKeyDown}
                  disabled={sending}
                />
                <button
                  type="submit"
                  disabled={sending || !draft.trim()}
                  aria-label="Send message"
                  className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand-600 text-white transition-colors hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-40"
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
      {!isUser && <CompanionMascot className="h-7 w-8 shrink-0" />}
      <div
        className={cn(
          "max-w-[88%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed sm:max-w-[75%]",
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
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="flex items-end gap-2">
      <CompanionMascot className="h-7 w-8 shrink-0" />
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
