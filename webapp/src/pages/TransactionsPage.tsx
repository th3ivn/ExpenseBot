import { useState } from 'react';
import { Search } from 'lucide-react';
import { TransactionList } from '../components/transactions/TransactionList';
import { TransactionDetail } from '../components/transactions/TransactionDetail';
import { AddTransaction } from '../components/transactions/AddTransaction';
import { FloatingButton } from '../components/ui/FloatingButton';
import { TabSwitcher } from '../components/ui/TabSwitcher';
import { useTransactions } from '../hooks/useTransactions';
import type { Transaction, TransactionType } from '../types';

const TYPE_TABS = [
  { id: 'all', label: 'Всі' },
  { id: 'expense', label: 'Витрати' },
  { id: 'income', label: 'Доходи' },
  { id: 'transfer', label: 'Перекази' },
];

export function TransactionsPage() {
  const [filter, setFilter] = useState('all');
  const [selected, setSelected] = useState<Transaction | null>(null);
  const [addOpen, setAddOpen] = useState(false);

  const { transactions, loading, refetch, deleteTransaction } = useTransactions({
    type: filter === 'all' ? undefined : (filter as TransactionType),
    limit: 50,
  });

  return (
    <div className="flex flex-col bg-bg-primary" style={{ height: '100dvh' }}>
      {/* Header */}
      <div
        className="flex-shrink-0 px-4 pb-3 bg-bg-primary"
        style={{ paddingTop: 'max(12px, env(safe-area-inset-top))' }}
      >
        <div className="flex items-center justify-between mb-3">
          <h1 className="text-text-primary text-xl font-bold">Операції</h1>
          <button
            type="button"
            disabled
            aria-label="Пошук (скоро)"
            className="w-10 h-10 rounded-full bg-bg-secondary flex items-center justify-center opacity-40 cursor-not-allowed"
          >
            <Search size={18} className="text-text-secondary" />
          </button>
        </div>
        <TabSwitcher tabs={TYPE_TABS} active={filter} onChange={setFilter} />
      </div>

      <div className="flex-1 overflow-y-auto pt-2">
        <TransactionList
          transactions={transactions}
          loading={loading}
          onSelect={setSelected}
        />
      </div>

      <FloatingButton onClick={() => setAddOpen(true)} />

      <TransactionDetail
        transaction={selected}
        onClose={() => setSelected(null)}
        onDelete={async (id) => {
          await deleteTransaction(id);
          refetch();
        }}
      />
      <AddTransaction
        isOpen={addOpen}
        onClose={() => setAddOpen(false)}
        onAdded={refetch}
      />
    </div>
  );
}
