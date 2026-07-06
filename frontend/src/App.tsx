import { useEffect, useMemo, useState } from 'react';

import { AssistantPanel } from './components/assistant/AssistantPanel';
import { SiteHealthCard } from './components/cards/SiteHealthCard';
import { TrafficLightBadge } from './components/status/TrafficLightBadge';
import type {
  AssistantQueryRequest,
  AssistantResponse,
  ConnectorStatusCard,
  DossierReadinessCard,
  EnterpriseReadinessRollup,
  ManufacturingSiteTopology,
  PersonaType,
  PersonaWorkflowCard,
  SiteHealthCard as SiteHealthCardModel,
} from './types/control-plane';

type ViewMode = 'dashboard' | 'topology' | 'qa' | 'dossier' | 'assistant' | 'admin';

type CapaQueueItem = {
  record_id: string;
  site_label: string;
  summary: string;
  owner: string;
  priority: string;
  status: string;
  due_label: string;
};

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

const PERSONAS: Array<{ id: PersonaType; label: string }> = [
  { id: 'system_admin', label: 'System Admin' },
  { id: 'qa', label: 'Quality Assurance' },
  { id: 'plant_ops', label: 'Plant Ops' },
  { id: 'engineering', label: 'Engineering' },
  { id: 'leadership', label: 'Leadership' },
];

const VIEWS: Array<{ id: ViewMode; label: string }> = [
  { id: 'dashboard', label: 'Dashboard' },
  { id: 'topology', label: 'Topology Map' },
  { id: 'qa', label: 'QA Release Board' },
  { id: 'dossier', label: 'Dossier Viewer' },
  { id: 'assistant', label: 'Assistant Chat' },
  { id: 'admin', label: 'Admin Diagnostics' },
];

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`${response.status} ${response.statusText}: ${body}`);
  }

  return response.json() as Promise<T>;
}

