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
    <div className="flex flex-col items-center">
      <div className="relative mx-auto flex h-40 w-40 items-center justify-center">
        <Doughnut
          data={{
            datasets: [
              {
                data: [value, 100 - value],
                backgroundColor: [color, "#e7e2d8"],
                borderWidth: 0,
              },
            ],
          }}
          options={{
            cutout: "80%",
            plugins: { legend: { display: false }, tooltip: { enabled: false } },
          }}
        />
        <div className="absolute flex flex-col items-center">
          <span className="stat-figure text-4xl font-semibold text-gray-900 dark:text-white">
            {score ?? "—"}
          </span>
          <span className="text-xs font-medium uppercase tracking-wide" style={{ color }}>
            {score !== null ? labelFor(score) : "No data yet"}
          </span>
        </div>
      </div>
      {/* Reading scale — the instrument-panel motif: this is a measurement, not a decoration. */}
      <div className="stat-figure mt-2 flex w-32 justify-between text-[10px] text-gray-400">
        <span>0</span>
        <span>50</span>
        <span>100</span>
      </div>
    </div>
  );
}
