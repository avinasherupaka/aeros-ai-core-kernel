import type { FC } from 'react';
import clsx from 'clsx';
import type { StatusBadgeProps } from '../../types/control-plane';

const STATUS_CONFIG: Record<string, { bg: string; dot: string; text: string; label: string }> = {
  green: { bg: 'bg-green-950/30', dot: 'bg-green-500', text: 'text-green-400', label: 'Green' },
  yellow: { bg: 'bg-yellow-950/30', dot: 'bg-yellow-500', text: 'text-yellow-400', label: 'Yellow' },
  red: { bg: 'bg-red-950/30', dot: 'bg-red-500', text: 'text-red-400', label: 'Red' },
  unknown: { bg: 'bg-slate-800', dot: 'bg-slate-500', text: 'text-slate-400', label: 'Unknown' },
};

export const TrafficLightBadge: FC<StatusBadgeProps> = ({ status, label }) => {
  const config = STATUS_CONFIG[status] ?? STATUS_CONFIG.unknown;

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium border border-slate-700',
        config.bg,
        config.text
      )}
      title={`Status: ${config.label}`}
      aria-label={`Status ${config.label}`}
    >
      <span
        aria-hidden
        className={clsx('w-1.5 h-1.5 rounded-full', config.dot)}
      />
      <span>{label ?? config.label}</span>
    </span>
  );
};
