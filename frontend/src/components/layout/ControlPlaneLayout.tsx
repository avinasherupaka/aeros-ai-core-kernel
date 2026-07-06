import type { FC, ReactNode } from 'react';

export interface ControlPlaneLayoutProps {
  sidebar?: ReactNode;
  header: ReactNode;
  content: ReactNode;
}

export const ControlPlaneLayout: FC<ControlPlaneLayoutProps> = ({ sidebar, header, content }) => (
  <div className="flex h-screen bg-slate-900 overflow-hidden text-slate-200">
    {sidebar && <div className="flex-shrink-0">{sidebar}</div>}
    <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
      <div className="bg-slate-900 border-b border-slate-800 px-6 py-4">
        {header}
      </div>
      <div className="flex-1 overflow-y-auto p-6 bg-slate-900">
        <div className="max-w-7xl mx-auto space-y-6">
          {content}
        </div>
      </div>
    </main>
  </div>
);
