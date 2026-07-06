import type { FC } from 'react';

export interface SLAIndicatorProps {
  breached: boolean;
}

export const SLAIndicator: FC<SLAIndicatorProps> = ({ breached }) => (
  <span className={breached ? 'sla-pill breached' : 'sla-pill'}>
    {breached ? 'SLA Breach' : 'SLA Within Target'}
  </span>
);
