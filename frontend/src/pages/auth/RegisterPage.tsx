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
    pseudonym: "",
    email: "",
    password: "",
    password_confirm: "",
  });
  const [ageConfirmed, setAgeConfirmed] = useState(false);
  const [consentAccepted, setConsentAccepted] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const update = (field: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [field]: e.target.value }));

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (form.password !== form.password_confirm) {
      showToast("Passwords do not match.", "error");
      return;
    }
    if (!ageConfirmed || !consentAccepted) {
      showToast("Please confirm your age and accept the privacy notice to continue.", "error");
      return;
    }
    setSubmitting(true);
    try {
      await register({ ...form, age_confirmed: ageConfirmed, consent_accepted: consentAccepted });
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
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Create your pseudonymous account</h1>
      <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
        No real name required — just a pseudonym and a recovery email.
      </p>

      <form onSubmit={handleSubmit} className="mt-6 space-y-4">
        <div>
          <label htmlFor="pseudonym" className="label">Pseudonym</label>
          <input
            id="pseudonym"
            required
            maxLength={50}
            className="input"
            placeholder="How you'll appear in the app"
            value={form.pseudonym}
            onChange={update("pseudonym")}
          />
        </div>
        <div>
          <label htmlFor="email" className="label">Recovery email</label>
          <input id="email" type="email" required className="input" value={form.email} onChange={update("email")} />
          <p className="mt-1 text-xs text-gray-400">Used only for login and account recovery — never shown to other users.</p>
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

        <div className="space-y-2 border-t border-gray-100 pt-4 dark:border-gray-800">
          <label className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-300">
            <input
              type="checkbox"
              required
              checked={ageConfirmed}
              onChange={(e) => setAgeConfirmed(e.target.checked)}
              className="mt-0.5 h-4 w-4 rounded border-gray-300 text-brand-600 focus:ring-brand-500"
            />
            I confirm that I am 18 years of age or older.
          </label>
          <label className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-300">
            <input
              type="checkbox"
              required
              checked={consentAccepted}
              onChange={(e) => setConsentAccepted(e.target.checked)}
              className="mt-0.5 h-4 w-4 rounded border-gray-300 text-brand-600 focus:ring-brand-500"
            />
            I have read and agree to the{" "}
            <Link to="/privacy" className="font-medium text-brand-600 hover:underline" target="_blank">
              privacy notice
            </Link>
            .
          </label>
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
