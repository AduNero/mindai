export type ResourceType =
  | "article"
  | "video"
  | "podcast"
  | "meditation"
  | "breathing_exercise"
  | "emergency";

export interface ResourceCategory {
  id: string;
  name: string;
  slug: string;
  description: string;
}

export interface Resource {
  id: string;
  title: string;
  description: string;
  resource_type: ResourceType;
  category: ResourceCategory | null;
  body: string;
  external_url: string;
  thumbnail: string | null;
  duration_minutes: number | null;
  tags: string[];
  is_published: boolean;
  view_count: number;
  created_at: string;
}

export interface EmergencyResource {
  id: string;
  country_code: string;
  name: string;
  phone_number: string;
  sms_number: string;
  website: string;
  description: string;
  is_24_7: boolean;
  language: string;
}
