import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Activity,
  AlertOctagon,
  Bot,
  ChevronLeft,
  ChevronRight,
  ClipboardList,
  FileText,
  LayoutGrid,
  Network,
  Radio,
  Settings,
  ShieldCheck,
  Building2,
} from 'lucide-react';
import { AssistantDrawer } from './components/assistant/AssistantDrawer';
import { CommandCenter } from './components/command/CommandCenter';
import { ConnectorHealthGrid } from './components/connectors/ConnectorHealthGrid';
import { PlantFloorMap } from './components/floormap/PlantFloorMap';
import { LeadershipMatrix } from './components/leadership/LeadershipMatrix';
import { QAReleaseBoardV2 } from './components/release/QAReleaseBoardV2';
import { AdminDiagnostics } from './components/pages/AdminDiagnostics';
import { DossierViewer } from './components/pages/DossierViewer';
import { LoadingState } from './components/shared/LoadingState';
import { cx, statusColor } from './lib/design';
import type {
  AssistantQueryRequest,
  AssistantResponse,
  CommandCenterEvent,
  ConnectorStatusCard,
  DossierReadinessCard,
  EnterpriseReadinessRollup,
  EventSummary,
  ManufacturingSiteTopology,
  PersonaType,
  PersonaWorkflowCard,
} from './types/control-plane';

type ViewMode = 'command' | 'floormap' | 'release' | 'connectors' | 'dossier' | 'leadership' | 'admin';

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
  { id: 'plant_ops', label: 'Plant Ops' },
  { id: 'qa', label: 'Quality Assurance' },
  { id: 'engineering', label: 'Engineering' },
  { id: 'system_admin', label: 'System Admin' },
  { id: 'leadership', label: 'Leadership' },
];

type NavItem = { id: ViewMode; label: string; icon: typeof Activity };

const NAV_BY_PERSONA: Record<PersonaType, NavItem[]> = {
  plant_ops: [
    { id: 'command', label: 'Active Event', icon: AlertOctagon },
    { id: 'floormap', label: 'Live Floor Map', icon: Network },
    { id: 'connectors', label: 'Connector Pulse', icon: Radio },
    { id: 'release', label: 'Deviation Queue', icon: ClipboardList },
  ],
  qa: [
    { id: 'release', label: 'Release Board', icon: ClipboardList },
    { id: 'command', label: 'Active Event', icon: AlertOctagon },
    { id: 'dossier', label: 'Dossier Review', icon: FileText },
    { id: 'floormap', label: 'Batch Floor Map', icon: Network },
  ],
  engineering: [
    { id: 'floormap', label: 'Asset Floor Map', icon: Network },
    { id: 'command', label: 'Excursion History', icon: AlertOctagon },
    { id: 'connectors', label: 'Connector Pulse', icon: Radio },
  ],
  system_admin: [
    { id: 'connectors', label: 'Connector Health', icon: Radio },
    { id: 'floormap', label: 'Topology', icon: Network },
    { id: 'admin', label: 'Diagnostics', icon: Settings },
  ],
  leadership: [
    { id: 'leadership', label: 'Readiness Matrix', icon: LayoutGrid },
    { id: 'command', label: 'Active Event', icon: AlertOctagon },
    { id: 'floormap', label: 'Site Topology', icon: Network },
  ],
};

const unique = (values: Array<string | undefined>): string[] =>
  [...new Set(values.filter((value): value is string => Boolean(value)))];

const resolveApiCandidates = (): string[] => {
  if (typeof window === 'undefined') {
    return unique([configuredApiBaseUrl, DEFAULT_API_URL]);
  }
  const sameOriginApi = `${window.location.protocol}//${window.location.hostname}:8000`;
  const normalizedConfigured = configuredApiBaseUrl?.replace(/\/$/, '');
  const configuredHost = normalizedConfigured ? new URL(normalizedConfigured).hostname : null;
  const browserHost = window.location.hostname;
  const rewrittenConfigured = configuredHost === 'api' && browserHost !== 'api' ? sameOriginApi : normalizedConfigured;
  return unique([rewrittenConfigured, sameOriginApi, DEFAULT_API_URL, window.location.origin, '']);
};

