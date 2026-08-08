import type { AdminActionLog, DashboardStats, Paginated, RiskAssessment } from "@/types";

import { apiClient } from "./client";

export const adminPanelApi = {
  dashboardStats: () => apiClient.get<DashboardStats>("/admin-panel/dashboard-stats/"),

  actionLogs: (params?: Record<string, string | number>) =>
    apiClient.get<Paginated<AdminActionLog>>("/admin-panel/action-logs/", { params }),

  riskAlerts: (params?: Record<string, string | number>) =>
    apiClient.get<Paginated<RiskAssessment>>("/admin-panel/risk-alerts/", { params }),

  reviewRiskAlert: (id: string, admin_notes?: string) =>
    apiClient.post<RiskAssessment>(`/admin-panel/risk-alerts/${id}/review/`, { admin_notes }),
};
