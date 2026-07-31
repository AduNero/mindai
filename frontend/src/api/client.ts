import axios, { AxiosError, AxiosHeaders, InternalAxiosRequestConfig } from "axios";

import { tokenStorage } from "@/utils/tokenStorage";

const BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  // Everywhere else this API is bearer-token (JWT) auth and ignores
  // cookies entirely, but /auth/librechat-session/ sets a session cookie
  // the browser needs to send/receive across origins for the LibreChat
  // SSO bridge to work (see pages/app/AIChatPage.tsx).
  withCredentials: true,
});

apiClient.interceptors.request.use((config) => {
  const token = tokenStorage.getAccess();
  if (token) {
    config.headers = config.headers ?? new AxiosHeaders();
    config.headers.set("Authorization", `Bearer ${token}`);
  }
  return config;
});

type RetryableConfig = InternalAxiosRequestConfig & { _retry?: boolean };

let isRefreshing = false;
let refreshWaiters: Array<(token: string | null) => void> = [];

function waitForRefresh(callback: (token: string | null) => void) {
  refreshWaiters.push(callback);
}

function resolveWaiters(token: string | null) {
  refreshWaiters.forEach((cb) => cb(token));
  refreshWaiters = [];
}

// Endpoints that must never trigger a refresh-and-retry (prevents infinite loops).
const REFRESH_EXEMPT_PATHS = ["/auth/login/", "/auth/refresh/", "/auth/register/"];

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetryableConfig | undefined;

    const isExempt = REFRESH_EXEMPT_PATHS.some((path) => originalRequest?.url?.includes(path));
    if (error.response?.status !== 401 || !originalRequest || originalRequest._retry || isExempt) {
      return Promise.reject(error);
    }

    const refreshToken = tokenStorage.getRefresh();
    if (!refreshToken) {
      tokenStorage.clear();
      redirectToLogin();
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        waitForRefresh((token) => {
          if (!token) {
            reject(error);
            return;
          }
          originalRequest.headers.set("Authorization", `Bearer ${token}`);
          resolve(apiClient(originalRequest));
        });
      });
    }

    isRefreshing = true;
    try {
      const { data } = await axios.post(`${BASE_URL}/auth/refresh/`, { refresh: refreshToken });
      tokenStorage.setAccess(data.access);
      resolveWaiters(data.access);
      originalRequest.headers.set("Authorization", `Bearer ${data.access}`);
      return await apiClient(originalRequest);
    } catch (refreshError) {
      resolveWaiters(null);
      tokenStorage.clear();
      redirectToLogin();
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  },
);

function redirectToLogin() {
  if (window.location.pathname !== "/login") {
    window.location.href = "/login";
  }
}
