import { FormEvent, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";

import { authApi } from "@/api";
import { useToast } from "@/context/ToastContext";
import { extractErrorMessage } from "@/utils/errors";

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { showToast } = useToast();

  const [email, setEmail] = useState(searchParams.get("email") || "");
  const [otp, setOtp] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [resending, setResending] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await authApi.verifyEmail(email, otp);
      showToast("Email verified. You can now log in.", "success");
      navigate("/login");
    } catch (err) {
      setError(extractErrorMessage(err, "This code is invalid or has expired."));
    } finally {
      setSubmitting(false);
    }
  };

  const handleResend = async () => {
    if (!email) {
      setError("Enter your email first.");
      return;
    }
    setResending(true);
    setError("");
    try {
      await authApi.resendVerification(email);
      showToast("If that account exists and is unverified, a new code has been sent.", "success");
    } catch (err) {
      setError(extractErrorMessage(err, "Something went wrong. Please try again."));
    } finally {
      setResending(false);
    }
  };

  return (
    <div className="card animate-slide-up">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Verify your email</h1>
      <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
        Enter the 6-digit code we sent to your email address.
      </p>

      <form onSubmit={handleSubmit} className="mt-6 space-y-4">
        <div>
          <label htmlFor="email" className="label">Email</label>
          <input
            id="email"
            type="email"
            required
            className="input"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <div>
          <label htmlFor="otp" className="label">Verification code</label>
          <input
            id="otp"
            inputMode="numeric"
            pattern="[0-9]{6}"
            maxLength={6}
            required
            autoComplete="one-time-code"
            className="input tracking-widest"
            value={otp}
            onChange={(e) => setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))}
          />
        </div>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button type="submit" disabled={submitting || otp.length !== 6} className="btn-primary w-full">
          {submitting ? "Verifying..." : "Verify email"}
        </button>
      </form>

      <button
        type="button"
        onClick={handleResend}
        disabled={resending}
        className="btn-outline mt-3 w-full"
      >
        {resending ? "Sending..." : "Resend code"}
      </button>

      <p className="mt-6 text-center text-sm text-gray-500 dark:text-gray-400">
        <Link to="/login" className="font-medium text-brand-600 hover:underline">
          Back to login
        </Link>
      </p>
    </div>
  );
}
