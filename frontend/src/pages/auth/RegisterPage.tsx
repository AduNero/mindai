import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/context/ToastContext";
import { extractErrorMessage } from "@/utils/errors";

export default function RegisterPage() {
  const { register } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
    password: "",
    password_confirm: "",
  });
  const [submitting, setSubmitting] = useState(false);

  const update = (field: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [field]: e.target.value }));

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (form.password !== form.password_confirm) {
      showToast("Passwords do not match.", "error");
      return;
    }
    setSubmitting(true);
    try {
      await register(form);
      showToast("Account created! Check your email for a verification code.", "success");
      navigate(`/verify-email?email=${encodeURIComponent(form.email)}`);
    } catch (err) {
      showToast(extractErrorMessage(err, "Registration failed."), "error");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="card animate-slide-up">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Create your account</h1>
      <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Start tracking your wellbeing today.</p>

      <form onSubmit={handleSubmit} className="mt-6 space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label htmlFor="first_name" className="label">First name</label>
            <input id="first_name" required className="input" value={form.first_name} onChange={update("first_name")} />
          </div>
          <div>
            <label htmlFor="last_name" className="label">Last name</label>
            <input id="last_name" required className="input" value={form.last_name} onChange={update("last_name")} />
          </div>
        </div>
        <div>
          <label htmlFor="email" className="label">Email</label>
          <input id="email" type="email" required className="input" value={form.email} onChange={update("email")} />
        </div>
        <div>
          <label htmlFor="password" className="label">Password</label>
          <input id="password" type="password" required minLength={10} className="input" value={form.password} onChange={update("password")} />
          <p className="mt-1 text-xs text-gray-400">At least 10 characters.</p>
        </div>
        <div>
          <label htmlFor="password_confirm" className="label">Confirm password</label>
          <input
            id="password_confirm"
            type="password"
            required
            className="input"
            value={form.password_confirm}
            onChange={update("password_confirm")}
          />
        </div>
        <button type="submit" disabled={submitting} className="btn-primary w-full">
          {submitting ? "Creating account..." : "Create account"}
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-gray-500 dark:text-gray-400">
        Already have an account?{" "}
        <Link to="/login" className="font-medium text-brand-600 hover:underline">
          Log in
        </Link>
      </p>
    </div>
  );
}
