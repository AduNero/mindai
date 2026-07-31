import { useEffect, useState } from "react";

import { adminPanelApi } from "@/api";
import { EmptyState } from "@/components/common/EmptyState";
import { FullPageSpinner } from "@/components/common/Spinner";
import { useToast } from "@/context/ToastContext";
import type { JournalReport } from "@/types";

export default function AdminJournalReportsPage() {
  const { showToast } = useToast();
  const [loading, setLoading] = useState(true);
  const [reports, setReports] = useState<JournalReport[]>([]);
  const [statusFilter, setStatusFilter] = useState("pending");

  const load = async (status: string) => {
    const { data } = await adminPanelApi.journalReports(status ? { status } : undefined);
    setReports(data.results);
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

  const handleResolve = async (id: string, status: "reviewed" | "actioned" | "dismissed", removeEntry: boolean) => {
    const notes = prompt("Review notes (optional):") ?? "";
    await adminPanelApi.resolveJournalReport(id, { status, review_notes: notes, remove_entry: removeEntry });
    setReports((prev) => prev.filter((r) => r.id !== id));
    showToast("Report resolved.", "success");
  };

  if (loading) return <FullPageSpinner />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Journal Moderation</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">Review reports filed against public journal entries.</p>
      </div>

      <div className="flex gap-2">
        {["pending", "reviewed", "actioned", "dismissed", ""].map((s) => (
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

      {reports.length === 0 ? (
        <EmptyState title="No reports here" description="Nothing to moderate in this filter right now." />
      ) : (
        <div className="space-y-3">
          {reports.map((r) => (
            <div key={r.id} className="card">
              <div className="flex items-center justify-between">
                <p className="font-medium text-gray-900 dark:text-gray-100">{r.journal_title}</p>
                <span className="badge bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300">{r.reason}</span>
              </div>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{r.details || "No additional details."}</p>
              <p className="mt-1 text-xs text-gray-400">
                Reported by {r.reported_by_email || "system (AI-flagged)"} · {new Date(r.created_at).toLocaleString()}
              </p>
              {r.status === "pending" && (
                <div className="mt-3 flex flex-wrap gap-2">
                  <button onClick={() => handleResolve(r.id, "actioned", true)} className="btn-danger text-xs">
                    Take down entry
                  </button>
                  <button onClick={() => handleResolve(r.id, "reviewed", false)} className="btn-outline text-xs">
                    Mark reviewed
                  </button>
                  <button onClick={() => handleResolve(r.id, "dismissed", false)} className="btn-outline text-xs">
                    Dismiss
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
