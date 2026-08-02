import { Doughnut } from "react-chartjs-2";

function colorFor(score: number) {
  if (score >= 75) return "#0ea5e9";
  if (score >= 50) return "#10b981";
  if (score >= 25) return "#f59e0b";
  return "#ef4444";
}

function labelFor(score: number) {
  if (score >= 75) return "Excellent";
  if (score >= 50) return "Good";
  if (score >= 25) return "Moderate";
  return "Needs attention";
}

export function WellnessScoreGauge({ score }: { score: number | null }) {
  const value = score ?? 0;
  const color = colorFor(value);

  return (
    <div className="relative mx-auto flex h-40 w-40 items-center justify-center">
      <Doughnut
        data={{
          datasets: [
            {
              data: [value, 100 - value],
              backgroundColor: [color, "#e5e7eb"],
              borderWidth: 0,
            },
          ],
        }}
        options={{
          cutout: "75%",
          plugins: { legend: { display: false }, tooltip: { enabled: false } },
        }}
      />
      <div className="absolute flex flex-col items-center">
        <span className="text-3xl font-bold text-gray-900 dark:text-white">{score ?? "—"}</span>
        <span className="text-xs font-medium" style={{ color }}>
          {score !== null ? labelFor(score) : "No data yet"}
        </span>
      </div>
    </div>
  );
}
