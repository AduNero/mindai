import { Line } from "react-chartjs-2";

import type { DailyMoodStat } from "@/types";

const MOOD_TO_SCORE: Record<string, number> = {
  depressed: 1,
  sad: 2,
  angry: 2,
  anxious: 3,
  tired: 3,
  neutral: 4,
  happy: 5,
  excited: 5,
};

interface MoodTrendChartProps {
  data: DailyMoodStat[];
}

export function MoodTrendChart({ data }: MoodTrendChartProps) {
  const labels = data.map((d) => new Date(d.date).toLocaleDateString(undefined, { month: "short", day: "numeric" }));
  const intensityValues = data.map((d) => d.average_intensity);
  const moodScores = data.map((d) => (d.dominant_mood ? MOOD_TO_SCORE[d.dominant_mood] : null));

  return (
    <Line
      data={{
        labels,
        datasets: [
          {
            label: "Mood intensity",
            data: intensityValues,
            borderColor: "#4f5fee",
            backgroundColor: "rgba(79, 95, 238, 0.12)",
            fill: true,
            tension: 0.35,
            spanGaps: true,
            yAxisID: "y",
          },
          {
            label: "Overall mood (1=low, 5=high)",
            data: moodScores,
            borderColor: "#10b981",
            backgroundColor: "rgba(16, 185, 129, 0.12)",
            tension: 0.35,
            spanGaps: true,
            yAxisID: "y1",
            borderDash: [4, 4],
          },
        ],
      }}
      options={{
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        scales: {
          y: { min: 0, max: 10, title: { display: true, text: "Intensity" } },
          y1: { min: 0, max: 5, position: "right", grid: { drawOnChartArea: false }, title: { display: true, text: "Mood" } },
        },
        plugins: { legend: { position: "bottom" } },
      }}
    />
  );
}
