import type { MeditationProgress, MeditationSession, Paginated, SleepEntry } from "@/types";

import { apiClient } from "./client";

export const wellnessApi = {
  listSleep: (params?: Record<string, string | number>) =>
    apiClient.get<Paginated<SleepEntry>>("/wellness/sleep/", { params }),

  createSleep: (payload: { entry_date: string; hours_slept: number; quality: number; notes?: string }) =>
    apiClient.post<SleepEntry>("/wellness/sleep/", payload),

  updateSleep: (id: string, payload: Partial<{ hours_slept: number; quality: number; notes: string }>) =>
    apiClient.patch<SleepEntry>(`/wellness/sleep/${id}/`, payload),

  removeSleep: (id: string) => apiClient.delete(`/wellness/sleep/${id}/`),

  listMeditation: (params?: Record<string, string | number>) =>
    apiClient.get<Paginated<MeditationSession>>("/wellness/meditation/", { params }),

  createMeditation: (payload: {
    resource?: string;
    duration_minutes: number;
    started_at: string;
    completed_at?: string;
    completed?: boolean;
  }) => apiClient.post<MeditationSession>("/wellness/meditation/", payload),

  meditationProgress: () => apiClient.get<MeditationProgress>("/wellness/meditation/progress/"),
};
