import { FormEvent, useEffect, useState } from "react";

import { appointmentsApi, usersApi } from "@/api";
import { EmptyState } from "@/components/common/EmptyState";
import { FullPageSpinner } from "@/components/common/Spinner";
import { useToast } from "@/context/ToastContext";
import type { Appointment, AppointmentStatus, CounselorProfile } from "@/types";
import { extractErrorMessage } from "@/utils/errors";

const STATUS_STYLES: Record<AppointmentStatus, string> = {
  pending: "bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300",
  approved: "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300",
  rejected: "bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300",
  cancelled: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300",
  rescheduled: "bg-sky-100 text-sky-700 dark:bg-sky-950 dark:text-sky-300",
  completed: "bg-brand-100 text-brand-700 dark:bg-brand-950 dark:text-brand-300",
};

export default function AppointmentsPage() {
  const { showToast } = useToast();
  const [loading, setLoading] = useState(true);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [counselors, setCounselors] = useState<CounselorProfile[]>([]);

  const [counselorId, setCounselorId] = useState("");
  const [scheduledAt, setScheduledAt] = useState("");
  const [reason, setReason] = useState("");
  const [booking, setBooking] = useState(false);

  useEffect(() => {
    Promise.all([appointmentsApi.list(), usersApi.listCounselors()])
      .then(([apptRes, counselorRes]) => {
        setAppointments(apptRes.data.results);
        setCounselors(counselorRes.data.results);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleBook = async (e: FormEvent) => {
    e.preventDefault();
    if (!counselorId || !scheduledAt) return;
    setBooking(true);
    try {
      const { data } = await appointmentsApi.create({
        counselor_id: counselorId,
        scheduled_at: new Date(scheduledAt).toISOString(),
        reason_for_visit: reason,
      });
      setAppointments((prev) => [data, ...prev]);
      showToast("Appointment requested — awaiting approval.", "success");
      setCounselorId("");
      setScheduledAt("");
      setReason("");
    } catch (err) {
      showToast(extractErrorMessage(err, "Couldn't book this appointment."), "error");
    } finally {
      setBooking(false);
    }
  };

  const handleCancel = async (id: string) => {
    const reasonInput = prompt("Reason for cancelling (optional):") ?? "";
    const { data } = await appointmentsApi.cancel(id, reasonInput);
    setAppointments((prev) => prev.map((a) => (a.id === id ? data : a)));
    showToast("Appointment cancelled.", "success");
  };

  if (loading) return <FullPageSpinner />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Appointments</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">Book time with a counselor, or manage upcoming sessions.</p>
      </div>

      <div className="card">
        <h3 className="font-semibold text-gray-900 dark:text-gray-100">Book a session</h3>
        {counselors.length === 0 ? (
          <p className="mt-3 text-sm text-gray-500 dark:text-gray-400">No counselors are currently accepting appointments.</p>
        ) : (
          <form onSubmit={handleBook} className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="label">Counselor</label>
              <select className="input" required value={counselorId} onChange={(e) => setCounselorId(e.target.value)}>
                <option value="">Select a counselor</option>
                {counselors.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.user.full_name} {c.specialization && `— ${c.specialization}`}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="label">Date & time</label>
              <input
                type="datetime-local"
                required
                className="input"
                value={scheduledAt}
                onChange={(e) => setScheduledAt(e.target.value)}
              />
            </div>
            <div className="sm:col-span-2">
              <label className="label">Reason for visit (optional)</label>
              <textarea className="input" rows={3} value={reason} onChange={(e) => setReason(e.target.value)} />
            </div>
            <div className="sm:col-span-2">
              <button type="submit" disabled={booking} className="btn-primary">
                {booking ? "Booking..." : "Request appointment"}
              </button>
            </div>
          </form>
        )}
      </div>

      <div className="card">
        <h3 className="font-semibold text-gray-900 dark:text-gray-100">Your appointments</h3>
        {appointments.length === 0 ? (
          <div className="mt-3">
            <EmptyState title="No appointments yet" description="Book a session with a counselor above." />
          </div>
        ) : (
          <ul className="mt-3 divide-y divide-gray-100 dark:divide-gray-800">
            {appointments.map((a) => (
              <li key={a.id} className="flex flex-wrap items-center justify-between gap-2 py-3 text-sm">
                <div>
                  <p className="font-medium text-gray-900 dark:text-gray-100">{a.counselor.user.full_name}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {new Date(a.scheduled_at).toLocaleString()} · {a.duration_minutes} min
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`badge ${STATUS_STYLES[a.status]}`}>{a.status}</span>
                  {(a.status === "pending" || a.status === "approved") && (
                    <button onClick={() => handleCancel(a.id)} className="text-xs font-medium text-red-500 hover:underline">
                      Cancel
                    </button>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
