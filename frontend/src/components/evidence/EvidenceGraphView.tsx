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
import { cx, titleCase } from '../../lib/design';
import { SectionLabel } from '../ui/primitives';

interface EvidenceGraphViewProps {
  graph: EvidenceGraph;
}

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

// Map node_type to a category color
const categoryColor = (nodeType: string): { bg: string; border: string; text: string } => {
  if (['Event', 'Risk', 'Deviation'].includes(nodeType)) {
    return { bg: 'bg-status-red-soft', border: 'border-status-red-line', text: 'text-status-red' };
  }
  if (['CAPA', 'HumanReview', 'Approval'].includes(nodeType)) {
    return { bg: 'bg-status-amber-soft', border: 'border-status-amber-line', text: 'text-status-amber' };
  }
  if (['EvidenceItem', 'LabResult', 'SOPClause'].includes(nodeType)) {
    return { bg: 'bg-status-green-soft', border: 'border-status-green-line', text: 'text-status-green' };
  }
  return { bg: 'bg-panel2', border: 'border-line2', text: 'text-ink2' };
};

type Positioned = EvidenceGraphNode & { x: number; y: number };

export function EvidenceGraphView({ graph }: EvidenceGraphViewProps) {
  const [selected, setSelected] = useState<Positioned | null>(null);
  const [hoveredEdge, setHoveredEdge] = useState<string | null>(null);

  // Layout: 5 fixed columns by lane, stacked vertically within each lane
  const positioned = useMemo<Positioned[]>(() => {
    const laneWidth = 220;
    const nodeHeight = 60;
    const laneStartX = 40;
    const startY = 60;

    const byLane = new Map<number, EvidenceGraphNode[]>();
    graph.nodes.forEach((node) => {
      const list = byLane.get(node.lane) ?? [];
      list.push(node);
      byLane.set(node.lane, list);
    });

    const result: Positioned[] = [];
    byLane.forEach((nodes, lane) => {
      const x = laneStartX + lane * laneWidth;
      nodes.forEach((node, index) => {
        result.push({ ...node, x, y: startY + index * nodeHeight });
      });
    });
    return result;
  }, [graph.nodes]);

  const posById = useMemo(() => {
    const map = new Map<string, Positioned>();
    positioned.forEach((node) => map.set(node.node_id, node));
    return map;
  }, [positioned]);

  // Compute SVG dimensions
  const maxLane = Math.max(...positioned.map((n) => n.lane), 0);
  const maxY = Math.max(...positioned.map((n) => n.y), 100);
  const svgWidth = (maxLane + 1) * 220 + 80;
  const svgHeight = maxY + 120;

  const connectedNodes = useMemo(() => {
    if (!selected) return new Set<string>();
    const connected = new Set<string>([selected.node_id]);
    graph.edges.forEach((edge) => {
      if (edge.source_id === selected.node_id) connected.add(edge.target_id);
      if (edge.target_id === selected.node_id) connected.add(edge.source_id);
    });
    return connected;
  }, [selected, graph.edges]);

  return (
    <div className="relative h-full w-full overflow-auto rounded-lg border border-line bg-panel shadow-panel">
      <SectionLabel className="absolute left-4 top-4 z-10">Evidence Graph — Causal Flow</SectionLabel>

      {/* Lane legend (bottom right) */}
      <div className="absolute bottom-4 right-4 z-10 rounded border border-line bg-panel px-3 py-2 text-[10px] text-ink3 shadow-raised">
        <div className="font-semibold text-ink2">Flow Stages</div>
        {graph.lanes.map((l) => (
          <div key={l.lane} className="mt-1">
            {l.lane}. {l.label}
          </div>
        ))}
      </div>

      <svg viewBox={`0 0 ${svgWidth} ${svgHeight}`} className="min-h-[500px] w-full" role="img" aria-label="Evidence graph">
        <defs>
          <marker id="arrow-flow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8" />
          </marker>
          <marker id="arrow-highlight" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#6366f1" />
          </marker>
        </defs>

        {/* Lane column headers */}
        {graph.lanes.map((lane) => (
          <text
            key={lane.lane}
            x={40 + lane.lane * 220}
            y={30}
            className="text-[11px] font-semibold uppercase tracking-wide fill-ink3"
          >
            {lane.label}
          </text>
        ))}

        {/* Edges */}
        {graph.edges.map((edge, index) => {
          const source = posById.get(edge.source_id);
          const target = posById.get(edge.target_id);
          if (!source || !target) return null;

          const x1 = source.x + 100;
          const y1 = source.y + 22;
          const x2 = target.x;
          const y2 = target.y + 22;
          const midX = (x1 + x2) / 2;

          const isHighlighted =
            (selected && (connectedNodes.has(edge.source_id) || connectedNodes.has(edge.target_id))) ||
            hoveredEdge === `${edge.source_id}-${edge.target_id}`;

          return (
            <g
              key={`${edge.source_id}-${edge.target_id}-${index}`}
              onMouseEnter={() => setHoveredEdge(`${edge.source_id}-${edge.target_id}`)}
              onMouseLeave={() => setHoveredEdge(null)}
              className="cursor-pointer"
            >
              <path
                d={`M ${x1} ${y1} C ${midX} ${y1}, ${midX} ${y2}, ${x2} ${y2}`}
                fill="none"
                stroke={isHighlighted ? '#6366f1' : '#cbd5e1'}
                strokeWidth={isHighlighted ? 2 : 1.2}
                markerEnd={isHighlighted ? 'url(#arrow-highlight)' : 'url(#arrow-flow)'}
              />
              {hoveredEdge === `${edge.source_id}-${edge.target_id}` && (
                <text x={midX} y={(y1 + y2) / 2 - 6} textAnchor="middle" className="text-[9px] fill-ink3">
                  {titleCase(edge.edge_type)}
                </text>
              )}
            </g>
          );
        })}

        {/* Nodes as foreignObject (HTML cards) */}
        {positioned.map((node) => {
          const color = categoryColor(node.node_type);
          const Icon = NODE_ICON[node.node_type] ?? Boxes;
          const isSelected = selected?.node_id === node.node_id;
          const isConnected = connectedNodes.has(node.node_id);
          const isPendingNode = node.pending;

          return (
            <foreignObject key={node.node_id} x={node.x} y={node.y} width={200} height={44}>
              <div
                className={cx(
                  'flex h-11 cursor-pointer items-center gap-2 rounded border px-2.5 py-2 shadow-sm transition-all',
                  color.bg,
                  color.border,
                  isSelected && 'ring-2 ring-brand shadow-raised',
                  isConnected && !isSelected && 'ring-1 ring-brand/40',
                  isPendingNode && 'animate-breathe'
                )}
                onClick={() => setSelected(node)}
                title={node.label}
              >
                <Icon size={16} className={color.text} />
                <div className="flex-1 overflow-hidden">
                  <div className="truncate text-xs font-medium text-ink">{node.label}</div>
                  <div className="truncate text-[10px] text-ink3">{titleCase(node.node_type)}</div>
                </div>
                {isPendingNode && <span className="h-2 w-2 rounded-full bg-status-amber animate-pulse" />}
              </div>
            </foreignObject>
          );
        })}
      </svg>

      {/* Detail panel */}
      {selected && (
        <div className="absolute right-0 top-0 z-20 flex h-full w-80 flex-col border-l border-line bg-panel shadow-float">
          <div className="flex items-center justify-between border-b border-line px-4 py-3">
            <div className="flex-1 overflow-hidden">
              <SectionLabel>{titleCase(selected.node_type)}</SectionLabel>
              <div className="mt-1 truncate text-sm font-semibold text-ink" title={selected.label}>
                {selected.label}
              </div>
            </div>
            <button onClick={() => setSelected(null)} className="rounded p-1 text-ink3 hover:bg-panel2 hover:text-ink">
              <X size={16} />
            </button>
          </div>
          <div className="flex-1 space-y-3 overflow-y-auto px-4 py-3 text-xs">
            {selected.pending && (
              <div className="flex items-center gap-2 rounded border border-status-amber-line bg-status-amber-soft px-3 py-2 text-status-amber">
                <UserCheck size={14} />
                Pending human review
              </div>
            )}
            {Object.entries(selected.attributes).length === 0 ? (
              <p className="text-ink3">No additional attributes.</p>
            ) : (
              Object.entries(selected.attributes).map(([key, value]) => (
                <div key={key} className="border-b border-line2 pb-2">
                  <SectionLabel>{titleCase(key)}</SectionLabel>
                  <div className="mt-1 text-ink2">{String(value)}</div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
