import { FormEvent, useEffect, useState } from "react";

import { usersApi } from "@/api";
import { FullPageSpinner } from "@/components/common/Spinner";
import { useToast } from "@/context/ToastContext";
import type { AdminUser, CounselorProfile } from "@/types";
import { extractErrorMessage } from "@/utils/errors";

export default function AdminCounselorsPage() {
  const { showToast } = useToast();
  const [loading, setLoading] = useState(true);
  const [counselors, setCounselors] = useState<CounselorProfile[]>([]);
  const [candidates, setCandidates] = useState<AdminUser[]>([]);

  const [userId, setUserId] = useState("");
  const [specialization, setSpecialization] = useState("");
  const [bio, setBio] = useState("");
  const [promoting, setPromoting] = useState(false);

  useEffect(() => {
    Promise.all([usersApi.admin.listCounselors(), usersApi.admin.listUsers({ role: "user" })])
      .then(([counselorRes, userRes]) => {
        setCounselors(counselorRes.data.results);
        setCandidates(userRes.data.results);
      })
      .finally(() => setLoading(false));
  }, []);

  const handlePromote = async (e: FormEvent) => {
    e.preventDefault();
    if (!userId) return;
    setPromoting(true);
    try {
      const { data } = await usersApi.admin.promoteToCounselor({ user_id: userId, specialization, bio });
      setCounselors((prev) => [data, ...prev]);
      setCandidates((prev) => prev.filter((c) => c.id !== userId));
      setUserId("");
      setSpecialization("");
      setBio("");
      showToast("User promoted to counselor.", "success");
    } catch (err) {
      showToast(extractErrorMessage(err, "Couldn't promote this user."), "error");
    } finally {
      setPromoting(false);
    }
  };

  const handleToggleAccepting = async (counselor: CounselorProfile) => {
    const { data } = await usersApi.admin.updateCounselor(counselor.id, {
      is_accepting_appointments: !counselor.is_accepting_appointments,
    });
    setCounselors((prev) => prev.map((c) => (c.id === counselor.id ? data : c)));
  };

  if (loading) return <FullPageSpinner />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Counselors</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">Promote users to counselors and manage availability.</p>
      </div>

      <div className="card">
        <h3 className="font-semibold text-gray-900 dark:text-gray-100">Promote a user</h3>
        <form onSubmit={handlePromote} className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className="label">User</label>
            <select className="input" required value={userId} onChange={(e) => setUserId(e.target.value)}>
              <option value="">Select a user</option>
              {candidates.map((c) => (
                <option key={c.id} value={c.id}>{c.full_name} ({c.email})</option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Specialization</label>
            <input className="input" value={specialization} onChange={(e) => setSpecialization(e.target.value)} />
          </div>
          <div className="sm:col-span-2">
            <label className="label">Bio</label>
            <textarea className="input" rows={2} value={bio} onChange={(e) => setBio(e.target.value)} />
          </div>
          <div className="sm:col-span-2">
            <button type="submit" disabled={promoting} className="btn-primary">
              {promoting ? "Promoting..." : "Promote to counselor"}
            </button>
          </div>
        </form>
      </div>

      <div className="card">
        <h3 className="font-semibold text-gray-900 dark:text-gray-100">All counselors</h3>
        <ul className="mt-3 divide-y divide-gray-100 dark:divide-gray-800">
          {counselors.map((c) => (
            <li key={c.id} className="flex items-center justify-between py-3 text-sm">
              <div>
                <p className="font-medium text-gray-900 dark:text-gray-100">{c.user.full_name}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">{c.specialization || "General"}</p>
              </div>
              <button
                onClick={() => handleToggleAccepting(c)}
                className={`badge ${c.is_accepting_appointments ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300" : "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300"}`}
              >
                {c.is_accepting_appointments ? "Accepting" : "Paused"}
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
