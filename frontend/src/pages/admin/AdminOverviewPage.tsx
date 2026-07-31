import { useEffect, useState } from "react";

import { adminPanelApi } from "@/api";
import { StatCard } from "@/components/dashboard/StatCard";
import { FullPageSpinner } from "@/components/common/Spinner";
import type { DashboardStats } from "@/types";

export default function AdminOverviewPage() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<DashboardStats | null>(null);

  useEffect(() => {
    adminPanelApi
      .dashboardStats()
      .then(({ data }) => setStats(data))
      .finally(() => setLoading(false));
  }, []);

  if (loading || !stats) return <FullPageSpinner />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Admin Overview</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">Platform-wide statistics at a glance.</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total users" value={stats.total_users} accent="brand" />
        <StatCard label="Active users (30d)" value={stats.active_users_30d} accent="emerald" />
        <StatCard label="High-risk users" value={stats.high_risk_users} accent="red" helpText="Unacknowledged high/critical risk" />
        <StatCard label="Total assessments" value={stats.total_assessments} accent="sky" />
        <StatCard label="Appointments" value={stats.total_appointments} helpText={`${stats.pending_appointments} pending`} accent="amber" />
        <StatCard label="AI chat sessions" value={stats.ai_chat_sessions} helpText={`${stats.ai_chat_messages} messages`} accent="brand" />
        <StatCard label="Mood entries (30d)" value={stats.mood_entries_30d} accent="emerald" />
        <StatCard label="Journal entries (30d)" value={stats.journal_entries_30d} helpText={`${stats.pending_journal_reports} pending reports`} accent="sky" />
      </div>
    </div>
  );
}
