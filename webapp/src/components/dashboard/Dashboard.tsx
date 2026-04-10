import { useState, useEffect } from 'react';
import { BudgetRing } from './BudgetRing';
import { AnalyticsCards } from './AnalyticsCards';
import { RecentTransactions } from './RecentTransactions';
import { useBudget } from '../../hooks/useBudget';
import { useStats } from '../../hooks/useStats';
import { useTransactions } from '../../hooks/useTransactions';
import { api } from '../../api/client';
import type { RecurringTransaction, Transaction } from '../../types';

interface DashboardProps {
  onSelectTransaction: (t: Transaction) => void;
}

export function Dashboard({ onSelectTransaction }: DashboardProps) {
  const { progress, loading: budgetLoading } = useBudget();
  const { trend, breakdown, savingsRate, loading: statsLoading } = useStats();
  const { transactions, loading: txLoading } = useTransactions({ limit: 10 });
  const [recurring, setRecurring] = useState<RecurringTransaction[]>([]);

  useEffect(() => {
    api.recurring.list().then(setRecurring).catch(() => {});
  }, []);

  return (
    <div className="space-y-5">
      <BudgetRing progress={progress} loading={budgetLoading} />

      <section>
        <h2 className="text-text-secondary text-xs font-medium uppercase tracking-wide mb-3 px-1">
          Аналітика
        </h2>
        <AnalyticsCards
          trend={trend}
          breakdown={breakdown}
          savingsRate={savingsRate}
          recurring={recurring}
          loading={statsLoading}
        />
      </section>

      <section>
        <h2 className="text-text-secondary text-xs font-medium uppercase tracking-wide mb-3 px-1">
          Останні транзакції
        </h2>
        <RecentTransactions
          transactions={transactions}
          loading={txLoading}
          onSelect={onSelectTransaction}
        />
      </section>
    </div>
  );
}
