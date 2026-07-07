import { useState, useMemo } from 'react';
import {
  Gauge,
  Thermometer,
  Droplet,
  Cpu,
  Network,
  Share2,
  Building2,
  MonitorDot,
  Factory,
  Database,
  HardDrive,
  Radio,
  Cloud,
  CloudCog,
  FlaskConical,
  ShieldCheck,
  Boxes,
  Wrench,
  Layers,
  Plug,
  X,
  ChevronRight,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import type { FloorMapSite, FloorMapNode, FloorMapLayer, FloorMapFlow, FloorNodeKind, TrafficLight } from '../../types/control-plane';
import { statusHex, statusColor, cx, titleCase } from '../../lib/design';
import { Panel, PanelHeader, StatusDot, StatusPill, Badge, Legend, EmptyHint } from '../ui/primitives';

// ─── ISA-95 Layer Configuration ───────────────────────────────────────────────
interface LayerConfig {
  level: string;
  label: string;
  yStart: number;
  yEnd: number;
  bgColor: string;
}

const LAYER_CONFIGS: LayerConfig[] = [
  { level: 'L4', label: 'Enterprise / Cloud', yStart: 40, yEnd: 240, bgColor: '#6366f1' },
  { level: 'L3', label: 'Edge / Site Systems', yStart: 280, yEnd: 480, bgColor: '#8b5cf6' },
  { level: 'L2', label: 'Supervisory Control', yStart: 520, yEnd: 720, bgColor: '#3b82f6' },
  { level: 'L1', label: 'Control', yStart: 760, yEnd: 960, bgColor: '#06b6d4' },
  { level: 'L0', label: 'Field / Sensing', yStart: 1000, yEnd: 1200, bgColor: '#10b981' },
];

const SVG_WIDTH = 1600;
const SVG_HEIGHT = 1240;
const LAYER_PADDING = 40;
const NODE_WIDTH = 168;
const NODE_HEIGHT = 100;
const NODE_SPACING = 20;

// ─── Node Icon Mapping ─────────────────────────────────────────────────────────
const NODE_ICONS: Record<FloorNodeKind, { Icon: LucideIcon; color: string }> = {
  sensor: { Icon: Gauge, color: '#10b981' },
  plc: { Icon: Cpu, color: '#06b6d4' },
  opcua: { Icon: Network, color: '#3b82f6' },
  bms: { Icon: Building2, color: '#3b82f6' },
  scada: { Icon: MonitorDot, color: '#3b82f6' },
  mes: { Icon: Factory, color: '#3b82f6' },
  historian: { Icon: Database, color: '#3b82f6' },
  edge_gateway: { Icon: HardDrive, color: '#8b5cf6' },
  mqtt_broker: { Icon: Radio, color: '#8b5cf6' },
  iot_core: { Icon: CloudCog, color: '#8b5cf6' },
  lims: { Icon: FlaskConical, color: '#6366f1' },
  qms: { Icon: ShieldCheck, color: '#6366f1' },
  erp: { Icon: Boxes, color: '#6366f1' },
  cmms: { Icon: Wrench, color: '#6366f1' },
  lakehouse: { Icon: Layers, color: '#6366f1' },
};

// ─── Coordinate Computation ────────────────────────────────────────────────────
interface NodeCoord {
  x: number;
  y: number;
}

function computeNodeCoordinates(site: FloorMapSite): Map<string, NodeCoord> {
  const coords = new Map<string, NodeCoord>();
  
  // Reverse layers so L4 is at top (index 0)
  const reversedLayers = [...site.layers].reverse();
  
  reversedLayers.forEach((layer, layerIndex) => {
    const layerConfig = LAYER_CONFIGS.find(c => c.level === layer.level);
    if (!layerConfig) return;
    
    const centerY = (layerConfig.yStart + layerConfig.yEnd) / 2;
    const nodeCount = layer.nodes.length;
    
    if (nodeCount === 0) return;
    
    // Calculate spacing to distribute nodes evenly across layer width
    const totalWidth = SVG_WIDTH - 2 * LAYER_PADDING;
    const availableWidth = totalWidth - nodeCount * NODE_WIDTH;
    const spacing = nodeCount > 1 ? availableWidth / (nodeCount + 1) : totalWidth / 2 - NODE_WIDTH / 2;
    
    layer.nodes.forEach((node, nodeIndex) => {
      const x = LAYER_PADDING + spacing + nodeIndex * (NODE_WIDTH + spacing);
      coords.set(node.id, { x: x + NODE_WIDTH / 2, y: centerY });
    });
  });
  
  return coords;
}

// ─── Flow Path Generator ───────────────────────────────────────────────────────
function createFlowPath(from: NodeCoord, to: NodeCoord): string {
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  const controlPointOffset = Math.abs(dy) * 0.5;
  
  return `M ${from.x} ${from.y} C ${from.x} ${from.y - controlPointOffset}, ${to.x} ${to.y + controlPointOffset}, ${to.x} ${to.y}`;
}

// ─── Node Detail Panel ──────────────────────────────────────────────────────────
interface NodeDetailPanelProps {
  node: FloorMapNode;
  onClose: () => void;
}

function NodeDetailPanel({ node, onClose }: NodeDetailPanelProps) {
  const sc = statusColor(node.status);
  
  return (
    <div className="absolute inset-y-0 right-0 w-96 bg-panel border-l border-line shadow-float z-50 flex flex-col animate-slide-up">
      <div className="flex items-start justify-between gap-3 border-b border-line px-4 py-3">
        <div className="flex-1 min-w-0">
          <div className="text-xs text-ink3 uppercase tracking-wider mb-1">{titleCase(node.kind)}</div>
          <div className="text-sm font-semibold text-ink truncate">{node.label}</div>
        </div>
        <button
          onClick={onClose}
          className="shrink-0 p-1 rounded hover:bg-panel2 text-ink3 hover:text-ink transition-colors"
        >
          <X size={16} />
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div>
          <div className="text-xs text-ink3 mb-2">Status</div>
          <StatusPill status={node.status} />
          {node.status_note && (
            <p className="text-xs text-ink2 mt-2">{node.status_note}</p>
          )}
        </div>
        
        {node.vendor && (
          <div>
            <div className="text-xs text-ink3 mb-1">Vendor</div>
            <div className="text-sm text-ink">{node.vendor}</div>
          </div>
        )}
        
        {node.protocol && (
          <div>
            <div className="text-xs text-ink3 mb-1">Protocol</div>
            <div className="text-sm text-ink font-mono">{node.protocol}</div>
          </div>
        )}
        
        {node.metric && (
          <div>
            <div className="text-xs text-ink3 mb-1">Current Metric</div>
            <div className="text-sm text-ink font-mono">{node.metric}</div>
          </div>
        )}
        
        {node.room && (
          <div>
            <div className="text-xs text-ink3 mb-1">Location</div>
            <div className="text-sm text-ink">{node.room}</div>
          </div>
        )}
        
        {node.has_connector && (
          <div className={cx('px-3 py-2 rounded border', sc.bg, sc.border)}>
            <div className="flex items-center gap-2 mb-1">
              <Badge tone="brand">Aeros</Badge>
              <span className="text-xs font-medium text-ink">Connector Active</span>
            </div>
            <p className="text-xs text-ink3">This node is instrumented with an Aeros connector</p>
          </div>
        )}
        
        {node.last_heartbeat_at && (
          <div>
            <div className="text-xs text-ink3 mb-1">Last Heartbeat</div>
            <div className="text-xs text-ink2 font-mono">{node.last_heartbeat_at}</div>
          </div>
        )}
        
        <div className="pt-3 border-t border-line">
          <div className="text-xs text-ink3 mb-1">Node ID</div>
          <div className="text-xs text-ink2 font-mono break-all">{node.id}</div>
        </div>
      </div>
    </div>
  );
}

// ─── Main Component ─────────────────────────────────────────────────────────────
export interface PlantFloorMapProps {
  sites: FloorMapSite[];
}

export function PlantFloorMap({ sites }: PlantFloorMapProps) {
  const [selectedSiteIndex, setSelectedSiteIndex] = useState(0);
  const [selectedNode, setSelectedNode] = useState<FloorMapNode | null>(null);
  
  // Empty state
  if (!sites || sites.length === 0) {
    return (
      <Panel className="h-full flex items-center justify-center">
        <EmptyHint
          icon={<Factory size={48} className="text-ink3" />}
          title="No floor map data"
          detail="Configure site topology to visualize the ISA-95 automation pyramid"
        />
      </Panel>
    );
  }
  
  const site = sites[selectedSiteIndex] || sites[0];
  const nodeCoords = useMemo(() => computeNodeCoordinates(site), [site]);
  
  // Build flow lookup for animation
  const flowMap = useMemo(() => {
    const map = new Map<string, FloorMapFlow[]>();
    site.flows.forEach(flow => {
      if (!map.has(flow.from)) map.set(flow.from, []);
      map.get(flow.from)!.push(flow);
    });
    return map;
  }, [site.flows]);
  
  return (
    <Panel className="h-full flex flex-col relative">
      <PanelHeader
        title="Live Floor Map"
        subtitle="Config-driven ISA-95 topology · IT / OT / Edge · live connector status"
        right={
          sites.length > 1 ? (
            <div className="flex gap-1">
              {sites.map((s, idx) => (
                <button
                  key={s.site_id}
                  onClick={() => setSelectedSiteIndex(idx)}
                  className={cx(
                    'px-2 py-1 text-xs rounded transition-colors',
                    idx === selectedSiteIndex
                      ? 'bg-brand text-white'
                      : 'text-ink3 hover:text-ink hover:bg-panel2'
                  )}
                >
                  {s.site_label}
                </button>
              ))}
            </div>
          ) : undefined
        }
      />
      
      {/* Site header */}
      <div className="px-4 py-2 border-b border-line flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm">
          <span className="font-medium text-ink">{site.site_label}</span>
          <ChevronRight size={14} className="text-ink3" />
          <span className="text-ink2">{site.area_label}</span>
        </div>
        
        <Legend
          items={[
            { status: 'green', label: 'Live feed' },
            { status: 'yellow', label: 'Replay / Degraded' },
            { status: 'red', label: 'Broken' },
          ]}
        />
      </div>
      
      {/* Scrollable diagram container */}
      <div className="flex-1 overflow-auto bg-app">
        <svg
          width={SVG_WIDTH}
          height={SVG_HEIGHT}
          className="block"
          style={{ minWidth: SVG_WIDTH, minHeight: SVG_HEIGHT }}
        >
          <defs>
            {/* Animated flow marker */}
            <marker
              id="flow-arrow-green"
              markerWidth="8"
              markerHeight="8"
              refX="7"
              refY="4"
              orient="auto"
            >
              <path d="M 0 0 L 8 4 L 0 8 z" fill={statusHex('green')} />
            </marker>
            <marker
              id="flow-arrow-yellow"
              markerWidth="8"
              markerHeight="8"
              refX="7"
              refY="4"
              orient="auto"
            >
              <path d="M 0 0 L 8 4 L 0 8 z" fill={statusHex('yellow')} />
            </marker>
            <marker
              id="flow-arrow-red"
              markerWidth="8"
              markerHeight="8"
              refX="7"
              refY="4"
              orient="auto"
            >
              <path d="M 0 0 L 8 4 L 0 8 z" fill={statusHex('red')} />
            </marker>
            <marker
              id="flow-arrow-unknown"
              markerWidth="8"
              markerHeight="8"
              refX="7"
              refY="4"
              orient="auto"
            >
              <path d="M 0 0 L 8 4 L 0 8 z" fill={statusHex('unknown')} />
            </marker>
          </defs>
          
          {/* Layer bands (L4 at top, L0 at bottom) */}
          {LAYER_CONFIGS.map((config, idx) => {
            const layer = site.layers.find(l => l.level === config.level);
            const isOdd = idx % 2 === 0;
            
            return (
              <g key={config.level}>
                {/* Band background */}
                <rect
                  x={0}
                  y={config.yStart}
                  width={SVG_WIDTH}
                  height={config.yEnd - config.yStart}
                  fill={isOdd ? '#f9fafb' : '#ffffff'}
                  stroke="#e5e7eb"
                  strokeWidth={1}
                />
                
                {/* Level badge */}
                <rect
                  x={10}
                  y={config.yStart + 10}
                  width={60}
                  height={24}
                  rx={4}
                  fill={config.bgColor}
                  opacity={0.1}
                />
                <text
                  x={40}
                  y={config.yStart + 26}
                  textAnchor="middle"
                  fontSize={12}
                  fontWeight={700}
                  fill={config.bgColor}
                  fontFamily="monospace"
                >
                  {config.level}
                </text>
                
                {/* Layer label & description */}
                <text
                  x={80}
                  y={config.yStart + 20}
                  fontSize={14}
                  fontWeight={600}
                  fill="#374151"
                >
                  {layer?.label || config.label}
                </text>
                {layer?.description && (
                  <text
                    x={80}
                    y={config.yStart + 36}
                    fontSize={11}
                    fill="#6b7280"
                  >
                    {layer.description}
                  </text>
                )}
              </g>
            );
          })}
          
          {/* Data flow lines (draw first, behind nodes) */}
          {site.flows.map((flow, idx) => {
            const fromCoord = nodeCoords.get(flow.from);
            const toCoord = nodeCoords.get(flow.to);
            
            if (!fromCoord || !toCoord) return null;
            
            const path = createFlowPath(fromCoord, toCoord);
            const color = statusHex(flow.status);
            const isFlowing = flow.status === 'green' || flow.status === 'yellow';
            
            return (
              <g key={idx}>
                {/* Glow effect */}
                <path
                  d={path}
                  fill="none"
                  stroke={color}
                  strokeWidth={6}
                  opacity={0.1}
                />
                {/* Main flow line */}
                <path
                  d={path}
                  fill="none"
                  stroke={color}
                  strokeWidth={2}
                  strokeDasharray={isFlowing ? '8 4' : flow.status === 'red' ? '4 4' : undefined}
                  opacity={flow.status === 'red' ? 0.4 : 0.8}
                  className={isFlowing ? 'animate-flow' : undefined}
                  markerEnd={`url(#flow-arrow-${flow.status})`}
                />
              </g>
            );
          })}
          
          {/* Nodes */}
          {site.layers.map(layer =>
            layer.nodes.map(node => {
              const coord = nodeCoords.get(node.id);
              if (!coord) return null;
              
              const iconData = NODE_ICONS[node.kind];
              const Icon = iconData.Icon;
              const sc = statusColor(node.status);
              const isSelected = selectedNode?.id === node.id;
              
              const x = coord.x - NODE_WIDTH / 2;
              const y = coord.y - NODE_HEIGHT / 2;
              
              return (
                <g
                  key={node.id}
                  onClick={() => setSelectedNode(node)}
                  style={{ cursor: 'pointer' }}
                  className="group"
                >
                  {/* Selection highlight */}
                  {isSelected && (
                    <rect
                      x={x - 4}
                      y={y - 4}
                      width={NODE_WIDTH + 8}
                      height={NODE_HEIGHT + 8}
                      rx={10}
                      fill="none"
                      stroke="#6366f1"
                      strokeWidth={2}
                      className="animate-pulse-node"
                    />
                  )}
                  
                  {/* Node background */}
                  <rect
                    x={x}
                    y={y}
                    width={NODE_WIDTH}
                    height={NODE_HEIGHT}
                    rx={8}
                    fill="#ffffff"
                    stroke="#e5e7eb"
                    strokeWidth={1.5}
                    className="group-hover:stroke-brand transition-colors"
                  />
                  
                  {/* Status LED */}
                  <circle
                    cx={x + NODE_WIDTH - 14}
                    cy={y + 16}
                    r={5}
                    fill={statusHex(node.status)}
                    stroke="#ffffff"
                    strokeWidth={1.5}
                    className={cx(node.status !== 'green' && 'animate-breathe')}
                  />
                  
                  {/* Icon (using foreignObject for Lucide React component) */}
                  <foreignObject
                    x={x + 12}
                    y={y + 12}
                    width={30}
                    height={30}
                  >
                    <div className="flex items-center justify-center w-full h-full">
                      <Icon size={24} color={iconData.color} strokeWidth={1.5} />
                    </div>
                  </foreignObject>
                  
                  {/* Aeros connector chip — compact, color-coded by connector status */}
                  {node.has_connector && (
                    <foreignObject
                      x={x + 48}
                      y={y + 13}
                      width={NODE_WIDTH - 68}
                      height={22}
                    >
                      <div
                        className="flex items-center gap-1 rounded-full border px-1.5 h-[22px] w-fit max-w-full"
                        style={{
                          backgroundColor: `${sc.hex}14`,
                          borderColor: `${sc.hex}55`,
                        }}
                        title={`Aeros connector · ${sc.label}`}
                      >
                        <Plug size={11} color={sc.hex} strokeWidth={2.25} />
                        <span
                          className="text-[9px] font-bold uppercase tracking-wide truncate"
                          style={{ color: sc.hex }}
                        >
                          Aeros
                        </span>
                      </div>
                    </foreignObject>
                  )}
                  
                  {/* Label */}
                  <text
                    x={x + NODE_WIDTH / 2}
                    y={y + 62}
                    textAnchor="middle"
                    fontSize={12}
                    fontWeight={600}
                    fill="#111827"
                    className="pointer-events-none"
                  >
                    {node.label.length > 20 ? node.label.slice(0, 18) + '…' : node.label}
                  </text>
                  
                  {/* Vendor / protocol footer */}
                  {node.vendor && (
                    <text
                      x={x + NODE_WIDTH / 2}
                      y={y + 80}
                      textAnchor="middle"
                      fontSize={9}
                      fill="#6b7280"
                      className="pointer-events-none"
                    >
                      {node.vendor}
                    </text>
                  )}
                </g>
              );
            })
          )}
        </svg>
      </div>
      
      {/* Detail panel */}
      {selectedNode && (
        <NodeDetailPanel
          node={selectedNode}
          onClose={() => setSelectedNode(null)}
        />
      )}
    </Panel>
  );
}
