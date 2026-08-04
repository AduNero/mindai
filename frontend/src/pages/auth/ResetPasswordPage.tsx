import { FormEvent, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";

import { authApi } from "@/api";
import { useToast } from "@/context/ToastContext";
import { extractErrorMessage } from "@/utils/errors";

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { showToast } = useToast();

  const [email, setEmail] = useState(searchParams.get("email") || "");
  const [otp, setOtp] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }
    setSubmitting(true);
    try {
      await authApi.confirmPasswordReset(email, otp, password, confirm);
      showToast("Password reset. Please log in with your new password.", "success");
      navigate("/login");
    } catch (err) {
      setError(extractErrorMessage(err, "This code is invalid or has expired."));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="card animate-slide-up">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Set a new password</h1>
      <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
        Enter the code we emailed you along with your new password.
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
          <label htmlFor="otp" className="label">Reset code</label>
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
        <div>
          <label htmlFor="password" className="label">New password</label>
          <input id="password" type="password" required minLength={10} className="input" value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        <div>
          <label htmlFor="confirm" className="label">Confirm new password</label>
          <input id="confirm" type="password" required className="input" value={confirm} onChange={(e) => setConfirm(e.target.value)} />
        </div>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button type="submit" disabled={submitting || otp.length !== 6} className="btn-primary w-full">
          {submitting ? "Resetting..." : "Reset password"}
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-gray-500 dark:text-gray-400">
        <Link to="/forgot-password" className="font-medium text-brand-600 hover:underline">
          Request a new code
        </Link>
      </p>
    </div>
  );
}
