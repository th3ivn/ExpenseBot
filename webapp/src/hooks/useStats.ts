import { useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';
import type { StatsSummary, TrendData, BreakdownData, SavingsRateData } from '../types';

export function useStats() {
  const [summary, setSummary] = useState<StatsSummary | null>(null);
  const [trend, setTrend] = useState<TrendData[]>([]);
  const [breakdown, setBreakdown] = useState<BreakdownData | null>(null);
  const [savingsRate, setSavingsRate] = useState<SavingsRateData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [s, t, b, r] = await Promise.all([
        api.stats.summary(),
        api.stats.trend(),
        api.stats.breakdown(),
        api.stats.savingsRate(),
      ]);
      setSummary(s);
      setTrend(t);
      setBreakdown(b);
      setSavingsRate(r);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Помилка завантаження');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { summary, trend, breakdown, savingsRate, loading, error, refetch: fetch };
}
