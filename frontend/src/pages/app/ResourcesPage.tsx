import { useEffect, useState } from "react";

import { resourcesApi } from "@/api";
import { EmptyState } from "@/components/common/EmptyState";
import { Modal } from "@/components/common/Modal";
import { FullPageSpinner } from "@/components/common/Spinner";
import type { EmergencyResource, Resource, ResourceType } from "@/types";

const TYPE_LABELS: Record<ResourceType, string> = {
  article: "Article",
  video: "Video",
  podcast: "Podcast",
  meditation: "Meditation",
  breathing_exercise: "Breathing Exercise",
  emergency: "Emergency",
};

const TYPE_FILTERS: { value: ResourceType | ""; label: string }[] = [
  { value: "", label: "All" },
  { value: "article", label: "Articles" },
  { value: "video", label: "Videos" },
  { value: "podcast", label: "Podcasts" },
  { value: "meditation", label: "Meditation" },
  { value: "breathing_exercise", label: "Breathing" },
];

export default function ResourcesPage() {
  const [loading, setLoading] = useState(true);
  const [resources, setResources] = useState<Resource[]>([]);
  const [emergency, setEmergency] = useState<EmergencyResource[]>([]);
  const [typeFilter, setTypeFilter] = useState<ResourceType | "">("");
  const [search, setSearch] = useState("");
  const [viewing, setViewing] = useState<Resource | null>(null);
  const [showEmergency, setShowEmergency] = useState(false);

  const load = async (params?: Record<string, string>) => {
    const { data } = await resourcesApi.list(params);
    setResources(data.results);
  };

  useEffect(() => {
    Promise.all([resourcesApi.list(), resourcesApi.emergency()])
      .then(([resRes, emergencyRes]) => {
        setResources(resRes.data.results);
        setEmergency(emergencyRes.data.results);
      })
      .finally(() => setLoading(false));
  }, []);

  const applyFilters = async (type: ResourceType | "", q: string) => {
    const params: Record<string, string> = {};
    if (type) params.resource_type = type;
    if (q) params.search = q;
    await load(Object.keys(params).length ? params : undefined);
  };

  if (loading) return <FullPageSpinner />;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Resource Center</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">Articles, videos, podcasts, and mindfulness exercises.</p>
        </div>
        <button onClick={() => setShowEmergency(true)} className="btn-danger">
          🚨 Emergency Resources
        </button>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <input
          className="input max-w-xs"
          placeholder="Search resources..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            applyFilters(typeFilter, e.target.value);
          }}
        />
        <div className="flex flex-wrap gap-2">
          {TYPE_FILTERS.map((f) => (
            <button
              key={f.value}
              onClick={() => {
                setTypeFilter(f.value);
                applyFilters(f.value, search);
              }}
              className={`rounded-full px-3 py-1.5 text-xs font-medium ${
                typeFilter === f.value
                  ? "bg-brand-600 text-white"
                  : "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300"
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {resources.length === 0 ? (
        <EmptyState title="No resources found" description="Try a different search or filter." />
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {resources.map((r) => (
            <button key={r.id} onClick={() => setViewing(r)} className="card text-left hover:shadow-md">
              {r.thumbnail && (
                <img src={r.thumbnail} alt="" className="mb-3 h-32 w-full rounded-xl object-cover" />
              )}
              <span className="badge bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300">
                {TYPE_LABELS[r.resource_type]}
              </span>
              <h3 className="mt-2 font-semibold text-gray-900 dark:text-gray-100">{r.title}</h3>
              <p className="mt-1 line-clamp-2 text-sm text-gray-500 dark:text-gray-400">{r.description}</p>
              {r.duration_minutes && (
                <p className="mt-2 text-xs text-gray-400">{r.duration_minutes} min</p>
              )}
            </button>
          ))}
        </div>
      )}

      <Modal open={!!viewing} onClose={() => setViewing(null)} title={viewing?.title ?? ""} maxWidth="max-w-2xl">
        {viewing && (
          <div className="space-y-4">
            <p className="text-sm text-gray-500 dark:text-gray-400">{viewing.description}</p>
            {viewing.body && (
              <p className="whitespace-pre-wrap text-sm text-gray-700 dark:text-gray-200">{viewing.body}</p>
            )}
            {viewing.external_url && (
              <a href={viewing.external_url} target="_blank" rel="noreferrer" className="btn-primary inline-flex">
                Open {TYPE_LABELS[viewing.resource_type]}
              </a>
            )}
            <div className="flex flex-wrap gap-1.5">
              {viewing.tags.map((tag) => (
                <span key={tag} className="badge bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}
      </Modal>

      <Modal open={showEmergency} onClose={() => setShowEmergency(false)} title="Emergency Resources">
        <div className="space-y-3">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            If you're in immediate danger, contact local emergency services right away. MindCare AI
            cannot provide emergency assistance.
          </p>
          {emergency.length === 0 ? (
            <p className="text-sm text-gray-400">No emergency resources are configured for your region yet.</p>
          ) : (
            emergency.map((r) => (
              <div key={r.id} className="rounded-xl border border-gray-200 p-3 dark:border-gray-800">
                <p className="font-medium text-gray-900 dark:text-gray-100">{r.name}</p>
                <p className="text-sm text-gray-600 dark:text-gray-300">{r.phone_number} {r.is_24_7 && "· 24/7"}</p>
                {r.website && (
                  <a href={r.website} target="_blank" rel="noreferrer" className="text-xs text-brand-600 hover:underline">
                    {r.website}
                  </a>
                )}
              </div>
            ))
          )}
        </div>
      </Modal>
    </div>
  );
}
