import type { ReactNode } from 'react';
import { cx, statusColor, type Status } from '../../lib/design';

/** Elevated white content panel. */
export function Panel({ className, children }: { className?: string; children: ReactNode }) {
  return <div className={cx('rounded-lg border border-line bg-panel shadow-panel', className)}>{children}</div>;
}

export function PanelHeader({ title, subtitle, right }: { title: ReactNode; subtitle?: ReactNode; right?: ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-3 border-b border-line px-4 py-3">
      <div>
        <div className="text-sm font-semibold text-ink">{title}</div>
        {subtitle && <div className="mt-0.5 text-xs text-ink3">{subtitle}</div>}
      </div>
      {right}
    </div>
  );
}

export function SectionLabel({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cx('text-[11px] font-semibold uppercase tracking-wider text-ink3', className)}>{children}</div>;
}

export function StatusDot({ status, pulse, size = 10 }: { status: Status; pulse?: boolean; size?: number }) {
  const sc = statusColor(status);
  return (
    <span
      className={cx('inline-block rounded-full', sc.dot, pulse && status !== 'green' && 'animate-breathe')}
      style={{ width: size, height: size }}
    />
  );
}

export function StatusPill({ status, label, className }: { status: Status; label?: string; className?: string }) {
  const sc = statusColor(status);
  return (
    <span className={cx('inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[11px] font-medium', sc.bg, sc.border, sc.text, className)}>
      <span className={cx('h-1.5 w-1.5 rounded-full', sc.dot)} />
      {label ?? sc.label}
    </span>
  );
}

export function Badge({ children, tone = 'neutral', className }: { children: ReactNode; tone?: 'neutral' | 'brand'; className?: string }) {
  const tones = {
    neutral: 'bg-panel2 text-ink2 border-line',
    brand: 'bg-brand-soft text-brand border-brand-ring',
  } as const;
  return <span className={cx('inline-flex items-center rounded border px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wide', tones[tone], className)}>{children}</span>;
}

export function ProgressBar({ pct, className }: { pct: number; className?: string }) {
  const clamped = Math.max(0, Math.min(100, pct));
  const tone = clamped >= 90 ? 'bg-status-green' : clamped >= 60 ? 'bg-status-amber' : 'bg-status-red';
  return (
    <div className={cx('h-2 overflow-hidden rounded-full bg-panel3', className)}>
      <div className={cx('h-full rounded-full transition-all', tone)} style={{ width: `${clamped}%` }} />
    </div>
  );
}

export function Legend({ items }: { items: Array<{ status: Status; label: string }> }) {
  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
      {items.map((item) => (
        <span key={item.label} className="flex items-center gap-1.5 text-[11px] text-ink3">
          <StatusDot status={item.status} size={8} />
          {item.label}
        </span>
      ))}
    </div>
  );
}

export function EmptyHint({ title, detail, icon }: { title: string; detail?: string; icon?: ReactNode }) {
  return (
    <div className="flex h-full min-h-[200px] flex-col items-center justify-center p-8 text-center">
      {icon}
      <p className="mt-3 text-sm font-medium text-ink2">{title}</p>
      {detail && <p className="mt-1 max-w-md text-xs text-ink3">{detail}</p>}
    </div>
  );
}
