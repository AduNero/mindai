export type UserRole = "user" | "admin";

export interface User {
  id: string;
  email: string;
  pseudonym: string;
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
  timezone: string;
  theme_preference: "light" | "dark" | "system";
  created_at: string;
  updated_at: string;
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
