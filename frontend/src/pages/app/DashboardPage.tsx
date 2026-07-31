import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { aiApi, journalsApi, moodsApi, recommendationsApi, wellnessApi } from "@/api";
import { MoodQuickLog } from "@/components/dashboard/MoodQuickLog";
import { MoodTrendChart } from "@/components/dashboard/MoodTrendChart";
import { StatCard } from "@/components/dashboard/StatCard";
import { WellnessScoreGauge } from "@/components/dashboard/WellnessScoreGauge";
import { EmptyState } from "@/components/common/EmptyState";
import { FullPageSpinner } from "@/components/common/Spinner";
import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/context/ToastContext";
import type {
  DailyMoodStat,
  JournalStats,
  MeditationProgress,
  MoodEntry,
  Recommendation,
  WellnessScoreSnapshot,
} from "@/types";
import { MOOD_EMOJI, MOOD_LABEL } from "@/types";

type MoodRange = "weekly" | "monthly";

export default function DashboardPage() {
  const { user } = useAuth();
  const { showToast } = useToast();

  const [loading, setLoading] = useState(true);
  const [currentMood, setCurrentMood] = useState<MoodEntry | null>(null);
  const [moodSeries, setMoodSeries] = useState<DailyMoodStat[]>([]);
  const [moodRange, setMoodRange] = useState<MoodRange>("weekly");
  const [wellness, setWellness] = useState<WellnessScoreSnapshot | null>(null);
  const [journalStats, setJournalStats] = useState<JournalStats | null>(null);
  const [meditation, setMeditation] = useState<MeditationProgress | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);

  const loadMoodSeries = async (range: MoodRange) => {
    const { data } = range === "weekly" ? await moodsApi.weekly() : await moodsApi.monthly();
    setMoodSeries(data);
  };

  useEffect(() => {
    let cancelled = false;

    async function load() {
      const results = await Promise.allSettled([
        moodsApi.current(),
        moodsApi.weekly(),
        aiApi.wellnessScoreCurrent(),
        journalsApi.stats(),
        wellnessApi.meditationProgress(),
        recommendationsApi.list({ status: "pending", page_size: 4 }),
      ]);
      if (cancelled) return;

      if (results[0].status === "fulfilled") setCurrentMood(results[0].value.data);
      if (results[1].status === "fulfilled") setMoodSeries(results[1].value.data);
      if (results[2].status === "fulfilled") setWellness(results[2].value.data);
      if (results[3].status === "fulfilled") setJournalStats(results[3].value.data);
      if (results[4].status === "fulfilled") setMeditation(results[4].value.data);
      if (results[5].status === "fulfilled") setRecommendations(results[5].value.data.results);

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

  const handleRecommendationAction = async (id: string, status: "completed" | "dismissed") => {
    await recommendationsApi.updateStatus(id, status);
    setRecommendations((prev) => prev.filter((r) => r.id !== id));
  };

  if (loading) return <FullPageSpinner />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          {getGreeting()}, {user?.first_name}
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">Here's how things are looking today.</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Current mood"
          value={currentMood ? `${MOOD_EMOJI[currentMood.mood]} ${MOOD_LABEL[currentMood.mood]}` : "Not logged"}
          helpText={currentMood ? `Intensity ${currentMood.intensity}/10` : "Log your mood below"}
        />
        <StatCard label="Journal entries" value={journalStats?.total_entries ?? 0} helpText="All time" />
        <StatCard
          label="Meditation this week"
          value={`${meditation?.minutes_this_week ?? 0} min`}
          helpText={`${meditation?.sessions_this_week ?? 0} sessions`}
        />
        <StatCard
          label="Pending recommendations"
          value={recommendations.length}
          helpText="Personalized for you"
        />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="card lg:col-span-2">
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

        <div className="card flex flex-col items-center justify-center">
          <h3 className="self-start font-semibold text-gray-900 dark:text-gray-100">Wellness score</h3>
          <div className="mt-2">
            <WellnessScoreGauge score={wellness?.overall_score ?? null} />
          </div>
          <Link to="/reports" className="mt-2 text-xs text-brand-600 hover:underline">
            View full breakdown
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <MoodQuickLog onLogged={(entry) => setCurrentMood(entry)} />

        <div className="card">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-gray-900 dark:text-gray-100">Recommended for you</h3>
            <Link to="/reports" className="text-xs text-brand-600 hover:underline">
              See all
            </Link>
          </div>
          {recommendations.length === 0 ? (
            <div className="mt-4">
              <EmptyState title="No recommendations yet" description="Log your mood or write a journal entry to get personalized suggestions." />
            </div>
          ) : (
            <ul className="mt-4 space-y-3">
              {recommendations.map((rec) => (
                <li key={rec.id} className="rounded-xl border border-gray-200 p-3 dark:border-gray-800">
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{rec.title}</p>
                  <p className="mt-0.5 text-xs text-gray-500 dark:text-gray-400">{rec.description}</p>
                  <div className="mt-2 flex gap-2">
                    <button
                      onClick={() => handleRecommendationAction(rec.id, "completed")}
                      className="text-xs font-medium text-emerald-600 hover:underline"
                    >
                      Mark done
                    </button>
                    <button
                      onClick={() => handleRecommendationAction(rec.id, "dismissed")}
                      className="text-xs font-medium text-gray-400 hover:underline"
                    >
                      Dismiss
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
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
