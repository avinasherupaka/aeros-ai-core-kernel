import { useMemo, useState } from 'react';
import {
  AlertTriangle,
  Beaker,
  Boxes,
  ClipboardCheck,
  FileCheck2,
  FlaskConical,
  Gauge,
  Package,
  ShieldAlert,
  Stamp,
  Thermometer,
  UserCheck,
  Wrench,
  Zap,
  X,
} from 'lucide-react';
import type { EvidenceGraph, EvidenceGraphNode } from '../../types/control-plane';
import { cx } from '../../lib/design';

interface EvidenceGraphViewProps {
  graph: EvidenceGraph;
  completenessPct?: number;
}

// Concentric ring assignment: Event at center → context → evidence → decisions.
const RING: Record<string, number> = {
  Event: 0,
  Batch: 1,
  Product: 1,
  Room: 1,
  Equipment: 1,
  UtilitySystem: 1,
  Sensor: 1,
  MaterialLot: 1,
  Risk: 2,
  Deviation: 2,
  SOPClause: 2,
  LabResult: 2,
  EvidenceItem: 2,
  WorkOrder: 2,
  CAPA: 3,
  HumanReview: 3,
  Approval: 3,
};

const NODE_ICON: Record<string, typeof Zap> = {
  Event: Zap,
  Batch: Package,
  Product: Boxes,
  Room: Thermometer,
  Equipment: Gauge,
  UtilitySystem: Wrench,
  Sensor: Thermometer,
  MaterialLot: Package,
  Risk: ShieldAlert,
  Deviation: AlertTriangle,
  SOPClause: FileCheck2,
  LabResult: FlaskConical,
  EvidenceItem: Beaker,
  WorkOrder: Wrench,
  CAPA: ClipboardCheck,
  HumanReview: UserCheck,
  Approval: Stamp,
};

const RING_RADIUS = [0, 150, 260, 360];
const CX = 420;
const CY = 300;

type Positioned = EvidenceGraphNode & { x: number; y: number; ring: number };

const nodeStatus = (node: EvidenceGraphNode): 'red' | 'yellow' | 'green' | 'neutral' => {
  const type = node.node_type;
  if (type === 'Event' || type === 'Risk' || type === 'Deviation') return 'red';
  if (type === 'CAPA' || type === 'HumanReview' || type === 'Approval') return 'yellow';
  if (type === 'EvidenceItem' || type === 'LabResult' || type === 'SOPClause') return 'green';
  return 'neutral';
};

const statusStroke: Record<string, string> = {
  red: '#ef4444',
  yellow: '#f59e0b',
  green: '#10b981',
  neutral: '#64748b',
};

const isPending = (node: EvidenceGraphNode): boolean =>
  node.node_type === 'HumanReview' || node.node_type === 'Approval';

