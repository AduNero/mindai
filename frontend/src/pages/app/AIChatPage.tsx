import { FormEvent, useEffect, useRef, useState } from "react";

import { authApi, chatApi } from "@/api";
import { EmptyState } from "@/components/common/EmptyState";
import { FullPageSpinner } from "@/components/common/Spinner";
import { useToast } from "@/context/ToastContext";
import type { ChatMessage, ChatSession } from "@/types";
import { cn } from "@/utils/cn";

type Tab = "live" | "history";

export default function AIChatPage() {
  const [tab, setTab] = useState<Tab>("live");

  return (
    <div className="flex h-[calc(100vh-8.5rem)] flex-col gap-4">
      <div className="flex gap-1 self-start rounded-lg bg-gray-100 p-1 text-sm dark:bg-gray-800">
        {(["live", "history"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={cn(
              "rounded-md px-4 py-1.5 font-medium capitalize transition-colors",
              tab === t ? "bg-white text-gray-900 shadow-sm dark:bg-gray-700 dark:text-white" : "text-gray-500",
            )}
          >
            {t === "live" ? "Live Chat" : "History"}
          </button>
        ))}
      </div>

      {tab === "live" ? <LiveChatPanel /> : <ChatHistoryPanel />}
    </div>
  );
}

/**
 * Embeds LibreChat directly. The user is already logged into MindCare (JWT);
 * `establishLibreChatSession` bridges that to a Django session cookie so
 * when LibreChat's OpenID strategy (OPENID_AUTO_REDIRECT=true) redirects
 * this iframe to MindCare's /o/authorize/ endpoint, it's recognized without
 * a second login. See apps.users.oidc / docs/architecture/librechat-integration.md.
 */
