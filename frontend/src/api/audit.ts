import type { AuditLog, Paginated } from "@/types";

import { apiClient } from "./client";

export const auditApi = {
  logs: (params?: Record<string, string | number>) =>
    apiClient.get<Paginated<AuditLog>>("/audit/logs/", { params }),
};
