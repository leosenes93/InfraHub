import { Route, Routes } from "react-router-dom";

import { AppLayout } from "@/components/layout/AppLayout";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { AssetDetail } from "@/pages/AssetDetail";
import { AuditLog } from "@/pages/AuditLog";
import { Dashboard } from "@/pages/Dashboard";
import { DockerContainers } from "@/pages/DockerContainers";
import { Inventory } from "@/pages/Inventory";
import { Login } from "@/pages/Login";

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Dashboard />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/inventory"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Inventory />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/inventory/:assetId"
        element={
          <ProtectedRoute>
            <AppLayout>
              <AssetDetail />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/docker"
        element={
          <ProtectedRoute>
            <AppLayout>
              <DockerContainers />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/audit"
        element={
          <ProtectedRoute>
            <AppLayout>
              <AuditLog />
            </AppLayout>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}
