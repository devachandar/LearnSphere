import { ReactElement } from "react";
import { Navigate } from "react-router-dom";
import { useAuthStore } from "../store/auth";
import { Role } from "../types";

export default function RequireAuth({ roles, children }: { roles?: Role[]; children: ReactElement }) {
  const { user, hydrated } = useAuthStore();

  if (!hydrated) return null;
  if (!user) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(user.role)) return <Navigate to="/" replace />;

  return children;
}
