import { useEffect, useState } from "react";

import { moodsApi } from "@/api";
import { MoodQuickLog } from "@/components/dashboard/MoodQuickLog";
import { MoodTrendChart } from "@/components/dashboard/MoodTrendChart";
import { EmptyState } from "@/components/common/EmptyState";
import { FullPageSpinner } from "@/components/common/Spinner";
import { useToast } from "@/context/ToastContext";
import type { DailyMoodStat, MoodEntry } from "@/types";
import { MOOD_EMOJI, MOOD_LABEL, MOOD_OPTIONS } from "@/types";

type MoodRange = "weekly" | "monthly";

export default function MoodTrackerPage() {
  const { showToast } = useToast();
  const [loading, setLoading] = useState(true);
  const [entries, setEntries] = useState<MoodEntry[]>([]);
  const [series, setSeries] = useState<DailyMoodStat[]>([]);
  const [range, setRange] = useState<MoodRange>("weekly");
  const [moodFilter, setMoodFilter] = useState("");

  const loadEntries = async (mood?: string) => {
    const { data } = await moodsApi.list(mood ? { mood } : undefined);
    setEntries(data.results);
  };

  const loadSeries = async (r: MoodRange) => {
    const { data } = r === "weekly" ? await moodsApi.weekly() : await moodsApi.monthly();
    setSeries(data);
  };

  useEffect(() => {
    Promise.all([loadEntries(), loadSeries(range)]).finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleRangeChange = async (r: MoodRange) => {
    setRange(r);
    await loadSeries(r);
  };

  const handleFilterChange = async (mood: string) => {
    setMoodFilter(mood);
    await loadEntries(mood || undefined);
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this mood entry?")) return;
    await moodsApi.remove(id);
    setEntries((prev) => prev.filter((e) => e.id !== id));
    showToast("Mood entry deleted.", "success");
  };

  if (loading) return <FullPageSpinner />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Mood Tracker</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">Log how you feel and watch the trend over time.</p>
      </div>

      <MoodQuickLog onLogged={(entry) => setEntries((prev) => [entry, ...prev])} />

      <div className="card">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-gray-900 dark:text-gray-100">Trend</h3>
          <div className="flex gap-1 rounded-lg bg-gray-100 p-1 text-xs dark:bg-gray-800">
            {(["weekly", "monthly"] as MoodRange[]).map((r) => (
              <button
                key={r}
                onClick={() => handleRangeChange(r)}
                className={`rounded-md px-2.5 py-1 font-medium capitalize transition-colors ${
                  range === r ? "bg-white text-gray-900 shadow-sm dark:bg-gray-700 dark:text-white" : "text-gray-500"
                }`}
              >
                {r}
              </button>
            ))}
          </div>
        </div>
        <div className="mt-4 h-64">
          <MoodTrendChart data={series} />
        </div>
      </div>

      <div className="card">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h3 className="font-semibold text-gray-900 dark:text-gray-100">History</h3>
          <select
            value={moodFilter}
            onChange={(e) => handleFilterChange(e.target.value)}
            className="input w-auto"
          >
            <option value="">All moods</option>
            {MOOD_OPTIONS.map((m) => (
              <option key={m.value} value={m.value}>
                {m.emoji} {m.label}
              </option>
            ))}
          </select>
        </div>

        {entries.length === 0 ? (
          <div className="mt-4">
            <EmptyState title="No mood entries yet" description="Log your first mood check-in above." />
          </div>
        ) : (
          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-xs uppercase text-gray-400">
                <tr>
                  <th className="py-2">Mood</th>
                  <th className="py-2">Intensity</th>
                  <th className="py-2">Date</th>
                  <th className="py-2">Notes</th>
                  <th className="py-2" />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                {entries.map((entry) => (
                  <tr key={entry.id}>
                    <td className="py-3">
                      <span className="mr-1">{MOOD_EMOJI[entry.mood]}</span>
                      {MOOD_LABEL[entry.mood]}
                    </td>
                    <td className="py-3">{entry.intensity}/10</td>
                    <td className="py-3 text-gray-500 dark:text-gray-400">
                      {entry.entry_date} {entry.entry_time.slice(0, 5)}
                    </td>
                    <td className="max-w-xs truncate py-3 text-gray-500 dark:text-gray-400">{entry.notes}</td>
                    <td className="py-3 text-right">
                      <button
                        onClick={() => handleDelete(entry.id)}
                        className="text-xs font-medium text-red-500 hover:underline"
                      >
                        Delete
                      </button>
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
