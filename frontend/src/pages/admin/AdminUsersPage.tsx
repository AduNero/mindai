import { useEffect, useState } from "react";

import { usersApi } from "@/api";
import { FullPageSpinner } from "@/components/common/Spinner";
import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/context/ToastContext";
import type { AdminUser } from "@/types";
import { extractErrorMessage } from "@/utils/errors";

export default function AdminUsersPage() {
  const { user: currentUser } = useAuth();
  const { showToast } = useToast();
  const [loading, setLoading] = useState(true);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [search, setSearch] = useState("");

  const load = async (params?: Record<string, string>) => {
    const { data } = await usersApi.admin.listUsers(params);
    setUsers(data.results);
  };

  useEffect(() => {
    load().finally(() => setLoading(false));
  }, []);

  const handleSearch = async (value: string) => {
    setSearch(value);
    await load(value ? { search: value } : undefined);
  };

  const handleToggleActive = async (user: AdminUser) => {
    const { data } = await usersApi.admin.updateUser(user.id, { is_active: !user.is_active });
    setUsers((prev) => prev.map((u) => (u.id === user.id ? data : u)));
    showToast(`User ${data.is_active ? "activated" : "suspended"}.`, "success");
  };

  const handlePromoteToAdmin = async (user: AdminUser) => {
    if (!window.confirm(`Give ${user.full_name} (${user.email}) full admin access?`)) return;
    try {
      const { data } = await usersApi.admin.updateUser(user.id, { role: "admin" });
      setUsers((prev) => prev.map((u) => (u.id === user.id ? data : u)));
      showToast(`${data.full_name} is now an admin.`, "success");
    } catch (err) {
      showToast(extractErrorMessage(err, "Couldn't promote this user."), "error");
    }
  };

  const handleRemoveAdmin = async (user: AdminUser) => {
    if (!window.confirm(`Remove admin access from ${user.full_name} (${user.email})?`)) return;
    try {
      const { data } = await usersApi.admin.updateUser(user.id, { role: "user" });
      setUsers((prev) => prev.map((u) => (u.id === user.id ? data : u)));
      showToast(`Admin access removed from ${data.full_name}.`, "success");
    } catch (err) {
      showToast(extractErrorMessage(err, "Couldn't remove admin access."), "error");
    }
  };

  if (loading) return <FullPageSpinner />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Users</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">Manage user accounts and access.</p>
      </div>

      <input
        className="input max-w-sm"
        placeholder="Search by name or email..."
        value={search}
        onChange={(e) => handleSearch(e.target.value)}
      />

      <div className="overflow-x-auto rounded-2xl border border-gray-200 dark:border-gray-800">
        <table className="w-full text-left text-sm">
          <thead className="bg-gray-50 text-xs uppercase text-gray-400 dark:bg-gray-900">
            <tr>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Email</th>
              <th className="px-4 py-3">Role</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Verified</th>
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
            {users.map((u) => (
              <tr key={u.id}>
                <td className="px-4 py-3">{u.full_name}</td>
                <td className="px-4 py-3 text-gray-500 dark:text-gray-400">{u.email}</td>
                <td className="px-4 py-3 capitalize">{u.role}</td>
                <td className="px-4 py-3">
                  <span className={`badge ${u.is_active ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300" : "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300"}`}>
                    {u.is_active ? "Active" : "Suspended"}
                  </span>
                </td>
                <td className="px-4 py-3">{u.is_email_verified ? "✓" : "—"}</td>
                <td className="px-4 py-3 text-right space-x-3 whitespace-nowrap">
                  {u.role !== "admin" && (
                    <button onClick={() => handlePromoteToAdmin(u)} className="text-xs font-medium text-brand-600 hover:underline">
                      Make admin
                    </button>
                  )}
                  {u.role === "admin" && u.id !== currentUser?.id && (
                    <button onClick={() => handleRemoveAdmin(u)} className="text-xs font-medium text-red-600 hover:underline">
                      Remove admin
                    </button>
                  )}
                  <button onClick={() => handleToggleActive(u)} className="text-xs font-medium text-brand-600 hover:underline">
                    {u.is_active ? "Suspend" : "Activate"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
