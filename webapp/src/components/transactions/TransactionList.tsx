import { ChevronRight } from 'lucide-react';
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
      <div className="px-4 space-y-3">
        {Array.from({ length: 3 }).map((_, g) => (
          <div key={g}>
            <div className="h-4 w-24 bg-bg-secondary rounded mb-2 animate-pulse" />
            <div className="bg-bg-secondary rounded-3xl overflow-hidden">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="flex items-center gap-3 px-4 py-3.5 border-b border-bg-tertiary last:border-0">
                  <div className="w-11 h-11 rounded-full bg-bg-tertiary animate-pulse flex-shrink-0" />
                  <div className="flex-1 space-y-2">
                    <div className="h-3.5 bg-bg-tertiary rounded animate-pulse w-2/3" />
                    <div className="h-3 bg-bg-tertiary rounded animate-pulse w-1/4" />
                  </div>
                  <div className="h-4 w-16 bg-bg-tertiary rounded animate-pulse" />
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (transactions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-text-secondary">
        <span className="text-5xl mb-4">💸</span>
        <span className="text-sm">Транзакцій немає</span>
      </div>
    );
  }

  // Group by date
  const groups = new Map<string, Transaction[]>();
  for (const t of transactions) {
    const label = formatDate(t.date);
    if (!groups.has(label)) groups.set(label, []);
    groups.get(label)!.push(t);
  }

  return (
    <div className="px-4 pb-4 space-y-4">
      {Array.from(groups.entries()).map(([dateLabel, items]) => (
        <div key={dateLabel}>
          <p className="text-text-secondary text-xs font-medium mb-2 px-1">{dateLabel}</p>
          <div className="bg-bg-secondary rounded-3xl overflow-hidden">
            {items.map((t, idx) => (
              <button
                key={t.id}
                type="button"
                onClick={() => onSelect(t)}
                className={`w-full flex items-center gap-3 px-4 py-3.5 active:bg-bg-elevated transition-colors text-left ${
                  idx < items.length - 1 ? 'border-b border-bg-tertiary' : ''
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
                  <div className="text-text-secondary text-xs mt-0.5 truncate">
                    {t.category?.name ??
                      (t.type === 'transfer'
                        ? 'Переказ'
                        : t.type === 'income'
                          ? 'Дохід'
                          : 'Витрата')}
                  </div>
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
        </div>
      ))}
    </div>
  );
}
