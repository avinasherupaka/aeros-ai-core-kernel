import type { FC } from 'react';

export interface EmptyStateProps {
  title: string;
  detail: string;
}

export const EmptyState: FC<EmptyStateProps> = ({ title, detail }) => (
  <div className="state-panel empty">
    <p className="state-title">{title}</p>
    <p className="state-detail">{detail}</p>
  </div>
);
