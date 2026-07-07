import type { SeriesPoint, SeriesMeta } from '../../types/control-plane';
import { EmptyHint } from '../ui/primitives';
import { TrendingUp } from 'lucide-react';

interface SparklineProps {
  series: SeriesPoint[];
  meta: SeriesMeta;
  height?: number;
}

/** GMP-grade control chart with limit lines, breach shading, and peak annotation. */
export function Sparkline({ series, meta, height = 220 }: SparklineProps) {
  const values = series.map((p) => p.value).filter((v): v is number => v !== null);
  
  if (values.length === 0) {
    return <EmptyHint title="No time-series data" detail="No valid measurements in the window" icon={<TrendingUp className="text-ink3" size={24} />} />;
  }

  const width = 100; // Percentage-based for responsiveness
  const pad = { top: 12, right: 48, bottom: 32, left: 8 };
  
  // Collect all limit lines
  const limits: Array<{ value: number; label: string; color: string; dash: string }> = [];
  if (meta.alert_limit != null) {
    limits.push({ value: meta.alert_limit, label: `Alert ${meta.alert_limit}${meta.unit ?? ''}`, color: '#d97706', dash: '4,3' });
  }
  if (meta.action_limit != null) {
    limits.push({ value: meta.action_limit, label: `Action ${meta.action_limit}${meta.unit ?? ''}`, color: '#ea580c', dash: '4,3' });
  }
  if (meta.critical_limit != null) {
    limits.push({ value: meta.critical_limit, label: `Critical ${meta.critical_limit}${meta.unit ?? ''}`, color: '#dc2626', dash: '4,3' });
  }
  
  const limitValues = limits.map((l) => l.value);
  const min = Math.min(...values, ...limitValues) * 0.95;
  const max = Math.max(...values, ...limitValues) * 1.05;
  const span = max - min || 1;

  const chartWidth = width - pad.left - pad.right;
  const chartHeight = height - pad.top - pad.bottom;
  
  const xScale = (index: number) => pad.left + (index / Math.max(series.length - 1, 1)) * chartWidth;
  const yScale = (value: number) => pad.top + chartHeight - ((value - min) / span) * chartHeight;

  // Build the line path
  const linePath = series
    .map((p, i) => (p.value === null ? null : `${i === 0 ? 'M' : 'L'} ${xScale(i)} ${yScale(p.value)}`))
    .filter(Boolean)
    .join(' ');

  const areaPath = linePath + ` L ${xScale(series.length - 1)} ${yScale(min)} L ${xScale(0)} ${yScale(min)} Z`;

  // Breach shading
  const breachFrom = meta.breach_from_index ?? null;
  const breachTo = meta.breach_to_index ?? null;
  const hasBreachWindow = breachFrom != null && breachTo != null && breachFrom < breachTo;

  // Peak marker
  const peakIdx = meta.peak_index ?? null;
  const peakVal = meta.peak_value ?? null;
  const hasPeak = peakIdx != null && peakVal != null && peakIdx >= 0 && peakIdx < series.length;

  return (
    <div className="flex flex-col gap-2">
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full" preserveAspectRatio="xMidYMid meet" style={{ height }}>
        <defs>
          <linearGradient id="control-chart-fill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#6366f1" stopOpacity={0.12} />
            <stop offset="100%" stopColor="#6366f1" stopOpacity={0} />
          </linearGradient>
        </defs>

        {/* Breach window shading */}
        {hasBreachWindow && (
          <rect
            x={xScale(breachFrom)}
            y={pad.top}
            width={xScale(breachTo) - xScale(breachFrom)}
            height={chartHeight}
            fill="#dc2626"
            fillOpacity={0.08}
            stroke="#dc2626"
            strokeWidth={0.5}
            strokeDasharray="2,2"
          />
        )}

        {/* Limit lines */}
        {limits.map((limit, i) => (
          <g key={i}>
            <line
              x1={pad.left}
              x2={width - pad.right}
              y1={yScale(limit.value)}
              y2={yScale(limit.value)}
              stroke={limit.color}
              strokeWidth={1.2}
              strokeDasharray={limit.dash}
            />
            <text
              x={width - pad.right + 4}
              y={yScale(limit.value) + 3}
              className="text-[8px] fill-current"
              style={{ color: limit.color }}
            >
              {limit.label}
            </text>
          </g>
        ))}

        {/* Area + Line */}
        <path d={areaPath} fill="url(#control-chart-fill)" />
        <path d={linePath} fill="none" stroke="#6366f1" strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />

        {/* Peak annotation */}
        {hasPeak && (
          <g transform={`translate(${xScale(peakIdx)}, ${yScale(peakVal)})`}>
            <circle r={4} fill="#dc2626" stroke="#fff" strokeWidth={1.5} />
            <text x={0} y={-10} textAnchor="middle" className="text-[9px] font-semibold fill-current" style={{ color: '#dc2626' }}>
              {peakVal.toFixed(1)}{meta.unit ?? ''}
            </text>
          </g>
        )}

        {/* X axis label */}
        <text
          x={pad.left + chartWidth / 2}
          y={height - 6}
          textAnchor="middle"
          className="text-[10px] fill-ink3"
        >
          {meta.window_label}
        </text>

        {/* Y axis label */}
        <text
          x={4}
          y={pad.top - 2}
          className="text-[9px] fill-ink3"
        >
          {meta.unit ?? ''}
        </text>
      </svg>

      {/* Guidance caption */}
      {meta.guidance && (
        <p className="px-2 text-[10px] italic text-ink3">{meta.guidance}</p>
      )}

      {/* Compact legend */}
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 px-2 text-[9px]">
        <span className="flex items-center gap-1 text-ink3">
          <span className="h-2 w-3 rounded-sm bg-brand" />
          Measured
        </span>
        {limits.map((limit, i) => (
          <span key={i} className="flex items-center gap-1" style={{ color: limit.color }}>
            <span className="h-[1px] w-3 border-t" style={{ borderColor: limit.color, borderStyle: 'dashed' }} />
            {limit.label.split(' ')[0]}
          </span>
        ))}
        {hasBreachWindow && (
          <span className="flex items-center gap-1 text-status-red">
            <span className="h-2 w-3 rounded-sm bg-status-red opacity-20" />
            Breach
          </span>
        )}
      </div>
    </div>
  );
}
