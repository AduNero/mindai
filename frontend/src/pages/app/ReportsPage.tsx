import { FormEvent, useEffect, useState } from "react";
import { Line } from "react-chartjs-2";

import { aiApi, reportsApi } from "@/api";
import { EmptyState } from "@/components/common/EmptyState";
import { FullPageSpinner } from "@/components/common/Spinner";
import { useToast } from "@/context/ToastContext";
import type { GeneratedReport, ReportFormat, ReportType, WellnessScoreSnapshot } from "@/types";

const REPORT_TYPES: { value: ReportType; label: string }[] = [
  { value: "daily", label: "Daily" },
  { value: "weekly", label: "Weekly" },
  { value: "monthly", label: "Monthly" },
  { value: "yearly", label: "Yearly" },
  { value: "mental_health", label: "Mental Health Summary" },
];

function todayISO(offsetDays = 0) {
  const d = new Date();
  d.setDate(d.getDate() + offsetDays);
  return d.toISOString().slice(0, 10);
}

export default function ReportsPage() {
  const { showToast } = useToast();
  const [loading, setLoading] = useState(true);
  const [history, setHistory] = useState<WellnessScoreSnapshot[]>([]);
  const [reports, setReports] = useState<GeneratedReport[]>([]);

  const [reportType, setReportType] = useState<ReportType>("monthly");
  const [format, setFormat] = useState<ReportFormat>("pdf");
  const [periodStart, setPeriodStart] = useState(todayISO(-30));
  const [periodEnd, setPeriodEnd] = useState(todayISO());
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    Promise.all([aiApi.wellnessScoreHistory(90), reportsApi.list()])
      .then(([historyRes, reportsRes]) => {
        setHistory(historyRes.data);
        setReports(reportsRes.data.results);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleGenerate = async (e: FormEvent) => {
    e.preventDefault();
    setGenerating(true);
    try {
      const { data } = await reportsApi.generate({
        report_type: reportType,
        format,
        period_start: periodStart,
        period_end: periodEnd,
      });
      setReports((prev) => [data, ...prev]);
      showToast(
        data.status === "completed" ? "Report generated." : "Report generation failed.",
        data.status === "completed" ? "success" : "error",
      );
    } catch {
      showToast("Couldn't generate the report — please try again.", "error");
    } finally {
      setGenerating(false);
    }
  };

  if (loading) return <FullPageSpinner />;

  const sorted = [...history].sort((a, b) => a.score_date.localeCompare(b.score_date));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Reports</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">Wellness trends and downloadable summaries.</p>
      </div>

      <div className="card">
        <h3 className="font-semibold text-gray-900 dark:text-gray-100">Wellness score — last 90 days</h3>
        <div className="mt-4 h-64">
          {sorted.length === 0 ? (
            <EmptyState title="Not enough data yet" description="Your wellness score builds up as you track mood, journal, and more." />
          ) : (
            <Line
              data={{
                labels: sorted.map((s) => new Date(s.score_date).toLocaleDateString(undefined, { month: "short", day: "numeric" })),
                datasets: [
                  {
                    label: "Wellness score",
                    data: sorted.map((s) => s.overall_score),
                    borderColor: "#2f6456",
                    backgroundColor: "rgba(47,100,86,0.12)",
                    fill: true,
                    tension: 0.35,
                  },
                ],
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                scales: { y: { min: 0, max: 100 } },
                plugins: { legend: { display: false } },
              }}
            />
          )}
        </div>
      </div>

      <div className="card">
        <h3 className="font-semibold text-gray-900 dark:text-gray-100">Generate a report</h3>
        <form onSubmit={handleGenerate} className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <label className="label">Type</label>
            <select className="input" value={reportType} onChange={(e) => setReportType(e.target.value as ReportType)}>
              {REPORT_TYPES.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
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
      </div>

      <div className="card">
        <h3 className="font-semibold text-gray-900 dark:text-gray-100">Your reports</h3>
        {reports.length === 0 ? (
          <div className="mt-3">
            <EmptyState title="No reports yet" description="Generate your first report above." />
          </div>
        ) : (
          <ul className="mt-3 divide-y divide-gray-100 dark:divide-gray-800">
            {reports.map((r) => (
              <li key={r.id} className="flex items-center justify-between py-3 text-sm">
                <div>
                  <p className="font-medium text-gray-900 dark:text-gray-100">
                    {r.report_type.replace("_", " ")} · {r.format.toUpperCase()}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {r.period_start} to {r.period_end} · {r.status}
                  </p>
                </div>
                {r.status === "completed" && r.file ? (
                  <a href={r.file} target="_blank" rel="noreferrer" className="btn-outline text-xs">
                    Download
                  </a>
                ) : (
                  <span className="text-xs text-gray-400 capitalize">{r.status}</span>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
