import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";

import { notificationsApi } from "@/api";
import type { Notification } from "@/types";
import { cn } from "@/utils/cn";

export function NotificationBell() {
  const [open, setOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [recent, setRecent] = useState<Notification[]>([]);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let cancelled = false;

    const fetchUnread = async () => {
      try {
        const { data } = await notificationsApi.unreadCount();
        if (!cancelled) setUnreadCount(data.unread_count);
      } catch {
        // Silently ignore — the bell just won't show a badge this cycle.
      }
    };

    fetchUnread();
    const interval = setInterval(fetchUnread, 60_000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleToggle = async () => {
    const next = !open;
    setOpen(next);
    if (next) {
      try {
        const { data } = await notificationsApi.list({ page_size: 5 });
        setRecent(data.results);
      } catch {
        setRecent([]);
      }
    }
  };

  const handleMarkAllRead = async () => {
    await notificationsApi.markAllRead();
    setUnreadCount(0);
    setRecent((prev) => prev.map((n) => ({ ...n, is_read: true })));
  };

  return (
    <div className="relative" ref={containerRef}>
      <button
        type="button"
        onClick={handleToggle}
        aria-label="Notifications"
        className="relative flex h-9 w-9 items-center justify-center rounded-full text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-100"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="h-5 w-5">
          <path
            fillRule="evenodd"
            d="M5.25 9a6.75 6.75 0 0113.5 0v.75c0 2.123.8 4.057 2.118 5.52a.75.75 0 01-.297 1.206c-1.544.57-3.16.99-4.831 1.243a3.75 3.75 0 11-7.48 0 24.585 24.585 0 01-4.831-1.244.75.75 0 01-.298-1.205A8.217 8.217 0 005.25 9.75V9zm4.502 8.9a2.25 2.25 0 104.496 0 25.057 25.057 0 01-4.496 0z"
            clipRule="evenodd"
          />
        </svg>
        {unreadCount > 0 && (
          <span className="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-semibold text-white">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 z-40 mt-2 w-80 animate-slide-up rounded-2xl border border-gray-200 bg-white p-2 shadow-xl dark:border-gray-800 dark:bg-gray-900">
          <div className="flex items-center justify-between px-2 py-1">
            <p className="text-sm font-semibold">Notifications</p>
            {unreadCount > 0 && (
              <button onClick={handleMarkAllRead} className="text-xs text-brand-600 hover:underline">
                Mark all read
              </button>
            )}
          </div>
          <div className="max-h-80 overflow-y-auto">
            {recent.length === 0 ? (
              <p className="px-2 py-6 text-center text-sm text-gray-500 dark:text-gray-400">
                You're all caught up.
              </p>
            ) : (
              recent.map((n) => (
                <div
                  key={n.id}
                  className={cn(
                    "rounded-xl px-2 py-2 text-sm",
                    !n.is_read && "bg-brand-50 dark:bg-brand-950/40",
                  )}
                >
                  <p className="font-medium text-gray-900 dark:text-gray-100">{n.title}</p>
                  {n.body && <p className="mt-0.5 text-xs text-gray-500 dark:text-gray-400">{n.body}</p>}
                </div>
              ))
            )}
          </div>
          <Link
            to="/settings"
            onClick={() => setOpen(false)}
            className="mt-1 block rounded-xl px-2 py-2 text-center text-xs font-medium text-brand-600 hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            Manage notification preferences
          </Link>
        </div>
      )}
    </div>
  );
}
