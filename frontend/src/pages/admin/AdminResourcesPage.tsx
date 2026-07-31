import { FormEvent, useEffect, useState } from "react";

import { resourcesApi } from "@/api";
import { Modal } from "@/components/common/Modal";
import { FullPageSpinner } from "@/components/common/Spinner";
import { useToast } from "@/context/ToastContext";
import type { EmergencyResource, Resource, ResourceType } from "@/types";

const RESOURCE_TYPES: ResourceType[] = ["article", "video", "podcast", "meditation", "breathing_exercise"];

export default function AdminResourcesPage() {
  const { showToast } = useToast();
  const [loading, setLoading] = useState(true);
  const [resources, setResources] = useState<Resource[]>([]);
  const [emergency, setEmergency] = useState<EmergencyResource[]>([]);
  const [createOpen, setCreateOpen] = useState(false);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [resourceType, setResourceType] = useState<ResourceType>("article");
  const [body, setBody] = useState("");
  const [externalUrl, setExternalUrl] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const [emCountry, setEmCountry] = useState("");
  const [emName, setEmName] = useState("");
  const [emPhone, setEmPhone] = useState("");

  useEffect(() => {
    Promise.all([resourcesApi.admin.list(), resourcesApi.admin.listEmergency()])
      .then(([resRes, emRes]) => {
        setResources(resRes.data.results);
        setEmergency(emRes.data.results);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const formData = new FormData();
      formData.append("title", title);
      formData.append("description", description);
      formData.append("resource_type", resourceType);
      formData.append("body", body);
      formData.append("external_url", externalUrl);
      formData.append("is_published", "true");
      const { data } = await resourcesApi.admin.create(formData);
      setResources((prev) => [data, ...prev]);
      setCreateOpen(false);
      setTitle("");
      setDescription("");
      setBody("");
      setExternalUrl("");
      showToast("Resource published.", "success");
    } catch {
      showToast("Couldn't create this resource.", "error");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this resource?")) return;
    await resourcesApi.admin.remove(id);
    setResources((prev) => prev.filter((r) => r.id !== id));
  };

  const handleTogglePublish = async (resource: Resource) => {
    const formData = new FormData();
    formData.append("is_published", String(!resource.is_published));
    const { data } = await resourcesApi.admin.update(resource.id, formData);
    setResources((prev) => prev.map((r) => (r.id === resource.id ? data : r)));
  };

  const handleAddEmergency = async (e: FormEvent) => {
    e.preventDefault();
    const { data } = await resourcesApi.admin.createEmergency({
      country_code: emCountry.toUpperCase(),
      name: emName,
      phone_number: emPhone,
      is_24_7: true,
    });
    setEmergency((prev) => [data, ...prev]);
    setEmCountry("");
    setEmName("");
    setEmPhone("");
    showToast("Emergency resource added.", "success");
  };

  if (loading) return <FullPageSpinner />;

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Resources</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">Manage the Resource Center content.</p>
        </div>
        <button onClick={() => setCreateOpen(true)} className="btn-primary">
          + New resource
        </button>
      </div>

      <div className="overflow-x-auto rounded-2xl border border-gray-200 dark:border-gray-800">
        <table className="w-full text-left text-sm">
          <thead className="bg-gray-50 text-xs uppercase text-gray-400 dark:bg-gray-900">
            <tr>
              <th className="px-4 py-3">Title</th>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3">Views</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
            {resources.map((r) => (
              <tr key={r.id}>
                <td className="px-4 py-3">{r.title}</td>
                <td className="px-4 py-3 capitalize">{r.resource_type.replace("_", " ")}</td>
                <td className="px-4 py-3">{r.view_count}</td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => handleTogglePublish(r)}
                    className={`badge ${r.is_published ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300" : "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300"}`}
                  >
                    {r.is_published ? "Published" : "Draft"}
                  </button>
                </td>
                <td className="px-4 py-3 text-right">
                  <button onClick={() => handleDelete(r.id)} className="text-xs font-medium text-red-500 hover:underline">
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h3 className="font-semibold text-gray-900 dark:text-gray-100">Emergency resources</h3>
        <form onSubmit={handleAddEmergency} className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-4">
          <input className="input uppercase" maxLength={2} placeholder="Country (US)" required value={emCountry} onChange={(e) => setEmCountry(e.target.value)} />
          <input className="input" placeholder="Name" required value={emName} onChange={(e) => setEmName(e.target.value)} />
          <input className="input" placeholder="Phone" required value={emPhone} onChange={(e) => setEmPhone(e.target.value)} />
          <button type="submit" className="btn-primary">Add</button>
        </form>
        <ul className="mt-4 divide-y divide-gray-100 dark:divide-gray-800">
          {emergency.map((e) => (
            <li key={e.id} className="flex items-center justify-between py-2 text-sm">
              <span>{e.name} ({e.country_code})</span>
              <span className="text-gray-500 dark:text-gray-400">{e.phone_number}</span>
            </li>
          ))}
        </ul>
      </div>

      <Modal open={createOpen} onClose={() => setCreateOpen(false)} title="New resource">
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="label">Title</label>
            <input className="input" required value={title} onChange={(e) => setTitle(e.target.value)} />
          </div>
          <div>
            <label className="label">Type</label>
            <select className="input" value={resourceType} onChange={(e) => setResourceType(e.target.value as ResourceType)}>
              {RESOURCE_TYPES.map((t) => (
                <option key={t} value={t}>{t.replace("_", " ")}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Description</label>
            <textarea className="input" rows={2} value={description} onChange={(e) => setDescription(e.target.value)} />
          </div>
          {resourceType === "article" ? (
            <div>
              <label className="label">Body</label>
              <textarea className="input" rows={5} value={body} onChange={(e) => setBody(e.target.value)} />
            </div>
          ) : (
            <div>
              <label className="label">External URL</label>
              <input className="input" value={externalUrl} onChange={(e) => setExternalUrl(e.target.value)} />
            </div>
          )}
          <button type="submit" disabled={submitting} className="btn-primary w-full">
            {submitting ? "Publishing..." : "Publish resource"}
          </button>
        </form>
      </Modal>
    </div>
  );
}
