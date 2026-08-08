export type NotificationType = "daily_reminder" | "journal_reminder" | "mood_reminder" | "system" | "risk_alert";

export interface Notification {
  id: string;
  notification_type: NotificationType;
  channel: "in_app" | "email" | "both";
  title: string;
  body: string;
  is_read: boolean;
  read_at: string | null;
  created_at: string;
}

export interface NotificationPreference {
  daily_reminder: boolean;
  journal_reminder: boolean;
  mood_reminder: boolean;
  email_enabled: boolean;
  in_app_enabled: boolean;
  preferred_reminder_time: string;
}
