import { GaugeChart } from '../ui/GaugeChart';
import { formatCurrency, getSavingsLevel } from '../../utils/format';
import type { SavingsRateData } from '../../types';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';

interface SavingsRateProps {
  data: SavingsRateData | null;
  loading: boolean;
}

export function SavingsRate({ data, loading }: SavingsRateProps) {
  if (loading || !data) {
    return <div className="h-64 bg-bg-secondary rounded-2xl animate-pulse" />;
  }

  const level = getSavingsLevel(data.rate);

  return (
    <div className="space-y-3">
      <div className="bg-bg-secondary rounded-2xl p-4 flex flex-col items-center">
        <GaugeChart value={data.rate} max={50} size={140} color={level.color} />
        <p className="text-text-primary text-3xl font-bold -mt-2">{data.rate.toFixed(1)}%</p>
        <p className="font-semibold text-sm mt-1" style={{ color: level.color }}>
          {level.label}
        </p>

        <div className="w-full grid grid-cols-3 gap-2 mt-4">
          <MetricCell label="Доходи" value={formatCurrency(data.income)} className="text-accent-green" />
          <MetricCell label="Збережено" value={formatCurrency(data.savings)} className="text-accent-cyan" />
          <MetricCell label="Норма" value={`${data.rate.toFixed(1)}%`} className="text-text-primary" />
        </div>
      </div>

      {data.monthly.length > 0 && (
        <div className="bg-bg-secondary rounded-2xl p-4">
          <p className="text-text-secondary text-xs font-medium mb-3">По місяцях</p>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={data.monthly} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2C2C2E" />
              <XAxis dataKey="month" tick={{ fill: '#8E8E93', fontSize: 10 }} tickLine={false} axisLine={false} />
              <YAxis tick={{ fill: '#8E8E93', fontSize: 10 }} tickLine={false} axisLine={false} />
              <Tooltip
                contentStyle={{ background: '#1C1C1E', border: '1px solid #2C2C2E', borderRadius: 8 }}
                labelStyle={{ color: '#8E8E93', fontSize: 11 }}
                itemStyle={{ fontSize: 11 }}
                formatter={(v) => [`${Number(v).toLocaleString('uk-UA')} ₴`, '']}
              />
              <Bar dataKey="income" fill="#34C759" radius={[3, 3, 0, 0]} name="Дохід" />
              <Bar dataKey="expenses" fill="#FF3B30" radius={[3, 3, 0, 0]} name="Витрати" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

function MetricCell({
  label,
  value,
  className,
}: {
  label: string;
  value: string;
  className?: string;
}) {
  return (
    <div className="flex flex-col items-center bg-bg-tertiary rounded-xl p-2 gap-0.5">
      <span className="text-text-secondary text-[10px]">{label}</span>
      <span className={`font-semibold text-xs ${className}`}>{value}</span>
    </div>
  );
}
