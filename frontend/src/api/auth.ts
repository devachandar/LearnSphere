import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import client from "./client";
import { useAuthStore } from "../store/auth";
import { AuthUser, Role } from "../types";

interface SessionResponse {
  user: AuthUser;
  accessToken: string;
  refreshToken: string;
}

export function useBootstrapAuth() {
  const setHydrated = useAuthStore((s) => s.setHydrated);
  const token = localStorage.getItem("learnsphere_access_token");

  return useQuery({
    queryKey: ["auth", "bootstrap"],
    queryFn: async () => {
      if (!token) {
        setHydrated(null);
        return null;
      }
      try {
        const res = await client.get<AuthUser>("/auth/me");
        setHydrated(res.data);
        return res.data;
      } catch {
        setHydrated(null);
        return null;
      }
    },
  });
}

export function useLogin() {
  const setSession = useAuthStore((s) => s.setSession);
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { email: string; password: string }) =>
      (await client.post<SessionResponse>("/auth/login", vars)).data,
    onSuccess: (data) => {
      setSession(data.user, data.accessToken, data.refreshToken);
      qc.invalidateQueries();
    },
  });
}

export interface RegisterPayload {
  email: string;
  password: string;
  fullName: string;
  role: Role;
  organizationName?: string;
  inviteCode?: string;
}

export function useRegister() {
  const setSession = useAuthStore((s) => s.setSession);
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (vars: RegisterPayload) => (await client.post<SessionResponse>("/auth/register", vars)).data,
    onSuccess: (data) => {
      setSession(data.user, data.accessToken, data.refreshToken);
      qc.invalidateQueries();
    },
  });
}

export function useLogout() {
  const logout = useAuthStore((s) => s.logout);
  return () => {
    const refreshToken = localStorage.getItem("learnsphere_refresh_token");
    client.post("/auth/logout", { refreshToken }).catch(() => {});
    logout();
  };
}

export function useOrganizationMembers() {
  return useQuery({
    queryKey: ["org-members"],
    queryFn: async () => (await client.get("/auth/organization/members")).data,
  });
}
