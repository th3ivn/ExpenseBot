import { useEffect, useState } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { TrendingUp, PieChart, CalendarClock, Banknote } from 'lucide-react';
import { TrendChart } from '../components/analytics/TrendChart';
import { ExpenseBreakdown } from '../components/analytics/ExpenseBreakdown';
import { SavingsRate } from '../components/analytics/SavingsRate';
import { PlannedExpenses } from '../components/analytics/PlannedExpenses';
import { useStats } from '../hooks/useStats';
import { api } from '../api/client';
import type { RecurringTransaction } from '../types';

const NAV_ITEMS = [
  { path: '/analytics',           label: 'Тренд',       icon: TrendingUp,    exact: true },
  { path: '/analytics/breakdown', label: 'Витрати',     icon: PieChart },
  { path: '/analytics/savings',   label: 'Збереження',  icon: Banknote },
  { path: '/analytics/planned',   label: 'Заплановані', icon: CalendarClock },
];

const TITLES: Record<string, string> = {
  '/analytics':           'Тренд витрат',
  '/analytics/breakdown': 'Деталізація витрат',
  '/analytics/savings':   'Норма збережень',
  '/analytics/planned':   'Заплановані витрати',
};

export function AnalyticsPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { trend, breakdown, savingsRate, loading } = useStats();
  const [recurring, setRecurring] = useState<RecurringTransaction[]>([]);
  const [rLoading, setRLoading] = useState(true);

  useEffect(() => {
    api.recurring
      .list()
      .then(setRecurring)
      .catch(() => {})
      .finally(() => setRLoading(false));
  }, []);

  const isActive = (path: string, exact?: boolean) =>
    exact ? location.pathname === path : location.pathname.startsWith(path);

  const title = TITLES[location.pathname] ?? 'Аналітика';

  return (
    <div className="flex flex-col bg-bg-primary" style={{ height: '100%' }}>
      {/* Header */}
      <div
        className="flex-shrink-0 px-4 pb-3 bg-bg-primary"
        style={{ paddingTop: 'max(12px, env(safe-area-inset-top))' }}
      >
        <h1 className="text-text-primary text-xl font-bold mb-3 text-center">{title}</h1>
        {/* Sub-nav */}
        <div className="flex gap-2 overflow-x-auto pb-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.path, item.exact);
            return (
              <button
                key={item.path}
                type="button"
                onClick={() => navigate(item.path)}
                className={`flex-shrink-0 flex items-center gap-1.5 px-3.5 py-2 rounded-full text-sm font-medium transition-colors ${
                  active
                    ? 'bg-accent-cyan text-bg-primary'
                    : 'bg-bg-secondary text-text-secondary'
                }`}
              >
                <Icon size={14} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 pb-8">
        <Routes>
          <Route index element={<TrendChart data={trend} loading={loading} />} />
          <Route path="breakdown" element={<ExpenseBreakdown data={breakdown} loading={loading} />} />
          <Route path="savings" element={<SavingsRate data={savingsRate} loading={loading} />} />
          <Route path="planned" element={<PlannedExpenses data={recurring} loading={rLoading} />} />
        </Routes>
      </div>
    </div>
  );
}
