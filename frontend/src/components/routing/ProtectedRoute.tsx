import { Navigate, useLocation } from "react-router-dom";
import { PropsWithChildren } from "react";
import { useAuth } from "@/contexts/AuthContext";

type ProtectedRouteProps = PropsWithChildren<{
  redirectTo?: string;
}>;

export default function ProtectedRoute({ children, redirectTo = "/auth/sign-in" }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    // Можно заменить на глобальный спиннер/скелетон
    return null;
  }

  if (!isAuthenticated) {
    const params = new URLSearchParams();
    params.set("next", location.pathname + location.search);
    return <Navigate to={`${redirectTo}?${params.toString()}`} replace />;
  }

  return <>{children}</>;
}
