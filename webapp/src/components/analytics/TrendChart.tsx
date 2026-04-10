import { LineChart } from '../ui/LineChart';
import type { TrendData } from '../../types';
import { formatCurrency } from '../../utils/format';

interface TrendChartProps {
  data: TrendData[];
  loading: boolean;
}

export function TrendChart({ data, loading }: TrendChartProps) {
  if (loading) {
    return <div className="h-56 bg-bg-secondary rounded-2xl animate-pulse" />;
  }

  const latest = data[data.length - 1];
  const trendChange =
    data.length >= 2
      ? ((data[data.length - 1].current - data[data.length - 2].current) /
          (data[data.length - 2].current || 1)) *
        100
      : 0;

  return (
    <div className="bg-bg-secondary rounded-2xl p-4">
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-text-secondary text-xs">Поточний місяць</p>
          <p className="text-text-primary text-xl font-bold mt-0.5">
            {latest ? formatCurrency(latest.current) : '—'}
          </p>
        </div>
        <div className="text-right">
          <span
            className={`text-sm font-semibold ${trendChange >= 0 ? 'text-accent-red' : 'text-accent-green'}`}
          >
            {trendChange >= 0 ? '▲' : '▼'} {Math.abs(trendChange).toFixed(1)}%
          </span>
          <p className="text-text-secondary text-xs mt-0.5">vs попередній</p>
        </div>
      </div>
      <LineChart data={data} />
      <div className="flex items-center gap-4 mt-3">
        <div className="flex items-center gap-1.5">
          <div className="w-4 h-0.5 bg-accent-cyan rounded" />
          <span className="text-text-secondary text-xs">Поточний</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-4 h-0.5 bg-text-secondary rounded" style={{ borderTop: '2px dashed #8E8E93', background: 'none' }} />
          <span className="text-text-secondary text-xs">Середнє (3 міс.)</span>
        </div>
      </div>
    </div>
  );
}
