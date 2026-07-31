import type { ContentAnalysis, MoodPrediction, Paginated, RiskAssessment, WellnessScoreSnapshot } from "@/types";

import { apiClient } from "./client";

export const aiApi = {
  getContentAnalysis: (appLabel: string, model: string, objectId: string) =>
    apiClient.get<ContentAnalysis>(`/ai/analysis/${appLabel}/${model}/${objectId}/`),

  wellnessScoreHistory: (days?: number) =>
    apiClient.get<WellnessScoreSnapshot[]>("/ai/wellness-score/", { params: days ? { days } : undefined }),

  wellnessScoreCurrent: () => apiClient.get<WellnessScoreSnapshot | null>("/ai/wellness-score/current/"),

  moodPredictions: () => apiClient.get<MoodPrediction[]>("/ai/mood-predictions/"),

  riskAssessments: (params?: Record<string, string | number>) =>
    apiClient.get<Paginated<RiskAssessment>>("/ai/risk-assessments/", { params }),

  acknowledgeRisk: (id: string) => apiClient.post<RiskAssessment>(`/ai/risk-assessments/${id}/acknowledge/`),
};
