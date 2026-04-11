import { useState } from 'react';
import { Dashboard } from '../components/dashboard/Dashboard';
import { AddTransaction } from '../components/transactions/AddTransaction';
import { TransactionDetail } from '../components/transactions/TransactionDetail';
import { FloatingButton } from '../components/ui/FloatingButton';
import { useTransactions } from '../hooks/useTransactions';
import type { Transaction } from '../types';

export function DashboardPage() {
  const [addOpen, setAddOpen] = useState(false);
  const [selected, setSelected] = useState<Transaction | null>(null);
  const { refetch, deleteTransaction } = useTransactions({ limit: 1 });

  return (
    <div className="relative flex flex-col bg-bg-primary" style={{ height: '100dvh' }}>
      <div className="flex-1 overflow-y-auto">
        <Dashboard onSelectTransaction={setSelected} />
      </div>

      <FloatingButton onClick={() => setAddOpen(true)} />

      <AddTransaction
        isOpen={addOpen}
        onClose={() => setAddOpen(false)}
        onAdded={refetch}
      />
      <TransactionDetail
        transaction={selected}
        onClose={() => setSelected(null)}
        onDelete={async (id) => {
          await deleteTransaction(id);
          refetch();
        }}
      />
    </div>
  );
}
