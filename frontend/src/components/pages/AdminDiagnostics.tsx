import type { FC } from 'react';

export interface AdminDiagnosticsProps {
  diagnostics: Record<string, unknown> | null;
  error: string | null;
}

export const AdminDiagnostics: FC<AdminDiagnosticsProps> = ({ diagnostics, error }) => (
  <section className="stack">
    <h2>Admin Diagnostics</h2>
    <p className="card-note">Admin-only infrastructure diagnostics remain restricted to this workspace.</p>
    {error ? <p className="status error">{error}</p> : null}
    {diagnostics ? (
      <article className="card">
        <p><strong>Mode:</strong> {String(diagnostics.mode ?? 'unknown')}</p>
        <p><strong>Sections:</strong> {Object.keys(diagnostics).join(', ')}</p>
        <pre className="markdown-box">{JSON.stringify(diagnostics, null, 2)}</pre>
      </article>
    ) : (
      <p className="status">Loading diagnostics…</p>
    )}
  </section>
);
