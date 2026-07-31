import { FormEvent, useEffect, useState } from "react";

import { authApi, notificationsApi } from "@/api";
import { useAuth } from "@/context/AuthContext";
import { useTheme } from "@/context/ThemeContext";
import { useToast } from "@/context/ToastContext";
import type { NotificationPreference, UserSession } from "@/types";
import { extractErrorMessage } from "@/utils/errors";

const REMINDER_TOGGLES: { key: keyof NotificationPreference; label: string }[] = [
  { key: "daily_reminder", label: "Daily check-in reminder" },
  { key: "mood_reminder", label: "Mood logging reminder" },
  { key: "journal_reminder", label: "Journal reminder" },
  { key: "meditation_reminder", label: "Meditation reminder" },
  { key: "assessment_reminder", label: "Assessment reminder" },
  { key: "appointment_reminder", label: "Appointment reminder" },
];

export default function SettingsPage() {
  const { logout } = useAuth();
  const { theme, setTheme } = useTheme();
  const { showToast } = useToast();

  const [prefs, setPrefs] = useState<NotificationPreference | null>(null);
  const [sessions, setSessions] = useState<UserSession[]>([]);
  const [loading, setLoading] = useState(true);

  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newPasswordConfirm, setNewPasswordConfirm] = useState("");
  const [changingPassword, setChangingPassword] = useState(false);

  useEffect(() => {
    Promise.all([notificationsApi.getPreferences(), authApi.listSessions()])
      .then(([prefsRes, sessionsRes]) => {
        setPrefs(prefsRes.data);
        setSessions(sessionsRes.data);
      })
      .finally(() => setLoading(false));
  }, []);

  const togglePref = async (key: keyof NotificationPreference) => {
    if (!prefs) return;
    const updated = { ...prefs, [key]: !prefs[key] };
    setPrefs(updated);
    await notificationsApi.updatePreferences({ [key]: updated[key] });
  };

  const handleChangePassword = async (e: FormEvent) => {
    e.preventDefault();
    if (newPassword !== newPasswordConfirm) {
      showToast("New passwords do not match.", "error");
      return;
    }
    setChangingPassword(true);
    try {
      await authApi.changePassword(oldPassword, newPassword, newPasswordConfirm);
      showToast("Password changed successfully.", "success");
      setOldPassword("");
      setNewPassword("");
      setNewPasswordConfirm("");
    } catch (err) {
      showToast(extractErrorMessage(err, "Couldn't change your password."), "error");
    } finally {
      setChangingPassword(false);
    }
  };

  const handleRevokeSession = async (id: string) => {
    await authApi.revokeSession(id);
    setSessions((prev) => prev.filter((s) => s.id !== id));
  };

  const handleLogoutAll = async () => {
    await authApi.logoutAll();
    await logout();
  };

  if (loading) return null;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Settings</h1>
      </div>

      <section className="card">
        <h2 className="font-semibold text-gray-900 dark:text-gray-100">Appearance</h2>
        <div className="mt-3 flex gap-2">
          {(["light", "dark", "system"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTheme(t)}
              className={`rounded-xl px-4 py-2 text-sm font-medium capitalize ${
                theme === t ? "bg-brand-600 text-white" : "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300"
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </section>

      <section className="card">
        <h2 className="font-semibold text-gray-900 dark:text-gray-100">Notification preferences</h2>
        {prefs && (
          <div className="mt-3 space-y-3">
            {REMINDER_TOGGLES.map(({ key, label }) => (
              <label key={key} className="flex items-center justify-between text-sm">
                {label}
                <input
                  type="checkbox"
                  checked={Boolean(prefs[key])}
                  onChange={() => togglePref(key)}
                  className="h-4 w-4 rounded border-gray-300 text-brand-600 focus:ring-brand-500"
                />
              </label>
            ))}
            <div className="flex items-center justify-between border-t border-gray-100 pt-3 text-sm dark:border-gray-800">
              Email notifications
              <input
                type="checkbox"
                checked={prefs.email_enabled}
                onChange={() => togglePref("email_enabled")}
                className="h-4 w-4 rounded border-gray-300 text-brand-600 focus:ring-brand-500"
              />
            </div>
          </div>
        )}
      </section>

      <section className="card">
        <h2 className="font-semibold text-gray-900 dark:text-gray-100">Change password</h2>
        <form onSubmit={handleChangePassword} className="mt-3 space-y-3">
          <input
            type="password"
            required
            placeholder="Current password"
            className="input"
            value={oldPassword}
            onChange={(e) => setOldPassword(e.target.value)}
          />
          <input
            type="password"
            required
            minLength={10}
            placeholder="New password"
            className="input"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
          />
          <input
            type="password"
            required
            placeholder="Confirm new password"
            className="input"
            value={newPasswordConfirm}
            onChange={(e) => setNewPasswordConfirm(e.target.value)}
          />
          <button type="submit" disabled={changingPassword} className="btn-primary">
            {changingPassword ? "Updating..." : "Update password"}
          </button>
        </form>
      </section>

      <section className="card">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold text-gray-900 dark:text-gray-100">Active sessions</h2>
          <button onClick={handleLogoutAll} className="text-xs font-medium text-red-500 hover:underline">
            Log out everywhere
          </button>
        </div>
        <ul className="mt-3 divide-y divide-gray-100 dark:divide-gray-800">
          {sessions.map((s) => (
            <li key={s.id} className="flex items-center justify-between py-2.5 text-sm">
              <div>
                <p className="text-gray-700 dark:text-gray-200">{s.device_label || "Unknown device"}</p>
                <p className="text-xs text-gray-400">{s.ip_address} · {new Date(s.created_at).toLocaleString()}</p>
              </div>
              {s.is_active && (
                <button onClick={() => handleRevokeSession(s.id)} className="text-xs text-red-500 hover:underline">
                  Revoke
                </button>
              )}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
