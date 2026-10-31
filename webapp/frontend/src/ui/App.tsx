import { Navigate, Route, Routes } from "react-router-dom";
import FloatingChat from "./components/FloatingChat";
import { AppLayout } from "./layout/AppLayout";
import { DashboardPage } from "./pages/DashboardPage";
import { ExecutePage } from "./pages/ExecutePage";
import { IdeationPage } from "./pages/IdeationPage";
import { LibraryPage } from "./pages/LibraryPage";
import { LogsPage } from "./pages/LogsPage";
import { ReviewPage } from "./pages/ReviewPage";
import { SettingsPage } from "./pages/SettingsPage";
import { StatusPage } from "./pages/StatusPage";
import { VaultPage } from "./pages/VaultPage";

export function App() {
  return (
    <AppLayout>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/ideation" element={<IdeationPage />} />
        <Route path="/execute" element={<ExecutePage />} />
        <Route path="/status" element={<StatusPage />} />
        <Route path="/review" element={<ReviewPage />} />
        <Route path="/vault" element={<VaultPage />} />
        <Route path="/library" element={<LibraryPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/logs" element={<LogsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <FloatingChat />
    </AppLayout>
  );
}
