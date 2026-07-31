import type { User } from "@/types";

const USER_KEY = "mindcare_user";

export const userStorage = {
  get: (): User | null => {
    const raw = localStorage.getItem(USER_KEY);
    if (!raw) return null;
    try {
      return JSON.parse(raw) as User;
    } catch {
      return null;
    }
  },
  set: (user: User): void => {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },
  clear: (): void => {
    localStorage.removeItem(USER_KEY);
  },
};
