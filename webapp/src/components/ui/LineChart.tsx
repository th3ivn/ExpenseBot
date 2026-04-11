import {
  LineChart as ReLineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import type { TrendData } from '../../types';

interface LineChartProps {
  data: TrendData[];
  mini?: boolean;
}

export function LineChart({ data, mini }: LineChartProps) {
  if (mini) {
    if (data.length === 0) {
      return <div style={{ height: 40 }} />;
    }
    return (
      <ResponsiveContainer width="100%" height={40}>
        <ReLineChart data={data} margin={{ top: 2, right: 2, left: 2, bottom: 2 }}>
          <Line
            type="monotone"
            dataKey="current"
            stroke="#00D4AA"
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
          />
          <Line
            type="monotone"
            dataKey="average"
            stroke="#8E8E93"
            strokeWidth={1.5}
            strokeDasharray="3 3"
            dot={false}
            isAnimationActive={false}
          />
        </ReLineChart>
      </ResponsiveContainer>
    );
  }

  if (data.length === 0) {
    return (
      <div
        style={{ height: 220 }}
        className="flex items-center justify-center text-text-secondary text-sm"
      >
        Немає даних
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={220} minWidth={10}>
      <ReLineChart data={data} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2C2C2E" />
        <XAxis
          dataKey="date"
          tick={{ fill: '#8E8E93', fontSize: 11 }}
          tickLine={false}
          axisLine={false}
        />
        <YAxis tick={{ fill: '#8E8E93', fontSize: 11 }} tickLine={false} axisLine={false} />
        <Tooltip
          contentStyle={{ background: '#1C1C1E', border: '1px solid #2C2C2E', borderRadius: 8 }}
          labelStyle={{ color: '#8E8E93', fontSize: 12 }}
          itemStyle={{ color: '#fff', fontSize: 12 }}
          formatter={(v) => [`${Number(v).toLocaleString('uk-UA')} ₴`, '']}
        />
        <Line
          type="monotone"
          dataKey="current"
          stroke="#00D4AA"
          strokeWidth={2.5}
          dot={{ fill: '#00D4AA', r: 3 }}
          name="Поточний"
        />
        <Line
          type="monotone"
          dataKey="average"
          stroke="#8E8E93"
          strokeWidth={2}
          strokeDasharray="5 5"
          dot={false}
          name="Середнє (3 міс.)"
        />
      </ReLineChart>
    </ResponsiveContainer>
  );
}
