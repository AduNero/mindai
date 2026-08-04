import { AxiosError } from "axios";

import type { ApiErrorPayload } from "@/types";

export function extractErrorMessage(error: unknown, fallback = "Something went wrong."): string {
  if (error instanceof AxiosError) {
    const payload = error.response?.data as ApiErrorPayload | undefined;
    if (payload?.error?.message) return payload.error.message;
    if (error.message) return error.message;
  }
  if (error instanceof Error) return error.message;
  return fallback;
}

/**
 * Machine-readable reason code set on some backend errors (e.g.
 * AuthenticationFailed("...", code="email_not_verified")) — lets the UI
 * branch on a stable value instead of matching the message text.
 */
export function extractErrorCode(error: unknown): string | undefined {
  if (error instanceof AxiosError) {
    const payload = error.response?.data as ApiErrorPayload | undefined;
    const details = payload?.error?.details;
    if (details && typeof details === "object" && "code" in details) {
      return String((details as { code: unknown }).code);
    }
  }
  return undefined;
}
