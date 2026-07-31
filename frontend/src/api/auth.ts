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

  verifyEmail: (token: string) => apiClient.post<{ message: string }>("/auth/verify-email/", { token }),

  resendVerification: (email: string) =>
    apiClient.post<{ message: string }>("/auth/resend-verification/", { email }),

  requestPasswordReset: (email: string) =>
    apiClient.post<{ message: string }>("/auth/password-reset/request/", { email }),

  confirmPasswordReset: (token: string, new_password: string, new_password_confirm: string) =>
    apiClient.post<{ message: string }>("/auth/password-reset/confirm/", {
      token,
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

  // Bridges JWT auth to a Django session cookie so the browser is
  // recognized when LibreChat's embedded OpenID flow redirects it to
  // MindCare's OIDC /o/authorize/ endpoint. See apps.users.views.EstablishOIDCSessionView.
  establishLibreChatSession: () => apiClient.post<{ message: string }>("/auth/librechat-session/"),
};
