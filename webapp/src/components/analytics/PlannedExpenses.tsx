import { formatCurrency } from '../../utils/format';
import type { RecurringTransaction } from '../../types';

interface PlannedExpensesProps {
  data: RecurringTransaction[];
  loading: boolean;
}

const FREQ_LABELS: Record<string, string> = {
  daily: 'Щодня',
  weekly: 'Щотижня',
  monthly: 'Щомісяця',
  yearly: 'Щороку',
};

export function PlannedExpenses({ data, loading }: PlannedExpensesProps) {
  if (loading) {
    return (
      <div className="space-y-2">
        {[0, 1, 2].map((i) => (
          <div key={i} className="h-16 bg-bg-secondary rounded-xl animate-pulse" />
        ))}
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 bg-bg-secondary rounded-2xl">
        <span className="text-4xl mb-3">📋</span>
        <p className="text-text-secondary text-sm">Немає запланованих витрат</p>
      </div>
    );
  }

  return (
    <div className="space-y-1">
      {data.map((r) => (
        <div
          key={r.id}
          className="flex items-center gap-3 px-3 py-3 bg-bg-secondary rounded-xl"
        >
          <div className="w-10 h-10 rounded-full bg-bg-tertiary flex items-center justify-center text-xl flex-shrink-0">
            {r.category?.emoji ?? '🔄'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-text-primary text-sm font-medium truncate">
              {r.description ?? r.category?.name ?? 'Без назви'}
            </p>
            <p className="text-text-secondary text-xs">
              {FREQ_LABELS[r.frequency] ?? r.frequency} • {r.next_date.slice(0, 10)}
            </p>
          </div>
          <span className="text-accent-red font-semibold text-sm">{formatCurrency(r.amount)}</span>
        </div>
      ))}
    </div>
  );
}
