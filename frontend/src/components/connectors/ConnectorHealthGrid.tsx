import React, { useState, useMemo } from 'react';
import {
  Radio, Server, Cloud, Database, Activity,
  ChevronRight, ChevronDown, AlertTriangle,
  Cpu, Gauge,
} from 'lucide-react';
import type { ConnectorStatusCard, TrafficLight } from '../../types/control-plane';
import { statusColor, cx } from '../../lib/design';
import { Panel, PanelHeader, StatusDot, Badge, Legend, EmptyHint } from '../ui/primitives';

// ─── Props ────────────────────────────────────────────────────────────────────

export interface ConnectorHealthGridProps {
  connectors: ConnectorStatusCard[];
}

// ─── Shared helpers ───────────────────────────────────────────────────────────

/** Deterministic SLA % derived from connector label hash. */
function deriveSla(c: ConnectorStatusCard): number {
  const hash = c.connector_label
    .split('')
    .reduce((acc, ch) => acc + ch.charCodeAt(0), 0);
  if (c.sla_breach) return 55 + (hash % 20);
  return 88 + (hash % 12);
}

// ═══════════════════════════════════════════════════════════════════════════════
// 1 ▸ INGESTION PULSE
// ═══════════════════════════════════════════════════════════════════════════════

interface PipelineStage {
  id: string;
  label: string;
  metric: string;
  status: TrafficLight;
  Icon: React.ElementType;
}

