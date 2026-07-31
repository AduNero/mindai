import type { CounselorProfile } from "./auth";

export type AppointmentStatus =
  | "pending"
  | "approved"
  | "rejected"
  | "cancelled"
  | "rescheduled"
  | "completed";

export interface Appointment {
  id: string;
  counselor: CounselorProfile;
  scheduled_at: string;
  duration_minutes: number;
  status: AppointmentStatus;
  reason_for_visit: string;
  cancellation_reason: string;
  rescheduled_from: string | null;
  created_at: string;
}

export interface AdminAppointment extends Appointment {
  notes: string;
  approved_by: string | null;
}
