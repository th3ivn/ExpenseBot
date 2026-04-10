import { RingChart } from '../ui/RingChart';
import { formatCurrency, formatPeriod } from '../../utils/format';
import type { BudgetProgress } from '../../types';

interface BudgetRingProps {
  progress: BudgetProgress | null;
  loading?: boolean;
}

export function BudgetRing({ progress, loading }: BudgetRingProps) {
  if (loading || !progress) {
    return (
      <div className="flex flex-col items-center py-6">
        <div className="w-40 h-40 rounded-full bg-bg-tertiary animate-pulse" />
        <div className="mt-6 w-full grid grid-cols-3 gap-2">
          {[0, 1, 2].map((i) => (
            <div key={i} className="h-10 bg-bg-tertiary rounded-lg animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  const { budget_amount, distributed, available, period_start, period_end } = progress;
  const isOverBudget = available < 0;

  return (
    <div className="flex flex-col items-center">
      <RingChart
        value={distributed}
        max={budget_amount}
        size={160}
        strokeWidth={14}
        color={isOverBudget ? '#FF3B30' : '#00D4AA'}
      >
        <span className="text-text-secondary text-xs text-center leading-tight px-2">
          {formatPeriod(period_start, period_end)}
        </span>
      </RingChart>

      <div className="mt-5 w-full grid grid-cols-3 gap-2">
        <MetricCell label="Бюджет" value={formatCurrency(budget_amount)} />
        <MetricCell label="Розподілено" value={formatCurrency(distributed)} />
        <MetricCell
          label="Доступно"
          value={formatCurrency(Math.abs(available))}
          prefix={isOverBudget ? '−' : ''}
          valueClass={isOverBudget ? 'text-accent-red' : 'text-text-primary'}
        />
      </div>
    </div>
  );
}

function MetricCell({
  label,
  value,
  prefix = '',
  valueClass = 'text-text-primary',
}: {
  label: string;
  value: string;
  prefix?: string;
  valueClass?: string;
}) {
  return (
    <div className="flex flex-col items-center bg-bg-tertiary rounded-xl p-2">
      <span className="text-text-secondary text-[10px] leading-none mb-1">{label}</span>
      <span className={`font-semibold text-xs leading-none ${valueClass}`}>
        {prefix}{value}
      </span>
    </div>
  );
}
