import { create } from "zustand";
import { AuthUser } from "../types";

interface AuthState {
  user: AuthUser | null;
  hydrated: boolean;
  setSession: (user: AuthUser, accessToken: string, refreshToken?: string) => void;
  setHydrated: (user: AuthUser | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  hydrated: false,
  setSession: (user, accessToken, refreshToken) => {
    localStorage.setItem("learnsphere_access_token", accessToken);
    if (refreshToken) localStorage.setItem("learnsphere_refresh_token", refreshToken);
    set({ user });
  },
  setHydrated: (user) => set({ user, hydrated: true }),
  logout: () => {
    localStorage.removeItem("learnsphere_access_token");
    localStorage.removeItem("learnsphere_refresh_token");
    set({ user: null });
  },
}));
