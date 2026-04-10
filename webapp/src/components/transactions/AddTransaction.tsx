import { useState, useEffect } from 'react';
import { BottomSheet } from '../ui/BottomSheet';
import { TabSwitcher } from '../ui/TabSwitcher';
import { api } from '../../api/client';
import type { Category, Account, Tag, TransactionType, RecurringFrequency } from '../../types';

interface AddTransactionProps {
  isOpen: boolean;
  onClose: () => void;
  onAdded: () => void;
}

const TABS = [
  { id: 'expense', label: 'Витрата' },
  { id: 'income', label: 'Дохід' },
  { id: 'transfer', label: 'Переказ' },
];

const REPEAT_OPTIONS: Array<{ value: RecurringFrequency | 'never'; label: string }> = [
  { value: 'never', label: 'Ніколи' },
  { value: 'daily', label: 'Щодня' },
  { value: 'weekly', label: 'Щотижня' },
  { value: 'monthly', label: 'Щомісяця' },
  { value: 'yearly', label: 'Щороку' },
];

function toLocalDateTimeString(date: Date) {
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

export function AddTransaction({ isOpen, onClose, onAdded }: AddTransactionProps) {
  const [tab, setTab] = useState<TransactionType>('expense');
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  const [merchant, setMerchant] = useState('');
  const [categoryId, setCategoryId] = useState<number | null>(null);
  const [accountId, setAccountId] = useState<number | null>(null);
  const [toAccountId, setToAccountId] = useState<number | null>(null);
  const [date, setDate] = useState(toLocalDateTimeString(new Date()));
  const [tagIds, setTagIds] = useState<number[]>([]);
  const [repeat, setRepeat] = useState<RecurringFrequency | 'never'>('never');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const [categories, setCategories] = useState<Category[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);

  useEffect(() => {
    if (!isOpen) return;
    Promise.all([api.categories.list(), api.accounts.list(), api.tags.list()])
      .then(([cats, accs, tgs]) => {
        setCategories(cats);
        setAccounts(accs);
        setTags(tgs);
        if (!accountId && accs.length > 0) setAccountId(accs[0].id);
      })
      .catch(() => {});
  }, [isOpen]); // eslint-disable-line react-hooks/exhaustive-deps

  const reset = () => {
    setAmount('');
    setDescription('');
    setMerchant('');
    setCategoryId(null);
    setToAccountId(null);
    setDate(toLocalDateTimeString(new Date()));
    setTagIds([]);
    setRepeat('never');
    setError('');
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  const handleSubmit = async () => {
    const num = parseFloat(amount.replace(',', '.'));
    if (!num || num <= 0) { setError('Введіть суму'); return; }
    if (!accountId) { setError('Оберіть рахунок'); return; }
    if (tab === 'transfer' && !toAccountId) { setError('Оберіть рахунок отримувача'); return; }

    setSaving(true);
    setError('');
    try {
      await api.transactions.create({
        type: tab,
        amount: num,
        description: description || undefined,
        merchant: merchant || undefined,
        category_id: categoryId ?? undefined,
        account_id: accountId,
        to_account_id: toAccountId ?? undefined,
        date: new Date(date).toISOString(),
        tag_ids: tagIds.length > 0 ? tagIds : undefined,
        recurring_frequency: repeat !== 'never' ? repeat : undefined,
      });
      onAdded();
      handleClose();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Помилка');
    } finally {
      setSaving(false);
    }
  };

  const amountColor =
    tab === 'expense' ? 'text-accent-red' : tab === 'income' ? 'text-accent-green' : 'text-accent-blue';

  return (
    <BottomSheet isOpen={isOpen} onClose={handleClose} title="Нова транзакція" fullHeight>
      <div className="px-4 pb-8 flex flex-col gap-4">
        <TabSwitcher
          tabs={TABS}
          active={tab}
          onChange={(id) => setTab(id as TransactionType)}
          className="mt-2"
        />

        {/* Amount */}
        <div className="flex items-center gap-2 bg-bg-tertiary rounded-xl px-4 py-3">
          <span className={`text-2xl font-bold ${amountColor}`}>₴</span>
          <input
            type="number"
            inputMode="decimal"
            placeholder="0.00"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className={`flex-1 bg-transparent text-2xl font-bold outline-none ${amountColor} placeholder-bg-tertiary`}
          />
        </div>

        {/* Category (not for transfer) */}
        {tab !== 'transfer' && (
          <div>
            <label className="text-text-secondary text-xs mb-2 block">Категорія</label>
            <div className="flex flex-wrap gap-2">
              {categories.map((c) => (
                <button
                  key={c.id}
                  onClick={() => setCategoryId(c.id === categoryId ? null : c.id)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm border transition-colors ${
                    categoryId === c.id
                      ? 'border-accent-cyan bg-accent-cyan/10 text-accent-cyan'
                      : 'border-bg-tertiary text-text-secondary'
                  }`}
                >
                  <span>{c.emoji}</span>
                  <span>{c.name}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Date */}
        <div>
          <label className="text-text-secondary text-xs mb-2 block">Дата і час</label>
          <input
            type="datetime-local"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="w-full bg-bg-tertiary text-text-primary rounded-xl px-4 py-3 text-sm outline-none"
          />
        </div>

        {/* Account */}
        <div>
          <label className="text-text-secondary text-xs mb-2 block">
            {tab === 'transfer' ? 'З рахунку' : 'Рахунок'}
          </label>
          <div className="flex gap-2 overflow-x-auto pb-1">
            {accounts.map((a) => (
              <button
                key={a.id}
                onClick={() => setAccountId(a.id)}
                className={`flex-shrink-0 flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm border transition-colors ${
                  accountId === a.id
                    ? 'border-accent-cyan bg-accent-cyan/10 text-accent-cyan'
                    : 'border-bg-tertiary text-text-secondary'
                }`}
              >
                <span>{a.emoji}</span>
                <span>{a.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* To account (transfer only) */}
        {tab === 'transfer' && (
          <div>
            <label className="text-text-secondary text-xs mb-2 block">На рахунок</label>
            <div className="flex gap-2 overflow-x-auto pb-1">
              {accounts
                .filter((a) => a.id !== accountId)
                .map((a) => (
                  <button
                    key={a.id}
                    onClick={() => setToAccountId(a.id)}
                    className={`flex-shrink-0 flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm border transition-colors ${
                      toAccountId === a.id
                        ? 'border-accent-blue bg-accent-blue/10 text-accent-blue'
                        : 'border-bg-tertiary text-text-secondary'
                    }`}
                  >
                    <span>{a.emoji}</span>
                    <span>{a.name}</span>
                  </button>
                ))}
            </div>
          </div>
        )}

        {/* Description */}
        <div>
          <label className="text-text-secondary text-xs mb-2 block">Опис (необов'язково)</label>
          <input
            type="text"
            placeholder="Коментар..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full bg-bg-tertiary text-text-primary rounded-xl px-4 py-3 text-sm outline-none placeholder-text-secondary"
          />
        </div>

        {/* Merchant */}
        {tab === 'expense' && (
          <div>
            <label className="text-text-secondary text-xs mb-2 block">Продавець (необов'язково)</label>
            <input
              type="text"
              placeholder="Назва магазину..."
              value={merchant}
              onChange={(e) => setMerchant(e.target.value)}
              className="w-full bg-bg-tertiary text-text-primary rounded-xl px-4 py-3 text-sm outline-none placeholder-text-secondary"
            />
          </div>
        )}

        {/* Tags */}
        {tags.length > 0 && (
          <div>
            <label className="text-text-secondary text-xs mb-2 block">Теги</label>
            <div className="flex flex-wrap gap-2">
              {tags.map((tag) => (
                <button
                  key={tag.id}
                  onClick={() =>
                    setTagIds((prev) =>
                      prev.includes(tag.id) ? prev.filter((id) => id !== tag.id) : [...prev, tag.id],
                    )
                  }
                  className="px-3 py-1 rounded-full text-xs text-white border transition-opacity"
                  style={{
                    backgroundColor: tagIds.includes(tag.id) ? tag.color : 'transparent',
                    borderColor: tag.color,
                    color: tagIds.includes(tag.id) ? '#fff' : tag.color,
                  }}
                >
                  {tag.name}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Repeat */}
        <div>
          <label className="text-text-secondary text-xs mb-2 block">Повтор</label>
          <div className="flex gap-2 overflow-x-auto pb-1">
            {REPEAT_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                onClick={() => setRepeat(opt.value)}
                className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs border transition-colors ${
                  repeat === opt.value
                    ? 'border-accent-cyan bg-accent-cyan/10 text-accent-cyan'
                    : 'border-bg-tertiary text-text-secondary'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {error && <p className="text-accent-red text-sm text-center">{error}</p>}

        <button
          onClick={handleSubmit}
          disabled={saving}
          className="w-full py-4 rounded-xl bg-accent-cyan text-bg-primary font-semibold text-base disabled:opacity-50 active:scale-[0.98] transition-transform mt-2"
        >
          {saving ? 'Збереження...' : 'Додати транзакцію'}
        </button>
      </div>
    </BottomSheet>
  );
}
