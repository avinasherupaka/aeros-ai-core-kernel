import type { EventStatus, TrafficLight } from '../types/control-plane';

export type Status = TrafficLight | EventStatus;

/** Map any operational status to muted ISA-101 status tokens. */
export const statusColor = (status: Status): { text: string; bg: string; border: string; dot: string; hex: string } => {
  switch (status) {
    case 'red':
      return { text: 'text-status-red', bg: 'bg-status-red/10', border: 'border-status-red/40', dot: 'bg-status-red', hex: '#ef4444' };
    case 'yellow':
      return { text: 'text-status-yellow', bg: 'bg-status-yellow/10', border: 'border-status-yellow/40', dot: 'bg-status-yellow', hex: '#f59e0b' };
    case 'green':
      return { text: 'text-status-green', bg: 'bg-status-green/10', border: 'border-status-green/30', dot: 'bg-status-green', hex: '#10b981' };
    default:
      return { text: 'text-slate-400', bg: 'bg-slate-700/20', border: 'border-slate-600/40', dot: 'bg-slate-500', hex: '#64748b' };
  }
};

export const statusHex = (status: Status): string => statusColor(status).hex;

export const cx = (...classes: Array<string | false | null | undefined>): string =>
  classes.filter(Boolean).join(' ');

/** Rank statuses so red sorts first (most urgent). */
export const statusRank = (status: Status): number => {
  switch (status) {
    case 'red':
      return 0;
    case 'yellow':
      return 1;
    case 'green':
      return 2;
    default:
      return 3;
  }
};

export const formatNumber = (value: number | null | undefined, digits = 1): string =>
  value === null || value === undefined ? '—' : Number(value).toFixed(digits);
