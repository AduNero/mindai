import { FormEvent, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";

import { authApi } from "@/api";
import { useToast } from "@/context/ToastContext";
import { extractErrorMessage } from "@/utils/errors";

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";
  const navigate = useNavigate();
  const { showToast } = useToast();

  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (password !== confirm) {
      showToast("Passwords do not match.", "error");
      return;
    }
    setSubmitting(true);
    try {
      await authApi.confirmPasswordReset(token, password, confirm);
      showToast("Password reset. Please log in with your new password.", "success");
      navigate("/login");
    } catch (err) {
      showToast(extractErrorMessage(err, "This reset link is invalid or expired."), "error");
    } finally {
      setSubmitting(false);
    }
  };

  if (!token) {
    return (
      <div className="card animate-slide-up text-center">
        <h1 className="text-xl font-bold text-gray-900 dark:text-white">Invalid link</h1>
        <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">This password reset link is missing a token.</p>
        <Link to="/forgot-password" className="btn-outline mt-6 w-full">
          Request a new link
        </Link>
      </div>
    );
  }

  return (
    <div className="card animate-slide-up">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Set a new password</h1>
      <form onSubmit={handleSubmit} className="mt-6 space-y-4">
        <div>
          <label htmlFor="password" className="label">New password</label>
          <input id="password" type="password" required minLength={10} className="input" value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        <div>
          <label htmlFor="confirm" className="label">Confirm new password</label>
          <input id="confirm" type="password" required className="input" value={confirm} onChange={(e) => setConfirm(e.target.value)} />
        </div>
        <button type="submit" disabled={submitting} className="btn-primary w-full">
          {submitting ? "Resetting..." : "Reset password"}
        </button>
      </form>
    </div>
  );
}
