import type { Mood } from "./common";
import type { SentimentResult } from "./ai";

export interface MoodEntry {
  id: string;
  mood: Mood;
  intensity: number;
  entry_date: string;
  entry_time: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface DailyMoodStat {
  date: string;
  average_intensity: number | null;
  dominant_mood: Mood | null;
  entry_count: number;
}

export interface Tag {
  id: string;
  name: string;
  slug: string;
}

export interface JournalEntry {
  id: string;
  title: string;
  body: string;
  mood: Mood | "";
  tags: string[];
  entry_date: string;
  is_flagged: boolean;
  sentiment: SentimentResult | null;
  created_at: string;
  updated_at: string;
}

export interface JournalStats {
  total_entries: number;
  flagged_entries: number;
  mood_breakdown: Record<string, number>;
}
