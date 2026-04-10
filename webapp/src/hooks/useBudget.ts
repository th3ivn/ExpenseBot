import { useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';
import type { Budget, BudgetProgress } from '../types';

export function useBudget() {
  const [budget, setBudget] = useState<Budget | null>(null);
  const [progress, setProgress] = useState<BudgetProgress | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [b, p] = await Promise.all([api.budget.get(), api.budget.progress()]);
      setBudget(b);
      setProgress(p);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Помилка завантаження');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  const setBudgetAmount = useCallback(
    async (amount: number, period_start_day?: number) => {
      const b = await api.budget.set({ amount, period_start_day });
      setBudget(b);
    },
    [],
  );

  return { budget, progress, loading, error, refetch: fetch, setBudgetAmount };
}
