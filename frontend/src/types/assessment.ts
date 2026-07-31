export type AssessmentCode = "phq9" | "gad7" | "stress" | "burnout" | "self_esteem";

export type Severity = "minimal" | "mild" | "moderate" | "moderately_severe" | "severe";

export interface AssessmentOption {
  value: number;
  label: string;
}

export interface AssessmentQuestion {
  id: string;
  order: number;
  text: string;
  options: AssessmentOption[];
}

export interface AssessmentTypeSummary {
  id: string;
  code: AssessmentCode;
  name: string;
  description: string;
  max_score: number;
}

export interface AssessmentType extends AssessmentTypeSummary {
  instructions: string;
  questions: AssessmentQuestion[];
}

export interface AssessmentAnswer {
  id: string;
  question: string;
  question_order: number;
  question_text: string;
  selected_value: number;
}

export interface AssessmentResult {
  id: string;
  assessment_type: AssessmentTypeSummary;
  total_score: number;
  severity: Severity;
  interpretation: string;
  taken_at: string;
  answers: AssessmentAnswer[];
}

export interface CrisisResource {
  name: string;
  phone_number: string;
  website: string;
  is_24_7: boolean;
}

export interface AssessmentSubmitResponse extends AssessmentResult {
  risk_flag: boolean;
  crisis_resources?: CrisisResource[];
}
