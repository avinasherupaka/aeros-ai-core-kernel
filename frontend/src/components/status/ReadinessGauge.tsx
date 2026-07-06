import type { FC } from 'react';

import type { TrafficLight } from '../../types/control-plane';

export interface ReadinessGaugeProps {
  value: number;
  status: TrafficLight;
}

export const ReadinessGauge: FC<ReadinessGaugeProps> = ({ value, status }) => {
  const bounded = Math.max(0, Math.min(value, 100));
  return (
    <div className="readiness-gauge">
      <div className={`readiness-gauge-fill ${status}`} style={{ width: `${bounded}%` }} />
      <span>{bounded}%</span>
    </div>
  );
};
