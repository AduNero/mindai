import type { Paginated, Recommendation, RecommendationTemplate } from "@/types";

import { apiClient } from "./client";

export const recommendationsApi = {
  list: (params?: Record<string, string | number>) =>
    apiClient.get<Paginated<Recommendation>>("/recommendations/", { params }),

  updateStatus: (id: string, status: "completed" | "dismissed") =>
    apiClient.patch<Recommendation>(`/recommendations/${id}/`, { status }),

  generate: () => apiClient.post<Recommendation[]>("/recommendations/generate/"),

  admin: {
    listTemplates: () => apiClient.get<Paginated<RecommendationTemplate>>("/recommendations/admin/templates/"),

    createTemplate: (payload: Partial<RecommendationTemplate>) =>
      apiClient.post<RecommendationTemplate>("/recommendations/admin/templates/", payload),

    updateTemplate: (id: string, payload: Partial<RecommendationTemplate>) =>
      apiClient.patch<RecommendationTemplate>(`/recommendations/admin/templates/${id}/`, payload),

    deleteTemplate: (id: string) => apiClient.delete(`/recommendations/admin/templates/${id}/`),
  },
};
