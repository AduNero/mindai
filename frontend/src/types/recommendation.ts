export type RecommendationCategory =
  | "physical_activity"
  | "mindfulness"
  | "breathing"
  | "sleep"
  | "nutrition"
  | "social"
  | "self_care"
  | "professional_help"
  | "entertainment"
  | "education";

export type RecommendationStatus = "pending" | "completed" | "dismissed";

export interface Recommendation {
  id: string;
  title: string;
  description: string;
  category: RecommendationCategory;
  source: "mood" | "journal" | "assessment" | "chat" | "system";
  status: RecommendationStatus;
  generated_at: string;
  responded_at: string | null;
}

export interface RecommendationTemplate {
  id: string;
  category: RecommendationCategory;
  title: string;
  description: string;
  action_url: string;
  trigger_conditions: Record<string, unknown>;
  is_active: boolean;
}
