import { useEffect, useState } from "react";

import { appointmentsApi } from "@/api";
import { EmptyState } from "@/components/common/EmptyState";
import { FullPageSpinner } from "@/components/common/Spinner";
import { useToast } from "@/context/ToastContext";
import type { AdminAppointment, AppointmentStatus } from "@/types";

const STATUS_STYLES: Record<AppointmentStatus, string> = {
  pending: "bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300",
  approved: "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300",
  rejected: "bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300",
  cancelled: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300",
  rescheduled: "bg-sky-100 text-sky-700 dark:bg-sky-950 dark:text-sky-300",
  completed: "bg-brand-100 text-brand-700 dark:bg-brand-950 dark:text-brand-300",
};

export default function AdminAppointmentsPage() {
  const { showToast } = useToast();
  const [loading, setLoading] = useState(true);
  const [appointments, setAppointments] = useState<AdminAppointment[]>([]);
  const [statusFilter, setStatusFilter] = useState("pending");

  const load = async (status: string) => {
    const { data } = await appointmentsApi.admin.list(status ? { status } : undefined);
    setAppointments(data.results);
  };

  useEffect(() => {
    load(statusFilter).finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleFilter = async (status: string) => {
    setStatusFilter(status);
    setLoading(true);
    await load(status);
    setLoading(false);
  };

  const handleApprove = async (id: string) => {
    const { data } = await appointmentsApi.admin.approve(id);
    setAppointments((prev) => prev.map((a) => (a.id === id ? data : a)));
    showToast("Appointment approved.", "success");
  };

  const handleReject = async (id: string) => {
    const notes = prompt("Reason for rejecting (optional):") ?? "";
    const { data } = await appointmentsApi.admin.reject(id, notes);
    setAppointments((prev) => prev.map((a) => (a.id === id ? data : a)));
    showToast("Appointment rejected.", "success");
  };

  if (loading) return <FullPageSpinner />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Appointments</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">Approve or reject counseling session requests.</p>
      </div>

      <div className="flex gap-2">
        {["pending", "approved", "rejected", "cancelled", ""].map((s) => (
          <button
            key={s || "all"}
            onClick={() => handleFilter(s)}
            className={`rounded-full px-3 py-1.5 text-xs font-medium capitalize ${
              statusFilter === s ? "bg-brand-600 text-white" : "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300"
            }`}
          >
            {s || "All"}
          </button>
        ))}
      </div>

      {appointments.length === 0 ? (
        <EmptyState title="Nothing here" description="No appointments match this filter." />
      ) : (
        <div className="space-y-3">
          {appointments.map((a) => (
            <div key={a.id} className="card flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="font-medium text-gray-900 dark:text-gray-100">{a.counselor.user.full_name}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {new Date(a.scheduled_at).toLocaleString()} · {a.duration_minutes} min
                </p>
                {a.reason_for_visit && <p className="mt-1 text-xs text-gray-400">{a.reason_for_visit}</p>}
              </div>
              <div className="flex items-center gap-2">
                <span className={`badge ${STATUS_STYLES[a.status]}`}>{a.status}</span>
                {a.status === "pending" && (
                  <>
                    <button onClick={() => handleApprove(a.id)} className="text-xs font-medium text-emerald-600 hover:underline">
                      Approve
                    </button>
                    <button onClick={() => handleReject(a.id)} className="text-xs font-medium text-red-500 hover:underline">
                      Reject
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
