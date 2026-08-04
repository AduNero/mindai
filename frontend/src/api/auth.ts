import type { LoginResponse, UserSession } from "@/types";

import { apiClient } from "./client";

export interface RegisterPayload {
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  password_confirm: string;
}

export const authApi = {
  register: (payload: RegisterPayload) =>
    apiClient.post<{ message: string; user_id: string }>("/auth/register/", payload),

  login: (email: string, password: string, remember_me: boolean) =>
    apiClient.post<LoginResponse>("/auth/login/", { email, password, remember_me }),

  refresh: (refresh: string) => apiClient.post<{ access: string }>("/auth/refresh/", { refresh }),

  logout: (refresh: string) => apiClient.post("/auth/logout/", { refresh }),

  logoutAll: () => apiClient.post("/auth/logout-all/"),

  verifyEmail: (email: string, otp: string) =>
    apiClient.post<{ message: string }>("/auth/verify-email/", { email, otp }),

  resendVerification: (email: string) =>
    apiClient.post<{ message: string }>("/auth/resend-verification/", { email }),

  requestPasswordReset: (email: string) =>
    apiClient.post<{ message: string }>("/auth/password-reset/request/", { email }),

  confirmPasswordReset: (email: string, otp: string, new_password: string, new_password_confirm: string) =>
    apiClient.post<{ message: string }>("/auth/password-reset/confirm/", {
      email,
      otp,
      new_password,
      new_password_confirm,
    }),

  changePassword: (old_password: string, new_password: string, new_password_confirm: string) =>
    apiClient.post<{ message: string }>("/auth/password/change/", {
      old_password,
      new_password,
      new_password_confirm,
    }),

  listSessions: () => apiClient.get<UserSession[]>("/auth/sessions/"),

  revokeSession: (id: string) => apiClient.delete(`/auth/sessions/${id}/`),

  deleteAccount: (password: string) => apiClient.post("/auth/account/delete/", { password }),
};
