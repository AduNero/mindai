export interface DashboardStats {
  total_users: number;
  active_users_30d: number;
  total_assessments: number;
  high_risk_users: number;
  total_appointments: number;
  pending_appointments: number;
  ai_chat_sessions: number;
  ai_chat_messages: number;
  mood_entries_30d: number;
  journal_entries_30d: number;
  pending_journal_reports: number;
}

export interface AdminActionLog {
  id: string;
  admin_user: string;
  admin_email: string;
  action: string;
  target_model: string;
  target_id: string;
  description: string;
  created_at: string;
}

export type JournalReportStatus = "pending" | "reviewed" | "actioned" | "dismissed";

export interface JournalReport {
  id: string;
  journal_entry: string;
  journal_title: string;
  reported_by: string | null;
  reported_by_email: string | null;
  reason: string;
  details: string;
  status: JournalReportStatus;
  reviewed_by: string | null;
  review_notes: string;
  reviewed_at: string | null;
  created_at: string;
}

export type ReportType = "daily" | "weekly" | "monthly" | "yearly" | "mental_health";
export type ReportFormat = "pdf" | "csv";
export type ReportStatus = "pending" | "completed" | "failed";

export interface GeneratedReport {
  id: string;
  report_type: ReportType;
  format: ReportFormat;
  period_start: string;
  period_end: string;
  file: string | null;
  status: ReportStatus;
  error_message: string;
  created_at: string;
  completed_at: string | null;
}

export interface AuditLog {
  id: string;
  user: string | null;
  user_email: string | null;
  action: string;
  model_name: string;
  object_id: string;
  ip_address: string | null;
  user_agent: string;
  metadata: Record<string, unknown>;
  created_at: string;
}
