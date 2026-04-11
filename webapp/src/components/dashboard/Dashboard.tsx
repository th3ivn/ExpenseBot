import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Settings, ChevronRight } from 'lucide-react';
import { BudgetRing } from './BudgetRing';
import { AnalyticsCards } from './AnalyticsCards';
import { RecentTransactions } from './RecentTransactions';
import { useBudget } from '../../hooks/useBudget';
import { useStats } from '../../hooks/useStats';
import { useTransactions } from '../../hooks/useTransactions';
import { api } from '../../api/client';
import { formatPeriod } from '../../utils/format';
import type { RecurringTransaction, Transaction } from '../../types';

interface DashboardProps {
  onSelectTransaction: (t: Transaction) => void;
}

export function Dashboard({ onSelectTransaction }: DashboardProps) {
  const { progress, loading: budgetLoading } = useBudget();
  const { trend, breakdown, savingsRate, loading: statsLoading } = useStats();
  const { transactions, loading: txLoading } = useTransactions({ limit: 10 });
  const [recurring, setRecurring] = useState<RecurringTransaction[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    api.recurring.list().then(setRecurring).catch(() => {});
  }, []);

  const periodLabel = progress
    ? formatPeriod(progress.period_start, progress.period_end)
    : '—';

  return (
    <div className="flex flex-col" style={{ minHeight: '100%' }}>
      {/* Sticky header */}
      <div
        className="sticky top-0 z-20 flex items-center justify-between px-4 pb-3 bg-bg-primary"
        style={{ paddingTop: 'max(12px, env(safe-area-inset-top))' }}
      >
        <button
          type="button"
          onClick={() => navigate('/settings/budget')}
          className="flex items-center gap-2 bg-bg-secondary rounded-full px-4 py-2 border border-white/10 active:opacity-70 transition-opacity"
        >
          <span className="text-text-primary text-sm font-semibold">{periodLabel}</span>
          <span className="w-2 h-2 rounded-full bg-accent-red flex-shrink-0" />
        </button>
        <button
          type="button"
          onClick={() => navigate('/settings')}
          className="w-10 h-10 rounded-full bg-bg-secondary flex items-center justify-center active:opacity-70 transition-opacity border border-white/10"
        >
          <Settings size={18} className="text-text-secondary" />
        </button>
      </div>

      {/* Content */}
      <div className="px-4 space-y-6 pb-28">
        <BudgetRing progress={progress} loading={budgetLoading} />

        <section>
          <h2 className="text-text-primary text-lg font-bold mb-3">Аналітика</h2>
          <AnalyticsCards
            trend={trend}
            breakdown={breakdown}
            savingsRate={savingsRate}
            recurring={recurring}
            loading={statsLoading}
          />
        </section>

        <section>
          <button
            type="button"
            onClick={() => navigate('/transactions')}
            className="flex items-center gap-1 mb-3 active:opacity-70 transition-opacity"
          >
            <h2 className="text-text-primary text-lg font-bold">Останні операції</h2>
            <ChevronRight size={20} className="text-text-secondary mt-0.5" />
          </button>
          <RecentTransactions
            transactions={transactions}
            loading={txLoading}
            onSelect={onSelectTransaction}
          />
        </section>
      </div>
    </div>
  );
}
