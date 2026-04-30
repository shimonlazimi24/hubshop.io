import { Navigate, Route, Routes } from "react-router-dom";
import { AuthLayout } from "./layouts/AuthLayout";
import { DashboardLayout } from "./layouts/DashboardLayout";
import { ConnectShopPage } from "./pages/ConnectShopPage";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { SettingsPage } from "./pages/SettingsPage";
import { ShopResultPage } from "./pages/ShopResultPage";
import { ShopDetailPage } from "./pages/ShopDetailPage";
import { ShopStatusPage } from "./pages/ShopStatusPage";
import { WorkspacePickPage } from "./pages/WorkspacePickPage";

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<AuthLayout />}>
        <Route index element={<LoginPage />} />
      </Route>
      <Route path="/register" element={<AuthLayout />}>
        <Route index element={<RegisterPage />} />
      </Route>

      <Route path="/" element={<DashboardLayout />}>
        <Route index element={<HomePage />} />
        <Route path="workspace" element={<WorkspacePickPage />} />
        <Route path="connect/shop" element={<ConnectShopPage />} />
        <Route path="connect/shop/result" element={<ShopResultPage />} />
        <Route path="shops" element={<ShopStatusPage />} />
        <Route path="shops/:shopId" element={<ShopDetailPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
