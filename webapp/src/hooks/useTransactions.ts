import { useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';
import type { Transaction, TransactionType, RecurringFrequency } from '../types';

export function useTransactions(params?: {
  offset?: number;
  limit?: number;
  type?: TransactionType;
  category_id?: number;
  account_id?: number;
  period_start?: string;
  period_end?: string;
}) {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Extract primitives to avoid object reference churn in dep array
  const offset = params?.offset;
  const limit = params?.limit;
  const type = params?.type;
  const category_id = params?.category_id;
  const account_id = params?.account_id;
  const period_start = params?.period_start;
  const period_end = params?.period_end;

  const fetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.transactions.list({
        offset,
        limit,
        type,
        category_id,
        account_id,
        period_start,
        period_end,
      });
      setTransactions(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Помилка завантаження');
    } finally {
      setLoading(false);
    }
  }, [offset, limit, type, category_id, account_id, period_start, period_end]);

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
