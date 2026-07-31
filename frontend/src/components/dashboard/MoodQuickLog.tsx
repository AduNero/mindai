import { useState } from "react";

import { moodsApi } from "@/api";
import { useToast } from "@/context/ToastContext";
import type { Mood, MoodEntry } from "@/types";
import { MOOD_OPTIONS } from "@/types";

interface MoodQuickLogProps {
  onLogged: (entry: MoodEntry) => void;
}

export function MoodQuickLog({ onLogged }: MoodQuickLogProps) {
  const { showToast } = useToast();
  const [selected, setSelected] = useState<Mood | null>(null);
  const [intensity, setIntensity] = useState(5);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!selected) return;
    setSubmitting(true);
    try {
      const now = new Date();
      const { data } = await moodsApi.create({
        mood: selected,
        intensity,
        entry_date: now.toISOString().slice(0, 10),
        entry_time: now.toTimeString().slice(0, 8),
      });
      showToast("Mood logged.", "success");
      onLogged(data);
      setSelected(null);
      setIntensity(5);
    } catch {
      showToast("Couldn't log your mood — please try again.", "error");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="card">
      <h3 className="font-semibold text-gray-900 dark:text-gray-100">How are you feeling right now?</h3>
      <div className="mt-4 grid grid-cols-4 gap-2 sm:grid-cols-8">
        {MOOD_OPTIONS.map((m) => (
          <button
            key={m.value}
            type="button"
            onClick={() => setSelected(m.value)}
            className={`flex flex-col items-center gap-1 rounded-xl border p-2 text-xs transition-colors ${
              selected === m.value
                ? "border-brand-500 bg-brand-50 dark:bg-brand-950/50"
                : "border-transparent hover:bg-gray-100 dark:hover:bg-gray-800"
            }`}
          >
            <span className="text-2xl">{m.emoji}</span>
            {m.label}
          </button>
        ))}
      </div>

      {selected && (
        <div className="mt-4">
          <label htmlFor="intensity" className="label">
            Intensity: {intensity}/10
          </label>
          <input
            id="intensity"
            type="range"
            min={1}
            max={10}
            value={intensity}
            onChange={(e) => setIntensity(Number(e.target.value))}
            className="w-full accent-brand-600"
          />
          <button onClick={handleSubmit} disabled={submitting} className="btn-primary mt-3 w-full">
            {submitting ? "Logging..." : "Log mood"}
          </button>
        </div>
      )}
    </div>
  );
}
