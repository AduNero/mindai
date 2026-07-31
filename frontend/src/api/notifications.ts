import type { Notification, NotificationPreference, Paginated } from "@/types";

import { apiClient } from "./client";

export const notificationsApi = {
  list: (params?: Record<string, string | number>) =>
    apiClient.get<Paginated<Notification>>("/notifications/", { params }),

  unreadCount: () => apiClient.get<{ unread_count: number }>("/notifications/unread-count/"),

  markRead: (id: string) => apiClient.post<{ marked_read: boolean }>(`/notifications/${id}/read/`),

  markAllRead: () => apiClient.post<{ marked_read_count: number }>("/notifications/read-all/"),

  getPreferences: () => apiClient.get<NotificationPreference>("/notifications/preferences/"),

  updatePreferences: (payload: Partial<NotificationPreference>) =>
    apiClient.patch<NotificationPreference>("/notifications/preferences/", payload),
};
