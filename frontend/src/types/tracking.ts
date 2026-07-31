import type { Mood } from "./common";

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

export type JournalVisibility = "private" | "public";

export interface JournalEntry {
  id: string;
  title: string;
  body: string;
  mood: Mood | "";
  tags: string[];
  entry_date: string;
  visibility: JournalVisibility;
  is_flagged: boolean;
  created_at: string;
  updated_at: string;
}

export interface JournalStats {
  total_entries: number;
  public_entries: number;
  private_entries: number;
  flagged_entries: number;
  mood_breakdown: Record<string, number>;
}

export interface SleepEntry {
  id: string;
  entry_date: string;
  hours_slept: string;
  quality: number;
  notes: string;
  created_at: string;
}

export interface MeditationSession {
  id: string;
  resource: string | null;
  duration_minutes: number;
  completed: boolean;
  started_at: string;
  completed_at: string | null;
  created_at: string;
}

export interface MeditationProgress {
  total_sessions: number;
  total_minutes: number;
  sessions_this_week: number;
  minutes_this_week: number;
}
