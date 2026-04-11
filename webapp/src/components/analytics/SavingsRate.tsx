import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import { GaugeChart } from '../ui/GaugeChart';
import { formatCurrency, getSavingsLevel } from '../../utils/format';
import type { SavingsRateData } from '../../types';

interface SavingsRateProps {
  data: SavingsRateData | null;
  loading: boolean;
}

const LEVELS = [
  { label: 'Зняття коштів', range: '< 0%',   color: '#FF3B30', bg: '#3A1010' },
  { label: 'Базовий',       range: '0–8%',    color: '#FF9500', bg: '#3A2800' },
  { label: 'Добре',         range: '8–15%',   color: '#FFD60A', bg: '#2E2800' },
  { label: 'Надійний',      range: '15–23%',  color: '#30D158', bg: '#0E2E18' },
  { label: 'Відмінно',      range: '23–33%',  color: '#00D4C8', bg: '#082E2C' },
  { label: 'Чудово',        range: '33–42%',  color: '#32D74B', bg: '#0A2E10' },
  { label: 'Elite',         range: '> 42%',   color: '#BF5AF2', bg: '#28103A' },
];

export function SavingsRate({ data, loading }: SavingsRateProps) {
  if (loading || !data) {
    return <div className="h-64 bg-bg-secondary rounded-3xl animate-pulse" />;
  }

  const level = getSavingsLevel(data.rate);

  return (
    <div className="space-y-4">
      {/* Hero */}
      <div>
        <p className="text-text-primary text-4xl font-bold">{level.label}</p>
      </div>

      {/* Gauge */}
      <div className="bg-bg-secondary rounded-3xl p-4 flex flex-col items-center">
        <GaugeChart value={data.rate} max={50} size={180} color={level.color} />
        <div className="w-full grid grid-cols-3 gap-3 mt-3">
          <MetricCell label="Дохід" value={formatCurrency(data.income)} color="#30D158" />
          <MetricCell label="Збережено" value={formatCurrency(data.savings)} color="#00D4C8" />
          <MetricCell label="Норма" value={`${data.rate.toFixed(1)}%`} color={level.color} />
        </div>
      </div>

      {/* Monthly bar chart */}
      {data.monthly.length > 0 && (
        <div className="bg-bg-secondary rounded-3xl p-4">
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={data.monthly} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#252B3B" vertical={false} />
              <XAxis dataKey="month" tick={{ fill: '#8E8E93', fontSize: 10 }} tickLine={false} axisLine={false} />
              <YAxis tick={{ fill: '#8E8E93', fontSize: 10 }} tickLine={false} axisLine={false} />
              <Tooltip
                contentStyle={{ background: '#1D2334', border: '1px solid #252B3B', borderRadius: 12 }}
                labelStyle={{ color: '#8E8E93', fontSize: 11 }}
                itemStyle={{ fontSize: 11 }}
                formatter={(v) => [`${Number(v).toLocaleString('uk-UA')} ₴`, '']}
              />
              <Bar dataKey="income" fill="#30D158" radius={[4, 4, 0, 0]} name="Дохід" />
              <Bar dataKey="expenses" fill="#FF3B30" radius={[4, 4, 0, 0]} name="Витрати" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Info */}
      <div className="bg-bg-secondary rounded-3xl p-4 space-y-3">
        <p className="text-text-primary font-semibold text-sm">Що таке норма збережень?</p>
        <p className="text-text-secondary text-sm leading-relaxed">
          Ваша норма збережень — це відсоток доходу, який ви зберігаєте щомісяця. Позитивне
          значення означає, що ви збільшуєте свої заощадження, від'ємне — що ви витрачаєте
          свої резерви. Оптимальна норма зазвичай становить 15–20% або вище.
        </p>

        {/* Level bands */}
        <div className="space-y-2 pt-1">
          {LEVELS.map((l) => (
            <div
              key={l.label}
              className="flex items-center justify-between rounded-2xl px-4 py-3"
              style={{ backgroundColor: l.bg }}
            >
              <span className="font-semibold text-sm" style={{ color: l.color }}>{l.label}</span>
              <span className="text-sm" style={{ color: l.color }}>{l.range}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function MetricCell({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="flex flex-col items-center bg-bg-tertiary rounded-2xl px-2 py-3 gap-1">
      <span className="text-text-secondary text-xs">{label}</span>
      <span className="font-semibold text-sm" style={{ color }}>{value}</span>
    </div>
  );
}
