const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export default function App() {
  return (
    <main style={{ fontFamily: 'Arial, sans-serif', margin: '3rem auto', maxWidth: '72rem', padding: '0 1.5rem' }}>
      <p style={{ color: '#4f46e5', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase' }}>
        Enterprise Manufacturing Control Plane
      </p>
      <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>Areos local UI scaffold</h1>
      <p style={{ color: '#374151', lineHeight: 1.6 }}>
        This Vite/React shell is ready to host the control plane dashboards, readiness workflows, and MCP assistant panel.
      </p>
      <section style={{ background: '#111827', borderRadius: '1rem', color: '#f9fafb', marginTop: '2rem', padding: '1.5rem' }}>
        <h2 style={{ marginTop: 0 }}>Runtime configuration</h2>
        <ul>
          <li>API base URL: {apiBaseUrl}</li>
          <li>Mode: local mock compose stack</li>
          <li>Frontend: React + TypeScript + Vite</li>
        </ul>
      </section>
    </main>
  );
}
