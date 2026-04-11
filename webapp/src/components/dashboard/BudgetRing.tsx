import { useNavigate } from 'react-router-dom';
import { RingChart } from '../ui/RingChart';
import { formatCurrency } from '../../utils/format';
import type { BudgetProgress } from '../../types';

interface BudgetRingProps {
  progress: BudgetProgress | null;
  loading?: boolean;
}

export function BudgetRing({ progress, loading }: BudgetRingProps) {
  const navigate = useNavigate();

  if (loading || !progress) {
    return (
      <div className="flex flex-col items-center py-4">
        <div className="w-52 h-52 rounded-full bg-bg-secondary animate-pulse" />
        <div className="mt-6 w-full grid grid-cols-3 gap-3">
          {[0, 1, 2].map((i) => (
            <div key={i} className="h-14 bg-bg-secondary rounded-2xl animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  const { budget_amount, distributed, available } = progress;
  const isOverBudget = available < 0;

  return (
    <div className="flex flex-col items-center">
      <button
        type="button"
        onClick={() => navigate('/settings/budget')}
        className="active:opacity-80 transition-opacity"
      >
        <RingChart
          value={distributed}
          max={budget_amount}
          size={208}
          strokeWidth={18}
          color={isOverBudget ? '#FF3B30' : '#00D4C8'}
        >
          {budget_amount === 0 ? (
            <p className="text-text-secondary text-sm text-center px-8 leading-snug">
              Натисніть, щоб встановити бюджет
            </p>
          ) : (
            <div className="flex flex-col items-center gap-1">
              <span className="text-text-primary text-3xl font-bold">
                {formatCurrency(budget_amount).replace(' ₴', '')}
              </span>
              <span className="text-text-secondary text-sm">₴ бюджет</span>
            </div>
          )}
        </RingChart>
      </button>

      <div className="mt-5 w-full grid grid-cols-3 gap-3">
        <MetricCell label="Бюджет" value={formatCurrency(budget_amount)} />
        <MetricCell label="Розподілено" value={formatCurrency(distributed)} />
        <MetricCell
          label="Доступно"
          value={`${isOverBudget ? '−' : ''}${formatCurrency(Math.abs(available))}`}
          valueColor={isOverBudget ? 'text-accent-red' : 'text-text-primary'}
        />
      </div>
    </div>
  );
}

function MetricCell({
  label,
  value,
  valueColor = 'text-text-primary',
}: {
  label: string;
  value: string;
  valueColor?: string;
}) {
  return (
    <div className="flex flex-col items-center bg-bg-secondary rounded-2xl px-2 py-3 gap-1">
      <span className="text-text-secondary text-xs leading-none">{label}</span>
      <span className={`font-semibold text-sm leading-none text-center ${valueColor}`}>
        {value}
      </span>
    </div>
  );
}
