import { Navigate, Route, Routes } from "react-router-dom";
import { AppLayout } from "./layout/AppLayout";
import { DashboardPage } from "./pages/DashboardPage";
import { IdeationPage } from "./pages/IdeationPage";
import { ExecutePage } from "./pages/ExecutePage";
import { StatusPage } from "./pages/StatusPage";
import { ReviewPage } from "./pages/ReviewPage";
import { VaultPage } from "./pages/VaultPage";
import { SettingsPage } from "./pages/SettingsPage";
import { LogsPage } from "./pages/LogsPage";
import { LibraryPage } from "./pages/LibraryPage";

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
    </AppLayout>
  );
}

