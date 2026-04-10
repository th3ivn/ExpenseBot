import { useNavigate } from 'react-router-dom';
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

  const topCategories = breakdown?.categories.slice(0, 3) ?? [];

  const savingsLevel = savingsRate ? getSavingsLevel(savingsRate.rate) : null;

  if (loading) {
    return (
      <div className="grid grid-cols-2 gap-3">
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="h-32 bg-bg-secondary rounded-2xl animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 gap-3">
      {/* Trend */}
      <button
        onClick={() => navigate('/analytics/trend')}
        className="bg-bg-secondary rounded-2xl p-3 flex flex-col text-left active:scale-[0.97] transition-transform"
      >
        <div className="flex items-center gap-1 mb-1">
          <span className="text-base">📈</span>
          <span className="text-text-secondary text-xs">Тренд</span>
        </div>
        <span
          className={`text-sm font-semibold ${trendChange >= 0 ? 'text-accent-red' : 'text-accent-green'}`}
        >
          {trendChange >= 0 ? '+' : ''}
          {trendChange.toFixed(1)}%
        </span>
        <div className="mt-2 flex-1">
          <LineChart data={trend} mini />
        </div>
      </button>

      {/* Top expenses donut */}
      <button
        onClick={() => navigate('/analytics/breakdown')}
        className="bg-bg-secondary rounded-2xl p-3 flex flex-col items-center text-center active:scale-[0.97] transition-transform"
      >
        <div className="flex items-center gap-1 mb-1 self-start">
          <span className="text-base">🕐</span>
          <span className="text-text-secondary text-xs">Витрати</span>
        </div>
        <DonutChart
          data={topCategories.map((c) => ({ value: c.amount, color: c.color, label: c.name }))}
          size={72}
          strokeWidth={10}
          centerLabel={breakdown ? formatCurrency(breakdown.total).replace(' ₴', '') : '—'}
          centerSublabel="₴"
        />
      </button>

      {/* Planned */}
      <button
        onClick={() => navigate('/analytics/planned')}
        className="bg-bg-secondary rounded-2xl p-3 flex flex-col text-left active:scale-[0.97] transition-transform"
      >
        <div className="flex items-center gap-1 mb-1">
          <span className="text-base">📋</span>
          <span className="text-text-secondary text-xs">Заплановані</span>
        </div>
        {recurring.length === 0 ? (
          <span className="text-text-secondary text-xs mt-1">Немає</span>
        ) : (
          <div className="mt-1 space-y-1">
            {recurring.slice(0, 2).map((r) => (
              <div key={r.id} className="flex justify-between items-center">
                <span className="text-text-secondary text-[10px] truncate max-w-[80px]">
                  {r.description ?? 'Без назви'}
                </span>
                <span className="text-accent-red text-[10px] font-medium">
                  {formatCurrency(r.amount)}
                </span>
              </div>
            ))}
          </div>
        )}
        <span className="text-accent-cyan text-xs mt-auto pt-1">
          {recurring.length} шт.
        </span>
      </button>

      {/* Savings rate */}
      <button
        onClick={() => navigate('/analytics/savings')}
        className="bg-bg-secondary rounded-2xl p-3 flex flex-col items-center active:scale-[0.97] transition-transform"
      >
        <div className="flex items-center gap-1 mb-1 self-start">
          <span className="text-base">📊</span>
          <span className="text-text-secondary text-xs">Збереження</span>
        </div>
        <GaugeChart
          value={savingsRate?.rate ?? 0}
          max={50}
          size={80}
          color={savingsLevel?.color ?? '#8E8E93'}
        />
        <span className="text-text-primary font-bold text-sm -mt-1">
          {savingsRate?.rate?.toFixed(1) ?? '—'}%
        </span>
        {savingsLevel && (
          <span className="text-[10px] mt-0.5" style={{ color: savingsLevel.color }}>
            {savingsLevel.label}
          </span>
        )}
      </button>
    </div>
  );
}
