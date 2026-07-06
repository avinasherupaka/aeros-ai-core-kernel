import type { FC } from 'react';

export interface LoadingStateProps {
  title?: string;
  detail?: string;
}

export const LoadingState: FC<LoadingStateProps> = ({
  title = 'Loading control-plane data…',
  detail = 'Collecting enterprise readiness, workflow, and evidence signals.',
}) => (
  <div className="state-panel loading" role="status" aria-live="polite">
    <div className="spinner" aria-hidden />
    <div>
      <p className="state-title">{title}</p>
      <p className="state-detail">{detail}</p>
    </div>
  </div>
);
