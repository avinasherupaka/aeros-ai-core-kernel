import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  Activity,
  AlertOctagon,
  ChevronLeft,
  ChevronRight,
  ClipboardList,
  FileText,
  LayoutGrid,
  Network,
  Radio,
  RefreshCw,
  Settings,
  ShieldCheck,
  Building2,
  WifiOff,
} from 'lucide-react';
import { CommandCenter } from './components/command/CommandCenter';
import { ConnectorHealthGrid } from './components/connectors/ConnectorHealthGrid';
import { PlantFloorMap } from './components/floormap/PlantFloorMap';
import { LeadershipMatrix } from './components/leadership/LeadershipMatrix';
import { QAReleaseBoardV2 } from './components/release/QAReleaseBoardV2';
import { AdminDiagnostics } from './components/pages/AdminDiagnostics';
import { DossierViewer } from './components/pages/DossierViewer';
import { DendrixAssistant } from './components/assistant/DendrixAssistant';
import { LoadingState } from './components/shared/LoadingState';
import { cx, statusColor } from './lib/design';
import type {
  AssistantResponse,
  CommandCenterEvent,
  ConnectorStatusCard,
  DossierReadinessCard,
  EnterpriseReadinessRollup,
  EventSummary,
  FloorMapSite,
  FullDossier,
  PersonaWorkflowCard,
} from './types/control-plane';

type ViewMode = 'command' | 'floormap' | 'release' | 'connectors' | 'dossier' | 'readiness' | 'admin';
type ConnState = 'connecting' | 'online' | 'degraded' | 'offline';

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
const MAX_BACKOFF_MS = 20000;

type NavItem = { id: ViewMode; label: string; icon: typeof Activity; affinity: string };

