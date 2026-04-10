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

const TYPE_SIGNS = {
  expense: '−',
  income: '+',
  transfer: '⇄',
};

export function RecentTransactions({ transactions, loading, onSelect }: RecentTransactionsProps) {
  if (loading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-14 bg-bg-secondary rounded-xl animate-pulse" />
        ))}
      </div>
    );
  }

  if (transactions.length === 0) {
    return (
      <div className="text-center py-8 text-text-secondary text-sm">
        Транзакцій ще немає
      </div>
    );
  }

  return (
    <div className="space-y-1">
      {transactions.slice(0, 10).map((t) => (
        <button
          key={t.id}
          onClick={() => onSelect(t)}
          className="w-full flex items-center gap-3 px-3 py-2.5 bg-bg-secondary rounded-xl active:bg-bg-tertiary transition-colors text-left"
        >
          <div className="w-9 h-9 rounded-full bg-bg-tertiary flex items-center justify-center text-lg flex-shrink-0">
            {t.category?.emoji ?? '💸'}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-text-primary text-sm font-medium truncate">
              {t.merchant ?? t.description ?? t.category?.name ?? 'Без назви'}
            </div>
            <div className="text-text-secondary text-xs">{formatDate(t.date)}</div>
          </div>
          <span className={`font-semibold text-sm ${TYPE_COLORS[t.type]}`}>
            {TYPE_SIGNS[t.type]} {formatCurrency(t.amount)}
          </span>
        </button>
      ))}
    </div>
  );
}