function LiveChatPanel() {
  const [ready, setReady] = useState(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    authApi
      .establishLibreChatSession()
      .then(() => {
        if (!cancelled) setReady(true);
      })
      .catch(() => {
        if (!cancelled) setError(true);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (error) {
    return (
      <div className="card flex-1">
        <EmptyState
          icon="⚠️"
          title="Couldn't connect to Live Chat"
          description="We weren't able to establish your session. Try refreshing, or use the History tab in the meantime."
        />
      </div>
    );
  }

  if (!ready) {
    return (
      <div className="card flex flex-1 items-center justify-center">
        <FullPageSpinner />
      </div>
    );
  }

  return (
    <iframe
      title="MindCare AI Therapy Chat"
      src={import.meta.env.VITE_LIBRECHAT_URL}
      className="flex-1 rounded-2xl border border-gray-200 dark:border-gray-800"
      allow="clipboard-write"
    />
  );
}

/**
 * Native session browser — search/export/list backed by ChatSession/
 * ChatMessage, which mirrors both locally-sent messages (send()) and
 * LibreChat-synced ones (apps.chat.services.librechat_sync). Doubles as a
 * lightweight fallback chat when LibreChat itself isn't reachable.
 */
function ChatHistoryPanel() {
  const { showToast } = useToast();
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [activeTitle, setActiveTitle] = useState("");
  const [draft, setDraft] = useState("");
  const [search, setSearch] = useState("");
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

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
  }, [messages]);

  const selectSession = async (id: string) => {
    setActiveId(id);
    const { data } = await chatApi.getSession(id);
    setMessages(data.messages);
    setActiveTitle(data.title);
  };

  const handleSyncNow = async () => {
    setSyncing(true);
    try {
      const { data } = await chatApi.syncLibreChatNow();
      await loadSessions();
      showToast(
        data.synced_conversations > 0
          ? `Synced ${data.synced_conversations} conversation(s) from Live Chat.`
          : "No new Live Chat conversations to sync.",
        "success",
      );
    } catch {
      showToast("Couldn't sync Live Chat history right now.", "error");
    } finally {
      setSyncing(false);
    }
  };

  const handleNewSession = async () => {
    const { data } = await chatApi.createSession("New conversation");
    setSessions((prev) => [data, ...prev]);
    setActiveId(data.id);
    setMessages([]);
    setActiveTitle(data.title);
  };

  const handleSend = async (e: FormEvent) => {
    e.preventDefault();
    if (!draft.trim()) return;

    let sessionId = activeId;
    if (!sessionId) {
      const { data } = await chatApi.createSession("New conversation");
      setSessions((prev) => [data, ...prev]);
      sessionId = data.id;
      setActiveId(sessionId);
    }

    setSending(true);
    try {
      const { data } = await chatApi.sendMessage(sessionId, draft);
      setMessages((prev) => [...prev, data]);
      setDraft("");
      const refreshed = await chatApi.getSession(sessionId);
      setActiveTitle(refreshed.data.title);
      setSessions((prev) =>
        prev.map((s) => (s.id === sessionId ? { ...s, title: refreshed.data.title, message_count: refreshed.data.message_count } : s)),
      );
    } catch {
      showToast("Couldn't send your message — please try again.", "error");
    } finally {
      setSending(false);
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
    <div className="grid flex-1 grid-cols-1 gap-4 overflow-hidden md:grid-cols-[280px_1fr]">
      <div className="card flex flex-col overflow-hidden p-3">
        <div className="mb-3 flex gap-2">
          <button onClick={handleNewSession} className="btn-primary flex-1 text-sm">
            + New
          </button>
          <button onClick={handleSyncNow} disabled={syncing} className="btn-outline text-sm" title="Pull latest Live Chat history">
            {syncing ? "..." : "Sync"}
          </button>
        </div>
        <input
          className="input mb-3"
          placeholder="Search chats..."
          value={search}
          onChange={(e) => handleSearch(e.target.value)}
        />
        <div className="flex-1 space-y-1 overflow-y-auto">
          {sessions.length === 0 ? (
            <p className="px-2 py-4 text-center text-xs text-gray-400">No conversations yet.</p>
          ) : (
            sessions.map((s) => (
              <button
                key={s.id}
                onClick={() => selectSession(s.id)}
                className={cn(
                  "block w-full truncate rounded-xl px-3 py-2 text-left text-sm",
                  s.id === activeId
                    ? "bg-brand-50 font-medium text-brand-700 dark:bg-brand-950 dark:text-brand-300"
                    : "text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800",
                )}
              >
                {s.title || "New conversation"}
              </button>
            ))
          )}
        </div>
      </div>

      <div className="card flex flex-col overflow-hidden">
        {!activeId ? (
          <EmptyState icon="💬" title="No conversation selected" description="Pick one from the list, or start a new one." />
        ) : (
          <>
            <div className="flex items-center justify-between border-b border-gray-100 pb-3 dark:border-gray-800">
              <h2 className="truncate font-semibold text-gray-900 dark:text-gray-100">{activeTitle}</h2>
              <button onClick={handleExport} className="btn-outline text-xs">
                Export
              </button>
            </div>

            <div className="flex-1 space-y-3 overflow-y-auto py-4">
              {messages.length === 0 && (
                <p className="text-center text-sm text-gray-400">No messages in this conversation yet.</p>
              )}
              {messages.map((m) => (
                <div key={m.id} className={cn("flex", m.sender === "user" ? "justify-end" : "justify-start")}>
                  <div
                    className={cn(
                      "max-w-[75%] rounded-2xl px-4 py-2.5 text-sm",
                      m.sender === "user"
                        ? "bg-brand-600 text-white"
                        : "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100",
                    )}
                  >
                    {m.content}
                  </div>
                </div>
              ))}
              <div ref={bottomRef} />
            </div>

            <form onSubmit={handleSend} className="flex gap-2 border-t border-gray-100 pt-3 dark:border-gray-800">
              <input
                className="input"
                placeholder="Type a message..."
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
              />
              <button type="submit" disabled={sending || !draft.trim()} className="btn-primary">
                Send
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}
