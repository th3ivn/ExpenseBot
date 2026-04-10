export type TransactionType = 'expense' | 'income' | 'transfer';
export type RecurringFrequency = 'daily' | 'weekly' | 'monthly' | 'yearly';

export interface User {
  id: number;
  telegram_id: number;
  first_name: string;
  username?: string;
}

export interface Category {
  id: number;
  name: string;
  emoji: string;
  color: string;
  group_name?: string;
  sort_order: number;
  is_active: boolean;
}

export interface Account {
  id: number;
  name: string;
  emoji: string;
  opening_balance: number;
  current_balance: number;
  is_active: boolean;
  sort_order: number;
}

export interface Transaction {
  id: number;
  type: TransactionType;
  amount: number;
  description?: string;
  merchant?: string;
  category?: Category;
  account_id: number;
  account?: Account;
  to_account_id?: number;
  to_account?: Account;
  date: string;
  created_at: string;
  tags: Tag[];
}

export interface Tag {
  id: number;
  name: string;
  color: string;
}

export interface Budget {
  id: number;
  amount: number;
  period_start_day: number;
  is_active: boolean;
}

export interface BudgetProgress {
  budget_amount: number;
  distributed: number;
  available: number;
  period_start: string;
  period_end: string;
}

export interface RecurringTransaction {
  id: number;
  type: TransactionType;
  amount: number;
  description?: string;
  category?: Category;
  account_id: number;
  to_account_id?: number;
  frequency: RecurringFrequency;
  next_date: string;
  is_active: boolean;
}

export interface StatsSummary {
  budget_amount: number;
  distributed: number;
  available: number;
  period_start: string;
  period_end: string;
}

export interface TrendData {
  date: string;
  current: number;
  average: number;
}

export interface BreakdownItem {
  name: string;
  emoji: string;
  color: string;
  amount: number;
  percentage: number;
}

export interface BreakdownData {
  groups: BreakdownItem[];
  categories: BreakdownItem[];
  total: number;
}

export interface SavingsRateData {
  rate: number;
  income: number;
  savings: number;
  level: string;
  level_color: string;
  monthly: Array<{ month: string; rate: number; income: number; expenses: number }>;
}

export interface UserSettings {
  budget_period_start_day: number;
  theme: string;
}

export interface MerchantRule {
  id: number;
  merchant_pattern: string;
  category_id: number;
  category?: Category;
}
