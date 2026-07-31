import { useEffect, useState } from "react";

import { auditApi } from "@/api";
import { FullPageSpinner } from "@/components/common/Spinner";
import type { AuditLog } from "@/types";

export default function AdminAuditLogsPage() {
  const [loading, setLoading] = useState(true);
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [actionFilter, setActionFilter] = useState("");

  const load = async (action?: string) => {
    const { data } = await auditApi.logs(action ? { action } : undefined);
    setLogs(data.results);
  };

  useEffect(() => {
    load().finally(() => setLoading(false));
  }, []);

  const handleFilter = async (action: string) => {
    setActionFilter(action);
    setLoading(true);
    await load(action || undefined);
    setLoading(false);
  };

  if (loading) return <FullPageSpinner />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Audit Logs</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">Security-relevant events across the platform.</p>
      </div>

      <input
        className="input max-w-xs"
        placeholder="Filter by action (e.g. login_failed)"
        value={actionFilter}
        onChange={(e) => handleFilter(e.target.value)}
      />

      <div className="overflow-x-auto rounded-2xl border border-gray-200 dark:border-gray-800">
        <table className="w-full text-left text-sm">
          <thead className="bg-gray-50 text-xs uppercase text-gray-400 dark:bg-gray-900">
            <tr>
              <th className="px-4 py-3">Action</th>
              <th className="px-4 py-3">User</th>
              <th className="px-4 py-3">IP</th>
              <th className="px-4 py-3">When</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
            {logs.map((log) => (
              <tr key={log.id}>
                <td className="px-4 py-3">
                  <span className="badge bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300">{log.action}</span>
                </td>
                <td className="px-4 py-3 text-gray-500 dark:text-gray-400">{log.user_email || "—"}</td>
                <td className="px-4 py-3 text-gray-500 dark:text-gray-400">{log.ip_address || "—"}</td>
                <td className="px-4 py-3 text-gray-500 dark:text-gray-400">{new Date(log.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
