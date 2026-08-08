import { FormEvent, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/context/ToastContext";
import type { User } from "@/types";
import { extractErrorCode, extractErrorMessage } from "@/utils/errors";

export default function LoginPage() {
  const { login } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [needsVerification, setNeedsVerification] = useState(false);

  const from = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname || "/dashboard";

  const goToNext = (user: User) => navigate(user.role === "admin" ? "/admin" : from, { replace: true });

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setNeedsVerification(false);
    try {
      const user = await login(email, password, rememberMe);
      showToast(`Welcome back, ${user.pseudonym}!`, "success");
      goToNext(user);
    } catch (err) {
      if (extractErrorCode(err) === "email_not_verified") {
        setNeedsVerification(true);
      } else {
        showToast(extractErrorMessage(err, "Login failed. Check your credentials."), "error");
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="card animate-slide-up">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Welcome back</h1>
      <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Log in to continue to your dashboard.</p>

      <form onSubmit={handleSubmit} className="mt-6 space-y-4">
        <div>
          <label htmlFor="email" className="label">Email</label>
          <input id="email" type="email" required className="input" value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
        <div>
          <label htmlFor="password" className="label">Password</label>
          <input
            id="password"
            type="password"
            required
            className="input"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <div className="flex items-center justify-between text-sm">
          <label className="flex items-center gap-2 text-gray-600 dark:text-gray-300">
            <input
              type="checkbox"
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
              className="h-4 w-4 rounded border-gray-300 text-brand-600 focus:ring-brand-500"
            />
            Remember me
          </label>
          <Link to="/forgot-password" className="font-medium text-brand-600 hover:underline">
            Forgot password?
          </Link>
        </div>
        {needsVerification && (
          <div className="rounded-xl bg-amber-50 p-4 text-sm text-amber-800 dark:bg-amber-950 dark:text-amber-200">
            This account's email hasn't been verified yet.{" "}
            <Link
              to={`/verify-email?email=${encodeURIComponent(email)}`}
              className="font-medium underline"
            >
              Verify it now
            </Link>
            .
          </div>
        )}
        <button type="submit" disabled={submitting} className="btn-primary w-full">
          {submitting ? "Logging in..." : "Log in"}
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-gray-500 dark:text-gray-400">
        Don't have an account?{" "}
        <Link to="/register" className="font-medium text-brand-600 hover:underline">
          Sign up
        </Link>
      </p>
    </div>
  );
}
