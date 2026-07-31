import type { JournalEntry, JournalStats, Paginated, Tag } from "@/types";

import { apiClient } from "./client";

export interface JournalEntryPayload {
  title: string;
  body: string;
  mood?: string;
  tags?: string[];
  entry_date: string;
  visibility?: "private" | "public";
}

export const journalsApi = {
  list: (params?: Record<string, string | number>) =>
    apiClient.get<Paginated<JournalEntry>>("/journals/", { params }),

  get: (id: string) => apiClient.get<JournalEntry>(`/journals/${id}/`),

  create: (payload: JournalEntryPayload) => apiClient.post<JournalEntry>("/journals/", payload),

  update: (id: string, payload: Partial<JournalEntryPayload>) =>
    apiClient.patch<JournalEntry>(`/journals/${id}/`, payload),

  remove: (id: string) => apiClient.delete(`/journals/${id}/`),

  stats: () => apiClient.get<JournalStats>("/journals/stats/"),

  tags: () => apiClient.get<Paginated<Tag>>("/journals/tags/"),

  report: (journal_entry: string, reason: string, details?: string) =>
    apiClient.post("/journals/reports/", { journal_entry, reason, details }),
};
