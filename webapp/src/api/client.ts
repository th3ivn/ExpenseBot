import { getInitData } from '../utils/telegram';
import { getSavingsLevel } from '../utils/format';
import type {
  Transaction,
  Category,
  Account,
  Tag,
  Budget,
  BudgetProgress,
  RecurringTransaction,
  StatsSummary,
  TrendData,
  BreakdownData,
  BreakdownItem,
  SavingsRateData,
  UserSettings,
  MerchantRule,
  TransactionType,
  RecurringFrequency,
} from '../types';

const BASE_URL = (import.meta.env.VITE_API_URL as string | undefined) ?? '/api';

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const initData = getInitData();
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${initData}`,
      ...(options.headers as Record<string, string> | undefined),
    },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

// ── Transactions ────────────────────────────────────────────────
export const api = {
  transactions: {
    list(params?: {
      offset?: number;
      limit?: number;
      type?: TransactionType;
      category_id?: number;
      account_id?: number;
      period_start?: string;
      period_end?: string;
    }): Promise<Transaction[]> {
      const q = new URLSearchParams();
      if (params) {
        Object.entries(params).forEach(([k, v]) => {
          if (v !== undefined) q.set(k, String(v));
        });
      }
      return request<Transaction[]>(`/transactions?${q}`);
    },

    get(id: number): Promise<Transaction> {
      return request<Transaction>(`/transactions/${id}`);
    },

    create(data: {
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
    }): Promise<Transaction> {
      return request<Transaction>('/transactions', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },

    update(
      id: number,
      data: Partial<{
        type: TransactionType;
        amount: number;
        description: string;
        merchant: string;
        category_id: number;
        account_id: number;
        to_account_id: number;
        date: string;
        tag_ids: number[];
      }>,
    ): Promise<Transaction> {
      return request<Transaction>(`/transactions/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    },

    delete(id: number): Promise<void> {
      return request<void>(`/transactions/${id}`, { method: 'DELETE' });
    },
  },

  // ── Categories ─────────────────────────────────────────────────
  categories: {
    list(): Promise<Category[]> {
      return request<Category[]>('/categories');
    },
    create(data: { name: string; emoji: string; color: string; group_name?: string }): Promise<Category> {
      return request<Category>('/categories', { method: 'POST', body: JSON.stringify(data) });
    },
    update(id: number, data: Partial<Category>): Promise<Category> {
      return request<Category>(`/categories/${id}`, { method: 'PUT', body: JSON.stringify(data) });
    },
    delete(id: number): Promise<void> {
      return request<void>(`/categories/${id}`, { method: 'DELETE' });
    },
  },

  // ── Accounts ───────────────────────────────────────────────────
  accounts: {
    list(): Promise<Account[]> {
      return request<Account[]>('/accounts');
    },
    create(data: { name: string; emoji: string; opening_balance?: number }): Promise<Account> {
      return request<Account>('/accounts', { method: 'POST', body: JSON.stringify(data) });
    },
    update(id: number, data: Partial<Account>): Promise<Account> {
      return request<Account>(`/accounts/${id}`, { method: 'PUT', body: JSON.stringify(data) });
    },
    delete(id: number): Promise<void> {
      return request<void>(`/accounts/${id}`, { method: 'DELETE' });
    },
  },

  // ── Tags ───────────────────────────────────────────────────────
  tags: {
    list(): Promise<Tag[]> {
      return request<Tag[]>('/tags');
    },
    create(data: { name: string; color: string }): Promise<Tag> {
      return request<Tag>('/tags', { method: 'POST', body: JSON.stringify(data) });
    },
    delete(id: number): Promise<void> {
      return request<void>(`/tags/${id}`, { method: 'DELETE' });
    },
  },

  // ── Budget ─────────────────────────────────────────────────────
  // Backend: GET /api/budgets/current → { budget, period_start, period_end, distributed, available }
  budget: {
    async get(): Promise<Budget | null> {
      const raw = await request<{ budget: Budget | null; period_start: string; period_end: string; distributed: number; available: number }>('/budgets/current');
      return raw.budget;
    },
    async set(data: { amount: number; period_start_day?: number }): Promise<Budget> {
      return request<Budget>('/budgets', { method: 'POST', body: JSON.stringify(data) });
    },
    async progress(): Promise<BudgetProgress> {
      const raw = await request<{
        budget: { amount: number } | null;
        period_start: string;
        period_end: string;
        distributed: number;
        available: number;
      }>('/budgets/current');
      return {
        budget_amount: Number(raw.budget?.amount ?? 0),
        distributed: Number(raw.distributed),
        available: Number(raw.available),
        period_start: raw.period_start,
        period_end: raw.period_end,
      };
    },
  },

  // ── Stats ──────────────────────────────────────────────────────
  // Backend returns different shapes — adapt them to frontend types here.
  stats: {
    summary(): Promise<StatsSummary> {
      return request<StatsSummary>('/stats/summary');
    },
    async trend(): Promise<TrendData[]> {
      const raw = await request<{
        current_period: Array<{ date: string; amount: number }>;
        avg_daily_prev: number;
      }>('/stats/trend');
      const avg = Number(raw.avg_daily_prev ?? 0);
      return (raw.current_period ?? []).map((p) => ({
        date: p.date,
        current: Number(p.amount),
        average: avg,
      }));
    },
    async breakdown(): Promise<BreakdownData> {
      const raw = await request<{
        items: Array<{
          category_name: string;
          group_name: string | null;
          emoji: string;
          color: string;
          total: number;
          percentage: number;
        }>;
        total: number;
      }>('/stats/breakdown');
      const items = raw.items ?? [];
      const total = Number(raw.total ?? 0);

      const categories: BreakdownItem[] = items.map((i) => ({
        name: i.category_name,
        emoji: i.emoji,
        color: i.color,
        amount: Number(i.total),
        percentage: Number(i.percentage),
      }));

      // Aggregate categories into groups by group_name
      const groupMap = new Map<string, BreakdownItem>();
      items.forEach((i) => {
        const key = i.group_name ?? i.category_name;
        const existing = groupMap.get(key);
        if (existing) {
          existing.amount += Number(i.total);
        } else {
          groupMap.set(key, {
            name: key,
            emoji: i.emoji,
            color: i.color,
            amount: Number(i.total),
            percentage: 0,
          });
        }
      });
      const groups: BreakdownItem[] = Array.from(groupMap.values()).map((g) => ({
        ...g,
        percentage: total > 0 ? (g.amount / total) * 100 : 0,
      }));

      return { categories, groups, total };
    },
    async savingsRate(): Promise<SavingsRateData> {
      const raw = await request<{
        year: number;
        months: Array<{ month: string; income: number; expenses: number; savings_rate: number }>;
        avg_savings_rate: number;
      }>('/stats/savings-rate');
      const rate = Number(raw.avg_savings_rate ?? 0);
      const months = raw.months ?? [];
      const totalIncome = months.reduce((s, m) => s + Number(m.income), 0);
      const totalExpenses = months.reduce((s, m) => s + Number(m.expenses), 0);
      const level = getSavingsLevel(rate);
      return {
        rate,
        income: totalIncome,
        savings: totalIncome - totalExpenses,
        level: level.label,
        level_color: level.color,
        monthly: months.map((m) => ({
          month: m.month,
          rate: Number(m.savings_rate),
          income: Number(m.income),
          expenses: Number(m.expenses),
        })),
      };
    },
  },

  // ── Recurring ──────────────────────────────────────────────────
  recurring: {
    list(): Promise<RecurringTransaction[]> {
      return request<RecurringTransaction[]>('/recurring');
    },
    create(data: {
      type: TransactionType;
      amount: number;
      description?: string;
      category_id?: number;
      account_id: number;
      to_account_id?: number;
      frequency: RecurringFrequency;
      next_date: string;
      is_active?: boolean;
    }): Promise<RecurringTransaction> {
      return request<RecurringTransaction>('/recurring', { method: 'POST', body: JSON.stringify(data) });
    },
    update(id: number, data: Partial<{
      type: TransactionType;
      amount: number;
      description: string;
      category_id: number;
      account_id: number;
      to_account_id: number;
      frequency: RecurringFrequency;
      next_date: string;
      is_active: boolean;
    }>): Promise<RecurringTransaction> {
      return request<RecurringTransaction>(`/recurring/${id}`, { method: 'PUT', body: JSON.stringify(data) });
    },
    delete(id: number): Promise<void> {
      return request<void>(`/recurring/${id}`, { method: 'DELETE' });
    },
  },

  // ── Settings ───────────────────────────────────────────────────
  settings: {
    get(): Promise<UserSettings> {
      return request<UserSettings>('/settings');
    },
    update(data: Partial<UserSettings>): Promise<UserSettings> {
      return request<UserSettings>('/settings', { method: 'PUT', body: JSON.stringify(data) });
    },
  },

  // ── Merchant Rules ─────────────────────────────────────────────
  merchantRules: {
    list(): Promise<MerchantRule[]> {
      return request<MerchantRule[]>('/merchant-rules');
    },
    create(data: { merchant_pattern: string; category_id: number }): Promise<MerchantRule> {
      return request<MerchantRule>('/merchant-rules', { method: 'POST', body: JSON.stringify(data) });
    },
    delete(id: number): Promise<void> {
      return request<void>(`/merchant-rules/${id}`, { method: 'DELETE' });
    },
  },
};
