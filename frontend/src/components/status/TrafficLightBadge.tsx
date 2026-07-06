import type { FC } from 'react';

import type { StatusBadgeProps } from '../../types/control-plane';

const STATUS_CONFIG: Record<string, { color: string; label: string }> = {
  green: { color: '#16a34a', label: 'Green' },
  yellow: { color: '#f59e0b', label: 'Yellow' },
  red: { color: '#dc2626', label: 'Red' },
  unknown: { color: '#6b7280', label: 'Unknown' },
};

export const TrafficLightBadge: FC<StatusBadgeProps> = ({ status, label }) => {
  const config = STATUS_CONFIG[status] ?? STATUS_CONFIG.unknown;

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.45rem',
        padding: '0.2rem 0.55rem',
        borderRadius: '999px',
        border: `1px solid ${config.color}`,
        color: '#111827',
        background: '#ffffff',
        fontSize: '0.8rem',
        fontWeight: 600,
      }}
      title={`Status: ${config.label}`}
      aria-label={`Status ${config.label}`}
    >
      <span
        aria-hidden
        style={{
          width: '0.55rem',
          height: '0.55rem',
          borderRadius: '50%',
          background: config.color,
          display: 'inline-block',
        }}
      />
      <span>{label ?? config.label}</span>
    </span>
  );
};
