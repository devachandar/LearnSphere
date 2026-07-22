import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import client from "./client";
import { Organization } from "../types";

export function useMyOrganization() {
  return useQuery({
    queryKey: ["organization", "me"],
    queryFn: async () => (await client.get<Organization>("/admin/organizations/me")).data,
  });
}

export function useOrganizations() {
  return useQuery({
    queryKey: ["organizations"],
    queryFn: async () => (await client.get<Organization[]>("/admin/organizations")).data,
  });
}

export function useSetOrgStatus() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { id: string; status: string }) =>
      (await client.patch(`/admin/organizations/${vars.id}/status`, { status: vars.status })).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["organizations"] }),
  });
}

export function useOrgAnalytics() {
  return useQuery({
    queryKey: ["analytics", "organization"],
    queryFn: async () => (await client.get("/analytics/organization")).data,
  });
}

export function usePlatformAnalytics() {
  return useQuery({
    queryKey: ["analytics", "platform"],
    queryFn: async () => (await client.get("/analytics/platform")).data,
  });
}

export function useCourseMetrics(courseId?: string) {
  return useQuery({
    queryKey: ["analytics", "course", courseId],
    queryFn: async () => (await client.get(`/analytics/courses/${courseId}`)).data,
    enabled: !!courseId,
  });
}

export function useSupportTickets() {
  return useQuery({
    queryKey: ["support-tickets"],
    queryFn: async () => (await client.get("/admin/support-tickets")).data,
  });
}

export function useCreateSupportTicket() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { subject: string; body: string }) =>
      (await client.post("/admin/support-tickets", vars)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["support-tickets"] }),
  });
}
