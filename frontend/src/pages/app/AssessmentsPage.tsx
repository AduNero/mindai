import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { assessmentsApi } from "@/api";
import { EmptyState } from "@/components/common/EmptyState";
import { FullPageSpinner } from "@/components/common/Spinner";
import type { AssessmentResult, AssessmentTypeSummary, Severity } from "@/types";

const SEVERITY_COLORS: Record<Severity, string> = {
  minimal: "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300",
  mild: "bg-sky-100 text-sky-700 dark:bg-sky-950 dark:text-sky-300",
  moderate: "bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300",
  moderately_severe: "bg-orange-100 text-orange-700 dark:bg-orange-950 dark:text-orange-300",
  severe: "bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300",
};

export default function AssessmentsPage() {
  const [loading, setLoading] = useState(true);
  const [types, setTypes] = useState<AssessmentTypeSummary[]>([]);
  const [results, setResults] = useState<AssessmentResult[]>([]);

  useEffect(() => {
    Promise.all([assessmentsApi.listTypes(), assessmentsApi.listResults({ page_size: 10 })])
      .then(([typesRes, resultsRes]) => {
        setTypes(typesRes.data.results);
        setResults(resultsRes.data.results);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <FullPageSpinner />;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Mental Health Assessments</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Validated screening tools — not a diagnosis, but a useful check-in.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {types.map((type) => (
          <div key={type.id} className="card flex flex-col">
            <h3 className="font-semibold text-gray-900 dark:text-gray-100">{type.name}</h3>
            <p className="mt-1.5 flex-1 text-sm text-gray-500 dark:text-gray-400">{type.description}</p>
            <Link to={`/assessments/${type.code}`} className="btn-primary mt-4">
              Take assessment
            </Link>
          </div>
        ))}
      </div>

      <div>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">History</h2>
        {results.length === 0 ? (
          <div className="mt-3">
            <EmptyState title="No assessments taken yet" description="Take your first assessment above to start tracking trends." />
          </div>
        ) : (
          <div className="mt-3 overflow-x-auto rounded-2xl border border-gray-200 dark:border-gray-800">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-50 text-xs uppercase text-gray-400 dark:bg-gray-900">
                <tr>
                  <th className="px-4 py-3">Assessment</th>
                  <th className="px-4 py-3">Score</th>
                  <th className="px-4 py-3">Severity</th>
                  <th className="px-4 py-3">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                {results.map((r) => (
                  <tr key={r.id}>
                    <td className="px-4 py-3">{r.assessment_type.name}</td>
                    <td className="px-4 py-3">
                      {r.total_score} / {r.assessment_type.max_score}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`badge ${SEVERITY_COLORS[r.severity]}`}>{r.severity.replace("_", " ")}</span>
                    </td>
                    <td className="px-4 py-3 text-gray-500 dark:text-gray-400">
                      {new Date(r.taken_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
