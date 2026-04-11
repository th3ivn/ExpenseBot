import { useState } from 'react';
import { ChevronRight } from 'lucide-react';
import { TabSwitcher } from '../ui/TabSwitcher';
import { DonutChart } from '../ui/DonutChart';
import { formatCurrency } from '../../utils/format';
import type { BreakdownData, BreakdownItem } from '../../types';

interface ExpenseBreakdownProps {
  data: BreakdownData | null;
  loading: boolean;
}

export function ExpenseBreakdown({ data, loading }: ExpenseBreakdownProps) {
  const [view, setView] = useState<'groups' | 'categories'>('groups');

  if (loading || !data) {
    return <div className="h-64 bg-bg-secondary rounded-3xl animate-pulse" />;
  }

  const items: BreakdownItem[] = view === 'groups' ? data.groups : data.categories;

  return (
    <div className="space-y-4">
      <TabSwitcher
        tabs={[
          { id: 'groups', label: 'Групи' },
          { id: 'categories', label: 'Категорії' },
        ]}
        active={view}
        onChange={(id) => setView(id as 'groups' | 'categories')}
      />

      {/* Donut */}
      <div className="flex justify-center py-4">
        <DonutChart
          data={
            items.length > 0
              ? items.map((i) => ({ value: i.amount, color: i.color }))
              : [{ value: 1, color: '#252B3B' }]
          }
          size={220}
          strokeWidth={32}
          centerLabel={formatCurrency(data.total)}
          centerSublabel="Всього"
        />
      </div>

      {/* List */}
      <div className="bg-bg-secondary rounded-3xl overflow-hidden">
        {items.map((item, idx) => (
          <button
            key={item.name}
            type="button"
            className={`w-full flex items-center gap-3 px-4 py-3.5 active:bg-bg-elevated transition-colors text-left ${
              idx < items.length - 1 ? 'border-b border-bg-tertiary' : ''
            }`}
          >
            <div
              className="w-3 h-3 rounded-full flex-shrink-0"
              style={{ backgroundColor: item.color }}
            />
            <span className="flex-1 text-text-primary text-sm">
              {item.emoji ? `${item.emoji} ` : ''}{item.name}
            </span>
            <span className="text-text-primary text-sm font-semibold">
              {formatCurrency(item.amount)}
            </span>
            <ChevronRight size={14} className="text-bg-tertiary" />
          </button>
        ))}
      </div>
    </div>
  );
}
