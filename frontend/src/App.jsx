import { Navigate, Route, Routes } from "react-router";

import { useTheme } from "./hooks/useTheme";
import AppLayout from "./layouts/AppLayout/AppLayout";
import DashboardPage from "./pages/DashboardPage/DashboardPage";
import SensorsPage from "./pages/SensorsPage/SensorsPage";
import HistoryPage from "./pages/HistoryPage/HistoryPage";

export default function App() {
  useTheme();

  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route
          index
          element={<Navigate to="/dashboard" replace />}
        />

        <Route
          path="/dashboard"
          element={<DashboardPage />}
        />

        <Route
          path="/sensors"
          element={<SensorsPage />}
        />

        <Route
          path="*"
          element={<Navigate to="/dashboard" replace />}
        />

        <Route
          path="/history"
          element={<HistoryPage />}
        />
        
      </Route>
    </Routes>
  );
}