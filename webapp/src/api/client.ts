import { getInitData } from '../utils/telegram';
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
      skip?: number;
      limit?: number;
      type?: TransactionType;
      category_id?: number;
      account_id?: number;
      date_from?: string;
      date_to?: string;
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
  budget: {
    get(): Promise<Budget | null> {
      return request<Budget | null>('/budget');
    },
    set(data: { amount: number; period_start_day?: number }): Promise<Budget> {
      return request<Budget>('/budget', { method: 'POST', body: JSON.stringify(data) });
    },
    progress(): Promise<BudgetProgress> {
      return request<BudgetProgress>('/budget/progress');
    },
  },

  // ── Stats ──────────────────────────────────────────────────────
  stats: {
    summary(): Promise<StatsSummary> {
      return request<StatsSummary>('/stats/summary');
    },
    trend(months?: number): Promise<TrendData[]> {
      const q = months ? `?months=${months}` : '';
      return request<TrendData[]>(`/stats/trend${q}`);
    },
    breakdown(period?: string): Promise<BreakdownData> {
      const q = period ? `?period=${period}` : '';
      return request<BreakdownData>(`/stats/breakdown${q}`);
    },
    savingsRate(): Promise<SavingsRateData> {
      return request<SavingsRateData>('/stats/savings-rate');
    },
  },

  // ── Recurring ──────────────────────────────────────────────────
  recurring: {
    list(): Promise<RecurringTransaction[]> {
      return request<RecurringTransaction[]>('/recurring');
    },
    create(data: Omit<RecurringTransaction, 'id'>): Promise<RecurringTransaction> {
      return request<RecurringTransaction>('/recurring', { method: 'POST', body: JSON.stringify(data) });
    },
    update(id: number, data: Partial<RecurringTransaction>): Promise<RecurringTransaction> {
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
