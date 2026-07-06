import { useCallback, useEffect, useMemo, useState } from 'react';

import { ControlPlaneLayout } from './components/layout/ControlPlaneLayout';
import { PersonaTabBar } from './components/layout/PersonaTabBar';
import { AdminDiagnostics } from './components/pages/AdminDiagnostics';
import { AssistantChat } from './components/pages/AssistantChat';
import { DashboardPage } from './components/pages/DashboardPage';
import { DossierViewer } from './components/pages/DossierViewer';
import { QAReleaseBoard } from './components/pages/QAReleaseBoard';
import { TopologyMapPage } from './components/pages/TopologyMapPage';
import { EmptyState } from './components/shared/EmptyState';
import { ErrorState } from './components/shared/ErrorState';
import { LoadingState } from './components/shared/LoadingState';
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

const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
const REQUEST_TIMEOUT_MS = 6000;
const DEFAULT_API_URL = 'http://localhost:8000';

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

const unique = (values: Array<string | undefined>): string[] => [...new Set(values.filter((value): value is string => Boolean(value)))];

const resolveApiCandidates = (): string[] => {
  if (typeof window === 'undefined') {
    return unique([configuredApiBaseUrl, DEFAULT_API_URL]);
  }

  const sameOriginApi = `${window.location.protocol}//${window.location.hostname}:8000`;
  const localApi = DEFAULT_API_URL;
  const normalizedConfigured = configuredApiBaseUrl?.replace(/\/$/, '');

  const configuredHost = normalizedConfigured ? new URL(normalizedConfigured).hostname : null;
  const browserHost = window.location.hostname;
  const rewrittenConfigured = configuredHost === 'api' && browserHost !== 'api' ? sameOriginApi : normalizedConfigured;

  return unique([
    rewrittenConfigured,
    sameOriginApi,
    localApi,
    window.location.origin,
    '',
  ]);
};

const toUrl = (baseUrl: string, path: string): string => {
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path;
  }
  if (!baseUrl) {
    return path;
  }
  return `${baseUrl.replace(/\/$/, '')}${path}`;
};

