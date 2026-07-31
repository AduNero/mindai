import type { AdminAppointment, Appointment, Paginated } from "@/types";

import { apiClient } from "./client";

export interface AppointmentCreatePayload {
  counselor_id: string;
  scheduled_at: string;
  duration_minutes?: number;
  reason_for_visit?: string;
}

export const appointmentsApi = {
  list: (params?: Record<string, string | number>) =>
    apiClient.get<Paginated<Appointment>>("/appointments/", { params }),

  create: (payload: AppointmentCreatePayload) => apiClient.post<Appointment>("/appointments/", payload),

  cancel: (id: string, cancellation_reason?: string) =>
    apiClient.post<Appointment>(`/appointments/${id}/cancel/`, { cancellation_reason }),

  reschedule: (id: string, scheduled_at: string) =>
    apiClient.post<Appointment>(`/appointments/${id}/reschedule/`, { scheduled_at }),

  admin: {
    list: (params?: Record<string, string | number>) =>
      apiClient.get<Paginated<AdminAppointment>>("/appointments/admin/list/", { params }),

    approve: (id: string, notes?: string) =>
      apiClient.post<AdminAppointment>(`/appointments/admin/${id}/approve/`, { notes }),

    reject: (id: string, notes?: string) =>
      apiClient.post<AdminAppointment>(`/appointments/admin/${id}/reject/`, { notes }),
  },
};
