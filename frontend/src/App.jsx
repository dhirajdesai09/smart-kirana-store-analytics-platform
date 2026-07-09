import { Navigate, Route, Routes } from "react-router-dom";

import AppLayout from "./layouts/AppLayout.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import Analytics from "./pages/Analytics.jsx";
import AuthPage from "./pages/AuthPage.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Inventory from "./pages/Inventory.jsx";
import Reports from "./pages/Reports.jsx";
import Sales from "./pages/Sales.jsx";
import Settings from "./pages/Settings.jsx";

export default function App() {
  return (
    <Routes>
      <Route path="/auth" element={<AuthPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="inventory" element={<Inventory />} />
        <Route path="sales" element={<Sales />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="reports" element={<Reports />} />
        <Route path="settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
