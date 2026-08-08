import type { RiskLevel } from "./common";

export type SentimentLabel = "positive" | "negative" | "neutral";
export type SentimentUserAction = "pending" | "accepted" | "rejected" | "corrected";

export interface SentimentResult {
  id: string;
  label: SentimentLabel;
  confidence: number;
  model_version: string;
  user_action: SentimentUserAction;
  corrected_label: SentimentLabel | "";
  actioned_at: string | null;
  created_at: string;
}

export interface RiskAssessment {
  id: string;
  risk_level: RiskLevel;
  detection_source: "journal";
  confidence_score: number;
  resources_shown_at: string | null;
  acknowledged_at: string | null;
  created_at: string;
}
