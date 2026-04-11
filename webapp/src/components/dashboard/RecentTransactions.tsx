import { ChevronRight } from 'lucide-react';
import { formatCurrency, formatDate } from '../../utils/format';
import type { Transaction } from '../../types';

interface RecentTransactionsProps {
  transactions: Transaction[];
  loading: boolean;
  onSelect: (t: Transaction) => void;
}

const TYPE_COLORS = {
  expense: 'text-accent-red',
  income: 'text-accent-green',
  transfer: 'text-accent-blue',
};
const TYPE_SIGNS = { expense: '−', income: '+', transfer: '⇄' };

export function RecentTransactions({ transactions, loading, onSelect }: RecentTransactionsProps) {
  if (loading) {
    return (
      <div className="bg-bg-secondary rounded-3xl overflow-hidden">
        {Array.from({ length: 4 }).map((_, i) => (
          <div
            key={i}
            className="flex items-center gap-3 px-4 py-3.5 border-b border-bg-tertiary last:border-0"
          >
            <div className="w-11 h-11 rounded-full bg-bg-tertiary animate-pulse flex-shrink-0" />
            <div className="flex-1 space-y-2">
              <div className="h-3.5 bg-bg-tertiary rounded animate-pulse w-3/4" />
              <div className="h-3 bg-bg-tertiary rounded animate-pulse w-1/3" />
            </div>
            <div className="h-4 w-16 bg-bg-tertiary rounded animate-pulse" />
          </div>
        ))}
      </div>
    );
  }

  if (transactions.length === 0) {
    return (
      <div className="bg-bg-secondary rounded-3xl flex items-center justify-center py-10">
        <p className="text-text-secondary text-sm">Транзакцій ще немає</p>
      </div>
    );
  }

  return (
    <div className="bg-bg-secondary rounded-3xl overflow-hidden">
      {transactions.slice(0, 8).map((t, idx) => (
        <button
          key={t.id}
          type="button"
          onClick={() => onSelect(t)}
          className={`w-full flex items-center gap-3 px-4 py-3.5 active:bg-bg-elevated transition-colors text-left ${
            idx < Math.min(transactions.length, 8) - 1 ? 'border-b border-bg-tertiary' : ''
          }`}
        >
          <div
            className="w-11 h-11 rounded-full flex items-center justify-center text-xl flex-shrink-0"
            style={{ backgroundColor: t.category?.color ? `${t.category.color}33` : '#252B3B' }}
          >
            {t.category?.emoji ?? '💸'}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-text-primary text-sm font-medium truncate">
              {t.merchant ?? t.description ?? t.category?.name ?? 'Без назви'}
            </div>
            <div className="text-text-secondary text-xs mt-0.5">{formatDate(t.date)}</div>
          </div>
          <div className="flex items-center gap-1.5 flex-shrink-0">
            <span className={`font-semibold text-sm ${TYPE_COLORS[t.type]}`}>
              {TYPE_SIGNS[t.type]}{formatCurrency(t.amount)}
            </span>
            <ChevronRight size={14} className="text-bg-tertiary" />
          </div>
        </button>
      ))}
    </div>
  );
}
