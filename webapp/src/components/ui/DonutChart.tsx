interface DonutChartProps {
  data: Array<{ value: number; color: string; label?: string }>;
  size?: number;
  strokeWidth?: number;
  centerLabel?: string;
  centerSublabel?: string;
}

export function DonutChart({
  data,
  size = 80,
  strokeWidth = 10,
  centerLabel,
  centerSublabel,
}: DonutChartProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const total = data.reduce((s, d) => s + d.value, 0);

  let offset = 0;
  const slices = data.map((d) => {
    const fraction = total > 0 ? d.value / total : 0;
    const dash = fraction * circumference;
    const gap = circumference - dash;
    const slice = { ...d, dash, gap, offset };
    offset += dash;
    return slice;
  });

  const cx = size / 2;
  const cy = size / 2;
  const fontSize = size > 150 ? 18 : size > 80 ? 12 : 9;
  const subFontSize = size > 150 ? 13 : size > 80 ? 10 : 8;

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        <circle cx={cx} cy={cy} r={radius} fill="none" stroke="#252B3B" strokeWidth={strokeWidth} />
        {slices.map((s, i) => (
          <circle
            key={i}
            cx={cx} cy={cy} r={radius}
            fill="none"
            stroke={s.color}
            strokeWidth={strokeWidth}
            strokeDasharray={`${s.dash} ${s.gap}`}
            strokeDashoffset={-s.offset}
            strokeLinecap="butt"
          />
        ))}
      </svg>
      {(centerLabel ?? centerSublabel) && (
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none px-2">
          {centerSublabel && (
            <span className="text-text-secondary text-center leading-tight" style={{ fontSize: subFontSize }}>
              {centerSublabel}
            </span>
          )}
          {centerLabel && (
            <span className="text-text-primary font-bold text-center leading-tight" style={{ fontSize }}>
              {centerLabel}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
