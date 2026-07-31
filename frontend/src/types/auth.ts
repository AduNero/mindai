export type UserRole = "user" | "admin" | "counselor";

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: UserRole;
  is_email_verified: boolean;
  created_at: string;
}

export interface AdminUser extends User {
  is_active: boolean;
  is_locked: boolean;
  last_login: string | null;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface Profile {
  id: string;
  user: User;
  profile_picture: string | null;
  bio: string;
  date_of_birth: string | null;
  gender: string;
  phone_number: string;
  country_code: string;
  timezone: string;
  emergency_contact_name: string;
  emergency_contact_phone: string;
  theme_preference: "light" | "dark" | "system";
  created_at: string;
  updated_at: string;
}

export interface CounselorProfile {
  id: string;
  user: User;
  specialization: string;
  license_number: string;
  years_of_experience: number;
  bio: string;
  is_accepting_appointments: boolean;
  approved_by_admin: boolean;
  created_at: string;
}

export interface UserSession {
  id: string;
  device_label: string;
  ip_address: string | null;
  remember_me: boolean;
  created_at: string;
  expires_at: string;
  revoked_at: string | null;
  is_active: boolean;
}
