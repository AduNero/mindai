import { FormEvent, useEffect, useState } from "react";

import { reportsApi } from "@/api";
import { EmptyState } from "@/components/common/EmptyState";
import { FullPageSpinner } from "@/components/common/Spinner";
import { useToast } from "@/context/ToastContext";
import type { GeneratedReport, ReportFormat, ReportType } from "@/types";

function todayISO(offsetDays = 0) {
  const d = new Date();
  d.setDate(d.getDate() + offsetDays);
  return d.toISOString().slice(0, 10);
}

export default function AdminReportsPage() {
  const { showToast } = useToast();
  const [loading, setLoading] = useState(true);
  const [reports, setReports] = useState<GeneratedReport[]>([]);
  const [reportType, setReportType] = useState<ReportType>("monthly");
  const [format, setFormat] = useState<ReportFormat>("csv");
  const [periodStart, setPeriodStart] = useState(todayISO(-30));
  const [periodEnd, setPeriodEnd] = useState(todayISO());
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    reportsApi
      .list()
      .then(({ data }) => setReports(data.results))
      .finally(() => setLoading(false));
  }, []);

  const handleGenerate = async (e: FormEvent) => {
    e.preventDefault();
    setGenerating(true);
    try {
      const { data } = await reportsApi.generate({ report_type: reportType, format, period_start: periodStart, period_end: periodEnd });
      setReports((prev) => [data, ...prev]);
      showToast("Report generated.", "success");
    } catch {
      showToast("Couldn't generate the report.", "error");
    } finally {
      setGenerating(false);
    }
  };

  if (loading) return <FullPageSpinner />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Reports</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Generate oversight reports summarizing your own activity data (see docs for platform-wide analytics).
        </p>
      </div>

      <form onSubmit={handleGenerate} className="card grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div>
          <label className="label">Type</label>
          <select className="input" value={reportType} onChange={(e) => setReportType(e.target.value as ReportType)}>
            {["daily", "weekly", "monthly", "yearly", "mental_health"].map((t) => (
              <option key={t} value={t}>{t.replace("_", " ")}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="label">Format</label>
          <select className="input" value={format} onChange={(e) => setFormat(e.target.value as ReportFormat)}>
            <option value="pdf">PDF</option>
            <option value="csv">CSV</option>
          </select>
        </div>
        <div>
          <label className="label">From</label>
          <input type="date" className="input" value={periodStart} onChange={(e) => setPeriodStart(e.target.value)} />
        </div>
        <div>
          <label className="label">To</label>
          <input type="date" className="input" value={periodEnd} onChange={(e) => setPeriodEnd(e.target.value)} />
        </div>
        <div className="sm:col-span-2 lg:col-span-4">
          <button type="submit" disabled={generating} className="btn-primary">
            {generating ? "Generating..." : "Generate report"}
          </button>
        </div>
      </form>

      {reports.length === 0 ? (
        <EmptyState title="No reports yet" description="Generate one above." />
      ) : (
        <ul className="card divide-y divide-gray-100 dark:divide-gray-800">
          {reports.map((r) => (
            <li key={r.id} className="flex items-center justify-between py-3 text-sm">
              <div>
                <p className="font-medium text-gray-900 dark:text-gray-100">{r.report_type.replace("_", " ")} · {r.format.toUpperCase()}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">{r.period_start} to {r.period_end} · {r.status}</p>
              </div>
              {r.status === "completed" && r.file && (
                <a href={r.file} target="_blank" rel="noreferrer" className="btn-outline text-xs">Download</a>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
