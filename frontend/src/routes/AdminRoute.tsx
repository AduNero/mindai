import { Navigate, Outlet } from "react-router-dom";

import { FullPageSpinner } from "@/components/common/Spinner";
import { useAuth } from "@/context/AuthContext";

export function AdminRoute() {
  const { user, isLoading } = useAuth();

  if (isLoading) return <FullPageSpinner />;

  if (!user || user.role !== "admin") {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}
