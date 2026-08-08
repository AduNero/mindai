import { useEffect, useState } from "react";

import { adminPanelApi } from "@/api";
import { EmptyState } from "@/components/common/EmptyState";
import { FullPageSpinner } from "@/components/common/Spinner";
import { useToast } from "@/context/ToastContext";
import type { RiskAssessment, RiskLevel } from "@/types";

const LEVEL_STYLES: Record<RiskLevel, string> = {
  none: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300",
  low: "bg-sky-100 text-sky-700 dark:bg-sky-950 dark:text-sky-300",
  moderate: "bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300",
  high: "bg-orange-100 text-orange-700 dark:bg-orange-950 dark:text-orange-300",
  critical: "bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300",
};

export default function AdminRiskAlertsPage() {
  const { showToast } = useToast();
  const [loading, setLoading] = useState(true);
  const [alerts, setAlerts] = useState<RiskAssessment[]>([]);

  useEffect(() => {
    adminPanelApi
      .riskAlerts()
      .then(({ data }) => setAlerts(data.results))
      .finally(() => setLoading(false));
  }, []);

  const handleReview = async (id: string) => {
    const notes = prompt("Review notes:") ?? "";
    const { data } = await adminPanelApi.reviewRiskAlert(id, notes);
    setAlerts((prev) => prev.map((a) => (a.id === id ? data : a)));
    showToast("Risk alert reviewed.", "success");
  };

  if (loading) return <FullPageSpinner />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Risk Alerts</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Deterministic crisis-phrase detections from journal entries. Review promptly. Only the
          risk tier is stored — the triggering text itself is never logged.
        </p>
      </div>

      {alerts.length === 0 ? (
        <EmptyState title="No risk alerts" description="Nothing has been flagged recently." />
      ) : (
        <div className="space-y-3">
          {alerts.map((a) => (
            <div key={a.id} className="card">
              <div className="flex items-center justify-between">
                <span className={`badge ${LEVEL_STYLES[a.risk_level]}`}>{a.risk_level}</span>
                <p className="text-xs text-gray-400">{new Date(a.created_at).toLocaleString()}</p>
              </div>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">
                Source: <span className="capitalize">{a.detection_source}</span>
              </p>
              <div className="mt-3 flex items-center gap-3">
                <span className="text-xs text-gray-400">
                  {a.acknowledged_at ? "User acknowledged resources" : "Not yet acknowledged by user"}
                </span>
                <button onClick={() => handleReview(a.id)} className="text-xs font-medium text-brand-600 hover:underline">
                  Mark reviewed
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
