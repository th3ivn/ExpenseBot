interface GaugeChartProps {
  value: number;
  min?: number;
  max?: number;
  size?: number;
  color?: string;
}

export function GaugeChart({ value, min = 0, max = 50, size = 100, color = '#00D4AA' }: GaugeChartProps) {
  const strokeWidth = 12;
  const radius = (size - strokeWidth) / 2;
  const cx = size / 2;
  const cy = size / 2;

  // 180-degree arc (semicircle)
  const startAngle = -180;
  const endAngle = 0;
  const angleRange = endAngle - startAngle;

  const ratio = Math.min(Math.max((value - min) / (max - min), 0), 1);
  const fillAngle = startAngle + ratio * angleRange;

  function polarToCartesian(cx: number, cy: number, r: number, angleDeg: number) {
    const rad = ((angleDeg - 90) * Math.PI) / 180;
    return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
  }

  function describeArc(cx: number, cy: number, r: number, start: number, end: number) {
    const s = polarToCartesian(cx, cy, r, end);
    const e = polarToCartesian(cx, cy, r, start);
    const large = end - start <= 180 ? 0 : 1;
    return `M ${s.x} ${s.y} A ${r} ${r} 0 ${large} 0 ${e.x} ${e.y}`;
  }

  const trackPath = describeArc(cx, cy, radius, startAngle, endAngle);
  const fillPath = ratio > 0 ? describeArc(cx, cy, radius, startAngle, fillAngle) : '';

  return (
    <div className="inline-flex flex-col items-center">
      <svg width={size} height={size / 2 + strokeWidth / 2 + 4}>
        <path d={trackPath} fill="none" stroke="#2C2C2E" strokeWidth={strokeWidth} strokeLinecap="round" />
        {fillPath && (
          <path d={fillPath} fill="none" stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" />
        )}
      </svg>
    </div>
  );
}
