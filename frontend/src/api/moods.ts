import type { DailyMoodStat, MoodEntry, Paginated } from "@/types";

import { apiClient } from "./client";

export interface MoodEntryPayload {
  mood: string;
  intensity: number;
  entry_date: string;
  entry_time: string;
  notes?: string;
}

export const moodsApi = {
  list: (params?: Record<string, string | number>) =>
    apiClient.get<Paginated<MoodEntry>>("/moods/", { params }),

  create: (payload: MoodEntryPayload) => apiClient.post<MoodEntry>("/moods/", payload),

  update: (id: string, payload: Partial<MoodEntryPayload>) =>
    apiClient.patch<MoodEntry>(`/moods/${id}/`, payload),

  remove: (id: string) => apiClient.delete(`/moods/${id}/`),

  current: () => apiClient.get<MoodEntry | null>("/moods/current/"),

  weekly: () => apiClient.get<DailyMoodStat[]>("/moods/weekly/"),

  monthly: () => apiClient.get<DailyMoodStat[]>("/moods/monthly/"),

  choices: () => apiClient.get<{ value: string; label: string }[]>("/moods/choices/"),
};
