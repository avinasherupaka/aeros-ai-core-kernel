import type { FC, ReactNode } from 'react';

export interface ControlPlaneLayoutProps {
  header: ReactNode;
  controls: ReactNode;
  content: ReactNode;
}

export const ControlPlaneLayout: FC<ControlPlaneLayoutProps> = ({ header, controls, content }) => (
  <main className="app-shell">
    {header}
    <section className="tabs">{controls}</section>
    {content}
  </main>
);
