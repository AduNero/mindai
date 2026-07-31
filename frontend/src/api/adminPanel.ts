import type {
  AdminActionLog,
  DashboardStats,
  GeneratedReport,
  JournalReport,
  Paginated,
  RiskAssessment,
} from "@/types";

import { apiClient } from "./client";

export const adminPanelApi = {
  dashboardStats: () => apiClient.get<DashboardStats>("/admin-panel/dashboard-stats/"),

  actionLogs: (params?: Record<string, string | number>) =>
    apiClient.get<Paginated<AdminActionLog>>("/admin-panel/action-logs/", { params }),

  journalReports: (params?: Record<string, string | number>) =>
    apiClient.get<Paginated<JournalReport>>("/admin-panel/journal-reports/", { params }),

  resolveJournalReport: (
    id: string,
    payload: { status: "reviewed" | "actioned" | "dismissed"; review_notes?: string; remove_entry?: boolean },
  ) => apiClient.post<JournalReport>(`/admin-panel/journal-reports/${id}/resolve/`, payload),

  riskAlerts: (params?: Record<string, string | number>) =>
    apiClient.get<Paginated<RiskAssessment>>("/admin-panel/risk-alerts/", { params }),

  reviewRiskAlert: (id: string, admin_notes?: string) =>
    apiClient.post<RiskAssessment>(`/admin-panel/risk-alerts/${id}/review/`, { admin_notes }),
};

export const reportsApi = {
  list: (params?: Record<string, string | number>) =>
    apiClient.get<Paginated<GeneratedReport>>("/admin-panel/reports/", { params }),

  generate: (payload: {
    report_type: string;
    format: "pdf" | "csv";
    period_start: string;
    period_end: string;
  }) => apiClient.post<GeneratedReport>("/admin-panel/reports/", payload),

  get: (id: string) => apiClient.get<GeneratedReport>(`/admin-panel/reports/${id}/`),
};
