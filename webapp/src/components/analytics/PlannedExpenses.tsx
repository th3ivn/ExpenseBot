import { CalendarClock } from 'lucide-react';
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
      <div className="space-y-3">
        {[0, 1, 2].map((i) => (
          <div key={i} className="h-16 bg-bg-secondary rounded-3xl animate-pulse" />
        ))}
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 bg-bg-secondary rounded-3xl gap-3">
        <CalendarClock size={40} className="text-bg-tertiary" />
        <p className="text-text-primary font-semibold">Немає запланованих витрат</p>
        <p className="text-text-secondary text-sm text-center px-6">
          Немає витрат, запланованих на цей період
        </p>
      </div>
    );
  }

  return (
    <div className="bg-bg-secondary rounded-3xl overflow-hidden">
      {data.map((r, idx) => (
        <div
          key={r.id}
          className={`flex items-center gap-3 px-4 py-3.5 ${
            idx < data.length - 1 ? 'border-b border-bg-tertiary' : ''
          }`}
        >
          <div
            className="w-11 h-11 rounded-full flex items-center justify-center text-xl flex-shrink-0"
            style={{ backgroundColor: r.category?.color ? `${r.category.color}33` : '#252B3B' }}
          >
            {r.category?.emoji ?? '🔄'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-text-primary text-sm font-medium truncate">
              {r.description ?? r.category?.name ?? 'Без назви'}
            </p>
            <p className="text-text-secondary text-xs mt-0.5">
              {FREQ_LABELS[r.frequency] ?? r.frequency} · {r.next_date.slice(0, 10)}
            </p>
          </div>
          <span className="text-accent-red font-semibold text-sm flex-shrink-0">
            −{formatCurrency(r.amount)}
          </span>
        </div>
      ))}
    </div>
  );
}
