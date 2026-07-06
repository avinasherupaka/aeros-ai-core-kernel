import type { FC, ReactNode } from 'react';

export interface DrilldownCardProps {
  title: string;
  subtitle?: string;
  action?: ReactNode;
  children: ReactNode;
}

export const DrilldownCard: FC<DrilldownCardProps> = ({ title, subtitle, action, children }) => (
  <article className="card drilldown-card">
    <header className="card-head">
      <div>
        <h3>{title}</h3>
        {subtitle ? <p className="card-subtitle">{subtitle}</p> : null}
      </div>
      {action}
    </header>
    <div>{children}</div>
  </article>
);
