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

  // Extract primitives to avoid JSON.stringify in dep array
  const skip = params?.skip;
  const limit = params?.limit;
  const type = params?.type;
  const category_id = params?.category_id;
  const account_id = params?.account_id;
  const date_from = params?.date_from;
  const date_to = params?.date_to;

  const fetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.transactions.list({
        skip,
        limit,
        type,
        category_id,
        account_id,
        date_from,
        date_to,
      });
      setTransactions(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Помилка завантаження');
    } finally {
      setLoading(false);
    }
  }, [skip, limit, type, category_id, account_id, date_from, date_to]);

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
