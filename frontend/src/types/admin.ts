export interface DashboardStats {
  total_users: number;
  active_users_30d: number;
  high_risk_users: number;
  mood_entries_30d: number;
  journal_entries_30d: number;
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
