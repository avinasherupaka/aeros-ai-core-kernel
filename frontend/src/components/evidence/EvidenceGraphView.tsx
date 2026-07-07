import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  AlertTriangle,
  Beaker,
  Boxes,
  ClipboardCheck,
  FileCheck2,
  FlaskConical,
  Gauge,
  Maximize2,
  Package,
  ShieldAlert,
  Stamp,
  Thermometer,
  UserCheck,
  Wrench,
  Zap,
  ZoomIn,
  ZoomOut,
  RotateCcw,
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

// Layout constants — landscape, left→right lane flow
const LANE_WIDTH = 236;
const NODE_WIDTH = 200;
const NODE_HEIGHT = 44;
const ROW_PITCH = 76; // vertical distance between stacked nodes (prevents card overlap)
const LANE_START_X = 40;
const START_Y = 64;
const clamp = (v: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, v));

export function EvidenceGraphView({ graph }: EvidenceGraphViewProps) {
  const [selected, setSelected] = useState<Positioned | null>(null);
  const [hoveredEdge, setHoveredEdge] = useState<string | null>(null);
  const [zoomOpen, setZoomOpen] = useState(false);

  // Layout: fixed columns by lane, evenly stacked and vertically centered within each lane
  const positioned = useMemo<Positioned[]>(() => {
    const byLane = new Map<number, EvidenceGraphNode[]>();
    graph.nodes.forEach((node) => {
      const list = byLane.get(node.lane) ?? [];
      list.push(node);
      byLane.set(node.lane, list);
    });

    let maxCount = 0;
    byLane.forEach((nodes) => {
      maxCount = Math.max(maxCount, nodes.length);
    });
    const columnHeight = maxCount * ROW_PITCH;

    const result: Positioned[] = [];
    byLane.forEach((nodes, lane) => {
      const x = LANE_START_X + lane * LANE_WIDTH;
      const stackHeight = nodes.length * ROW_PITCH;
      const offsetY = (columnHeight - stackHeight) / 2;
      nodes.forEach((node, index) => {
        result.push({ ...node, x, y: START_Y + offsetY + index * ROW_PITCH });
      });
    });
    return result;
  }, [graph.nodes]);

  const posById = useMemo(() => {
    const map = new Map<string, Positioned>();
    positioned.forEach((node) => map.set(node.node_id, node));
    return map;
  }, [positioned]);

  const maxLane = Math.max(...positioned.map((n) => n.lane), 0);
  const maxY = Math.max(...positioned.map((n) => n.y), 100);
  const svgWidth = (maxLane + 1) * LANE_WIDTH + 80;
  const svgHeight = maxY + NODE_HEIGHT + 80;

  const connectedNodes = useMemo(() => {
    if (!selected) return new Set<string>();
    const connected = new Set<string>([selected.node_id]);
    graph.edges.forEach((edge) => {
      if (edge.source_id === selected.node_id) connected.add(edge.target_id);
      if (edge.target_id === selected.node_id) connected.add(edge.source_id);
    });
    return connected;
  }, [selected, graph.edges]);

  // Shared SVG content (defs + lane headers + edges + nodes) reused inline and in the zoom modal
  const graphContent = (
    <>
      <defs>
        <marker id="arrow-flow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8" />
        </marker>
        <marker id="arrow-highlight" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#6366f1" />
        </marker>
      </defs>

      {/* Lane guide bands + headers */}
      {graph.lanes.map((lane, i) => {
        const bandX = LANE_START_X + lane.lane * LANE_WIDTH - 16;
        return (
          <g key={lane.lane}>
            {i % 2 === 1 && (
              <rect x={bandX} y={44} width={LANE_WIDTH} height={svgHeight - 60} fill="#f8fafc" />
            )}
            <text
              x={LANE_START_X + lane.lane * LANE_WIDTH}
              y={32}
              className="text-[11px] font-semibold uppercase tracking-wide fill-ink3"
            >
              {lane.label}
            </text>
          </g>
        );
      })}

      {/* Edges */}
      {graph.edges.map((edge, index) => {
        const source = posById.get(edge.source_id);
        const target = posById.get(edge.target_id);
        if (!source || !target) return null;

        const x1 = source.x + NODE_WIDTH;
        const y1 = source.y + NODE_HEIGHT / 2;
        const x2 = target.x;
        const y2 = target.y + NODE_HEIGHT / 2;
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
          <foreignObject key={node.node_id} x={node.x} y={node.y} width={NODE_WIDTH} height={NODE_HEIGHT}>
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
    </>
  );

  return (
    <div className="relative flex h-full w-full flex-col overflow-hidden rounded-lg border border-line bg-panel shadow-panel">
      <div className="flex items-center justify-between border-b border-line px-4 py-2">
        <SectionLabel>Evidence Graph — Causal Flow</SectionLabel>
        <div className="flex items-center gap-3">
          <div className="hidden items-center gap-3 text-[10px] text-ink3 lg:flex">
            {graph.lanes.map((l) => (
              <span key={l.lane}>
                <span className="font-semibold text-ink2">{l.lane}</span> {l.label}
              </span>
            ))}
          </div>
          <button
            onClick={() => setZoomOpen(true)}
            className="flex items-center gap-1 rounded border border-line2 bg-panel2 px-2 py-1 text-[11px] text-ink2 hover:border-brand-ring hover:bg-brand-soft hover:text-brand"
            title="Expand to full-screen — pan & zoom"
          >
            <Maximize2 size={13} />
            Expand
          </button>
        </div>
      </div>

      <div className="relative flex-1 overflow-auto">
        <svg
          viewBox={`0 0 ${svgWidth} ${svgHeight}`}
          className="h-full min-h-[360px] w-full cursor-zoom-in"
          role="img"
          aria-label="Evidence graph"
          onDoubleClick={() => setZoomOpen(true)}
        >
          {graphContent}
        </svg>

        {/* Inline detail panel */}
        {selected && !zoomOpen && <NodeDetail node={selected} onClose={() => setSelected(null)} />}
      </div>

      {zoomOpen && (
        <ZoomModal
          svgWidth={svgWidth}
          svgHeight={svgHeight}
          onClose={() => setZoomOpen(false)}
          selected={selected}
          onClearSelected={() => setSelected(null)}
        >
          {graphContent}
        </ZoomModal>
      )}
    </div>
  );
}

// ─── Node detail slide-in panel ─────────────────────────────────────────────────
function NodeDetail({ node, onClose }: { node: Positioned; onClose: () => void }) {
  return (
    <div className="absolute right-0 top-0 z-20 flex h-full w-80 flex-col border-l border-line bg-panel shadow-float">
      <div className="flex items-center justify-between border-b border-line px-4 py-3">
        <div className="flex-1 overflow-hidden">
          <SectionLabel>{titleCase(node.node_type)}</SectionLabel>
          <div className="mt-1 truncate text-sm font-semibold text-ink" title={node.label}>
            {node.label}
          </div>
        </div>
        <button onClick={onClose} className="rounded p-1 text-ink3 hover:bg-panel2 hover:text-ink">
          <X size={16} />
        </button>
      </div>
      <div className="flex-1 space-y-3 overflow-y-auto px-4 py-3 text-xs">
        {node.pending && (
          <div className="flex items-center gap-2 rounded border border-status-amber-line bg-status-amber-soft px-3 py-2 text-status-amber">
            <UserCheck size={14} />
            Pending human review
          </div>
        )}
        {Object.entries(node.attributes).length === 0 ? (
          <p className="text-ink3">No additional attributes.</p>
        ) : (
          Object.entries(node.attributes).map(([key, value]) => (
            <div key={key} className="border-b border-line2 pb-2">
              <SectionLabel>{titleCase(key)}</SectionLabel>
              <div className="mt-1 text-ink2">{String(value)}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

// ─── Full-screen pan/zoom modal ─────────────────────────────────────────────────
interface ZoomModalProps {
  svgWidth: number;
  svgHeight: number;
  onClose: () => void;
  selected: Positioned | null;
  onClearSelected: () => void;
  children: React.ReactNode;
}

function ZoomModal({ svgWidth, svgHeight, onClose, selected, onClearSelected, children }: ZoomModalProps) {
  const [view, setView] = useState({ scale: 1, tx: 0, ty: 0 });
  const drag = useRef<{ x: number; y: number; tx: number; ty: number } | null>(null);
  const [dragging, setDragging] = useState(false);

  const reset = useCallback(() => setView({ scale: 1, tx: 0, ty: 0 }), []);
  const zoomBy = useCallback(
    (factor: number) => setView((v) => ({ ...v, scale: clamp(v.scale * factor, 0.3, 5) })),
    []
  );

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
      if (e.key === '+' || e.key === '=') zoomBy(1.2);
      if (e.key === '-') zoomBy(1 / 1.2);
      if (e.key === '0') reset();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose, zoomBy, reset]);

  const onWheel = (e: React.WheelEvent) => {
    const factor = e.deltaY < 0 ? 1.08 : 1 / 1.08;
    setView((v) => ({ ...v, scale: clamp(v.scale * factor, 0.3, 5) }));
  };

  const onMouseDown = (e: React.MouseEvent) => {
    drag.current = { x: e.clientX, y: e.clientY, tx: view.tx, ty: view.ty };
    setDragging(true);
  };
  const onMouseMove = (e: React.MouseEvent) => {
    if (!drag.current) return;
    setView((v) => ({
      ...v,
      tx: drag.current!.tx + (e.clientX - drag.current!.x),
      ty: drag.current!.ty + (e.clientY - drag.current!.y),
    }));
  };
  const endDrag = () => {
    drag.current = null;
    setDragging(false);
  };

  return (
    <div className="fixed inset-0 z-[100] flex flex-col bg-white/95 backdrop-blur-sm">
      <div className="flex items-center justify-between border-b border-line bg-panel px-5 py-3">
        <div>
          <div className="text-sm font-semibold text-ink">Evidence Graph — Causal Flow</div>
          <div className="text-[11px] text-ink3">Scroll to zoom · drag to pan · Esc to close</div>
        </div>
        <div className="flex items-center gap-1.5">
          <button onClick={() => zoomBy(1 / 1.2)} className="rounded border border-line2 bg-panel2 p-1.5 text-ink2 hover:bg-panel3" title="Zoom out">
            <ZoomOut size={16} />
          </button>
          <span className="w-12 text-center text-xs font-medium text-ink2">{Math.round(view.scale * 100)}%</span>
          <button onClick={() => zoomBy(1.2)} className="rounded border border-line2 bg-panel2 p-1.5 text-ink2 hover:bg-panel3" title="Zoom in">
            <ZoomIn size={16} />
          </button>
          <button onClick={reset} className="ml-1 rounded border border-line2 bg-panel2 p-1.5 text-ink2 hover:bg-panel3" title="Reset view">
            <RotateCcw size={16} />
          </button>
          <button onClick={onClose} className="ml-2 rounded border border-line2 bg-panel2 p-1.5 text-ink2 hover:bg-status-red-soft hover:text-status-red" title="Close">
            <X size={16} />
          </button>
        </div>
      </div>

      <div
        className={cx('relative flex-1 overflow-hidden bg-app', dragging ? 'cursor-grabbing' : 'cursor-grab')}
        onWheel={onWheel}
        onMouseDown={onMouseDown}
        onMouseMove={onMouseMove}
        onMouseUp={endDrag}
        onMouseLeave={endDrag}
      >
        <svg viewBox={`0 0 ${svgWidth} ${svgHeight}`} className="h-full w-full" role="img" aria-label="Evidence graph (zoomable)">
          <g transform={`translate(${view.tx} ${view.ty}) scale(${view.scale})`}>{children}</g>
        </svg>

        {selected && <NodeDetail node={selected} onClose={onClearSelected} />}
      </div>
    </div>
  );
}
