export interface Paginated<T> {
  count: number;
  total_pages: number;
  current_page: number;
  page_size: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiErrorPayload {
  success: false;
  error: {
    code: string;
    message: string;
    details: unknown;
  };
}

export type Mood =
  | "happy"
  | "neutral"
  | "sad"
  | "angry"
  | "anxious"
  | "tired"
  | "excited"
  | "depressed";

export const MOOD_OPTIONS: { value: Mood; label: string; emoji: string }[] = [
  { value: "happy", label: "Happy", emoji: "😊" },
  { value: "neutral", label: "Neutral", emoji: "😐" },
  { value: "sad", label: "Sad", emoji: "😢" },
  { value: "angry", label: "Angry", emoji: "😡" },
  { value: "anxious", label: "Anxious", emoji: "😰" },
  { value: "tired", label: "Tired", emoji: "😴" },
  { value: "excited", label: "Excited", emoji: "😍" },
  { value: "depressed", label: "Depressed", emoji: "😞" },
];

export const MOOD_EMOJI: Record<Mood, string> = MOOD_OPTIONS.reduce(
  (acc, m) => ({ ...acc, [m.value]: m.emoji }),
  {} as Record<Mood, string>,
);

export const MOOD_LABEL: Record<Mood, string> = MOOD_OPTIONS.reduce(
  (acc, m) => ({ ...acc, [m.value]: m.label }),
  {} as Record<Mood, string>,
);

export type RiskLevel = "none" | "low" | "moderate" | "high" | "critical";
