import { useState } from "react";

import type { JournalEntryPayload } from "@/api/journals";
import type { JournalEntry, Mood } from "@/types";
import { MOOD_OPTIONS } from "@/types";

interface JournalEntryFormProps {
  initial?: JournalEntry;
  onSubmit: (payload: JournalEntryPayload) => Promise<void>;
  submitLabel?: string;
}

export function JournalEntryForm({ initial, onSubmit, submitLabel = "Save entry" }: JournalEntryFormProps) {
  const [title, setTitle] = useState(initial?.title ?? "");
  const [body, setBody] = useState(initial?.body ?? "");
  const [mood, setMood] = useState<Mood | "">(initial?.mood ?? "");
  const [tags, setTags] = useState(initial?.tags.join(", ") ?? "");
  const [entryDate, setEntryDate] = useState(initial?.entry_date ?? new Date().toISOString().slice(0, 10));
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await onSubmit({
        title,
        body,
        mood: mood || undefined,
        tags: tags.split(",").map((t) => t.trim()).filter(Boolean),
        entry_date: entryDate,
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="je-title" className="label">Title</label>
        <input id="je-title" required className="input" value={title} onChange={(e) => setTitle(e.target.value)} />
      </div>
      <div>
        <label htmlFor="je-body" className="label">What's on your mind?</label>
        <textarea id="je-body" required rows={6} className="input" value={body} onChange={(e) => setBody(e.target.value)} />
        <p className="mt-1 text-xs text-gray-400">
          On save, this gets a tentative AI sentiment label — not a diagnosis or emotional assessment.
        </p>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label htmlFor="je-mood" className="label">Mood</label>
          <select id="je-mood" className="input" value={mood} onChange={(e) => setMood(e.target.value as Mood | "")}>
            <option value="">None</option>
            {MOOD_OPTIONS.map((m) => (
              <option key={m.value} value={m.value}>
                {m.emoji} {m.label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="je-date" className="label">Date</label>
          <input id="je-date" type="date" className="input" value={entryDate} onChange={(e) => setEntryDate(e.target.value)} />
        </div>
      </div>
      <div>
        <label htmlFor="je-tags" className="label">Tags (comma-separated)</label>
        <input id="je-tags" className="input" placeholder="school, stress" value={tags} onChange={(e) => setTags(e.target.value)} />
      </div>
      <button type="submit" disabled={submitting} className="btn-primary w-full">
        {submitting ? "Saving..." : submitLabel}
      </button>
    </form>
  );
}
