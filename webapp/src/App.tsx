import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { useEffect } from 'react';
import { DashboardPage } from './pages/DashboardPage';
import { TransactionsPage } from './pages/TransactionsPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { SettingsPage } from './pages/SettingsPage';
import { useTelegram } from './hooks/useTelegram';

const NAV_TABS = [
  { path: '/', label: 'Дашборд', icon: '🏠' },
  { path: '/transactions', label: 'Транзакції', icon: '💳' },
  { path: '/analytics', label: 'Аналітика', icon: '📊' },
  { path: '/settings', label: 'Налаштування', icon: '⚙️' },
];

export default function App() {
  const { tg } = useTelegram();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (tg) {
      tg.ready();
      tg.expand();
    }
  }, [tg]);

  const isActive = (path: string) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  return (
    <div className="flex flex-col bg-bg-primary text-text-primary" style={{ height: '100dvh' }}>
      <div className="flex-1 overflow-y-auto">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/transactions" element={<TransactionsPage />} />
          <Route path="/analytics/*" element={<AnalyticsPage />} />
          <Route path="/settings/*" element={<SettingsPage />} />
        </Routes>
      </div>

      <nav className="flex-shrink-0 flex items-center border-t border-bg-tertiary bg-bg-secondary">
        {NAV_TABS.map((tab) => (
          <button
            key={tab.path}
            onClick={() => navigate(tab.path)}
            className={`flex-1 flex flex-col items-center justify-center py-2.5 gap-0.5 transition-colors ${
              isActive(tab.path) ? 'text-accent-cyan' : 'text-text-secondary'
            }`}
          >
            <span className="text-xl leading-none">{tab.icon}</span>
            <span className="text-[10px] leading-none">{tab.label}</span>
          </button>
        ))}
      </nav>
    </div>
  );
}
