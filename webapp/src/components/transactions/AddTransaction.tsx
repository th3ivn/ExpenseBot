import { useState, useEffect } from 'react';
import {
  Upload, FolderOpen, Calendar, CreditCard, AlignLeft, Tag, RefreshCw, ArrowLeft, ArrowRight,
} from 'lucide-react';
import { BottomSheet } from '../ui/BottomSheet';
import { TabSwitcher } from '../ui/TabSwitcher';
import { api } from '../../api/client';
import type { Category, Account, Tag as TagType, TransactionType, RecurringFrequency } from '../../types';

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
  const [tags, setTags] = useState<TagType[]>([]);

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

  const handleClose = () => { reset(); onClose(); };

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

  const selectedCategory = categories.find((c) => c.id === categoryId);
  const lastUsedCategory = categories[0];

  return (
    <BottomSheet isOpen={isOpen} onClose={handleClose} title="Додати транзакцію" fullHeight>
      <div className="px-4 pb-8 flex flex-col gap-3">
        <TabSwitcher
          tabs={TABS}
          active={tab}
          onChange={(id) => setTab(id as TransactionType)}
          className="mt-1"
        />

        {/* Amount */}
        <div className="flex items-center justify-center bg-bg-tertiary rounded-2xl px-5 py-4">
          <span className={`text-3xl font-bold ${amountColor} mr-1`}>₴</span>
          <input
            type="number"
            inputMode="decimal"
            placeholder="0"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className={`bg-transparent text-3xl font-bold outline-none ${amountColor} placeholder-bg-elevated text-center min-w-0 flex-1`}
          />
        </div>

        {/* Category (not for transfer) */}
        {tab !== 'transfer' && (
          <div className="bg-bg-tertiary rounded-2xl overflow-hidden">
            <div className="w-full flex items-center gap-3 px-4 py-3.5">
              <FolderOpen size={18} className="text-text-secondary flex-shrink-0" />
              <span className="flex-1 text-text-primary text-sm">
                {selectedCategory
                  ? `${selectedCategory.emoji} ${selectedCategory.name}`
                  : 'Обрати категорію'}
              </span>
            </div>
            {/* Category chips */}
            {categories.length > 0 && (
              <div className="px-4 pb-3">
                {lastUsedCategory && !categoryId && (
                  <div className="mb-2">
                    <p className="text-text-secondary text-xs mb-1.5">Пропозиції</p>
                    <button
                      type="button"
                      onClick={() => setCategoryId(lastUsedCategory.id)}
                      className="flex items-center gap-2 bg-bg-elevated rounded-xl px-3 py-2 active:opacity-70 transition-opacity"
                    >
                      <span>{lastUsedCategory.emoji}</span>
                      <span className="text-text-primary text-sm">{lastUsedCategory.name}</span>
                      <span className="text-xs text-accent-cyan bg-accent-cyan/10 rounded-full px-2 py-0.5">
                        Останнє
                      </span>
                    </button>
                  </div>
                )}
                <div className="flex flex-wrap gap-2">
                  {categories.map((c) => (
                    <button
                      key={c.id}
                      type="button"
                      onClick={() => setCategoryId(c.id === categoryId ? null : c.id)}
                      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm border transition-all ${
                        categoryId === c.id
                          ? 'border-accent-cyan bg-accent-cyan/10 text-accent-cyan'
                          : 'border-bg-elevated text-text-secondary'
                      }`}
                    >
                      <span>{c.emoji}</span>
                      <span>{c.name}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Main fields card */}
        <div className="bg-bg-tertiary rounded-2xl overflow-hidden">
          {/* Date */}
          <div className="flex items-center gap-3 px-4 py-3.5 border-b border-bg-elevated">
            <Calendar size={18} className="text-text-secondary flex-shrink-0" />
            <span className="text-text-secondary text-sm w-16 flex-shrink-0">Дата</span>
            <input
              type="datetime-local"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="flex-1 bg-transparent text-text-primary text-sm outline-none text-right"
            />
          </div>

          {/* Account from */}
          <div className="flex items-center gap-3 px-4 py-3 border-b border-bg-elevated">
            {tab === 'transfer' ? (
              <ArrowLeft size={18} className="text-text-secondary flex-shrink-0" />
            ) : (
              <CreditCard size={18} className="text-text-secondary flex-shrink-0" />
            )}
            <span className="text-text-secondary text-sm flex-shrink-0">
              {tab === 'transfer' ? 'Звідки' : 'Рахунок'}
            </span>
            <div className="flex-1 flex gap-1.5 justify-end overflow-x-auto">
              {accounts.map((a) => (
                <button
                  key={a.id}
                  type="button"
                  onClick={() => setAccountId(a.id)}
                  className={`flex-shrink-0 flex items-center gap-1 px-2.5 py-1 rounded-full text-xs border transition-all ${
                    accountId === a.id
                      ? 'border-accent-cyan bg-accent-cyan/10 text-accent-cyan'
                      : 'border-bg-elevated text-text-secondary'
                  }`}
                >
                  <span>{a.emoji}</span>
                  <span>{a.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* To account (transfer) */}
          {tab === 'transfer' && (
            <div className="flex items-center gap-3 px-4 py-3 border-b border-bg-elevated">
              <ArrowRight size={18} className="text-text-secondary flex-shrink-0" />
              <span className="text-text-secondary text-sm flex-shrink-0">Куди</span>
              <div className="flex-1 flex gap-1.5 justify-end overflow-x-auto">
                {accounts
                  .filter((a) => a.id !== accountId)
                  .map((a) => (
                    <button
                      key={a.id}
                      type="button"
                      onClick={() => setToAccountId(a.id)}
                      className={`flex-shrink-0 flex items-center gap-1 px-2.5 py-1 rounded-full text-xs border transition-all ${
                        toAccountId === a.id
                          ? 'border-accent-blue bg-accent-blue/10 text-accent-blue'
                          : 'border-bg-elevated text-text-secondary'
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
          <div className="flex items-center gap-3 px-4 py-3.5 border-b border-bg-elevated">
            <AlignLeft size={18} className="text-text-secondary flex-shrink-0" />
            <input
              type="text"
              placeholder="Необов'язковий опис"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="flex-1 bg-transparent text-text-primary text-sm outline-none placeholder-text-secondary"
            />
          </div>

          {/* Tags */}
          {tags.length > 0 && (
            <div className="flex items-start gap-3 px-4 py-3.5 border-b border-bg-elevated">
              <Tag size={18} className="text-text-secondary flex-shrink-0 mt-0.5" />
              <div className="flex flex-wrap gap-1.5">
                {tags.map((tag) => (
                  <button
                    key={tag.id}
                    type="button"
                    onClick={() =>
                      setTagIds((prev) =>
                        prev.includes(tag.id) ? prev.filter((id) => id !== tag.id) : [...prev, tag.id],
                      )
                    }
                    className="px-3 py-1 rounded-full text-xs border transition-all"
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
          <div className="flex items-center gap-3 px-4 py-3">
            <RefreshCw size={18} className="text-text-secondary flex-shrink-0" />
            <span className="text-text-secondary text-sm flex-shrink-0">Повтор</span>
            <div className="flex-1 flex gap-1.5 justify-end overflow-x-auto">
              {REPEAT_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => setRepeat(opt.value)}
                  className={`flex-shrink-0 px-2.5 py-1 rounded-full text-xs border transition-all ${
                    repeat === opt.value
                      ? 'border-accent-cyan bg-accent-cyan/10 text-accent-cyan'
                      : 'border-bg-elevated text-text-secondary'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {error && <p className="text-accent-red text-sm text-center">{error}</p>}

        <button
          type="button"
          onClick={handleSubmit}
          disabled={saving}
          className="w-full py-4 rounded-2xl bg-accent-cyan text-bg-primary font-bold text-base disabled:opacity-50 active:scale-[0.98] transition-transform mt-1 flex items-center justify-center gap-2"
        >
          <Upload size={18} />
          <span>{saving ? 'Збереження...' : 'Додати'}</span>
        </button>
      </div>
    </BottomSheet>
  );
}
