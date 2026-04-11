import { useEffect } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { DashboardPage } from './pages/DashboardPage';
import { TransactionsPage } from './pages/TransactionsPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { SettingsPage } from './pages/SettingsPage';
import { useTelegram } from './hooks/useTelegram';

export default function App() {
  const { tg } = useTelegram();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (!tg) return;
    const isRoot = location.pathname === '/';
    if (isRoot) {
      tg.BackButton?.hide();
    } else {
      tg.BackButton?.show();
      const handler = () => navigate(-1);
      tg.BackButton?.onClick(handler);
      return () => {
        tg.BackButton?.offClick(handler);
      };
    }
  }, [location.pathname, tg, navigate]);

  return (
    <div
      className="bg-bg-primary text-text-primary"
      style={{ height: '100dvh', overflow: 'hidden' }}
    >
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/transactions" element={<TransactionsPage />} />
        <Route path="/analytics/*" element={<AnalyticsPage />} />
        <Route path="/settings/*" element={<SettingsPage />} />
      </Routes>
    </div>
  );
}
