import { useNavigate } from 'react-router-dom';
import { TrendingUp, PieChart, CalendarClock, Banknote } from 'lucide-react';
import { LineChart } from '../ui/LineChart';
import { DonutChart } from '../ui/DonutChart';
import { GaugeChart } from '../ui/GaugeChart';
import { formatCurrency, getSavingsLevel } from '../../utils/format';
import type { TrendData, BreakdownData, SavingsRateData, RecurringTransaction } from '../../types';

interface AnalyticsCardsProps {
  trend: TrendData[];
  breakdown: BreakdownData | null;
  savingsRate: SavingsRateData | null;
  recurring: RecurringTransaction[];
  loading: boolean;
}

export function AnalyticsCards({
  trend,
  breakdown,
  savingsRate,
  recurring,
  loading,
}: AnalyticsCardsProps) {
  const navigate = useNavigate();

  const trendChange =
    trend.length >= 2
      ? ((trend[trend.length - 1].current - trend[trend.length - 2].current) /
          (trend[trend.length - 2].current || 1)) *
        100
      : 0;

  const topCategories = breakdown?.categories?.slice(0, 3) ?? [];
  const savingsLevel = savingsRate ? getSavingsLevel(savingsRate.rate) : null;

  if (loading) {
    return (
      <div className="grid grid-cols-2 gap-3">
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="h-40 bg-bg-secondary rounded-3xl animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 gap-3">
      {/* Trend */}
      <button
        type="button"
        onClick={() => navigate('/analytics')}
        className="rounded-3xl p-4 flex flex-col text-left active:scale-[0.97] transition-transform"
        style={{ backgroundColor: '#141D2E' }}
      >
        <div className="flex items-center gap-2 mb-2">
          <TrendingUp size={15} className="text-text-secondary" />
          <span className="text-text-secondary text-xs font-medium">Тренд</span>
        </div>
        <span className={`text-2xl font-bold ${trendChange >= 0 ? 'text-accent-red' : 'text-accent-green'}`}>
          {trendChange >= 0 ? '+' : ''}{trendChange.toFixed(0)}%
        </span>
        <div className="mt-2 flex-1 min-h-[40px]">
          <LineChart data={trend} mini />
        </div>
        {trend.length === 0 && (
          <div className="flex items-center gap-1.5 mt-1">
            <span className="text-text-secondary text-xs">— Немає даних</span>
          </div>
        )}
      </button>

      {/* Breakdown */}
      <button
        type="button"
        onClick={() => navigate('/analytics/breakdown')}
        className="rounded-3xl p-4 flex flex-col active:scale-[0.97] transition-transform"
        style={{ backgroundColor: '#1A1030' }}
      >
        <div className="flex items-center gap-2 mb-2">
          <PieChart size={15} className="text-text-secondary" />
          <span className="text-text-secondary text-xs font-medium">Витрати</span>
        </div>
        <span className="text-text-primary text-lg font-bold leading-tight">
          {breakdown ? formatCurrency(breakdown.total) : '—'}
        </span>
        <div className="flex-1 flex items-center justify-center mt-2">
          <DonutChart
            data={
              topCategories.length > 0
                ? topCategories.map((c) => ({ value: c.amount, color: c.color, label: c.name }))
                : [{ value: 1, color: '#252B3B', label: '' }]
            }
            size={72}
            strokeWidth={12}
          />
        </div>
        {topCategories[0] && (
          <div className="flex items-center gap-1.5 mt-1">
            <span
              className="w-2 h-2 rounded-full flex-shrink-0"
              style={{ backgroundColor: topCategories[0].color }}
            />
            <span className="text-text-secondary text-xs truncate">{topCategories[0].name}</span>
          </div>
        )}
      </button>

      {/* Planned */}
      <button
        type="button"
        onClick={() => navigate('/analytics/planned')}
        className="rounded-3xl p-4 flex flex-col text-left active:scale-[0.97] transition-transform"
        style={{ backgroundColor: '#1C1008' }}
      >
        <div className="flex items-center gap-2 mb-2">
          <CalendarClock size={15} className="text-text-secondary" />
          <span className="text-text-secondary text-xs font-medium">Заплановані</span>
        </div>
        <span className="text-text-primary text-2xl font-bold">
          {formatCurrency(
            recurring
              .filter((r) => r.type === 'expense')
              .reduce((s, r) => s + r.amount, 0),
          )}
        </span>
        <div className="flex-1 flex flex-col justify-end mt-2">
          {recurring.length === 0 ? (
            <span className="text-text-secondary text-xs">Немає витрат</span>
          ) : (
            <span className="text-text-secondary text-xs">{recurring.length} шт.</span>
          )}
        </div>
      </button>

      {/* Savings rate */}
      <button
        type="button"
        onClick={() => navigate('/analytics/savings')}
        className="rounded-3xl p-4 flex flex-col active:scale-[0.97] transition-transform"
        style={{ backgroundColor: '#1C1008' }}
      >
        <div className="flex items-center gap-2 mb-2">
          <Banknote size={15} className="text-text-secondary" />
          <span className="text-text-secondary text-xs font-medium">Збереження</span>
        </div>
        <span className="text-text-primary text-2xl font-bold">
          {savingsRate?.rate?.toFixed(0) ?? '0'}%
        </span>
        <div className="flex-1 flex items-center justify-center mt-1">
          <GaugeChart
            value={savingsRate?.rate ?? 0}
            max={50}
            size={80}
            color={savingsLevel?.color ?? '#8E8E93'}
          />
        </div>
        {savingsLevel && (
          <div className="flex items-center gap-1.5 -mt-1">
            <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: savingsLevel.color }} />
            <span className="text-xs font-medium" style={{ color: savingsLevel.color }}>
              {savingsLevel.label}
            </span>
          </div>
        )}
      </button>
    </div>
  );
}
