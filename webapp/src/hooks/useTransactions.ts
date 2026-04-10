import { useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';
import type { Transaction, TransactionType, RecurringFrequency } from '../types';

export function useTransactions(params?: {
  skip?: number;
  limit?: number;
  type?: TransactionType;
  category_id?: number;
  account_id?: number;
  date_from?: string;
  date_to?: string;
}) {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.transactions.list(params);
      setTransactions(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Помилка завантаження');
    } finally {
      setLoading(false);
    }
  }, [JSON.stringify(params)]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    fetch();
  }, [fetch]);

  const addTransaction = useCallback(
    async (data: {
      type: TransactionType;
      amount: number;
      description?: string;
      merchant?: string;
      category_id?: number;
      account_id: number;
      to_account_id?: number;
      date: string;
      tag_ids?: number[];
      recurring_frequency?: RecurringFrequency;
    }) => {
      const created = await api.transactions.create(data);
      setTransactions((prev) => [created, ...prev]);
      return created;
    },
    [],
  );

  const deleteTransaction = useCallback(async (id: number) => {
    await api.transactions.delete(id);
    setTransactions((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return { transactions, loading, error, refetch: fetch, addTransaction, deleteTransaction };
}
