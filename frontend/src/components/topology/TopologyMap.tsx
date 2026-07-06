import React, { useMemo, useState } from 'react';
import type { ManufacturingSiteTopology, TopologyNode as TopologyNodeModel } from '../../types/control-plane';
import { TopologyNode } from './TopologyNode';
import { Network } from 'lucide-react';

export interface TopologyMapProps {
  topology: ManufacturingSiteTopology;
}

const LEVEL_MAP: Record<string, number> = {
  enterprise: 0,
  site: 0,
  system: 1,
  area: 2,
  line: 2,
  cell: 2,
  asset: 2,
  connector: 3,
};

export const TopologyMap: React.FC<TopologyMapProps> = ({ topology }) => {
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  const { nodeLayout, edges, viewBox } = useMemo(() => {
    const levels: TopologyNodeModel[][] = [[], [], [], []];
    topology.nodes.forEach((n) => {
      const lvl = LEVEL_MAP[n.node_type] ?? 2;
      levels[lvl].push(n);
    });

    const width = 1200;
    const height = 800;
    const layout: Record<string, TopologyNodeModel & { x: number; y: number }> = {};

    levels.forEach((lvlNodes, lvlIdx) => {
      const y = 100 + lvlIdx * 200;
      lvlNodes.forEach((node, i) => {
        const x = (width / (lvlNodes.length + 1)) * (i + 1);
        layout[node.node_label] = { ...node, x, y };
      });
    });

    const mappedEdges = topology.edges.map((edge) => {
      const source = layout[edge.source_label];
      const target = layout[edge.target_label];
      return { ...edge, source, target };
    }).filter(e => e.source && e.target);

    return { nodeLayout: layout, edges: mappedEdges, viewBox: `0 0 ${width} ${height}` };
  }, [topology]);

  const handleNodeClick = (nodeId: string) => {
    setSelectedNodeId(selectedNodeId === nodeId ? null : nodeId);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'green': return '#10b981';
      case 'red': return '#ef4444';
      case 'yellow': return '#f59e0b';
      default: return '#64748b';
    }
  };

  return (
    <article className="bg-slate-900 border border-slate-700 rounded-lg overflow-hidden flex flex-col h-full relative font-sans">
      <div className="p-4 bg-slate-800 border-b border-slate-700 flex justify-between items-center z-10 shadow-md">
        <div>
          <h3 className="text-lg font-bold text-slate-200 flex items-center tracking-wide">
            <Network className="w-5 h-5 mr-2 text-cyan-400" />
            {topology.site_label}
          </h3>
          <p className="text-xs text-slate-400 mt-1 uppercase tracking-wider">{topology.archetype} | ISA-95 TOPOLOGY</p>
        </div>
        <div className="text-right flex space-x-2">
          <div className="px-3 py-1 bg-slate-950 border border-slate-600 rounded text-xs text-slate-300 shadow-inner">
            <span className="text-cyan-400 font-bold">{topology.nodes.length}</span> NODES
          </div>
          <div className="px-3 py-1 bg-slate-950 border border-slate-600 rounded text-xs text-slate-300 shadow-inner">
            <span className="text-cyan-400 font-bold">{topology.edges.length}</span> FLOWS
          </div>
        </div>
      </div>
      
      <div className="flex-1 relative overflow-auto bg-[#0f172a]" style={{ minHeight: '600px' }}>
        {/* SCADA style grid background */}
        <div className="absolute inset-0 z-0 opacity-10 pointer-events-none" 
             style={{ backgroundImage: 'linear-gradient(#475569 1px, transparent 1px), linear-gradient(90deg, #475569 1px, transparent 1px)', backgroundSize: '40px 40px' }}>
        </div>
        
        <svg className="absolute inset-0 w-full h-full min-w-[1000px] min-h-[600px]" viewBox={viewBox} preserveAspectRatio="xMidYMid meet">
          <defs>
            <marker id="arrow-green" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#10b981" opacity="0.6" />
            </marker>
            <marker id="arrow-red" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#ef4444" opacity="0.6" />
            </marker>
            <marker id="arrow-yellow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#f59e0b" opacity="0.6" />
            </marker>
            <marker id="arrow-unknown" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b" opacity="0.6" />
            </marker>
            <filter id="glow">
              <feGaussianBlur stdDeviation="2.5" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>

          {/* Edges */}
          {edges.map((edge, i) => {
            const { source, target } = edge;
            // Draw S-Curve
            const x1 = source.x;
            const y1 = source.y;
            const x2 = target.x;
            const y2 = target.y;
            const dy = Math.abs(y2 - y1);
            const path = `M ${x1} ${y1} C ${x1} ${y1 + dy / 2}, ${x2} ${y2 - dy / 2}, ${x2} ${y2}`;
            const color = getStatusColor(edge.status);
            const markerId = `url(#arrow-${edge.status})`;

            return (
              <g key={`edge-${i}`}>
                <path
                  d={path}
                  fill="none"
                  stroke={color}
                  strokeWidth="2"
                  opacity="0.4"
                  markerEnd={y2 > y1 ? markerId : undefined}
                  markerStart={y1 > y2 ? markerId : undefined}
                  className="transition-all duration-300"
                />
                {/* Flow label */}
                <text
                  x={(x1 + x2) / 2}
                  y={(y1 + y2) / 2 - 8}
                  fill="#94a3b8"
                  fontSize="12"
                  textAnchor="middle"
                  className="font-mono"
                >
                  {edge.flow_type.toUpperCase()}
                </text>
              </g>
            );
          })}

          {/* Nodes */}
          {Object.values(nodeLayout).map((node) => (
            <foreignObject
              key={node.node_id}
              x={node.x - 120}
              y={node.y - 40}
              width="240"
              height={selectedNodeId === node.node_id ? "200" : "80"}
              className="overflow-visible"
            >
              <TopologyNode
                node={node}
                isExpanded={selectedNodeId === node.node_id}
                onClick={() => handleNodeClick(node.node_id)}
              />
            </foreignObject>
          ))}
        </svg>
      </div>
    </article>
  );
};