export function EvidenceGraphView({ graph, completenessPct = 0 }: EvidenceGraphViewProps) {
  const [selected, setSelected] = useState<Positioned | null>(null);

  const positioned = useMemo<Positioned[]>(() => {
    const byRing = new Map<number, EvidenceGraphNode[]>();
    graph.nodes.forEach((node) => {
      const ring = RING[node.node_type] ?? 2;
      const list = byRing.get(ring) ?? [];
      list.push(node);
      byRing.set(ring, list);
    });

    const result: Positioned[] = [];
    byRing.forEach((nodes, ring) => {
      const radius = RING_RADIUS[ring] ?? 360;
      if (ring === 0) {
        nodes.forEach((node) => result.push({ ...node, x: CX, y: CY, ring }));
        return;
      }
      const count = nodes.length;
      const startAngle = -Math.PI / 2;
      nodes.forEach((node, index) => {
        const angle = startAngle + (index / count) * Math.PI * 2;
        result.push({
          ...node,
          ring,
          x: CX + radius * Math.cos(angle),
          y: CY + radius * Math.sin(angle) * 0.72,
        });
      });
    });
    return result;
  }, [graph.nodes]);

  const posById = useMemo(() => {
    const map = new Map<string, Positioned>();
    positioned.forEach((node) => map.set(node.node_id, node));
    return map;
  }, [positioned]);

  const reviewNode = positioned.find((node) => node.node_type === 'HumanReview' || node.node_type === 'Approval');
  const ringCircumference = 2 * Math.PI * 26;
  const dashOffset = ringCircumference * (1 - Math.min(completenessPct, 100) / 100);

  return (
    <div className="relative h-full w-full overflow-hidden rounded-lg border border-surface-700 bg-surface-950">
      <div className="absolute left-3 top-3 z-10 flex items-center gap-2 text-xs font-medium uppercase tracking-wider text-slate-400">
        <span className="h-2 w-2 rounded-full bg-biotech-accent" />
        Evidence Graph
      </div>

      <svg viewBox="0 0 840 600" className="h-full w-full" role="img" aria-label="Evidence graph">
        <defs>
          <marker id="eg-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#475569" />
          </marker>
        </defs>

        {/* Concentric ring guides */}
        {[1, 2, 3].map((ring) => (
          <ellipse
            key={ring}
            cx={CX}
            cy={CY}
            rx={RING_RADIUS[ring]}
            ry={RING_RADIUS[ring] * 0.72}
            fill="none"
            stroke="#1b2333"
            strokeWidth={1}
            strokeDasharray="2 6"
          />
        ))}

        {/* Edges */}
        {graph.edges.map((edge, index) => {
          const source = posById.get(edge.source_id);
          const target = posById.get(edge.target_id);
          if (!source || !target) return null;
          const midX = (source.x + target.x) / 2;
          const midY = (source.y + target.y) / 2 - 24;
          return (
            <g key={`${edge.source_id}-${edge.target_id}-${index}`}>
              <path
                d={`M ${source.x} ${source.y} Q ${midX} ${midY} ${target.x} ${target.y}`}
                fill="none"
                stroke="#334155"
                strokeWidth={1.4}
                markerEnd="url(#eg-arrow)"
              />
              <text x={midX} y={midY} textAnchor="middle" className="fill-slate-500" style={{ fontSize: 8 }}>
                {edge.edge_type.replace(/_/g, ' ').toLowerCase()}
              </text>
            </g>
          );
        })}

        {/* Nodes */}
        {positioned.map((node) => {
          const status = nodeStatus(node);
          const stroke = statusStroke[status];
          const Icon = NODE_ICON[node.node_type] ?? Boxes;
          const pending = isPending(node);
          const isCenter = node.ring === 0;
          const r = isCenter ? 30 : 22;
          return (
            <g
              key={node.node_id}
              transform={`translate(${node.x}, ${node.y})`}
              className="cursor-pointer"
              onClick={() => setSelected(node)}
            >
              {pending && <circle r={r + 6} fill="none" stroke={stroke} strokeWidth={1} className="animate-pulse-node" />}
              <circle
                r={r}
                fill="#0f1420"
                stroke={stroke}
                strokeWidth={isCenter ? 2.5 : 1.6}
                className={cx(selected?.node_id === node.node_id && 'drop-shadow-[0_0_6px_rgba(56,189,248,0.6)]')}
              />
              <foreignObject x={-10} y={-10} width={20} height={20}>
                <div className="flex h-5 w-5 items-center justify-center">
                  <Icon size={isCenter ? 16 : 13} color={stroke} />
                </div>
              </foreignObject>
              <text y={r + 12} textAnchor="middle" className="fill-slate-300" style={{ fontSize: 9, fontWeight: 500 }}>
                {node.label.length > 22 ? `${node.label.slice(0, 20)}…` : node.label}
              </text>
            </g>
          );
        })}

        {/* Completeness ring around the human-review node */}
        {reviewNode && (
          <g transform={`translate(${reviewNode.x + 34}, ${reviewNode.y - 30})`}>
            <circle r={26} fill="none" stroke="#1b2333" strokeWidth={4} />
            <circle
              r={26}
              fill="none"
              stroke="#38bdf8"
              strokeWidth={4}
              strokeLinecap="round"
              strokeDasharray={ringCircumference}
              strokeDashoffset={dashOffset}
              transform="rotate(-90)"
            />
            <text textAnchor="middle" dy={4} className="fill-slate-100" style={{ fontSize: 12, fontWeight: 600 }}>
              {Math.round(completenessPct)}%
            </text>
          </g>
        )}
      </svg>

      {/* Progressive-disclosure detail panel */}
      {selected && (
        <div className="absolute right-0 top-0 z-20 flex h-full w-72 flex-col border-l border-surface-700 bg-surface-900/95 backdrop-blur">
          <div className="flex items-center justify-between border-b border-surface-700 px-4 py-3">
            <div>
              <div className="text-[10px] uppercase tracking-wider text-slate-500">{selected.node_type}</div>
              <div className="text-sm font-semibold text-slate-100">{selected.label}</div>
            </div>
            <button onClick={() => setSelected(null)} className="rounded p-1 text-slate-400 hover:bg-surface-700 hover:text-slate-100">
              <X size={16} />
            </button>
          </div>
          <div className="flex-1 space-y-3 overflow-y-auto px-4 py-3 text-xs">
            {isPending(selected) && (
              <div className="flex items-center gap-2 rounded border border-status-yellow/40 bg-status-yellow/10 px-3 py-2 text-status-yellow">
                <UserCheck size={14} />
                Human review required before release
              </div>
            )}
            {Object.entries(selected.attributes).length === 0 ? (
              <p className="text-slate-500">No additional attributes.</p>
            ) : (
              Object.entries(selected.attributes).map(([key, value]) => (
                <div key={key} className="border-b border-surface-800 pb-2">
                  <div className="text-[10px] uppercase tracking-wider text-slate-500">{key.replace(/_/g, ' ')}</div>
                  <div className="text-slate-200">{String(value)}</div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
