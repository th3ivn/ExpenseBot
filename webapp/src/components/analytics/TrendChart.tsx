import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  ReferenceLine,
} from 'recharts';
import type { TrendData } from '../../types';
import { formatCurrency } from '../../utils/format';

interface TrendChartProps {
  data: TrendData[];
  loading: boolean;
}

export function TrendChart({ data, loading }: TrendChartProps) {
  if (loading) {
    return <div className="h-72 bg-bg-secondary rounded-3xl animate-pulse" />;
  }

  const latest = data[data.length - 1];

  // Get current month label
  const now = new Date();
  const monthLabel = now.toLocaleDateString('uk-UA', { month: 'long', year: 'numeric' });

  return (
    <div className="space-y-4">
      <div>
        <p className="text-text-secondary text-sm">{monthLabel}</p>
        <p className="text-text-primary text-4xl font-bold mt-1">
          {latest ? formatCurrency(latest.current) : '0 ₴'}
        </p>
      </div>

      <div className="bg-bg-secondary rounded-3xl p-4">
        {data.length === 0 ? (
          <div className="h-48 flex items-center justify-center text-text-secondary text-sm">
            Немає даних
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={200} minWidth={10}>
            <AreaChart data={data} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="trendGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00D4C8" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#00D4C8" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#252B3B" vertical={false} />
              <XAxis
                dataKey="date"
                tick={{ fill: '#8E8E93', fontSize: 11 }}
                tickLine={false}
                axisLine={false}
              />
              <YAxis tick={{ fill: '#8E8E93', fontSize: 11 }} tickLine={false} axisLine={false} />
              <Tooltip
                contentStyle={{
                  background: '#1D2334',
                  border: '1px solid #252B3B',
                  borderRadius: 12,
                  padding: '8px 12px',
                }}
                labelStyle={{ color: '#8E8E93', fontSize: 11, marginBottom: 4 }}
                itemStyle={{ color: '#fff', fontSize: 12 }}
                formatter={(v) => [`${Number(v).toLocaleString('uk-UA')} ₴`, '']}
              />
              <Area
                type="monotone"
                dataKey="current"
                stroke="#00D4C8"
                strokeWidth={2.5}
                fill="url(#trendGrad)"
                dot={{ fill: '#00D4C8', r: 4, strokeWidth: 0 }}
                activeDot={{ fill: '#00D4C8', r: 6 }}
                name="Поточний"
              />
              <ReferenceLine
                y={data[0]?.average ?? 0}
                stroke="#8E8E93"
                strokeDasharray="5 5"
                strokeWidth={1.5}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}

        <div className="flex items-center gap-6 mt-3">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-accent-cyan" />
            <span className="text-text-secondary text-xs">
              {now.toLocaleDateString('uk-UA', { month: 'short', year: 'numeric' })}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-0 border-t-2 border-dashed border-text-secondary" />
            <span className="text-text-secondary text-xs">В середньому</span>
          </div>
        </div>
      </div>

      {/* Info */}
      <div className="bg-bg-secondary rounded-3xl p-4 space-y-3">
        <p className="text-text-primary font-semibold text-sm">Що таке тренд витрат?</p>
        <p className="text-text-secondary text-sm leading-relaxed">
          Порівняйте витрати поточного місяця з середнім показником за останні 3 місяці, щоб
          виявити закономірності та залишатися в рамках бюджетних цілей.
        </p>
        <p className="text-text-secondary text-sm leading-relaxed">
          Суцільна лінія показує ваші поточні витрати, а пунктирна — середні витрати за останні
          3 місяці.
        </p>
      </div>
    </div>
  );
}
