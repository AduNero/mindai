import type { EmergencyResource, Paginated, Resource, ResourceCategory } from "@/types";

import { apiClient } from "./client";

export const resourcesApi = {
  list: (params?: Record<string, string | number>) =>
    apiClient.get<Paginated<Resource>>("/resources/", { params }),

  get: (id: string) => apiClient.get<Resource>(`/resources/${id}/`),

  categories: () => apiClient.get<Paginated<ResourceCategory>>("/resources/categories/"),

  emergency: () => apiClient.get<Paginated<EmergencyResource>>("/resources/emergency/"),

  admin: {
    list: (params?: Record<string, string | number>) =>
      apiClient.get<Paginated<Resource>>("/resources/admin/resources/", { params }),

    create: (formData: FormData) =>
      apiClient.post<Resource>("/resources/admin/resources/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      }),

    update: (id: string, formData: FormData) =>
      apiClient.patch<Resource>(`/resources/admin/resources/${id}/`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      }),

    remove: (id: string) => apiClient.delete(`/resources/admin/resources/${id}/`),

    listEmergency: () => apiClient.get<Paginated<EmergencyResource>>("/resources/admin/emergency/"),

    createEmergency: (payload: Partial<EmergencyResource>) =>
      apiClient.post<EmergencyResource>("/resources/admin/emergency/", payload),

    updateEmergency: (id: string, payload: Partial<EmergencyResource>) =>
      apiClient.patch<EmergencyResource>(`/resources/admin/emergency/${id}/`, payload),

    removeEmergency: (id: string) => apiClient.delete(`/resources/admin/emergency/${id}/`),
  },
};
