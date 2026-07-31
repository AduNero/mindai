import { useEffect, useState } from "react";

import { journalsApi } from "@/api";
import type { JournalEntryPayload } from "@/api/journals";
import { EmptyState } from "@/components/common/EmptyState";
import { Modal } from "@/components/common/Modal";
import { FullPageSpinner } from "@/components/common/Spinner";
import { JournalEntryForm } from "@/components/journal/JournalEntryForm";
import { useToast } from "@/context/ToastContext";
import type { JournalEntry } from "@/types";
import { MOOD_EMOJI } from "@/types";

export default function JournalPage() {
  const { showToast } = useToast();
  const [loading, setLoading] = useState(true);
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [search, setSearch] = useState("");
  const [createOpen, setCreateOpen] = useState(false);
  const [editing, setEditing] = useState<JournalEntry | null>(null);
  const [viewing, setViewing] = useState<JournalEntry | null>(null);

  const load = async (params?: Record<string, string>) => {
    const { data } = await journalsApi.list(params);
    setEntries(data.results);
  };

  useEffect(() => {
    load().finally(() => setLoading(false));
  }, []);

  const handleSearch = async (value: string) => {
    setSearch(value);
    await load(value ? { search: value } : undefined);
  };

  const handleCreate = async (payload: JournalEntryPayload) => {
    const { data } = await journalsApi.create(payload);
    setEntries((prev) => [data, ...prev]);
    setCreateOpen(false);
    showToast("Journal entry saved.", "success");
  };

  const handleUpdate = async (payload: JournalEntryPayload) => {
    if (!editing) return;
    const { data } = await journalsApi.update(editing.id, payload);
    setEntries((prev) => prev.map((e) => (e.id === data.id ? data : e)));
    setEditing(null);
    showToast("Journal entry updated.", "success");
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this journal entry? This can't be undone.")) return;
    await journalsApi.remove(id);
    setEntries((prev) => prev.filter((e) => e.id !== id));
    setViewing(null);
    showToast("Journal entry deleted.", "success");
  };

  if (loading) return <FullPageSpinner />;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Journal</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">Write freely — entries are private by default.</p>
        </div>
        <button onClick={() => setCreateOpen(true)} className="btn-primary">
          + New entry
        </button>
      </div>

      <input
        className="input max-w-sm"
        placeholder="Search journal entries..."
        value={search}
        onChange={(e) => handleSearch(e.target.value)}
      />

      {entries.length === 0 ? (
        <EmptyState
          icon="📓"
          title="No journal entries yet"
          description="Start writing to track your thoughts and get AI-powered insights."
          action={
            <button onClick={() => setCreateOpen(true)} className="btn-primary">
              Write your first entry
            </button>
          }
        />
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {entries.map((entry) => (
            <button
              key={entry.id}
              onClick={() => setViewing(entry)}
              className="card text-left transition-shadow hover:shadow-md"
            >
              <div className="flex items-center justify-between">
                <h3 className="line-clamp-1 font-semibold text-gray-900 dark:text-gray-100">{entry.title}</h3>
                {entry.mood && <span>{MOOD_EMOJI[entry.mood]}</span>}
              </div>
              <p className="mt-1.5 line-clamp-3 text-sm text-gray-500 dark:text-gray-400">{entry.body}</p>
              <div className="mt-3 flex flex-wrap items-center gap-1.5">
                {entry.tags.map((tag) => (
                  <span key={tag} className="badge bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300">
                    {tag}
                  </span>
                ))}
              </div>
              <p className="mt-3 text-xs text-gray-400">
                {entry.entry_date} · {entry.visibility}
              </p>
            </button>
          ))}
        </div>
      )}

      <Modal open={createOpen} onClose={() => setCreateOpen(false)} title="New journal entry">
        <JournalEntryForm onSubmit={handleCreate} />
      </Modal>

      <Modal open={!!editing} onClose={() => setEditing(null)} title="Edit journal entry">
        {editing && <JournalEntryForm initial={editing} onSubmit={handleUpdate} submitLabel="Update entry" />}
      </Modal>

      <Modal open={!!viewing} onClose={() => setViewing(null)} title={viewing?.title ?? ""} maxWidth="max-w-2xl">
        {viewing && (
          <div className="space-y-4">
            <p className="whitespace-pre-wrap text-sm text-gray-700 dark:text-gray-200">{viewing.body}</p>
            <div className="flex flex-wrap gap-1.5">
              {viewing.tags.map((tag) => (
                <span key={tag} className="badge bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300">
                  {tag}
                </span>
              ))}
            </div>
            <div className="flex gap-2 border-t border-gray-100 pt-4 dark:border-gray-800">
              <button
                onClick={() => {
                  setEditing(viewing);
                  setViewing(null);
                }}
                className="btn-outline"
              >
                Edit
              </button>
              <button onClick={() => handleDelete(viewing.id)} className="btn-danger">
                Delete
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
