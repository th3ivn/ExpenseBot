import { formatCurrency, formatDate } from '../../utils/format';
import type { Transaction } from '../../types';

interface TransactionListProps {
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

export function TransactionList({ transactions, loading, onSelect }: TransactionListProps) {
  if (loading) {
    return (
      <div className="space-y-1 px-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="h-16 bg-bg-secondary rounded-xl animate-pulse" />
        ))}
      </div>
    );
  }

  if (transactions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-text-secondary">
        <span className="text-4xl mb-3">📭</span>
        <span className="text-sm">Транзакцій немає</span>
      </div>
    );
  }

  let lastDate = '';

  return (
    <div className="px-4 pb-4">
      {transactions.map((t) => {
        const dateLabel = formatDate(t.date);
        const showDate = dateLabel !== lastDate;
        lastDate = dateLabel;

        return (
          <div key={t.id}>
            {showDate && (
              <div className="text-text-secondary text-xs font-medium py-2 px-1">{dateLabel}</div>
            )}
            <button
              onClick={() => onSelect(t)}
              className="w-full flex items-center gap-3 px-3 py-3 bg-bg-secondary rounded-xl mb-1 active:bg-bg-tertiary transition-colors text-left"
            >
              <div className="w-10 h-10 rounded-full bg-bg-tertiary flex items-center justify-center text-xl flex-shrink-0">
                {t.category?.emoji ?? '💸'}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-text-primary text-sm font-medium truncate">
                  {t.merchant ?? t.description ?? t.category?.name ?? 'Без назви'}
                </div>
                <div className="text-text-secondary text-xs truncate">
                  {t.category?.name ?? (t.type === 'transfer' ? 'Переказ' : t.type === 'income' ? 'Дохід' : 'Витрата')}
                </div>
              </div>
              <span className={`font-semibold text-sm ${TYPE_COLORS[t.type]}`}>
                {TYPE_SIGNS[t.type]} {formatCurrency(t.amount)}
              </span>
            </button>
          </div>
        );
      })}
    </div>
  );
}
