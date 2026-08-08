import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { journalsApi, moodsApi } from "@/api";
import { MoodQuickLog } from "@/components/dashboard/MoodQuickLog";
import { MoodTrendChart } from "@/components/dashboard/MoodTrendChart";
import { StatCard } from "@/components/dashboard/StatCard";
import { FullPageSpinner } from "@/components/common/Spinner";
import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/context/ToastContext";
import type { DailyMoodStat, JournalStats, MoodEntry } from "@/types";
import { MOOD_EMOJI, MOOD_LABEL } from "@/types";

type MoodRange = "weekly" | "monthly";

export default function DashboardPage() {
  const { user } = useAuth();
  const { showToast } = useToast();

  const [loading, setLoading] = useState(true);
  const [currentMood, setCurrentMood] = useState<MoodEntry | null>(null);
  const [moodSeries, setMoodSeries] = useState<DailyMoodStat[]>([]);
  const [moodRange, setMoodRange] = useState<MoodRange>("weekly");
  const [journalStats, setJournalStats] = useState<JournalStats | null>(null);

  const loadMoodSeries = async (range: MoodRange) => {
    const { data } = range === "weekly" ? await moodsApi.weekly() : await moodsApi.monthly();
    setMoodSeries(data);
  };

  useEffect(() => {
    let cancelled = false;

    async function load() {
      const results = await Promise.allSettled([moodsApi.current(), moodsApi.weekly(), journalsApi.stats()]);
      if (cancelled) return;

      if (results[0].status === "fulfilled") setCurrentMood(results[0].value.data);
      if (results[1].status === "fulfilled") setMoodSeries(results[1].value.data);
      if (results[2].status === "fulfilled") setJournalStats(results[2].value.data);

      setLoading(false);
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleRangeChange = async (range: MoodRange) => {
    setMoodRange(range);
    try {
      await loadMoodSeries(range);
    } catch {
      showToast("Couldn't load mood trend.", "error");
    }
  };

  if (loading) return <FullPageSpinner />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          {getGreeting()}, {user?.pseudonym}
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">Here's a quick look at your mood and journal log.</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <StatCard
          label="Current mood"
          value={currentMood ? `${MOOD_EMOJI[currentMood.mood]} ${MOOD_LABEL[currentMood.mood]}` : "Not logged"}
          helpText={currentMood ? `Intensity ${currentMood.intensity}/10` : "Log your mood below"}
        />
        <StatCard label="Journal entries" value={journalStats?.total_entries ?? 0} helpText="All time" />
      </div>

      <div className="card">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-gray-900 dark:text-gray-100">Mood trend</h3>
          <div className="flex gap-1 rounded-lg bg-gray-100 p-1 text-xs dark:bg-gray-800">
            {(["weekly", "monthly"] as MoodRange[]).map((r) => (
              <button
                key={r}
                onClick={() => handleRangeChange(r)}
                className={`rounded-md px-2.5 py-1 font-medium capitalize transition-colors ${
                  moodRange === r ? "bg-white text-gray-900 shadow-sm dark:bg-gray-700 dark:text-white" : "text-gray-500"
                }`}
              >
                {r}
              </button>
            ))}
          </div>
        </div>
        <div className="mt-4 h-64">
          <MoodTrendChart data={moodSeries} />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <MoodQuickLog onLogged={(entry) => setCurrentMood(entry)} />

        <div className="card flex flex-col items-start justify-center">
          <h3 className="font-semibold text-gray-900 dark:text-gray-100">Write a journal entry</h3>
          <p className="mt-1.5 text-sm text-gray-500 dark:text-gray-400">
            Entries get a tentative, AI-suggested sentiment label you can accept, reject, or correct.
          </p>
          <Link to="/journal" className="btn-primary mt-4">
            Go to journal
          </Link>
        </div>
      </div>
    </div>
  );
}

function getGreeting() {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 18) return "Good afternoon";
  return "Good evening";
}
