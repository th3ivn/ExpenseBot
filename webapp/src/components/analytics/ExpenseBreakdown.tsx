import { useState } from 'react';
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
    return <div className="h-64 bg-bg-secondary rounded-2xl animate-pulse" />;
  }

  const items: BreakdownItem[] = view === 'groups' ? data.groups : data.categories;

  return (
    <div className="bg-bg-secondary rounded-2xl p-4">
      <TabSwitcher
        tabs={[
          { id: 'groups', label: 'Групи' },
          { id: 'categories', label: 'Категорії' },
        ]}
        active={view}
        onChange={(id) => setView(id as 'groups' | 'categories')}
        className="mb-4"
      />

      <div className="flex items-center gap-6">
        <DonutChart
          data={items.map((i) => ({ value: i.amount, color: i.color }))}
          size={120}
          strokeWidth={16}
          centerLabel={formatCurrency(data.total).split(' ')[0]}
          centerSublabel="₴"
        />
        <div className="flex-1 space-y-2">
          {items.slice(0, 5).map((item) => (
            <div key={item.name} className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: item.color }} />
              <span className="text-text-secondary text-xs truncate flex-1">
                {item.emoji} {item.name}
              </span>
              <span className="text-text-primary text-xs font-medium">{item.percentage.toFixed(0)}%</span>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-4 space-y-1">
        {items.map((item) => (
          <div key={item.name} className="flex items-center justify-between py-2 border-b border-bg-tertiary last:border-0">
            <div className="flex items-center gap-2">
              <span className="text-lg">{item.emoji}</span>
              <div>
                <p className="text-text-primary text-sm font-medium">{item.name}</p>
                <div className="flex items-center gap-1 mt-0.5">
                  <div className="h-1 rounded-full" style={{ width: `${item.percentage * 1.2}px`, backgroundColor: item.color }} />
                  <span className="text-text-secondary text-xs">{item.percentage.toFixed(1)}%</span>
                </div>
              </div>
            </div>
            <span className="text-accent-red font-semibold text-sm">{formatCurrency(item.amount)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