export default function App() {
  const [persona, setPersona] = useState<PersonaType>('qa');
  const [view, setView] = useState<ViewMode>('dashboard');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [sites, setSites] = useState<SiteHealthCardModel[]>([]);
  const [connectors, setConnectors] = useState<ConnectorStatusCard[]>([]);
  const [readiness, setReadiness] = useState<EnterpriseReadinessRollup | null>(null);
  const [topology, setTopology] = useState<ManufacturingSiteTopology[]>([]);
  const [workflow, setWorkflow] = useState<PersonaWorkflowCard | null>(null);
  const [queue, setQueue] = useState<CapaQueueItem[]>([]);

  const [batchId, setBatchId] = useState('BATCH-OSD-0421');
  const [dossier, setDossier] = useState<DossierReadinessCard | null>(null);
  const [assistantResponse, setAssistantResponse] = useState<AssistantResponse | null>(null);
  const [adminDiagnostics, setAdminDiagnostics] = useState<Record<string, unknown> | null>(null);
  const [adminError, setAdminError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      setLoading(true);
      setError(null);

      try {
        const [sitesData, connectorsData, readinessData, topologyData, workflowData, queueData, dossierData] = await Promise.all([
          fetchJson<{ sites: SiteHealthCardModel[] }>('/cp/sites'),
          fetchJson<{ connectors: ConnectorStatusCard[] }>('/cp/connectors'),
          fetchJson<{ enterprise_readiness: EnterpriseReadinessRollup }>('/cp/readiness'),
          fetchJson<{ topology: ManufacturingSiteTopology[] }>('/cp/topology'),
          fetchJson<{ workflow: PersonaWorkflowCard }>(`/cp/personas/${persona}/workflow`),
          fetchJson<{ queue: CapaQueueItem[] }>('/cp/capa/queue'),
          fetchJson<{ dossier: DossierReadinessCard }>(`/cp/dossiers/${encodeURIComponent(batchId)}`),
        ]);

        if (cancelled) {
          return;
        }

        setSites(sitesData.sites);
        setConnectors(connectorsData.connectors);
        setReadiness(readinessData.enterprise_readiness);
        setTopology(topologyData.topology);
        setWorkflow(workflowData.workflow);
        setQueue(queueData.queue);
        setDossier(dossierData.dossier);
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : 'Failed to load control-plane data.');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    load();

    return () => {
      cancelled = true;
    };
  }, [persona, batchId]);

  useEffect(() => {
    if (view !== 'admin') {
      return;
    }

    let cancelled = false;

    const loadAdmin = async () => {
      setAdminError(null);
      try {
        const data = await fetchJson<Record<string, unknown>>('/cp/admin/diagnostics');
        if (!cancelled) {
          setAdminDiagnostics(data);
        }
      } catch (adminLoadError) {
        if (!cancelled) {
          setAdminError(adminLoadError instanceof Error ? adminLoadError.message : 'Failed to load admin diagnostics.');
          setAdminDiagnostics(null);
        }
      }
    };

    loadAdmin();

    return () => {
      cancelled = true;
    };
  }, [view]);

  const statusSummary = useMemo(() => {
    if (!readiness) {
      return null;
    }
    return [
      { label: 'Overall', value: readiness.overall_status, status: readiness.overall_status },
      { label: 'Sites', value: String(readiness.total_sites), status: readiness.overall_status },
      { label: 'Red', value: String(readiness.red_sites), status: readiness.red_sites ? 'red' : 'green' },
      { label: 'Yellow', value: String(readiness.yellow_sites), status: readiness.yellow_sites ? 'yellow' : 'green' },
      { label: 'Green', value: String(readiness.green_sites), status: readiness.green_sites ? 'green' : 'unknown' },
    ] as const;
  }, [readiness]);

  const submitAssistantQuestion = async (request: AssistantQueryRequest) => {
    setAssistantResponse(null);
    setError(null);

    try {
      const response = await fetchJson<AssistantResponse>('/cp/assistant/query', {
        method: 'POST',
        body: JSON.stringify(request),
      });
      setAssistantResponse(response);
      setView('assistant');
    } catch (queryError) {
      setError(queryError instanceof Error ? queryError.message : 'Assistant query failed.');
    }
  };

  const loadBatch = async () => {
    setError(null);
    try {
      const response = await fetchJson<{ dossier: DossierReadinessCard }>(`/cp/dossiers/${encodeURIComponent(batchId)}`);
      setDossier(response.dossier);
    } catch (dossierError) {
      setError(dossierError instanceof Error ? dossierError.message : 'Failed to load dossier.');
    }
  };

  return (
    <main className="app-shell">
      <header className="hero">
        <p className="eyebrow">Enterprise Manufacturing Control Plane</p>
        <h1>Areos control-plane dashboard</h1>
        <p className="subtitle">Domain-safe observability, readiness workflows, QA release posture, and MCP assistant guidance.</p>
        <div className="runtime-meta">
          <span>API: {apiBaseUrl}</span>
          <span>Mode: local mock compose stack</span>
          <span>Frontend: React + TypeScript + Vite</span>
        </div>
      </header>

      <section className="tabs">
        <div>
          <p className="tabs-label">Persona</p>
          <div className="tab-row">
            {PERSONAS.map((item) => (
              <button
                key={item.id}
                type="button"
                className={item.id === persona ? 'tab active' : 'tab'}
                onClick={() => setPersona(item.id)}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>
        <div>
          <p className="tabs-label">Workspace</p>
          <div className="tab-row">
            {VIEWS.map((item) => (
              <button
                key={item.id}
                type="button"
                className={item.id === view ? 'tab active' : 'tab'}
                onClick={() => setView(item.id)}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>
      </section>

      {loading ? <p className="status">Loading control-plane data…</p> : null}
      {error ? <p className="status error">{error}</p> : null}

      {!loading && view === 'dashboard' ? (
        <section className="stack">
          <h2>Dashboard</h2>
          {statusSummary ? (
            <div className="metric-grid">
              {statusSummary.map((metric) => (
                <article key={metric.label} className="card">
                  <p className="metric-label">{metric.label}</p>
                  <p className="metric-value">{metric.value}</p>
                  <TrafficLightBadge status={metric.status} />
                </article>
              ))}
            </div>
          ) : null}

          <h3>Site readiness</h3>
          <div className="grid columns-2">
            {sites.map((site) => (
              <SiteHealthCard key={site.site_id} site={site} />
            ))}
          </div>

          <h3>Connector health</h3>
          <div className="card table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Connector</th>
                  <th>System</th>
                  <th>Status</th>
                  <th>SLA</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {connectors.map((connector) => (
                  <tr key={connector.connector_label}>
                    <td>{connector.connector_label}</td>
                    <td>{connector.system_type}</td>
                    <td><TrafficLightBadge status={connector.status} /></td>
                    <td>{connector.sla_breach ? 'Breach' : 'Within target'}</td>
                    <td>{connector.recommended_action ?? 'No action needed'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {workflow ? (
            <article className="card">
              <h3 style={{ marginTop: 0 }}>{workflow.persona_label} workflow</h3>
              <p>{workflow.primary_objective}</p>
              <div className="metric-grid">
                {workflow.kpis.map((kpi) => (
                  <div key={kpi.label}>
                    <p className="metric-label">{kpi.label}</p>
                    <p className="metric-value">{kpi.value}</p>
                    <TrafficLightBadge status={kpi.status} />
                  </div>
                ))}
              </div>
            </article>
          ) : null}
        </section>
      ) : null}

      {!loading && view === 'topology' ? (
        <section className="stack">
          <h2>Topology map</h2>
          <div className="grid columns-2">
            {topology.map((siteTopology) => (
              <article key={siteTopology.site_label} className="card">
                <h3>{siteTopology.site_label}</h3>
                <p>{siteTopology.archetype}</p>
                <p><strong>Nodes:</strong> {siteTopology.nodes.length} | <strong>Flows:</strong> {siteTopology.edges.length}</p>
                <ul>
                  {siteTopology.nodes.slice(0, 10).map((node) => (
                    <li key={node.node_id}>
                      {node.node_label} ({node.node_type}) <TrafficLightBadge status={node.status} />
                    </li>
                  ))}
                </ul>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      {!loading && view === 'qa' ? (
        <section className="stack">
          <h2>QA release board</h2>
          <div className="card table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Record</th>
                  <th>Site</th>
                  <th>Summary</th>
                  <th>Owner</th>
                  <th>Priority</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {queue.map((item) => (
                  <tr key={item.record_id}>
                    <td>{item.record_id}</td>
                    <td>{item.site_label}</td>
                    <td>{item.summary}</td>
                    <td>{item.owner}</td>
                    <td>{item.priority}</td>
                    <td>{item.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}

      {!loading && view === 'dossier' ? (
        <section className="stack">
          <h2>Dossier viewer</h2>
          <div className="card">
            <label htmlFor="batch-id">Batch ID</label>
            <div className="inline-form">
              <input id="batch-id" value={batchId} onChange={(event) => setBatchId(event.target.value)} />
              <button type="button" className="primary-button" onClick={loadBatch}>Load dossier</button>
            </div>
          </div>
          {dossier ? (
            <article className="card">
              <h3 style={{ marginTop: 0 }}>{dossier.batch_label}</h3>
              <p>{dossier.product_label} · {dossier.site_label}</p>
              <p><strong>Recommendation:</strong> {dossier.release_recommendation}</p>
              <div className="metric-grid">
                <div><p className="metric-label">Completeness</p><p className="metric-value">{dossier.completeness_pct}%</p></div>
                <div><p className="metric-label">Open CAPAs</p><p className="metric-value">{dossier.open_capas}</p></div>
                <div><p className="metric-label">QA review</p><p className="metric-value">{dossier.qa_review_status}</p></div>
                <div><p className="metric-label">Human approval</p><p className="metric-value">{dossier.human_approval_required ? 'Required' : 'Not required'}</p></div>
              </div>
              <TrafficLightBadge status={dossier.dossier_status} label="Dossier status" />
              <h4>Missing evidence</h4>
              <ul>
                {dossier.missing_evidence.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </article>
          ) : null}
        </section>
      ) : null}

      {!loading && view === 'assistant' ? (
        <section className="stack">
          <h2>Assistant</h2>
          <AssistantPanel
            persona={persona}
            response={assistantResponse ?? undefined}
            onSubmit={submitAssistantQuestion}
          />
        </section>
      ) : null}

      {!loading && view === 'admin' ? (
        <section className="stack">
          <h2>Admin diagnostics</h2>
          {adminError ? <p className="status error">{adminError}</p> : null}
          {adminDiagnostics ? (
            <article className="card">
              <p><strong>Mode:</strong> {String(adminDiagnostics.mode ?? 'unknown')}</p>
              <p><strong>Sections:</strong> {Object.keys(adminDiagnostics).join(', ')}</p>
              <pre className="markdown-box">{JSON.stringify(adminDiagnostics, null, 2)}</pre>
            </article>
          ) : (
            <p className="status">Loading diagnostics…</p>
          )}
        </section>
      ) : null}
    </main>
  );
}
