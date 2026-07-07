import type { EventStatus, TrafficLight } from '../types/control-plane';

export type Status = TrafficLight | EventStatus;

export interface StatusTokens {
  text: string;
  bg: string;
  border: string;
  dot: string;
  hex: string;
  label: string;
}

/** Map any operational status to accessible light-theme status tokens. */
export const statusColor = (status: Status): StatusTokens => {
  switch (status) {
    case 'red':
      return { text: 'text-status-red', bg: 'bg-status-red-soft', border: 'border-status-red-line', dot: 'bg-status-red', hex: '#dc2626', label: 'Critical' };
    case 'yellow':
      return { text: 'text-status-amber', bg: 'bg-status-amber-soft', border: 'border-status-amber-line', dot: 'bg-status-amber', hex: '#d97706', label: 'Warning' };
    case 'green':
      return { text: 'text-status-green', bg: 'bg-status-green-soft', border: 'border-status-green-line', dot: 'bg-status-green', hex: '#059669', label: 'Nominal' };
    default:
      return { text: 'text-ink3', bg: 'bg-status-neutral-soft', border: 'border-line', dot: 'bg-status-neutral', hex: '#94a3b8', label: 'Not evaluated' };
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

export const titleCase = (value: string | null | undefined): string =>
  !value ? '' : value.replace(/[_-]+/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
