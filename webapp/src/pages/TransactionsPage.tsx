import { useState } from 'react';
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
    <div className="flex flex-col h-full">
      <div className="px-4 pt-4 pb-2">
        <TabSwitcher tabs={TYPE_TABS} active={filter} onChange={setFilter} />
      </div>

      <div className="flex-1 overflow-y-auto">
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
