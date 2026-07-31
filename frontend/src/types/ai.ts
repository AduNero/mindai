import type { Mood, RiskLevel } from "./common";

export type Sentiment = "positive" | "negative" | "neutral";

export type Emotion =
  | "joy"
  | "fear"
  | "sadness"
  | "anger"
  | "love"
  | "surprise"
  | "optimism"
  | "disappointment";

export interface SentimentResult {
  id: string;
  sentiment: Sentiment;
  confidence_score: number;
  stress_score: number;
  anxiety_score: number;
  burnout_score: number;
  depression_indicator_score: number;
  keywords: string[];
  model_version: string;
  analyzed_at: string;
}

export interface EmotionResult {
  id: string;
  dominant_emotion: Emotion;
  scores: Record<string, number>;
  model_version: string;
  analyzed_at: string;
}

export interface ContentAnalysis {
  sentiment: SentimentResult | null;
  emotion: EmotionResult | null;
}

export interface RiskAssessment {
  id: string;
  risk_level: RiskLevel;
  detection_source: "journal" | "chat" | "assessment";
  triggered_phrases: string[];
  confidence_score: number;
  resources_shown_at: string | null;
  acknowledged_at: string | null;
  created_at: string;
}

export interface WellnessScoreSnapshot {
  id: string;
  score_date: string;
  overall_score: number;
  mood_component: number;
  journal_component: number;
  assessment_component: number;
  sleep_component: number;
  activity_component: number;
  chat_sentiment_component: number;
}

export interface MoodPrediction {
  id: string;
  predicted_for_date: string;
  predicted_mood: Mood;
  confidence_score: number;
  based_on_window_days: number;
  generated_at: string;
}
