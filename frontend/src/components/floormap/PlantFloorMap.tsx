import React, { useState, useMemo } from 'react';
import {
  Cloud,
  Server,
  Cpu,
  Thermometer,
  Factory,
  X,
  Boxes,
  Activity,
  Gauge,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import type {
  ManufacturingSiteTopology,
  TopologyNode,
  DataFlowEdge,
  TrafficLight,
} from '../../types/control-plane';
import { statusHex, statusColor, cx } from '../../lib/design';

// ─── SVG canvas constants ─────────────────────────────────────────────────────
const SVG_W = 1400;
const SVG_H = 900;
const PAD_X = 70;
const USABLE_W = SVG_W - PAD_X * 2;

// Layer band Y boundaries
const L4_Y1 = 46;
const L4_Y2 = 212;
const L4_CY = 129;
const L3_Y1 = 238;
const L3_Y2 = 398;
const L3_CY = 318;
const L12_Y1 = 422;

// Node dimensions
const L4_W = 154;
const L4_H = 66;
const L3_W = 140;
const L3_H = 56;
const EQ_W = 90;
const EQ_H = 66;
const EQ_GAP = 10;

// Room zone dimensions
const ROOM_Y = 442;
const ROOM_H = 418;
const ROOM_GAP = 16;
const ROOM_MIN_W = 185;

// ─── Icon registry ────────────────────────────────────────────────────────────
type IconName =
  | 'Cloud'
  | 'Server'
  | 'Cpu'
  | 'Thermometer'
  | 'Factory'
  | 'Boxes'
  | 'Activity'
  | 'Gauge';

const ICON_MAP: Record<IconName, LucideIcon> = {
  Cloud,
  Server,
  Cpu,
  Thermometer,
  Factory,
  Boxes,
  Activity,
  Gauge,
};

// ─── Sensor detection ─────────────────────────────────────────────────────────
function isSensor(n: TopologyNode): boolean {
  if (n.node_type !== 'asset') return false;
  const hay = (
    n.node_label +
    ' ' +
    Object.values(n.metadata).join(' ')
  ).toLowerCase();
  return [
    'sensor',
    'temp',
    'thermometer',
    'gauge',
    'probe',
    'thermocouple',
    'pressure',
    'humidity',
    'flowmeter',
    'flow meter',
  ].some(kw => hay.includes(kw));
}

function getIconName(n: TopologyNode): IconName {
  switch (n.node_type) {
    case 'enterprise':
      return 'Cloud';
    case 'site':
      return 'Cloud';
    case 'connector':
      return 'Activity';
    case 'system':
      return 'Server';
    case 'area':
      return 'Factory';
    case 'line':
      return 'Boxes';
    case 'cell':
      return 'Cpu';
    case 'asset':
      return isSensor(n) ? 'Thermometer' : 'Cpu';
    default:
      return 'Cpu';
  }
}

// ─── Misc helpers ─────────────────────────────────────────────────────────────
function trunc(s: string, max: number): string {
  return s.length > max ? s.slice(0, max - 1) + '…' : s;
}

// ─── Layout types & computation ───────────────────────────────────────────────
interface NodePos {
  x: number;
  y: number;
  w: number;
  h: number;
}

function computeLayout(nodes: TopologyNode[]): Map<string, NodePos> {
  const pos = new Map<string, NodePos>();

  const l4 = nodes.filter(
    n =>
      n.node_type === 'enterprise' ||
      n.node_type === 'connector' ||
      n.node_type === 'site',
  );
  const l3 = nodes.filter(n => n.node_type === 'system');
  const rooms = nodes.filter(
    n => n.node_type === 'area' || n.node_type === 'line',
  );
  const equip = nodes.filter(
    n => n.node_type === 'cell' || n.node_type === 'asset',
  );

  // L4 – evenly distribute across full width
  l4.forEach((n, i) => {
    pos.set(n.node_label, {
      x: PAD_X + (i + 0.5) * (USABLE_W / Math.max(l4.length, 1)),
      y: L4_CY,
      w: L4_W,
      h: L4_H,
    });
  });

  // L3 – same distribution logic
  l3.forEach((n, i) => {
    pos.set(n.node_label, {
      x: PAD_X + (i + 0.5) * (USABLE_W / Math.max(l3.length, 1)),
      y: L3_CY,
      w: L3_W,
      h: L3_H,
    });
  });

  // Rooms + child equipment
  const roomCount = Math.max(rooms.length, 1);
  const roomW = Math.max(
    (USABLE_W - (roomCount - 1) * ROOM_GAP) / roomCount,
    ROOM_MIN_W,
  );
  const roomIds = new Set(rooms.map(r => r.node_id));

  rooms.forEach((room, ri) => {
    const rx = PAD_X + ri * (roomW + ROOM_GAP);
    pos.set(room.node_label, {
      x: rx + roomW / 2,
      y: ROOM_Y + ROOM_H / 2,
      w: roomW,
      h: ROOM_H,
    });

    const children = equip.filter(n => n.parent_id === room.node_id);
    const cols = Math.max(
      Math.floor((roomW - 20) / (EQ_W + EQ_GAP)),
      1,
    );
    children.forEach((child, ci) => {
      pos.set(child.node_label, {
        x: rx + 12 + (ci % cols) * (EQ_W + EQ_GAP) + EQ_W / 2,
        y: ROOM_Y + 48 + Math.floor(ci / cols) * (EQ_H + EQ_GAP) + EQ_H / 2,
        w: EQ_W,
        h: EQ_H,
      });
    });
  });

  // Orphan equipment – no resolved parent room
  const orphans = equip.filter(
    n => !n.parent_id || !roomIds.has(n.parent_id),
  );
  const obx =
    rooms.length > 0
      ? PAD_X + rooms.length * (roomW + ROOM_GAP) + 12
      : PAD_X;
  orphans.forEach((n, i) => {
    pos.set(n.node_label, {
      x: obx + (i % 4) * (EQ_W + EQ_GAP) + EQ_W / 2,
      y: ROOM_Y + 48 + Math.floor(i / 4) * (EQ_H + EQ_GAP) + EQ_H / 2,
      w: EQ_W,
      h: EQ_H,
    });
  });

  return pos;
}

// ─── SVG icon helper ──────────────────────────────────────────────────────────
// Renders a Lucide icon as nested SVG inside the outer SVG context.
function SvgIcon({
  name,
  x,
  y,
  size,
  color,
}: {
  name: IconName;
  x: number;
  y: number;
  size: number;
  color: string;
}) {
  const Icon = ICON_MAP[name];
  const half = size / 2;
  return (
    <g transform={`translate(${(x - half).toFixed(1)},${(y - half).toFixed(1)})`}>
      <Icon size={size} color={color} strokeWidth={1.5} />
    </g>
  );
}

// ─── Detail panel ─────────────────────────────────────────────────────────────
type PanelTarget =
  | { kind: 'node'; data: TopologyNode }
  | { kind: 'edge'; data: DataFlowEdge };

function KvRow({
  label,
  value,
  mono = false,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div className="flex gap-2 py-0.5 items-start">
      <span className="text-xs text-slate-500 shrink-0 w-24 truncate">
        {label}
      </span>
      <span
        className={cx(
          'text-xs text-slate-300 break-all flex-1',
          mono ? 'font-mono text-[10px] leading-relaxed' : '',
        )}
      >
        {value}
      </span>
    </div>
  );
}

function DetailPanel({
  target,
  onClose,
}: {
  target: PanelTarget;
  onClose: () => void;
}) {
  const status: TrafficLight = target.data.status;
  const sc = statusColor(status);

  const title =
    target.kind === 'node'
      ? target.data.node_label
      : `${target.data.source_label} → ${target.data.target_label}`;

  const subtitle =
    target.kind === 'node'
      ? target.data.node_type
      : target.data.flow_type;

  return (
    <div className="absolute inset-y-0 right-0 w-80 z-20 flex flex-col bg-surface-900 border-l border-surface-700 shadow-2xl">
      {/* Header */}
      <div className="flex items-start justify-between px-4 py-3 border-b border-surface-700 shrink-0">
        <div className="min-w-0 flex-1">
          <p className="text-[10px] tracking-[0.14em] text-slate-600 uppercase mb-0.5">
            {subtitle}
          </p>
          <h3 className="text-sm font-semibold text-slate-100 leading-snug truncate">
            {title}
          </h3>
        </div>
        <button
          onClick={onClose}
          className="ml-3 mt-0.5 shrink-0 p-1 rounded text-slate-500 hover:text-slate-200 hover:bg-surface-800 transition-colors"
        >
          <X size={14} />
        </button>
      </div>

      {/* Status chip */}
      <div
        className={cx(
          'mx-4 mt-3 mb-1 px-3 py-1.5 rounded flex items-center gap-2 border shrink-0',
          sc.bg,
          sc.border,
        )}
      >
        <span className={cx('w-2 h-2 rounded-full shrink-0', sc.dot)} />
        <span
          className={cx(
            'text-xs font-semibold tracking-widest',
            sc.text,
          )}
        >
          {status.toUpperCase()}
        </span>
      </div>

      {/* Scrollable body */}
      <div className="flex-1 overflow-y-auto min-h-0 px-4 py-3 space-y-4">
        {target.kind === 'node' ? (
          <>
            <section>
              <p className="text-[10px] tracking-[0.12em] text-slate-600 uppercase mb-1.5">
                Node
              </p>
              <KvRow label="ID" value={target.data.node_id} mono />
              <KvRow label="Type" value={target.data.node_type} />
              {target.data.parent_id && (
                <KvRow
                  label="Parent"
                  value={target.data.parent_id}
                  mono
                />
              )}
            </section>

            {Object.keys(target.data.metadata).length > 0 && (
              <section>
                <p className="text-[10px] tracking-[0.12em] text-slate-600 uppercase mb-1.5">
                  Metadata
                </p>
                {Object.entries(target.data.metadata).map(([k, v]) => (
                  <KvRow key={k} label={k} value={v} />
                ))}
              </section>
            )}
          </>
        ) : (
          <>
            <section>
              <p className="text-[10px] tracking-[0.12em] text-slate-600 uppercase mb-1.5">
                Flow
              </p>
              <KvRow label="Source" value={target.data.source_label} />
              <KvRow label="Target" value={target.data.target_label} />
              <KvRow label="Type" value={target.data.flow_type} />
              <KvRow
                label="Latency"
                value={target.data.latency_label ?? '—'}
              />
              <KvRow
                label="Data rate"
                value={target.data.data_rate_label ?? '—'}
              />
              <KvRow
                label="Last data"
                value={target.data.last_data_label ?? '—'}
              />
            </section>

            {target.data.degradation_reason && (
              <div className="px-3 py-2.5 rounded border bg-status-red/5 border-status-red/25">
                <p className="text-[10px] tracking-[0.12em] text-status-red uppercase font-semibold mb-1">
                  Degradation
                </p>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {target.data.degradation_reason}
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

// ─── Equipment node renderer (shared between room-children and orphans) ────────
function EquipmentNodeG({
  node,
  pos,
  selected,
  onSelect,
}: {
  node: TopologyNode;
  pos: NodePos;
  selected: boolean;
  onSelect: () => void;
}) {
  const hex = statusHex(node.status);
  const icon = getIconName(node);

  if (isSensor(node)) {
    const reading =
      node.metadata['reading'] ?? node.metadata['value'] ?? null;
    return (
      <g onClick={onSelect} style={{ cursor: 'pointer' }}>
        {selected && (
          <circle cx={pos.x} cy={pos.y} r={17} fill={hex} fillOpacity={0.12} />
        )}
        <circle
          cx={pos.x}
          cy={pos.y}
          r={11}
          fill={hex}
          fillOpacity={0.1}
          stroke={hex}
          strokeWidth={selected ? 2.5 : 1.2}
        />
        <circle cx={pos.x} cy={pos.y} r={5} fill={hex} />
        {reading && (
          <text
            x={pos.x}
            y={pos.y - 17}
            textAnchor="middle"
            fontSize={8}
            fill={hex}
            fontFamily="monospace"
            fontWeight={600}
          >
            {reading}
          </text>
        )}
        <text
          x={pos.x}
          y={pos.y + 24}
          textAnchor="middle"
          fontSize={8}
          fill="#475569"
        >
          {trunc(node.node_label, 12)}
        </text>
      </g>
    );
  }

  const ex = pos.x - EQ_W / 2;
  const ey = pos.y - EQ_H / 2;

  return (
    <g onClick={onSelect} style={{ cursor: 'pointer' }}>
      {selected && (
        <rect
          x={ex - 3}
          y={ey - 3}
          width={EQ_W + 6}
          height={EQ_H + 6}
          rx={9}
          fill="#60a5fa"
          fillOpacity={0.07}
          stroke="#60a5fa"
          strokeWidth={1}
          strokeOpacity={0.4}
        />
      )}
      <rect
        x={ex}
        y={ey}
        width={EQ_W}
        height={EQ_H}
        rx={6}
        fill="#0e1c30"
        stroke={selected ? '#60a5fa' : hex}
        strokeWidth={selected ? 2 : 1.5}
      />
      {/* status LED top-right */}
      <circle cx={ex + EQ_W - 7} cy={ey + 7} r={3.5} fill={hex} />
      {/* icon centered in upper half */}
      <SvgIcon name={icon} x={pos.x} y={pos.y - 11} size={13} color={hex} />
      {/* label */}
      <text
        x={pos.x}
        y={pos.y + 9}
        textAnchor="middle"
        fontSize={8.5}
        fill="#94a3b8"
      >
        {trunc(node.node_label, 11)}
      </text>
      {/* live reading if present */}
      {node.metadata['reading'] && (
        <text
          x={pos.x}
          y={pos.y + 20}
          textAnchor="middle"
          fontSize={7.5}
          fill={hex}
          fontFamily="monospace"
        >
          {node.metadata['reading']}
        </text>
      )}
    </g>
  );
}

// ─── Props & main export ──────────────────────────────────────────────────────
export interface PlantFloorMapProps {
  topology: ManufacturingSiteTopology[];
}

export function PlantFloorMap({ topology }: PlantFloorMapProps) {
  const [selected, setSelected] = useState<PanelTarget | null>(null);

  const site = topology[0];

  const positions = useMemo(
    () => (site ? computeLayout(site.nodes) : new Map<string, NodePos>()),
    [site],
  );

  // ── Empty state ──────────────────────────────────────────────────────────
  if (!site) {
    return (
      <div className="flex h-full w-full min-h-[600px] items-center justify-center rounded-lg border border-surface-700 bg-surface-950">
        <div className="text-center space-y-3">
          <Factory size={38} className="mx-auto text-slate-700" />
          <p className="text-sm text-slate-500">No topology data</p>
          <p className="text-xs text-slate-600">
            Provide at least one ManufacturingSiteTopology entry
          </p>
        </div>
      </div>
    );
  }

  // ── Node classification ───────────────────────────────────────────────────
  const nodes = site.nodes;
  const l4Nodes = nodes.filter(
    n =>
      n.node_type === 'enterprise' ||
      n.node_type === 'connector' ||
      n.node_type === 'site',
  );
  const l3Nodes = nodes.filter(n => n.node_type === 'system');
  const roomNodes = nodes.filter(
    n => n.node_type === 'area' || n.node_type === 'line',
  );
  const equipNodes = nodes.filter(
    n => n.node_type === 'cell' || n.node_type === 'asset',
  );
  const roomIds = new Set(roomNodes.map(r => r.node_id));

  const gp = (label: string) => positions.get(label);
  const isNodeSel = (n: TopologyNode) =>
    selected?.kind === 'node' && selected.data.node_id === n.node_id;

  const selectNode = (n: TopologyNode) =>
    setSelected({ kind: 'node', data: n });
  const selectEdge = (e: DataFlowEdge) =>
    setSelected({ kind: 'edge', data: e });

  return (
    <div className="relative h-full w-full min-h-[600px] rounded-lg border border-surface-700 bg-surface-950 overflow-hidden">
      {/* ── Title chip ─────────────────────────────────────────────────────── */}
      <div className="absolute top-3 left-4 z-10 flex items-center gap-2 px-3 py-1.5 rounded-md bg-surface-900/90 border border-surface-700 backdrop-blur-sm pointer-events-none select-none">
        <Factory size={12} className="text-slate-500 shrink-0" />
        <span className="text-[11px] font-semibold text-slate-300 tracking-wide">
          Plant Floor Map
        </span>
        <span className="text-slate-600 text-xs">·</span>
        <span className="text-[11px] text-slate-400 truncate max-w-[160px]">
          {site.site_label}
        </span>
        {site.archetype && (
          <>
            <span className="text-slate-700 text-xs">|</span>
            <span className="text-[10px] text-slate-600 truncate max-w-[100px]">
              {site.archetype}
            </span>
          </>
        )}
      </div>

      {/* ── SVG canvas ─────────────────────────────────────────────────────── */}
      <svg
        viewBox={`0 0 ${SVG_W} ${SVG_H}`}
        className="h-full w-full"
        style={{ display: 'block' }}
      >
        <defs>
          {/* Subtle dot grid */}
          <pattern
            id="pfm-grid"
            width="40"
            height="40"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M 40 0 L 0 0 0 40"
              fill="none"
              stroke="#1a2535"
              strokeWidth="0.4"
            />
          </pattern>

          {/* Arrow markers, one per status colour */}
          {(['green', 'yellow', 'red', 'unknown'] as const).map(s => (
            <marker
              key={s}
              id={`pfm-arr-${s}`}
              markerWidth="7"
              markerHeight="7"
              refX="5"
              refY="3"
              orient="auto"
            >
              <path d="M0,0 L0,6 L7,3 z" fill={statusHex(s)} />
            </marker>
          ))}
        </defs>

        {/* ── Solid BG + grid ───────────────────────────────────────────── */}
        <rect width={SVG_W} height={SVG_H} fill="#060b14" />
        <rect
          width={SVG_W}
          height={SVG_H}
          fill="url(#pfm-grid)"
          opacity={0.3}
        />

        {/* ── Layer band tints ──────────────────────────────────────────── */}
        <rect
          x={0}
          y={L4_Y1}
          width={SVG_W}
          height={L4_Y2 - L4_Y1}
          fill="#0c1827"
          fillOpacity={0.55}
        />
        <rect
          x={0}
          y={L3_Y1}
          width={SVG_W}
          height={L3_Y2 - L3_Y1}
          fill="#0d1626"
          fillOpacity={0.5}
        />
        <rect
          x={0}
          y={L12_Y1}
          width={SVG_W}
          height={SVG_H - L12_Y1}
          fill="#08101e"
          fillOpacity={0.5}
        />

        {/* ── Separator dashes ─────────────────────────────────────────── */}
        <line
          x1={0}
          y1={L4_Y2 + 10}
          x2={SVG_W}
          y2={L4_Y2 + 10}
          stroke="#1e3a5f"
          strokeWidth={1}
          strokeDasharray="5 9"
        />
        <line
          x1={0}
          y1={L3_Y2 + 10}
          x2={SVG_W}
          y2={L3_Y2 + 10}
          stroke="#1e3a5f"
          strokeWidth={1}
          strokeDasharray="5 9"
        />

        {/* ── Layer labels (left edge) ──────────────────────────────────── */}
        {[
          { label: 'L4 · ENTERPRISE / CLOUD', y: L4_Y1 + 14 },
          { label: 'L3 · SCADA / MES', y: L3_Y1 + 14 },
          { label: 'L1-2 · PHYSICAL FLOOR', y: L12_Y1 + 14 },
        ].map(({ label, y }) => (
          <text
            key={label}
            x={14}
            y={y}
            fontSize={9}
            fontWeight={700}
            fill="#253549"
            letterSpacing="0.13em"
            fontFamily="'JetBrains Mono','Fira Mono','Consolas',monospace"
          >
            {label}
          </text>
        ))}

        {/* ══════════════════════════════════════════════════
            DATA FLOW EDGES  — drawn first (behind nodes)
        ══════════════════════════════════════════════════ */}
        {site.edges.map((edge, ei) => {
          const src = gp(edge.source_label);
          const tgt = gp(edge.target_label);
          if (!src || !tgt) return null;

          const x1 = src.x;
          const y1 = src.y + src.h / 2 + 2;
          const x2 = tgt.x;
          const y2 = tgt.y - tgt.h / 2 - 2;
          const dy = Math.abs(y2 - y1);
          const ctrl = Math.max(dy * 0.4, 30);
          const d = `M ${x1} ${y1} C ${x1} ${y1 + ctrl}, ${x2} ${y2 - ctrl}, ${x2} ${y2}`;
          const hex = statusHex(edge.status);
          const flowing = edge.status === 'green';

          return (
            <g
              key={ei}
              onClick={() => selectEdge(edge)}
              style={{ cursor: 'pointer' }}
            >
              {/* soft glow */}
              <path
                d={d}
                stroke={hex}
                strokeWidth={7}
                fill="none"
                strokeOpacity={0.05}
              />
              {/* flow line */}
              <path
                d={d}
                stroke={hex}
                strokeWidth={1.5}
                fill="none"
                strokeOpacity={flowing ? 0.9 : 0.45}
                strokeDasharray={flowing ? '6 4' : undefined}
                className={flowing ? 'animate-flow' : undefined}
                markerEnd={`url(#pfm-arr-${edge.status})`}
              />
            </g>
          );
        })}

        {/* ══════════════════════════════════════════════════
            ROOM ZONES  (area / line containers)
        ══════════════════════════════════════════════════ */}
        {roomNodes.map(room => {
          const p = gp(room.node_label);
          if (!p) return null;
          const hex = statusHex(room.status);
          const rw = p.w;
          const rh = p.h;
          const rx = p.x - rw / 2;
          const ry = p.y - rh / 2;
          const children = equipNodes.filter(
            n => n.parent_id === room.node_id,
          );

          return (
            <g key={room.node_id}>
              {/* zone background */}
              <rect
                x={rx}
                y={ry}
                width={rw}
                height={rh}
                rx={8}
                fill="#060c16"
                stroke={hex}
                strokeWidth={1}
                strokeOpacity={0.32}
              />
              {/* top label bar */}
              <rect
                x={rx + 1}
                y={ry + 1}
                width={rw - 2}
                height={30}
                rx={7}
                fill={hex}
                fillOpacity={0.06}
              />
              {/* room label */}
              <text
                x={rx + 10}
                y={ry + 18}
                fontSize={10}
                fontWeight={700}
                fill="#3d5570"
                letterSpacing="0.08em"
                fontFamily="monospace"
              >
                {room.node_label.toUpperCase()}
              </text>
              {/* type sub-label */}
              <text
                x={rx + 10}
                y={ry + 29}
                fontSize={7.5}
                fill={hex}
                fillOpacity={0.55}
                letterSpacing="0.07em"
              >
                {room.node_type.toUpperCase()}
              </text>
              {/* status LED */}
              <circle
                cx={rx + rw - 14}
                cy={ry + 14}
                r={4.5}
                fill={hex}
                fillOpacity={0.88}
              />
              <circle
                cx={rx + rw - 14}
                cy={ry + 14}
                r={8}
                fill={hex}
                fillOpacity={0.14}
              />

              {/* ── Child equipment ─────────────────────── */}
              {children.map(child => {
                const cp = gp(child.node_label);
                if (!cp) return null;
                return (
                  <EquipmentNodeG
                    key={child.node_id}
                    node={child}
                    pos={cp}
                    selected={isNodeSel(child)}
                    onSelect={() => selectNode(child)}
                  />
                );
              })}
            </g>
          );
        })}

        {/* ══════════════════════════════════════════════════
            ORPHAN EQUIPMENT  (no resolved parent room)
        ══════════════════════════════════════════════════ */}
        {equipNodes
          .filter(n => !n.parent_id || !roomIds.has(n.parent_id))
          .map(node => {
            const p = gp(node.node_label);
            if (!p) return null;
            return (
              <EquipmentNodeG
                key={node.node_id}
                node={node}
                pos={p}
                selected={isNodeSel(node)}
                onSelect={() => selectNode(node)}
              />
            );
          })}

        {/* ══════════════════════════════════════════════════
            L4 NODES  (Enterprise / Cloud / Connector)
        ══════════════════════════════════════════════════ */}
        {l4Nodes.map(node => {
          const p = gp(node.node_label);
          if (!p) return null;
          const hex = statusHex(node.status);
          const sel = isNodeSel(node);
          const icon = getIconName(node);
          const rx = p.x - L4_W / 2;
          const ry = p.y - L4_H / 2;

          return (
            <g
              key={node.node_id}
              onClick={() => selectNode(node)}
              style={{ cursor: 'pointer' }}
            >
              {sel && (
                <rect
                  x={rx - 4}
                  y={ry - 4}
                  width={L4_W + 8}
                  height={L4_H + 8}
                  rx={26}
                  fill="#60a5fa"
                  fillOpacity={0.06}
                  stroke="#60a5fa"
                  strokeWidth={1}
                  strokeOpacity={0.35}
                />
              )}
              {/* outer glow */}
              <rect
                x={rx - 1}
                y={ry - 1}
                width={L4_W + 2}
                height={L4_H + 2}
                rx={23}
                fill={hex}
                fillOpacity={0.05}
              />
              {/* main body — large rx gives cloud/pill shape */}
              <rect
                x={rx}
                y={ry}
                width={L4_W}
                height={L4_H}
                rx={22}
                fill="#0d1929"
                stroke={sel ? '#60a5fa' : hex}
                strokeWidth={sel ? 2 : 1.5}
              />
              {/* top highlight */}
              <rect
                x={rx + 2}
                y={ry + 2}
                width={L4_W - 4}
                height={20}
                rx={20}
                fill={hex}
                fillOpacity={0.07}
              />
              {/* status LED */}
              <circle
                cx={rx + L4_W - 12}
                cy={ry + 12}
                r={4.5}
                fill={hex}
              />
              <circle
                cx={rx + L4_W - 12}
                cy={ry + 12}
                r={8}
                fill={hex}
                fillOpacity={0.18}
              />
              {/* icon */}
              <SvgIcon name={icon} x={rx + 22} y={p.y} size={15} color={hex} />
              {/* label */}
              <text
                x={rx + 42}
                y={p.y - 5}
                fontSize={10}
                fontWeight={700}
                fill="#c8d6e8"
                letterSpacing="0.02em"
              >
                {trunc(node.node_label, 16)}
              </text>
              <text
                x={rx + 42}
                y={p.y + 9}
                fontSize={8.5}
                fill="#3d566e"
                letterSpacing="0.07em"
              >
                {node.node_type.toUpperCase()}
              </text>
            </g>
          );
        })}

        {/* ══════════════════════════════════════════════════
            L3 NODES  (SCADA / MES server racks)
        ══════════════════════════════════════════════════ */}
        {l3Nodes.map(node => {
          const p = gp(node.node_label);
          if (!p) return null;
          const hex = statusHex(node.status);
          const sel = isNodeSel(node);
          const icon = getIconName(node);
          const rx = p.x - L3_W / 2;
          const ry = p.y - L3_H / 2;

          return (
            <g
              key={node.node_id}
              onClick={() => selectNode(node)}
              style={{ cursor: 'pointer' }}
            >
              {sel && (
                <rect
                  x={rx - 4}
                  y={ry - 4}
                  width={L3_W + 8}
                  height={L3_H + 8}
                  rx={8}
                  fill="#60a5fa"
                  fillOpacity={0.06}
                  stroke="#60a5fa"
                  strokeWidth={1}
                  strokeOpacity={0.35}
                />
              )}
              {/* main body — tight rx = server chassis */}
              <rect
                x={rx}
                y={ry}
                width={L3_W}
                height={L3_H}
                rx={4}
                fill="#0d1929"
                stroke={sel ? '#60a5fa' : hex}
                strokeWidth={sel ? 2 : 1.5}
              />
              {/* rack unit dividers */}
              {[13, 27, 41].map(yo => (
                <line
                  key={yo}
                  x1={rx + 15}
                  y1={ry + yo}
                  x2={rx + L3_W - 4}
                  y2={ry + yo}
                  stroke="#1e2d3f"
                  strokeWidth={0.9}
                />
              ))}
              {/* rack bay LEDs */}
              <rect
                x={rx + 3}
                y={ry + 5}
                width={8}
                height={6}
                rx={1}
                fill={hex}
                fillOpacity={0.75}
              />
              <rect
                x={rx + 3}
                y={ry + 19}
                width={8}
                height={6}
                rx={1}
                fill={hex}
                fillOpacity={0.45}
              />
              <rect
                x={rx + 3}
                y={ry + 33}
                width={8}
                height={6}
                rx={1}
                fill={hex}
                fillOpacity={0.2}
              />
              {/* status LED top-right */}
              <circle cx={rx + L3_W - 9} cy={ry + 9} r={4} fill={hex} />
              {/* icon */}
              <SvgIcon name={icon} x={rx + 24} y={p.y} size={13} color={hex} />
              {/* label */}
              <text
                x={rx + 41}
                y={p.y - 5}
                fontSize={10}
                fontWeight={700}
                fill="#c8d6e8"
                letterSpacing="0.02em"
              >
                {trunc(node.node_label, 14)}
              </text>
              <text
                x={rx + 41}
                y={p.y + 9}
                fontSize={8.5}
                fill="#3d566e"
                letterSpacing="0.07em"
              >
                {node.node_type.toUpperCase()}
              </text>
            </g>
          );
        })}
      </svg>

      {/* ── Slide-in detail panel ──────────────────────────────────────────── */}
      {selected && (
        <DetailPanel
          target={selected}
          onClose={() => setSelected(null)}
        />
      )}
    </div>
  );
}
