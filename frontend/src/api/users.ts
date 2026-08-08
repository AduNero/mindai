import type { AdminUser, Paginated, Profile } from "@/types";

import { apiClient } from "./client";

export const usersApi = {
  getMyProfile: () => apiClient.get<Profile>("/users/me/"),

  updateMyProfile: (payload: Partial<Profile>) => apiClient.patch<Profile>("/users/me/", payload),

  uploadProfilePicture: (file: File) => {
    const formData = new FormData();
    formData.append("profile_picture", file);
    return apiClient.post<Profile>("/users/me/picture/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  admin: {
    listUsers: (params?: Record<string, string | number>) =>
      apiClient.get<Paginated<AdminUser>>("/users/admin/list/", { params }),

    getUser: (id: string) => apiClient.get<AdminUser>(`/users/admin/${id}/`),

    updateUser: (id: string, payload: { role?: string; is_active?: boolean }) =>
      apiClient.patch<AdminUser>(`/users/admin/${id}/`, payload),

    deleteUser: (id: string) => apiClient.delete(`/users/admin/${id}/`),
  },
};
