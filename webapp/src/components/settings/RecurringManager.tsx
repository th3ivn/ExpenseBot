import { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { formatCurrency } from '../../utils/format';
import type { RecurringTransaction } from '../../types';

const FREQ_LABELS: Record<string, string> = {
  daily: 'Щодня',
  weekly: 'Щотижня',
  monthly: 'Щомісяця',
  yearly: 'Щороку',
};

export function RecurringManager() {
  const [items, setItems] = useState<RecurringTransaction[]>([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    api.recurring
      .list()
      .then(setItems)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleDelete = async (id: number) => {
    await api.recurring.delete(id).catch(() => {});
    setItems((prev) => prev.filter((r) => r.id !== id));
  };

  const handleToggle = async (r: RecurringTransaction) => {
    const updated = await api.recurring.update(r.id, { is_active: !r.is_active }).catch(() => null);
    if (updated) setItems((prev) => prev.map((x) => (x.id === r.id ? updated : x)));
  };

  if (loading) return <div className="h-32 animate-pulse bg-bg-secondary rounded-xl m-4" />;

  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-text-secondary px-4">
        <span className="text-4xl mb-3">🔄</span>
        <p className="text-sm">Немає регулярних транзакцій</p>
        <p className="text-xs mt-1 text-center">Додайте транзакцію та встановіть повтор</p>
      </div>
    );
  }

  return (
    <div className="px-4 pb-8 space-y-1">
      {items.map((r) => (
        <div key={r.id} className="flex items-center gap-3 px-3 py-3 bg-bg-secondary rounded-xl">
          <div className="w-10 h-10 rounded-full bg-bg-tertiary flex items-center justify-center text-xl flex-shrink-0">
            {r.category?.emoji ?? '🔄'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-text-primary text-sm font-medium truncate">
              {r.description ?? r.category?.name ?? 'Без назви'}
            </p>
            <p className="text-text-secondary text-xs">
              {FREQ_LABELS[r.frequency]} • {r.next_date.slice(0, 10)}
            </p>
          </div>
          <span className="text-accent-red font-semibold text-sm mr-2">{formatCurrency(r.amount)}</span>
          <button
            onClick={() => handleToggle(r)}
            className={`w-10 h-6 rounded-full transition-colors flex-shrink-0 ${r.is_active ? 'bg-accent-cyan' : 'bg-bg-tertiary'}`}
          >
            <div className={`w-4 h-4 rounded-full bg-white mx-auto transition-transform ${r.is_active ? 'translate-x-2' : '-translate-x-1'}`} />
          </button>
          <button onClick={() => handleDelete(r.id)} className="text-accent-red text-sm ml-1">✕</button>
        </div>
      ))}
    </div>
  );
}