const toUrl = (baseUrl: string, path: string): string => {
  if (path.startsWith('http://') || path.startsWith('https://')) return path;
  if (!baseUrl) return path;
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
      errors.push(`${candidate || '<relative>'}: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
  throw new Error(`All API candidates failed for ${path}. ${errors.join(' | ')}`);
}

export default function App() {
  const [persona, setPersona] = useState<PersonaType>('plant_ops');
  const [view, setView] = useState<ViewMode>('command');
  const [collapsed, setCollapsed] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeApiBase, setActiveApiBase] = useState<string>(configuredApiBaseUrl ?? '');

  const [connectors, setConnectors] = useState<ConnectorStatusCard[]>([]);
  const [readiness, setReadiness] = useState<EnterpriseReadinessRollup | null>(null);
  const [topology, setTopology] = useState<ManufacturingSiteTopology[]>([]);
  const [workflow, setWorkflow] = useState<PersonaWorkflowCard | null>(null);
  const [queue, setQueue] = useState<CapaQueueItem[]>([]);

  const [events, setEvents] = useState<EventSummary[]>([]);
  const [activeEvent, setActiveEvent] = useState<CommandCenterEvent | null>(null);
  const [eventLoading, setEventLoading] = useState(false);

  const [batchId, setBatchId] = useState('BATCH-OSD-2026-001');
  const [dossier, setDossier] = useState<DossierReadinessCard | null>(null);

  const [assistantOpen, setAssistantOpen] = useState(false);
  const [assistantResponse, setAssistantResponse] = useState<AssistantResponse | null>(null);
  const [assistantLoading, setAssistantLoading] = useState(false);

  const [adminDiagnostics, setAdminDiagnostics] = useState<Record<string, unknown> | null>(null);
  const [adminError, setAdminError] = useState<string | null>(null);

  const apiCandidates = useMemo(resolveApiCandidates, []);

  const bannerEvent = useMemo(() => events.find((event) => event.status === 'red') ?? events[0] ?? null, [events]);

  const loadCore = useCallback(async () => {
    setLoading(true);
    setError(null);

    const results = await Promise.allSettled([
      fetchJsonWithFallback<{ connectors: ConnectorStatusCard[] }>('/cp/connectors', apiCandidates),
      fetchJsonWithFallback<{ enterprise_readiness: EnterpriseReadinessRollup }>('/cp/readiness', apiCandidates),
      fetchJsonWithFallback<{ topology: ManufacturingSiteTopology[] }>('/cp/topology', apiCandidates),
      fetchJsonWithFallback<{ workflow: PersonaWorkflowCard }>(`/cp/personas/${persona}/workflow`, apiCandidates),
      fetchJsonWithFallback<{ queue: CapaQueueItem[] }>('/cp/capa/queue', apiCandidates),
      fetchJsonWithFallback<{ dossier: DossierReadinessCard }>(`/cp/dossiers/${encodeURIComponent(batchId)}`, apiCandidates),
      fetchJsonWithFallback<{ events: EventSummary[] }>('/cp/events', apiCandidates),
    ]);

    const failures: string[] = [];
    let discoveredBaseUrl: string | null = null;

    const collect = <T,>(
      result: PromiseSettledResult<{ data: T; baseUrl: string }>,
      assign: (value: T) => void,
      label: string,
    ) => {
      if (result.status === 'fulfilled') {
        discoveredBaseUrl ??= result.value.baseUrl;
        assign(result.value.data);
      } else {
        failures.push(`${label}: ${result.reason instanceof Error ? result.reason.message : String(result.reason)}`);
      }
    };

    collect(results[0], (value) => setConnectors(value.connectors), 'Connectors');
    collect(results[1], (value) => setReadiness(value.enterprise_readiness), 'Readiness');
    collect(results[2], (value) => setTopology(value.topology), 'Topology');
    collect(results[3], (value) => setWorkflow(value.workflow), 'Workflow');
    collect(results[4], (value) => setQueue(value.queue), 'CAPA queue');
    collect(results[5], (value) => setDossier(value.dossier), 'Dossier');
    collect(results[6], (value) => setEvents(value.events), 'Events');

    if (discoveredBaseUrl !== null) setActiveApiBase(discoveredBaseUrl);

    if (failures.length === results.length) {
      setError('Unable to load control-plane data from any API endpoint. Verify API service reachability and port mapping.');
    } else if (failures.length) {
      setError(`Some sections failed to load: ${failures.join(' · ')}`);
    }
    setLoading(false);
  }, [apiCandidates, batchId, persona]);

  useEffect(() => {
    loadCore().catch((loadError) => {
      setLoading(false);
      setError(loadError instanceof Error ? loadError.message : 'Failed to load control-plane data.');
    });
  }, [loadCore]);

  const loadEventDetail = useCallback(
    async (eventId: string) => {
      setEventLoading(true);
      try {
        const response = await fetchJsonWithFallback<{ event: CommandCenterEvent }>(
          `/cp/events/${encodeURIComponent(eventId)}`,
          apiCandidates,
        );
        setActiveEvent(response.data.event);
      } catch (detailError) {
        setError(detailError instanceof Error ? detailError.message : 'Failed to load event detail.');
      } finally {
        setEventLoading(false);
      }
    },
    [apiCandidates],
  );

  useEffect(() => {
    if (bannerEvent && !activeEvent) {
      loadEventDetail(bannerEvent.event_id);
    }
  }, [bannerEvent, activeEvent, loadEventDetail]);

  useEffect(() => {
    if (view !== 'admin') return;
    let cancelled = false;
    (async () => {
      setAdminError(null);
      try {
        const data = await fetchJsonWithFallback<Record<string, unknown>>('/cp/admin/diagnostics', apiCandidates);
        if (!cancelled) setAdminDiagnostics(data.data);
      } catch (adminLoadError) {
        if (!cancelled) {
          setAdminError(adminLoadError instanceof Error ? adminLoadError.message : 'Failed to load admin diagnostics.');
          setAdminDiagnostics(null);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [apiCandidates, view]);

  const askAssistant = useCallback(
    async (question: string) => {
      setAssistantOpen(true);
      setAssistantResponse(null);
      setAssistantLoading(true);
      const request: AssistantQueryRequest = {
        question,
        persona,
        event_id: activeEvent?.summary.event_id ?? bannerEvent?.event_id,
      };
      try {
        const response = await fetchJsonWithFallback<AssistantResponse>('/cp/assistant/query', apiCandidates, {
          method: 'POST',
          body: JSON.stringify(request),
        });
        setAssistantResponse(response.data);
      } catch (queryError) {
        setError(queryError instanceof Error ? queryError.message : 'Assistant query failed.');
      } finally {
        setAssistantLoading(false);
      }
    },
    [activeEvent, apiCandidates, bannerEvent, persona],
  );

  const loadBatch = async () => {
    setError(null);
    try {
      const response = await fetchJsonWithFallback<{ dossier: DossierReadinessCard }>(
        `/cp/dossiers/${encodeURIComponent(batchId)}`,
        apiCandidates,
      );
      setDossier(response.data.dossier);
    } catch (dossierError) {
      setError(dossierError instanceof Error ? dossierError.message : 'Failed to load dossier.');
    }
  };

  const navItems = NAV_BY_PERSONA[persona];

  useEffect(() => {
    if (!navItems.some((item) => item.id === view)) {
      setView(navItems[0].id);
    }
  }, [navItems, view]);

  const assistantContext = activeEvent
    ? `${activeEvent.summary.batch_label ?? activeEvent.summary.parameter} · ${activeEvent.summary.outcome.replace(/_/g, ' ')}`
    : 'Enterprise Control Plane';

  const suggestedQueries = activeEvent
    ? [
        'What is blocking batch release?',
        `What is the quality risk for this ${activeEvent.summary.parameter.toLowerCase()} excursion?`,
        'Show the evidence checklist',
      ]
    : ['What sites have active deviations?', 'Summarize enterprise readiness', 'Which connectors are degraded?'];

  const apiLabel = activeApiBase || (typeof window !== 'undefined' ? window.location.origin : '');
  const healthStatus = bannerEvent?.status === 'red' ? 'red' : bannerEvent?.status === 'yellow' ? 'yellow' : 'green';
  const healthSc = statusColor(healthStatus);

  return (
    <div className="flex h-screen flex-col bg-surface-950 text-slate-200">
      {/* TOP RAIL */}
      <header className="flex h-12 shrink-0 items-center justify-between border-b border-surface-700 bg-surface-900 px-4">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <ShieldCheck size={18} className="text-biotech-accent" />
            <span className="text-sm font-bold tracking-tight text-slate-100">AEROS</span>
          </div>
          <div className="hidden items-center gap-1.5 rounded border border-surface-700 bg-surface-850 px-2.5 py-1 text-xs text-slate-300 sm:flex">
            <Building2 size={13} className="text-slate-500" />
            acme_pharma <span className="text-slate-600">›</span> Hyderabad Plant
          </div>
        </div>

        {/* Active Event Banner */}
        {bannerEvent && (
          <button
            onClick={() => {
              loadEventDetail(bannerEvent.event_id);
              setView('command');
            }}
            className={cx(
              'flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium transition',
              statusColor(bannerEvent.status).border,
              statusColor(bannerEvent.status).bg,
              statusColor(bannerEvent.status).text,
            )}
          >
            <AlertOctagon size={13} className={bannerEvent.status === 'red' ? 'animate-pulse-node' : ''} />
            <span className="font-semibold">{bannerEvent.status === 'red' ? 'BREACH' : 'ALERT'}:</span>
            {bannerEvent.batch_label ?? bannerEvent.asset_label} · {bannerEvent.parameter}
            {bannerEvent.duration_minutes ? ` · ${bannerEvent.duration_minutes} min` : ''} · Action Required
          </button>
        )}

        <div className="flex items-center gap-3">
          <select
            value={persona}
            onChange={(e) => setPersona(e.target.value as PersonaType)}
            className="rounded border border-surface-700 bg-surface-850 px-2 py-1 text-xs text-slate-200 focus:outline-none"
          >
            {PERSONAS.map((option) => (
              <option key={option.id} value={option.id}>
                {option.label}
              </option>
            ))}
          </select>
          <button
            onClick={() => setAssistantOpen((open) => !open)}
            className={cx(
              'rounded border px-2 py-1 text-xs',
              assistantOpen ? 'border-biotech-accent text-biotech-accent' : 'border-surface-700 text-slate-300 hover:text-slate-100',
            )}
          >
            <Bot size={14} />
          </button>
          <div className="flex items-center gap-1.5" title={`System health: ${healthStatus}`}>
            <span className={cx('h-2.5 w-2.5 rounded-full', healthSc.dot, healthStatus !== 'green' && 'animate-breathe')} />
          </div>
        </div>
      </header>

      <div className="flex min-h-0 flex-1">
        {/* LEFT SIDEBAR */}
        <nav
          className={cx(
            'flex shrink-0 flex-col border-r border-surface-700 bg-surface-900 transition-all duration-200',
            collapsed ? 'w-16' : 'w-56',
          )}
        >
          <div className="flex-1 space-y-1 p-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = view === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setView(item.id)}
                  className={cx(
                    'flex w-full items-center gap-3 rounded px-3 py-2 text-sm transition',
                    active ? 'bg-biotech-accent/15 text-biotech-accent' : 'text-slate-400 hover:bg-surface-800 hover:text-slate-100',
                  )}
                  title={item.label}
                >
                  <Icon size={16} className="shrink-0" />
                  {!collapsed && <span className="truncate">{item.label}</span>}
                </button>
              );
            })}
          </div>
          <button
            onClick={() => setCollapsed((value) => !value)}
            className="flex items-center justify-center border-t border-surface-800 py-2 text-slate-500 hover:text-slate-200"
          >
            {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
          </button>
        </nav>

        {/* CONTENT */}
        <main className="min-w-0 flex-1 overflow-hidden">
          {loading ? (
            <LoadingState />
          ) : (
            <div className="h-full">
              {error && (
                <div className="border-b border-status-yellow/30 bg-status-yellow/5 px-4 py-2 text-xs text-status-yellow">
                  {error}
                </div>
              )}

              {view === 'command' && (
                <CommandCenter
                  event={activeEvent}
                  loading={eventLoading}
                  onAsk={askAssistant}
                  onOpenDossier={() => setView('dossier')}
                />
              )}
              {view === 'floormap' && <PlantFloorMap topology={topology} />}
              {view === 'release' && (
                <QAReleaseBoardV2
                  queue={queue}
                  dossier={dossier}
                  workflow={workflow}
                  onAsk={askAssistant}
                  onApprove={() => undefined}
                />
              )}
              {view === 'connectors' && <ConnectorHealthGrid connectors={connectors} />}
              {view === 'leadership' && <LeadershipMatrix readiness={readiness} />}
              {view === 'dossier' && (
                <div className="h-full overflow-y-auto p-4">
                  <DossierViewer batchId={batchId} dossier={dossier} onBatchChange={setBatchId} onLoad={loadBatch} />
                </div>
              )}
              {view === 'admin' && (
                <div className="h-full overflow-y-auto p-4">
                  <AdminDiagnostics diagnostics={adminDiagnostics} error={adminError} />
                </div>
              )}
            </div>
          )}
        </main>
      </div>

      <AssistantDrawer
        open={assistantOpen}
        contextLabel={assistantContext}
        response={assistantResponse}
        loading={assistantLoading}
        onClose={() => setAssistantOpen(false)}
        onSubmit={askAssistant}
        suggestedQueries={suggestedQueries}
      />

      <div className="flex h-6 shrink-0 items-center justify-between border-t border-surface-800 bg-surface-900 px-4 text-[10px] text-slate-600">
        <span className="flex items-center gap-1.5">
          <Activity size={10} /> API: {apiLabel || 'relative'}
        </span>
        <span>Mode: local mock · ISA-101 High-Performance HMI</span>
      </div>
    </div>
  );
}
