import type { ChatMessage, ChatSearchResult, ChatSessionDetail, Paginated } from "@/types";
import type { ChatSession } from "@/types";

import { apiClient } from "./client";

export const chatApi = {
  listSessions: (params?: Record<string, string | number>) =>
    apiClient.get<Paginated<ChatSession>>("/chat/sessions/", { params }),

  createSession: (title?: string) => apiClient.post<ChatSession>("/chat/sessions/", { title }),

  getSession: (id: string) => apiClient.get<ChatSessionDetail>(`/chat/sessions/${id}/`),

  updateSession: (id: string, payload: { title?: string; is_archived?: boolean }) =>
    apiClient.patch<ChatSession>(`/chat/sessions/${id}/`, payload),

  deleteSession: (id: string) => apiClient.delete(`/chat/sessions/${id}/`),

  getMessages: (id: string) => apiClient.get<ChatMessage[]>(`/chat/sessions/${id}/messages/`),

  sendMessage: (id: string, content: string) =>
    apiClient.post<ChatMessage>(`/chat/sessions/${id}/send/`, { content }),

  // JWT-protected — must be fetched through apiClient (Authorization header),
  // not linked to directly, so a Blob download is built from the response.
  exportSessionAsText: (id: string) =>
    apiClient.get<Blob>(`/chat/sessions/${id}/export/`, {
      params: { export_format: "txt" },
      responseType: "blob",
    }),

  search: (q: string) => apiClient.get<ChatSearchResult[]>("/chat/search/", { params: { q } }),

  syncLibreChatNow: () => apiClient.post<{ synced_conversations: number }>("/chat/sync-librechat/"),
};
