import DashboardPage from "./pages/DashboardPage/DashboardPage";
import { useTheme } from "./hooks/useTheme";

export default function App() {

  useTheme();

  return <DashboardPage />;
}
