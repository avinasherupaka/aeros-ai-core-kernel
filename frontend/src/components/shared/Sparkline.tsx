import type { SeriesPoint } from '../../types/control-plane';

interface SparklineProps {
  data: SeriesPoint[];
  limit?: number | null;
  actionLimit?: number | null;
  height?: number;
  color?: string;
}

/** Inline SVG sparkline with optional alert/action limit reference lines. */
export function Sparkline({ data, limit, actionLimit, height = 64, color = '#38bdf8' }: SparklineProps) {
  const values = data.map((point) => point.value).filter((value): value is number => value !== null);
  if (values.length === 0) {
    return <div className="text-xs text-slate-500">No time-series data</div>;
  }

  const width = 260;
  const pad = 6;
  const refs = [limit, actionLimit].filter((value): value is number => value !== null && value !== undefined);
  const min = Math.min(...values, ...refs);
  const max = Math.max(...values, ...refs);
  const span = max - min || 1;

  const x = (index: number) => pad + (index / (data.length - 1 || 1)) * (width - pad * 2);
  const y = (value: number) => height - pad - ((value - min) / span) * (height - pad * 2);

  const path = data
    .map((point, index) => (point.value === null ? null : `${index === 0 ? 'M' : 'L'} ${x(index)} ${y(point.value)}`))
    .filter(Boolean)
    .join(' ');

  const areaPath = `${path} L ${x(data.length - 1)} ${height - pad} L ${x(0)} ${height - pad} Z`;

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="w-full" preserveAspectRatio="none" style={{ height }}>
      <defs>
        <linearGradient id="spark-fill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity={0.25} />
          <stop offset="100%" stopColor={color} stopOpacity={0} />
        </linearGradient>
      </defs>
      {limit !== null && limit !== undefined && (
        <line x1={pad} x2={width - pad} y1={y(limit)} y2={y(limit)} stroke="#f59e0b" strokeWidth={1} strokeDasharray="4 3" />
      )}
      {actionLimit !== null && actionLimit !== undefined && (
        <line x1={pad} x2={width - pad} y1={y(actionLimit)} y2={y(actionLimit)} stroke="#ef4444" strokeWidth={1} strokeDasharray="4 3" />
      )}
      <path d={areaPath} fill="url(#spark-fill)" />
      <path d={path} fill="none" stroke={color} strokeWidth={1.6} strokeLinejoin="round" />
    </svg>
  );
}
