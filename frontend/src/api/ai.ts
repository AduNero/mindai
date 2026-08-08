import type { Paginated, RiskAssessment } from "@/types";

import { apiClient } from "./client";

export const aiApi = {
  riskAssessments: (params?: Record<string, string | number>) =>
    apiClient.get<Paginated<RiskAssessment>>("/ai/risk-assessments/", { params }),

  acknowledgeRisk: (id: string) => apiClient.post<RiskAssessment>(`/ai/risk-assessments/${id}/acknowledge/`),
};
