import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";
import type { AuthUser } from "@/lib/types";
import Login from "@/pages/Login";
import Workspace from "@/pages/Workspace";

// One <Route> per page in src/pages; BrowserRouter already wraps this in main.tsx.
export default function App() {
  const location = useLocation();
  const session = useQuery({ queryKey: ["me"], queryFn: () => apiGet<AuthUser>("/auth/me"), retry: false, staleTime: 60_000, enabled: location.pathname !== "/login" });

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/app/*" element={session.data ? <Workspace user={session.data} /> : <Navigate to="/login" replace />} />
      <Route path="*" element={<Navigate to={session.data ? "/app" : "/login"} replace />} />
    </Routes>
  );
}
