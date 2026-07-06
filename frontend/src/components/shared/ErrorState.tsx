import type { FC } from 'react';

export interface ErrorStateProps {
  title?: string;
  detail: string;
  onRetry?: () => void;
}

export const ErrorState: FC<ErrorStateProps> = ({
  title = 'Unable to load control-plane data',
  detail,
  onRetry,
}) => (
  <div className="state-panel error" role="alert">
    <div>
      <p className="state-title">{title}</p>
      <p className="state-detail">{detail}</p>
    </div>
    {onRetry ? (
      <button type="button" className="primary-button" onClick={onRetry}>
        Retry load
      </button>
    ) : null}
  </div>
);
