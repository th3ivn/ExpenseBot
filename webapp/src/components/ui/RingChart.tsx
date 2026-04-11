interface RingChartProps {
  value: number;
  max: number;
  size?: number;
  strokeWidth?: number;
  color?: string;
  children?: React.ReactNode;
}

export function RingChart({
  value,
  max,
  size = 200,
  strokeWidth = 16,
  color = '#00D4C8',
  children,
}: RingChartProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const ratio = max > 0 ? Math.min(value / max, 1) : 0;
  const dash = ratio * circumference;
  const cx = size / 2;
  const cy = size / 2;
  const ringColor = value > max ? '#FF3B30' : color;

  // Generate dot positions around the ring
  const dotCount = 36;
  const dotRadius = 3;
  const dotOrbitR = radius + strokeWidth * 0.85;
  const dots = Array.from({ length: dotCount }, (_, i) => {
    const angle = (i / dotCount) * 2 * Math.PI - Math.PI / 2;
    return {
      x: cx + dotOrbitR * Math.cos(angle),
      y: cy + dotOrbitR * Math.sin(angle),
    };
  });

  return (
    <div
      className="relative inline-flex items-center justify-center"
      style={{ width: size, height: size }}
    >
      <svg width={size} height={size} style={{ transform: 'rotate(0deg)' }}>
        {/* Dot pattern */}
        {dots.map((d, i) => (
          <circle key={i} cx={d.x} cy={d.y} r={dotRadius} fill="#252B3B" />
        ))}
        {/* Track */}
        <circle
          cx={cx} cy={cy} r={radius}
          fill="none"
          stroke="#1D2334"
          strokeWidth={strokeWidth}
          style={{ transform: 'rotate(-90deg)', transformOrigin: `${cx}px ${cy}px` }}
        />
        {/* Fill */}
        <circle
          cx={cx} cy={cy} r={radius}
          fill="none"
          stroke={ringColor}
          strokeWidth={strokeWidth}
          strokeDasharray={`${dash} ${circumference - dash}`}
          strokeLinecap="round"
          style={{
            transform: 'rotate(-90deg)',
            transformOrigin: `${cx}px ${cy}px`,
            transition: 'stroke-dasharray 0.6s ease',
          }}
        />
      </svg>
      {children && (
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          {children}
        </div>
      )}
    </div>
  );
}