async function fetchJsonFromBase<T>(baseUrl: string, path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(toUrl(baseUrl, path), {
      headers: { 'Content-Type': 'application/json' },
      ...init,
      signal: controller.signal,
    });

    if (!response.ok) {
      const body = await response.text();
      throw new Error(`${response.status} ${response.statusText}: ${body}`);
    }

    return response.json() as Promise<T>;
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new Error(`Request timed out after ${REQUEST_TIMEOUT_MS / 1000}s`);
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

async function fetchJsonWithFallback<T>(
  path: string,
  candidates: string[],
  init?: RequestInit,
): Promise<{ data: T; baseUrl: string }> {
  const errors: string[] = [];

  for (const candidate of candidates) {
    try {
      const data = await fetchJsonFromBase<T>(candidate, path, init);
      return { data, baseUrl: candidate };
    } catch (error) {
      const reason = error instanceof Error ? error.message : String(error);
      errors.push(`${candidate || '<relative>'}: ${reason}`);
    }
  }

  throw new Error(`All API candidates failed for ${path}. ${errors.join(' | ')}`);
}

export default function App() {
  const [persona, setPersona] = useState<PersonaType>('qa');
  const [view, setView] = useState<ViewMode>('dashboard');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeApiBase, setActiveApiBase] = useState<string>(configuredApiBaseUrl ?? '');

  const [sites, setSites] = useState<SiteHealthCardModel[]>([]);
  const [connectors, setConnectors] = useState<ConnectorStatusCard[]>([]);
  const [readiness, setReadiness] = useState<EnterpriseReadinessRollup | null>(null);
  const [topology, setTopology] = useState<ManufacturingSiteTopology[]>([]);
  const [workflow, setWorkflow] = useState<PersonaWorkflowCard | null>(null);
  const [queue, setQueue] = useState<CapaQueueItem[]>([]);

  const [batchId, setBatchId] = useState('BATCH-OSD-0421');
  const [dossier, setDossier] = useState<DossierReadinessCard | null>(null);
  const [assistantResponse, setAssistantResponse] = useState<AssistantResponse | null>(null);
  const [assistantLoading, setAssistantLoading] = useState(false);
  const [adminDiagnostics, setAdminDiagnostics] = useState<Record<string, unknown> | null>(null);
  const [adminError, setAdminError] = useState<string | null>(null);

  const apiCandidates = useMemo(resolveApiCandidates, []);

  const loadControlPlane = useCallback(async () => {
    setLoading(true);
    setError(null);

    const results = await Promise.allSettled([
      fetchJsonWithFallback<{ sites: SiteHealthCardModel[] }>('/cp/sites', apiCandidates),
      fetchJsonWithFallback<{ connectors: ConnectorStatusCard[] }>('/cp/connectors', apiCandidates),
      fetchJsonWithFallback<{ enterprise_readiness: EnterpriseReadinessRollup }>('/cp/readiness', apiCandidates),
      fetchJsonWithFallback<{ topology: ManufacturingSiteTopology[] }>('/cp/topology', apiCandidates),
      fetchJsonWithFallback<{ workflow: PersonaWorkflowCard }>(`/cp/personas/${persona}/workflow`, apiCandidates),
      fetchJsonWithFallback<{ queue: CapaQueueItem[] }>('/cp/capa/queue', apiCandidates),
      fetchJsonWithFallback<{ dossier: DossierReadinessCard }>(`/cp/dossiers/${encodeURIComponent(batchId)}`, apiCandidates),
    ]);

    const failures: string[] = [];
    let discoveredBaseUrl: string | null = null;

    const collect = <T,>(
      result: PromiseSettledResult<{ data: T; baseUrl: string }>,
      assign: (value: T) => void,
      failureLabel: string,
    ) => {
      if (result.status === 'fulfilled') {
        discoveredBaseUrl ??= result.value.baseUrl;
        assign(result.value.data);
      } else {
        failures.push(`${failureLabel}: ${result.reason instanceof Error ? result.reason.message : String(result.reason)}`);
      }
    };

    collect(results[0], (value) => setSites(value.sites), 'Sites');
    collect(results[1], (value) => setConnectors(value.connectors), 'Connectors');
    collect(results[2], (value) => setReadiness(value.enterprise_readiness), 'Readiness');
    collect(results[3], (value) => setTopology(value.topology), 'Topology');
    collect(results[4], (value) => setWorkflow(value.workflow), 'Workflow');
    collect(results[5], (value) => setQueue(value.queue), 'CAPA queue');
    collect(results[6], (value) => setDossier(value.dossier), 'Dossier');

    if (discoveredBaseUrl !== null) {
      setActiveApiBase(discoveredBaseUrl);
    }

    if (failures.length === results.length) {
      setError('Unable to load control-plane data from any API endpoint. Verify API service reachability and port mapping.');
    } else if (failures.length) {
      setError(`Some control-plane sections failed to load: ${failures.join(' · ')}`);
    }

    setLoading(false);
  }, [apiCandidates, batchId, persona]);

  useEffect(() => {
    let cancelled = false;

    const run = async () => {
      try {
        await loadControlPlane();
      } catch (loadError) {
        if (!cancelled) {
          setLoading(false);
          setError(loadError instanceof Error ? loadError.message : 'Failed to load control-plane data.');
        }
      }
    };

    run();

    return () => {
      cancelled = true;
    };
  }, [loadControlPlane]);

  useEffect(() => {
    if (view !== 'admin') {
      return;
    }

    let cancelled = false;

    const loadAdmin = async () => {
      setAdminError(null);
      try {
        const data = await fetchJsonWithFallback<Record<string, unknown>>('/cp/admin/diagnostics', apiCandidates);
        if (!cancelled) {
          setAdminDiagnostics(data.data);
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
  }, [apiCandidates, view]);

  const submitAssistantQuestion = async (request: AssistantQueryRequest) => {
    setAssistantResponse(null);
    setAssistantLoading(true);
    setError(null);

    try {
      const response = await fetchJsonWithFallback<AssistantResponse>('/cp/assistant/query', apiCandidates, {
        method: 'POST',
        body: JSON.stringify(request),
      });
      setAssistantResponse(response.data);
      setView('assistant');
    } catch (queryError) {
      setError(queryError instanceof Error ? queryError.message : 'Assistant query failed.');
    } finally {
      setAssistantLoading(false);
    }
  };

  const loadBatch = async () => {
    setError(null);

    try {
      const response = await fetchJsonWithFallback<{ dossier: DossierReadinessCard }>(
        `/cp/dossiers/${encodeURIComponent(batchId)}`,
        apiCandidates,
      );
      setDossier(response.data.dossier);
      setView('dossier');
    } catch (dossierError) {
      setError(dossierError instanceof Error ? dossierError.message : 'Failed to load dossier.');
    }
  };

  const apiLabel = activeApiBase || window.location.origin;

  return (
    <ControlPlaneLayout
      header={(
        <header className="hero">
          <p className="eyebrow">Enterprise Manufacturing Control Plane</p>
          <h1>Areos control-plane dashboard</h1>
          <p className="subtitle">
            Domain-safe observability, readiness workflows, QA release posture, and MCP assistant guidance.
          </p>
          <div className="runtime-meta">
            <span>API: {apiLabel}</span>
            <span>Mode: local mock compose stack</span>
            <span>Frontend: React + TypeScript + Vite</span>
          </div>
        </header>
      )}
      controls={(
        <>
          <PersonaTabBar
            label="Persona"
            options={PERSONAS}
            selected={persona}
            onSelect={(selectedPersona) => setPersona(selectedPersona as PersonaType)}
          />
          <PersonaTabBar
            label="Workspace"
            options={VIEWS}
            selected={view}
            onSelect={(selectedView) => setView(selectedView as ViewMode)}
          />
        </>
      )}
      content={(
        <>
          {loading ? <LoadingState /> : null}
          {error && !loading ? <ErrorState detail={error} onRetry={loadControlPlane} /> : null}

          {!loading && !sites.length && !connectors.length && !readiness ? (
            <EmptyState
              title="No control-plane data available"
              detail="Run the API and deterministic validation suite to populate enterprise workflow views."
            />
          ) : null}

          {!loading && view === 'dashboard' ? (
            <DashboardPage readiness={readiness} sites={sites} connectors={connectors} workflow={workflow} />
          ) : null}

          {!loading && view === 'topology' ? <TopologyMapPage topology={topology} /> : null}

          {!loading && view === 'qa' ? (
            <QAReleaseBoard queue={queue} dossier={dossier} workflow={workflow} />
          ) : null}

          {!loading && view === 'dossier' ? (
            <DossierViewer
              batchId={batchId}
              dossier={dossier}
              onBatchChange={setBatchId}
              onLoad={loadBatch}
            />
          ) : null}

          {!loading && view === 'assistant' ? (
            <>
              {assistantLoading ? <p className="status">Querying assistant…</p> : null}
              <AssistantChat persona={persona} response={assistantResponse} onSubmit={submitAssistantQuestion} />
            </>
          ) : null}

          {!loading && view === 'admin' ? (
            <AdminDiagnostics diagnostics={adminDiagnostics} error={adminError} />
          ) : null}
        </>
      )}
    />
  );
}
