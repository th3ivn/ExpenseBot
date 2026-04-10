import { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { formatCurrency } from '../../utils/format';
import type { Account } from '../../types';

export function AccountManager() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [name, setName] = useState('');
  const [emoji, setEmoji] = useState('💳');
  const [balance, setBalance] = useState('');
  const [saving, setSaving] = useState(false);

  const load = () => {
    setLoading(true);
    api.accounts
      .list()
      .then(setAccounts)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleAdd = async () => {
    if (!name) return;
    setSaving(true);
    try {
      await api.accounts.create({
        name,
        emoji,
        opening_balance: parseFloat(balance) || 0,
      });
      setName(''); setEmoji('💳'); setBalance(''); setShowAdd(false);
      load();
    } catch (e) { /* ignore */ }
    finally { setSaving(false); }
  };

  const handleDelete = async (id: number) => {
    await api.accounts.delete(id).catch(() => {});
    setAccounts((prev) => prev.filter((a) => a.id !== id));
  };

  if (loading) return <div className="h-32 animate-pulse bg-bg-secondary rounded-xl m-4" />;

  return (
    <div className="px-4 pb-8">
      <div className="space-y-1 mb-4">
        {accounts.map((a) => (
          <div key={a.id} className="flex items-center gap-3 px-3 py-3 bg-bg-secondary rounded-xl">
            <span className="text-2xl">{a.emoji}</span>
            <div className="flex-1">
              <p className="text-text-primary text-sm font-medium">{a.name}</p>
              <p className="text-text-secondary text-xs">
                Баланс: {formatCurrency(a.current_balance)}
              </p>
            </div>
            <button
              onClick={() => handleDelete(a.id)}
              className="text-accent-red text-sm"
            >
              ✕
            </button>
          </div>
        ))}
      </div>

      {showAdd ? (
        <div className="bg-bg-secondary rounded-xl p-4 space-y-3">
          <div className="grid grid-cols-2 gap-2">
            <input
              placeholder="Emoji"
              value={emoji}
              onChange={(e) => setEmoji(e.target.value)}
              className="bg-bg-tertiary text-text-primary rounded-lg px-3 py-2 text-sm outline-none"
            />
            <input
              placeholder="Назва"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="bg-bg-tertiary text-text-primary rounded-lg px-3 py-2 text-sm outline-none"
            />
          </div>
          <input
            type="number"
            placeholder="Початковий баланс"
            value={balance}
            onChange={(e) => setBalance(e.target.value)}
            className="w-full bg-bg-tertiary text-text-primary rounded-lg px-3 py-2 text-sm outline-none"
          />
          <div className="flex gap-2">
            <button onClick={() => setShowAdd(false)} className="flex-1 py-2 rounded-lg bg-bg-tertiary text-text-secondary text-sm">Скасувати</button>
            <button onClick={handleAdd} disabled={saving} className="flex-1 py-2 rounded-lg bg-accent-cyan text-bg-primary font-medium text-sm disabled:opacity-50">
              {saving ? '...' : 'Додати'}
            </button>
          </div>
        </div>
      ) : (
        <button
          onClick={() => setShowAdd(true)}
          className="w-full py-3 rounded-xl border border-dashed border-bg-tertiary text-text-secondary text-sm"
        >
          + Додати рахунок
        </button>
      )}
    </div>
  );
}
