import { useState } from 'react';
import { useBudget } from '../../hooks/useBudget';
import { formatCurrency, formatPeriod } from '../../utils/format';

export function BudgetManager() {
  const { budget, progress, loading, setBudgetAmount } = useBudget();
  const [editing, setEditing] = useState(false);
  const [amount, setAmount] = useState('');
  const [startDay, setStartDay] = useState('1');
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    const num = parseFloat(amount.replace(',', '.'));
    if (!num || num <= 0) return;
    setSaving(true);
    try {
      await setBudgetAmount(num, parseInt(startDay, 10));
      setEditing(false);
    } catch (e) { /* ignore */ }
    finally { setSaving(false); }
  };

  if (loading) return <div className="h-32 animate-pulse bg-bg-secondary rounded-xl m-4" />;

  return (
    <div className="px-4 pb-8 space-y-4">
      {progress && (
        <div className="bg-bg-secondary rounded-xl p-4">
          <p className="text-text-secondary text-xs mb-2">
            Поточний період: {formatPeriod(progress.period_start, progress.period_end)}
          </p>
          <div className="grid grid-cols-3 gap-2">
            <div className="flex flex-col items-center bg-bg-tertiary rounded-lg p-2">
              <span className="text-text-secondary text-[10px]">Бюджет</span>
              <span className="text-text-primary font-semibold text-xs">{formatCurrency(progress.budget_amount)}</span>
            </div>
            <div className="flex flex-col items-center bg-bg-tertiary rounded-lg p-2">
              <span className="text-text-secondary text-[10px]">Розподілено</span>
              <span className="text-text-primary font-semibold text-xs">{formatCurrency(progress.distributed)}</span>
            </div>
            <div className="flex flex-col items-center bg-bg-tertiary rounded-lg p-2">
              <span className="text-text-secondary text-[10px]">Доступно</span>
              <span className={`font-semibold text-xs ${progress.available < 0 ? 'text-accent-red' : 'text-text-primary'}`}>
                {formatCurrency(Math.abs(progress.available))}
              </span>
            </div>
          </div>
        </div>
      )}

      {editing ? (
        <div className="bg-bg-secondary rounded-xl p-4 space-y-3">
          <div>
            <label className="text-text-secondary text-xs mb-1 block">Сума бюджету (₴)</label>
            <input
              type="number"
              placeholder={budget ? String(budget.amount) : '10000'}
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="w-full bg-bg-tertiary text-text-primary rounded-lg px-3 py-2.5 text-sm outline-none"
            />
          </div>
          <div>
            <label className="text-text-secondary text-xs mb-1 block">День початку періоду (1–28)</label>
            <input
              type="number"
              min={1}
              max={28}
              value={startDay}
              onChange={(e) => setStartDay(e.target.value)}
              className="w-full bg-bg-tertiary text-text-primary rounded-lg px-3 py-2.5 text-sm outline-none"
            />
          </div>
          <div className="flex gap-2">
            <button onClick={() => setEditing(false)} className="flex-1 py-2 rounded-lg bg-bg-tertiary text-text-secondary text-sm">Скасувати</button>
            <button onClick={handleSave} disabled={saving} className="flex-1 py-2 rounded-lg bg-accent-cyan text-bg-primary font-medium text-sm disabled:opacity-50">
              {saving ? '...' : 'Зберегти'}
            </button>
          </div>
        </div>
      ) : (
        <button
          onClick={() => {
            setAmount(budget ? String(budget.amount) : '');
            setStartDay(String(budget?.period_start_day ?? 1));
            setEditing(true);
          }}
          className="w-full py-3 rounded-xl bg-accent-cyan/10 text-accent-cyan font-medium text-sm"
        >
          {budget ? 'Змінити бюджет' : 'Встановити бюджет'}
        </button>
      )}
    </div>
  );
}