// Unified navigation - every section is always visible. The affinity chip is a
// soft hint about which persona cares most, not a filter.
const NAV_ITEMS: NavItem[] = [
  { id: 'command', label: 'Active Event', icon: AlertOctagon, affinity: 'Plant Ops' },
  { id: 'floormap', label: 'Live Floor Map', icon: Network, affinity: 'Plant Ops' },
  { id: 'release', label: 'Release Board', icon: ClipboardList, affinity: 'Quality' },
  { id: 'dossier', label: 'Dossier Review', icon: FileText, affinity: 'Quality' },
  { id: 'connectors', label: 'Connector Pulse', icon: Radio, affinity: 'System Admin' },
  { id: 'readiness', label: 'Readiness Matrix', icon: LayoutGrid, affinity: 'Leadership' },
  { id: 'admin', label: 'Diagnostics', icon: Settings, affinity: 'System Admin' },
];

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
  const [view, setView] = useState<ViewMode>('command');
  const [collapsed, setCollapsed] = useState(false);
  const [loading, setLoading] = useState(true);
  const [connState, setConnState] = useState<ConnState>('connecting');
  const [degradedDetail, setDegradedDetail] = useState<string | null>(null);
  const [activeApiBase, setActiveApiBase] = useState<string>(configuredApiBaseUrl ?? '');
  const retryAttempt = useRef(0);
  const retryTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const [connectors, setConnectors] = useState<ConnectorStatusCard[]>([]);
  const [readiness, setReadiness] = useState<EnterpriseReadinessRollup | null>(null);
  const [floorSites, setFloorSites] = useState<FloorMapSite[]>([]);
  const [workflow, setWorkflow] = useState<PersonaWorkflowCard | null>(null);
  const [queue, setQueue] = useState<CapaQueueItem[]>([]);

  const [events, setEvents] = useState<EventSummary[]>([]);
  const [activeEvent, setActiveEvent] = useState<CommandCenterEvent | null>(null);
  const [eventLoading, setEventLoading] = useState(false);

  const [batchId] = useState('BATCH-OSD-2026-001');
  const [releaseDossier, setReleaseDossier] = useState<DossierReadinessCard | null>(null);

  const [dossierEventId, setDossierEventId] = useState<string | null>(null);
  const [fullDossier, setFullDossier] = useState<FullDossier | null>(null);
  const [dossierLoading, setDossierLoading] = useState(false);

  const [assistantOpen, setAssistantOpen] = useState(false);
  const [assistantResponse, setAssistantResponse] = useState<AssistantResponse | null>(null);
  const [assistantLoading, setAssistantLoading] = useState(false);

  const [adminDiagnostics, setAdminDiagnostics] = useState<Record<string, unknown> | null>(null);
  const [adminError, setAdminError] = useState<string | null>(null);

  const apiCandidates = useMemo(resolveApiCandidates, []);

  const bannerEvent = useMemo(
    () => events.find((event) => event.status === 'red') ?? events[0] ?? null,
    [events],
  );

  const scheduleRetry = useCallback((run: () => void) => {
    if (retryTimer.current) clearTimeout(retryTimer.current);
    const delay = Math.min(MAX_BACKOFF_MS, 3000 * 2 ** retryAttempt.current);
    retryAttempt.current += 1;
    retryTimer.current = setTimeout(run, delay);
  }, []);

  const loadCore = useCallback(async () => {
    const results = await Promise.allSettled([
      fetchJsonWithFallback<{ connectors: ConnectorStatusCard[] }>('/cp/connectors', apiCandidates),
      fetchJsonWithFallback<{ enterprise_readiness: EnterpriseReadinessRollup }>('/cp/readiness', apiCandidates),
      fetchJsonWithFallback<{ sites: FloorMapSite[] }>('/cp/floormap', apiCandidates),
      fetchJsonWithFallback<{ workflow: PersonaWorkflowCard }>('/cp/personas/qa/workflow', apiCandidates),
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
        failures.push(label);
      }
    };

    collect(results[0], (value) => setConnectors(value.connectors), 'Connectors');
    collect(results[1], (value) => setReadiness(value.enterprise_readiness), 'Readiness');
    collect(results[2], (value) => setFloorSites(value.sites), 'Floor map');
    collect(results[3], (value) => setWorkflow(value.workflow), 'Workflow');
    collect(results[4], (value) => setQueue(value.queue), 'CAPA queue');
    collect(results[5], (value) => setReleaseDossier(value.dossier), 'Dossier');
    collect(results[6], (value) => setEvents(value.events), 'Events');

    if (discoveredBaseUrl !== null) setActiveApiBase(discoveredBaseUrl);
    setLoading(false);

    if (failures.length === results.length) {
      setConnState('offline');
      setDegradedDetail(null);
      scheduleRetry(() => {
        loadCore().catch(() => undefined);
      });
    } else {
      retryAttempt.current = 0;
      if (failures.length) {
        setConnState('degraded');
        setDegradedDetail(`${failures.join(', ')} unavailable — retrying in the background.`);
      } else {
        setConnState('online');
        setDegradedDetail(null);
      }
    }
  }, [apiCandidates, batchId, scheduleRetry]);

  useEffect(() => {
    loadCore().catch(() => setLoading(false));
    return () => {
      if (retryTimer.current) clearTimeout(retryTimer.current);
    };
  }, [loadCore]);

  const manualRetry = useCallback(() => {
    retryAttempt.current = 0;
    setConnState('connecting');
    loadCore().catch(() => undefined);
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
      } catch {
        /* keep prior event; connectivity banner conveys the failure */
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

  // Dossier review: default to the active/banner event, fetch full GMP dossier.
  useEffect(() => {
    if (view !== 'dossier') return;
    const target = dossierEventId ?? activeEvent?.summary.event_id ?? bannerEvent?.event_id ?? events[0]?.event_id;
    if (!target) return;
    if (fullDossier && fullDossier.event_id === target && !dossierEventId) return;
    let cancelled = false;
    (async () => {
      setDossierLoading(true);
      try {
        const response = await fetchJsonWithFallback<{ dossier: FullDossier }>(
          `/cp/dossiers/events/${encodeURIComponent(target)}/full`,
          apiCandidates,
        );
        if (!cancelled) setFullDossier(response.data.dossier);
      } catch {
        /* leave previous dossier */
      } finally {
        if (!cancelled) setDossierLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [view, dossierEventId, apiCandidates]);

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
          setAdminError(adminLoadError instanceof Error ? adminLoadError.message : 'Failed to load diagnostics.');
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
      try {
        const response = await fetchJsonWithFallback<AssistantResponse>('/cp/assistant/query', apiCandidates, {
          method: 'POST',
          body: JSON.stringify({
            question,
            event_id: activeEvent?.summary.event_id ?? bannerEvent?.event_id,
          }),
        });
        setAssistantResponse(response.data);
      } catch {
        setAssistantResponse({
          question,
          summary: 'Dendrix is offline',
          response_markdown:
            'The assurance API is not reachable right now. Once the API service is up, re-ask your question and Dendrix will answer with live, cited data.',
          response_format: 'guided_remediation',
          deterministic_facts: [],
          inferred_explanations: [],
          recommended_actions: ['Verify the API container is running: docker compose --profile ui up -d api'],
          human_approval_required: false,
          gxp_decision_deferred: true,
          evidence_citations: [],
          prohibited_content_check_passed: true,
        });
      } finally {
        setAssistantLoading(false);
      }
    },
    [activeEvent, apiCandidates, bannerEvent],
  );

  const openDossierForEvent = useCallback((eventId: string) => {
    setDossierEventId(eventId);
    setView('dossier');
  }, []);

  // Context-aware assistant labels + suggestions per view.
  const { assistantContext, suggestedQueries } = useMemo(() => {
    const batchCtx = activeEvent?.summary.batch_label ?? bannerEvent?.batch_label;
    switch (view) {
      case 'command':
        return {
          assistantContext: batchCtx ? `Active event · ${batchCtx}` : 'Active Event',
          suggestedQueries: [
            'What is blocking batch release?',
            'What is the quality risk for this excursion?',
            'Show the evidence checklist',
          ],
        };
      case 'floormap':
        return {
          assistantContext: 'Live Floor Map',
          suggestedQueries: ['Which connectors are degraded?', 'What data is stale right now?', 'Show the edge gateway status'],
        };
      case 'release':
        return {
          assistantContext: 'Release Board',
          suggestedQueries: ['What is blocking batch release?', 'Which batches are ready to release?', 'Summarize open CAPAs'],
        };
      case 'dossier':
        return {
          assistantContext: fullDossier ? `Dossier · ${fullDossier.batch_label}` : 'Dossier Review',
          suggestedQueries: ['What evidence is missing?', 'Is this dossier audit-ready?', 'Summarize the impact assessment'],
        };
      case 'connectors':
        return {
          assistantContext: 'Connector Pulse',
          suggestedQueries: ['Which connectors are degraded?', 'What is the ingestion rate?', 'Which topics are stale?'],
        };
      case 'readiness':
        return {
          assistantContext: 'Readiness Matrix',
          suggestedQueries: ['What is driving the red cells?', 'Which site has the highest risk?', 'Summarize enterprise readiness'],
        };
      default:
        return {
          assistantContext: 'Diagnostics',
          suggestedQueries: ['Is the data backbone healthy?', 'Which connectors are down?', 'Summarize system status'],
        };
    }
  }, [view, activeEvent, bannerEvent, fullDossier]);

  const apiLabel = activeApiBase || (typeof window !== 'undefined' ? window.location.origin : '');
  const healthStatus =
    connState === 'offline' ? 'red' : connState === 'degraded' ? 'yellow' : bannerEvent?.status === 'red' ? 'red' : 'green';
  const healthSc = statusColor(healthStatus);

  return (
    <div className="flex h-screen flex-col bg-app text-ink2">
      {/* TOP RAIL */}
      <header className="flex h-12 shrink-0 items-center justify-between border-b border-line bg-panel px-4 shadow-panel">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <ShieldCheck size={18} className="text-brand" />
            <span className="text-sm font-bold tracking-tight text-ink">AEROS</span>
          </div>
          <div className="hidden items-center gap-1.5 rounded border border-line bg-panel2 px-2.5 py-1 text-xs text-ink2 sm:flex">
            <Building2 size={13} className="text-ink3" />
            acme_pharma <span className="text-ink3">›</span> Hyderabad Plant
          </div>
        </div>

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
          <div className="flex items-center gap-1.5 text-xs text-ink3" title={`Connectivity: ${connState}`}>
            <span className={cx('h-2.5 w-2.5 rounded-full', healthSc.dot, healthStatus !== 'green' && 'animate-breathe')} />
            <span className="hidden sm:inline capitalize">{connState}</span>
          </div>
        </div>
      </header>

      {/* Non-blocking connectivity banner */}
      {connState === 'offline' && (
        <div className="flex items-center justify-between gap-3 border-b border-status-red-line bg-status-red-soft px-4 py-2 text-xs text-status-red">
          <span className="flex items-center gap-2">
            <WifiOff size={14} />
            Can’t reach the assurance API. Retrying automatically…
            <code className="rounded bg-panel px-1.5 py-0.5 text-[11px] text-ink2">
              docker compose --profile ui up -d api
            </code>
          </span>
          <button
            onClick={manualRetry}
            className="flex items-center gap-1 rounded border border-status-red-line bg-panel px-2 py-1 font-medium text-status-red hover:bg-status-red-soft"
          >
            <RefreshCw size={12} /> Retry now
          </button>
        </div>
      )}
      {connState === 'degraded' && degradedDetail && (
        <div className="flex items-center gap-2 border-b border-status-amber-line bg-status-amber-soft px-4 py-1.5 text-xs text-status-amber">
          <Activity size={13} /> {degradedDetail}
        </div>
      )}

      <div className="flex min-h-0 flex-1">
        {/* LEFT SIDEBAR - unified, always-visible */}
        <nav
          className={cx(
            'flex shrink-0 flex-col border-r border-line bg-panel transition-all duration-200',
            collapsed ? 'w-16' : 'w-56',
          )}
        >
          <div className="flex-1 space-y-1 p-2">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const active = view === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setView(item.id)}
                  className={cx(
                    'flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm transition',
                    active ? 'bg-brand-soft font-medium text-brand' : 'text-ink2 hover:bg-panel2 hover:text-ink',
                  )}
                  title={item.label}
                >
                  <Icon size={16} className="shrink-0" />
                  {!collapsed && (
                    <span className="flex min-w-0 flex-1 items-center justify-between gap-2">
                      <span className="truncate">{item.label}</span>
                      <span className="shrink-0 rounded bg-panel3 px-1 py-0.5 text-[9px] font-medium uppercase tracking-wide text-ink3">
                        {item.affinity}
                      </span>
                    </span>
                  )}
                </button>
              );
            })}
          </div>
          <button
            onClick={() => setCollapsed((value) => !value)}
            className="flex items-center justify-center border-t border-line py-2 text-ink3 hover:text-ink"
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
              {view === 'command' && (
                <CommandCenter
                  event={activeEvent}
                  loading={eventLoading}
                  onOpenDossier={openDossierForEvent}
                />
              )}
              {view === 'floormap' && <PlantFloorMap sites={floorSites} />}
              {view === 'release' && (
                <QAReleaseBoardV2
                  queue={queue}
                  dossier={releaseDossier}
                  workflow={workflow}
                  onAsk={askAssistant}
                  onApprove={() => undefined}
                />
              )}
              {view === 'connectors' && <ConnectorHealthGrid connectors={connectors} />}
              {view === 'readiness' && <LeadershipMatrix readiness={readiness} />}
              {view === 'dossier' && (
                <DossierViewer
                  events={events}
                  dossier={fullDossier}
                  loading={dossierLoading}
                  selectedEventId={dossierEventId ?? fullDossier?.event_id ?? null}
                  onSelect={setDossierEventId}
                  onAsk={askAssistant}
                />
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

      <DendrixAssistant
        open={assistantOpen}
        onToggle={setAssistantOpen}
        contextLabel={assistantContext}
        suggestedQueries={suggestedQueries}
        response={assistantResponse}
        loading={assistantLoading}
        onSubmit={askAssistant}
      />

      <div className="flex h-6 shrink-0 items-center justify-between border-t border-line bg-panel px-4 text-[10px] text-ink3">
        <span className="flex items-center gap-1.5">
          <Activity size={10} /> API: {apiLabel || 'relative'} · {connState}
        </span>
        <span>ISA-101 High-Performance HMI · Aeros Assurance Control Plane</span>
      </div>
    </div>
  );
}
