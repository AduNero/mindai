import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { assessmentsApi } from "@/api";
import { FullPageSpinner } from "@/components/common/Spinner";
import { useToast } from "@/context/ToastContext";
import type { AssessmentCode, AssessmentSubmitResponse, AssessmentType } from "@/types";

export default function AssessmentTakePage() {
  const { code } = useParams<{ code: string }>();
  const navigate = useNavigate();
  const { showToast } = useToast();

  const [loading, setLoading] = useState(true);
  const [assessment, setAssessment] = useState<AssessmentType | null>(null);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<AssessmentSubmitResponse | null>(null);

  useEffect(() => {
    if (!code) return;
    assessmentsApi
      .getType(code as AssessmentCode)
      .then(({ data }) => setAssessment(data))
      .finally(() => setLoading(false));
  }, [code]);

  const allAnswered = assessment ? assessment.questions.every((q) => answers[q.id] !== undefined) : false;

  const handleSubmit = async () => {
    if (!assessment || !allAnswered) return;
    setSubmitting(true);
    try {
      const { data } = await assessmentsApi.submit({
        assessment_type: assessment.code,
        answers: Object.entries(answers).map(([question_id, selected_value]) => ({ question_id, selected_value })),
      });
      setResult(data);
    } catch {
      showToast("Couldn't submit your assessment — please try again.", "error");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <FullPageSpinner />;
  if (!assessment) return <p className="text-center text-gray-500">Assessment not found.</p>;

  if (result) {
    return (
      <div className="mx-auto max-w-xl space-y-4">
        <div className="card text-center">
          <p className="text-sm font-medium text-brand-600">{assessment.name}</p>
          <p className="mt-2 text-4xl font-bold text-gray-900 dark:text-white">
            {result.total_score} / {assessment.max_score}
          </p>
          <p className="mt-1 text-sm font-medium capitalize text-gray-600 dark:text-gray-300">
            {result.severity.replace("_", " ")}
          </p>
          <p className="mt-4 text-sm text-gray-600 dark:text-gray-300">{result.interpretation}</p>
        </div>

        {result.risk_flag && result.crisis_resources && (
          <div className="rounded-2xl border border-red-300 bg-red-50 p-5 dark:border-red-800 dark:bg-red-950/40">
            <h3 className="font-semibold text-red-800 dark:text-red-200">You're not alone</h3>
            <p className="mt-1 text-sm text-red-700 dark:text-red-300">
              Some of your responses suggest you may be going through a difficult time. MindCare AI
              isn't equipped to provide emergency support — please reach out to one of these
              resources or a trusted person.
            </p>
            <ul className="mt-3 space-y-2">
              {result.crisis_resources.map((r) => (
                <li key={r.name} className="text-sm text-red-800 dark:text-red-200">
                  <strong>{r.name}</strong> — {r.phone_number} {r.is_24_7 && "(24/7)"}
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="flex gap-3">
          <Link to="/assessments" className="btn-outline flex-1">
            Back to assessments
          </Link>
          <Link to="/appointments" className="btn-primary flex-1">
            Book a counselor
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <button onClick={() => navigate(-1)} className="text-sm text-gray-500 hover:underline">
          ← Back
        </button>
        <h1 className="mt-2 text-2xl font-bold text-gray-900 dark:text-white">{assessment.name}</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{assessment.instructions}</p>
      </div>

      <div className="space-y-5">
        {assessment.questions.map((q, index) => (
          <div key={q.id} className="card">
            <p className="font-medium text-gray-900 dark:text-gray-100">
              {index + 1}. {q.text}
            </p>
            <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2">
              {q.options.map((opt) => (
                <label
                  key={opt.value}
                  className={`flex cursor-pointer items-center gap-2 rounded-xl border px-3 py-2 text-sm ${
                    answers[q.id] === opt.value
                      ? "border-brand-500 bg-brand-50 dark:bg-brand-950/50"
                      : "border-gray-200 dark:border-gray-700"
                  }`}
                >
                  <input
                    type="radio"
                    name={q.id}
                    checked={answers[q.id] === opt.value}
                    onChange={() => setAnswers((prev) => ({ ...prev, [q.id]: opt.value }))}
                    className="text-brand-600"
                  />
                  {opt.label}
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>

      <button onClick={handleSubmit} disabled={!allAnswered || submitting} className="btn-primary w-full">
        {submitting ? "Submitting..." : "Submit assessment"}
      </button>
    </div>
  );
}
