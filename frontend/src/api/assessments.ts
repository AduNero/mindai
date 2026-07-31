import type {
  AssessmentCode,
  AssessmentResult,
  AssessmentSubmitResponse,
  AssessmentType,
  AssessmentTypeSummary,
  Paginated,
} from "@/types";

import { apiClient } from "./client";

export interface AssessmentSubmitPayload {
  assessment_type: AssessmentCode;
  answers: { question_id: string; selected_value: number }[];
}

export const assessmentsApi = {
  listTypes: () => apiClient.get<Paginated<AssessmentTypeSummary>>("/assessments/types/"),

  getType: (code: AssessmentCode) => apiClient.get<AssessmentType>(`/assessments/types/${code}/`),

  submit: (payload: AssessmentSubmitPayload) =>
    apiClient.post<AssessmentSubmitResponse>("/assessments/submit/", payload),

  listResults: (params?: Record<string, string | number>) =>
    apiClient.get<Paginated<AssessmentResult>>("/assessments/results/", { params }),

  getResult: (id: string) => apiClient.get<AssessmentResult>(`/assessments/results/${id}/`),
};
