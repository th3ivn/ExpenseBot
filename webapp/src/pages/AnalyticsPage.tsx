import { useEffect, useState } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { TrendChart } from '../components/analytics/TrendChart';
import { ExpenseBreakdown } from '../components/analytics/ExpenseBreakdown';
import { SavingsRate } from '../components/analytics/SavingsRate';
import { PlannedExpenses } from '../components/analytics/PlannedExpenses';
import { useStats } from '../hooks/useStats';
import { api } from '../api/client';
import type { RecurringTransaction } from '../types';

const NAV_ITEMS = [
  { path: '/analytics', label: '📈 Тренд', exact: true },
  { path: '/analytics/breakdown', label: '🕐 Витрати' },
  { path: '/analytics/savings', label: '📊 Збереження' },
  { path: '/analytics/planned', label: '📋 Заплановані' },
];

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

  const active = (path: string, exact?: boolean) =>
    exact ? location.pathname === path : location.pathname.startsWith(path);

  return (
    <div className="flex flex-col h-full">
      {/* Sub-nav */}
      <div className="flex gap-1 overflow-x-auto px-4 pt-4 pb-2 flex-shrink-0">
        {NAV_ITEMS.map((item) => (
          <button
            key={item.path}
            onClick={() => navigate(item.path)}
            className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
              active(item.path, item.exact)
                ? 'bg-accent-cyan text-bg-primary'
                : 'bg-bg-secondary text-text-secondary'
            }`}
          >
            {item.label}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto px-4 pb-4">
        <Routes>
          <Route
            index
            element={<TrendChart data={trend} loading={loading} />}
          />
          <Route
            path="breakdown"
            element={<ExpenseBreakdown data={breakdown} loading={loading} />}
          />
          <Route
            path="savings"
            element={<SavingsRate data={savingsRate} loading={loading} />}
          />
          <Route
            path="planned"
            element={<PlannedExpenses data={recurring} loading={rLoading} />}
          />
        </Routes>
      </div>
    </div>
  );
}