function IngestionPulse({ connectors }: { connectors: ConnectorStatusCard[] }) {
  const totalRecords = connectors.reduce((s, c) => s + (c.records_last_hour ?? 0), 0);
  const worstLatency = connectors.reduce((m, c) => Math.max(m, c.latency_ms ?? 0), 0);
  const hasIssue = connectors.some(c => c.sla_breach || !!c.degradation_reason);

  const evHr = connectors.length ? totalRecords : 12_480;
  const latMs = connectors.length ? (worstLatency || 42) : 42;

  const stages: PipelineStage[] = [
    {
      id: 'src',
      label: 'MQTT / OPC-UA',
      metric: `${evHr.toLocaleString()} ev/hr`,
      status: 'green',
      Icon: Radio,
    },
    {
      id: 'edge',
      label: 'Edge Gateway',
      metric: '4 nodes · live',
      status: 'green',
      Icon: Cpu,
    },
    {
      id: 'iot',
      label: 'IoT Core',
      metric: hasIssue ? 'partial breach' : '99.9% uptime',
      status: hasIssue ? 'yellow' : 'green',
      Icon: Cloud,
    },
    {
      id: 'sw',
      label: 'SiteWise',
      metric: `${latMs}ms p95`,
      status: latMs > 200 ? 'yellow' : 'green',
      Icon: Database,
    },
    {
      id: 'api',
      label: 'API Layer',
      metric: '< 80ms avg',
      status: 'green',
      Icon: Server,
    },
    {
      id: 'ui',
      label: 'UI',
      metric: '2s refresh',
      status: 'green',
      Icon: Activity,
    },
  ];

  return (
    <Panel className="p-4">
      <div className="flex items-center justify-between mb-4">
        <p className="text-xs font-semibold uppercase tracking-wider text-ink3">
          Ingestion Pulse
        </p>
        <span className="text-[10px] text-ink3 font-mono">live · data pipeline</span>
      </div>

      {/* Pipeline row */}
      <div className="flex items-center gap-0 overflow-x-auto pb-1 min-w-0">
        {stages.map((stage, i) => {
          const sc = statusColor(stage.status);
          return (
            <React.Fragment key={stage.id}>
              {/* Stage node */}
              <div
                className={cx(
                  'flex flex-col items-center gap-1.5 rounded-lg border px-3 py-2.5 flex-shrink-0 min-w-[96px]',
                  sc.bg,
                  sc.border,
                )}
              >
                <div className="flex items-center gap-1.5">
                  <StatusDot status={stage.status} size={6} />
                  <stage.Icon className={cx('w-3.5 h-3.5', sc.text)} />
                </div>
                <span className="text-[11px] font-semibold text-ink text-center leading-tight whitespace-nowrap">
                  {stage.label}
                </span>
                <span className="text-[10px] text-ink3 text-center whitespace-nowrap">
                  {stage.metric}
                </span>
              </div>

              {/* Arrow connector */}
              {i < stages.length - 1 && (
                <div className="flex items-center flex-shrink-0 mx-0.5">
                  <div className="w-4 h-px bg-line" />
                  <div
                    className="w-0 h-0 flex-shrink-0"
                    style={{
                      borderTop: '4px solid transparent',
                      borderBottom: '4px solid transparent',
                      borderLeft: '6px solid #cbd5e1',
                    }}
                  />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>

      {/* Overall throughput summary */}
      <div className="mt-3 flex items-center gap-3 flex-wrap">
        <div className="flex items-center gap-1.5 bg-panel2 rounded px-2.5 py-1">
          <Gauge className="w-3 h-3 text-ink3" />
          <span className="text-[11px] text-ink2">Total throughput</span>
          <span className="text-[11px] font-semibold text-status-green">
            {evHr.toLocaleString()} records/hr
          </span>
        </div>
        <div className="flex items-center gap-1.5 bg-panel2 rounded px-2.5 py-1">
          <Activity className="w-3 h-3 text-ink3" />
          <span className="text-[11px] text-ink2">Worst latency</span>
          <span
            className={cx(
              'text-[11px] font-semibold',
              latMs > 200 ? 'text-status-amber' : 'text-status-green',
            )}
          >
            {latMs}ms
          </span>
        </div>
        {hasIssue && (
          <div className="flex items-center gap-1.5 bg-status-amber-soft border border-status-amber-line rounded px-2.5 py-1">
            <AlertTriangle className="w-3 h-3 text-status-amber" />
            <span className="text-[11px] text-status-amber">1 connector degraded — SLA watch</span>
          </div>
        )}
      </div>
    </Panel>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 2 ▸ CONNECTOR HEALTH GRID
// ═══════════════════════════════════════════════════════════════════════════════

function ConnectorTile({ connector: c }: { connector: ConnectorStatusCard }) {
  const sc = statusColor(c.status);
  const lc = statusColor(c.latency_status);
  const sla = useMemo(() => deriveSla(c), [c.connector_label, c.sla_breach]);

  const slaBarColor =
    c.sla_breach
      ? 'bg-status-amber'
      : c.status === 'red'
      ? 'bg-status-red'
      : 'bg-status-green';

  const slaTextColor =
    c.sla_breach ? 'text-status-amber' : 'text-status-green';

  return (
    <div
      className={cx(
        'rounded-lg border p-3 flex flex-col gap-2 bg-panel transition-colors hover:bg-panel2',
        sc.border,
      )}
    >
      {/* ── Header ── */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <StatusDot status={c.status} size={8} />
          <span className="text-[13px] font-semibold text-ink truncate leading-snug">
            {c.connector_label}
          </span>
        </div>
        <Badge tone="neutral" className={cx(sc.bg, sc.text, sc.border)}>
          {c.status}
        </Badge>
      </div>

      {/* ── System type badge ── */}
      <p className="text-[10px] uppercase tracking-wider text-ink3 font-medium -mt-1">
        {c.system_type}
      </p>

      {/* ── Key metrics ── */}
      <div className="grid grid-cols-2 gap-x-3 gap-y-0.5 text-[11px]">
        <span className="text-ink3">Last sync</span>
        <span className="text-ink2 truncate">{c.last_ingestion_label}</span>

        <span className="text-ink3">Records/hr</span>
        <span className="text-ink2">
          {c.records_last_hour != null ? c.records_last_hour.toLocaleString() : '—'}
        </span>
      </div>

      {/* ── SLA compliance bar ── */}
      <div className="space-y-1">
        <div className="flex items-center justify-between text-[10px]">
          <span className="text-ink3">SLA compliance</span>
          <span className={cx('font-semibold', slaTextColor)}>{sla}%</span>
        </div>
        <div className="h-1.5 rounded-full bg-panel3 overflow-hidden">
          <div
            className={cx('h-full rounded-full', slaBarColor)}
            style={{ width: `${sla}%` }}
          />
        </div>
      </div>

      {/* ── Latency ── */}
      <div className="flex items-center justify-between text-[11px]">
        <span className="text-ink3">Latency</span>
        <span className={cx('font-semibold', lc.text)}>
          {c.latency_ms != null ? `${c.latency_ms} ms` : '—'}
        </span>
      </div>

      {/* ── Degradation warning ── */}
      {c.degradation_reason && (
        <div className="flex items-start gap-1.5 rounded-md bg-status-amber-soft border border-status-amber-line px-2 py-1.5 mt-0.5">
          <AlertTriangle className="w-3 h-3 text-status-amber flex-shrink-0 mt-px" />
          <span className="text-[10px] text-status-amber leading-snug">{c.degradation_reason}</span>
        </div>
      )}
    </div>
  );
}

function ConnectorGrid({ connectors }: { connectors: ConnectorStatusCard[] }) {
  const groups = useMemo(() => {
    const map = new Map<string, ConnectorStatusCard[]>();
    for (const c of connectors) {
      const key = c.system_type || 'Other';
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(c);
    }
    return Array.from(map.entries()).sort(([a], [b]) => a.localeCompare(b));
  }, [connectors]);

  return (
    <Panel className="p-4">
      <p className="text-xs font-semibold uppercase tracking-wider text-ink3 mb-4">
        Connector Health Grid
      </p>

      {connectors.length === 0 ? (
        <EmptyHint 
          title="No connectors configured" 
          detail="Connect a data source to begin ingestion."
        />
      ) : (
        <div className="space-y-6">
          {groups.map(([groupName, items]) => (
            <div key={groupName}>
              {/* Group header */}
              <div className="flex items-center gap-2 mb-2.5">
                <span className="text-[10px] uppercase tracking-wider font-semibold text-ink2">
                  {groupName}
                </span>
                <Badge tone="neutral">
                  {items.length}
                </Badge>
                <div className="flex-1 h-px bg-line ml-1" />
              </div>

              {/* Tile grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
                {items.map(c => (
                  <ConnectorTile key={c.connector_label} connector={c} />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </Panel>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// 3 ▸ UNS TOPIC EXPLORER
// ═══════════════════════════════════════════════════════════════════════════════

interface UNSLeafData {
  label: string;
  value: string;
  unit: string;
  freshness: string;
  status: TrafficLight;
}

interface UNSTreeData {
  path: string;
  segment: string;
  children?: UNSTreeData[];
  leaf?: UNSLeafData;
}

const UNS_TREE: UNSTreeData = {
  path: 'areos',
  segment: 'areos',
  children: [
    {
      path: 'areos/acme_pharma',
      segment: 'acme_pharma',
      children: [
        {
          path: 'areos/acme_pharma/hyd_site_01',
          segment: 'hyd_site_01',
          children: [
            {
              path: 'areos/acme_pharma/hyd_site_01/osd_manufacturing',
              segment: 'osd_manufacturing',
              children: [
                {
                  path: 'areos/acme_pharma/hyd_site_01/osd_manufacturing/compression_room_1',
                  segment: 'compression_room_1',
                  children: [
                    {
                      path: 'areos/acme_pharma/hyd_site_01/osd_manufacturing/compression_room_1/ahu_03',
                      segment: 'ahu_03',
                      children: [
                        {
                          path: 'areos/acme_pharma/hyd_site_01/osd_manufacturing/compression_room_1/ahu_03/environment',
                          segment: 'environment',
                          children: [
                            {
                              path: 'areos/acme_pharma/hyd_site_01/osd_manufacturing/compression_room_1/ahu_03/environment/relative_humidity',
                              segment: 'relative_humidity',
                              leaf: {
                                label: 'relative_humidity',
                                value: '63.2',
                                unit: '% RH',
                                freshness: '12s ago',
                                status: 'yellow',
                              },
                            },
                            {
                              path: 'areos/acme_pharma/hyd_site_01/osd_manufacturing/compression_room_1/ahu_03/environment/temperature',
                              segment: 'temperature',
                              leaf: {
                                label: 'temperature',
                                value: '21.4',
                                unit: '°C',
                                freshness: '12s ago',
                                status: 'green',
                              },
                            },
                            {
                              path: 'areos/acme_pharma/hyd_site_01/osd_manufacturing/compression_room_1/ahu_03/environment/differential_pressure',
                              segment: 'differential_pressure',
                              leaf: {
                                label: 'differential_pressure',
                                value: '+12.5',
                                unit: 'Pa',
                                freshness: '8s ago',
                                status: 'green',
                              },
                            },
                          ],
                        },
                      ],
                    },
                    {
                      path: 'areos/acme_pharma/hyd_site_01/osd_manufacturing/compression_room_1/tablet_press_01',
                      segment: 'tablet_press_01',
                      children: [
                        {
                          path: 'areos/acme_pharma/hyd_site_01/osd_manufacturing/compression_room_1/tablet_press_01/process',
                          segment: 'process',
                          children: [
                            {
                              path: 'areos/acme_pharma/hyd_site_01/osd_manufacturing/compression_room_1/tablet_press_01/process/main_compression_force',
                              segment: 'main_compression_force',
                              leaf: {
                                label: 'main_compression_force',
                                value: '14.8',
                                unit: 'kN',
                                freshness: '3s ago',
                                status: 'green',
                              },
                            },
                            {
                              path: 'areos/acme_pharma/hyd_site_01/osd_manufacturing/compression_room_1/tablet_press_01/process/turret_speed',
                              segment: 'turret_speed',
                              leaf: {
                                label: 'turret_speed',
                                value: '42',
                                unit: 'rpm',
                                freshness: '3s ago',
                                status: 'green',
                              },
                            },
                            {
                              path: 'areos/acme_pharma/hyd_site_01/osd_manufacturing/compression_room_1/tablet_press_01/process/tablet_weight',
                              segment: 'tablet_weight',
                              leaf: {
                                label: 'tablet_weight',
                                value: '502.1',
                                unit: 'mg',
                                freshness: '5s ago',
                                status: 'green',
                              },
                            },
                          ],
                        },
                      ],
                    },
                  ],
                },
              ],
            },
          ],
        },
      ],
    },
  ],
};

/** Default paths that are open on mount. */
const DEFAULT_EXPANDED = new Set<string>([
  'areos',
  'areos/acme_pharma',
  'areos/acme_pharma/hyd_site_01',
  'areos/acme_pharma/hyd_site_01/osd_manufacturing',
  'areos/acme_pharma/hyd_site_01/osd_manufacturing/compression_room_1',
  'areos/acme_pharma/hyd_site_01/osd_manufacturing/compression_room_1/ahu_03',
  'areos/acme_pharma/hyd_site_01/osd_manufacturing/compression_room_1/ahu_03/environment',
]);

function UNSLeafRow({ leaf }: { leaf: UNSLeafData }) {
  const sc = statusColor(leaf.status);
  return (
    <div className="flex items-center gap-2 py-0.5 px-2 rounded hover:bg-panel2 group">
      <StatusDot status={leaf.status} size={6} />
      <span className="text-[11px] font-mono text-ink2">{leaf.label}</span>
      <span className={cx('text-[11px] font-semibold', sc.text)}>
        {leaf.value}&thinsp;{leaf.unit}
      </span>
      <span className="text-[10px] text-ink3 ml-auto">{leaf.freshness}</span>
    </div>
  );
}

function UNSNode({
  node,
  expanded,
  toggle,
  depth,
}: {
  node: UNSTreeData;
  expanded: Set<string>;
  toggle: (path: string) => void;
  depth: number;
}) {
  const indentPx = depth * 14;

  if (node.leaf) {
    return (
      <div style={{ paddingLeft: indentPx }}>
        <UNSLeafRow leaf={node.leaf} />
      </div>
    );
  }

  const isOpen = expanded.has(node.path);
  const childCount = node.children?.length ?? 0;

  return (
    <div>
      <button
        onClick={() => toggle(node.path)}
        className="flex items-center gap-1 w-full text-left py-0.5 px-1.5 rounded hover:bg-panel2 transition-colors"
        style={{ paddingLeft: indentPx + 4 }}
      >
        {isOpen ? (
          <ChevronDown className="w-3 h-3 text-ink3 flex-shrink-0" />
        ) : (
          <ChevronRight className="w-3 h-3 text-ink3 flex-shrink-0" />
        )}
        <span className="text-[11px] font-mono text-ink">{node.segment}</span>
        <span className="text-[10px] text-ink3 font-mono">/</span>
        {childCount > 0 && (
          <span className="text-[10px] text-ink3 ml-1">
            ({childCount})
          </span>
        )}
      </button>

      {isOpen && node.children && (
        <div>
          {node.children.map(child => (
            <UNSNode
              key={child.path}
              node={child}
              expanded={expanded}
              toggle={toggle}
              depth={depth + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function UNSTopicExplorer() {
  const [expanded, setExpanded] = useState<Set<string>>(DEFAULT_EXPANDED);

  const toggle = (path: string) =>
    setExpanded(prev => {
      const next = new Set(prev);
      next.has(path) ? next.delete(path) : next.add(path);
      return next;
    });

  return (
    <Panel>
      <PanelHeader 
        title="UNS Topic Explorer" 
        subtitle="Unified Namespace — ISA-95 hierarchy · live broker topics"
        right={
          <span className="text-[10px] text-ink3 font-mono hidden sm:block">
            areos/{'{tenant}/{site}/{area}/{room}/{asset}/{domain}/{metric}'}
          </span>
        }
      />

      <div className="p-4">
        <div className="rounded-lg bg-panel3 border border-line2 p-3 overflow-x-auto">
          <UNSNode
            node={UNS_TREE}
            expanded={expanded}
            toggle={toggle}
            depth={0}
          />
        </div>

        {/* Legend */}
        <div className="mt-3">
          <Legend items={[
            { status: 'green', label: 'In spec' },
            { status: 'yellow', label: 'Near limit' },
            { status: 'red', label: 'Out of spec' },
          ]} />
        </div>
      </div>
    </Panel>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// ROOT EXPORT
// ═══════════════════════════════════════════════════════════════════════════════

export function ConnectorHealthGrid({ connectors }: ConnectorHealthGridProps) {
  return (
    <div className="space-y-4 p-3 overflow-y-auto h-full">
      <UNSTopicExplorer />
      <IngestionPulse connectors={connectors} />
      <ConnectorGrid connectors={connectors} />
    </div>
  );
}
