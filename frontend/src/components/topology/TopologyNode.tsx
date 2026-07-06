import React from 'react';
import type { TopologyNode as TopologyNodeModel } from '../../types/control-plane';
import { Server, Database, Factory, Activity, Box, Monitor, Network } from 'lucide-react';

export interface TopologyNodeProps {
  node: TopologyNodeModel;
  isExpanded?: boolean;
  onClick?: () => void;
}

const getIcon = (type: string) => {
  switch (type) {
    case 'enterprise': return <Network className="w-5 h-5" />;
    case 'site': return <Factory className="w-5 h-5" />;
    case 'system': return <Server className="w-5 h-5" />;
    case 'asset': return <Box className="w-5 h-5" />;
    case 'connector': return <Activity className="w-5 h-5" />;
    default: return <Monitor className="w-5 h-5" />;
  }
};

export const TopologyNode: React.FC<TopologyNodeProps> = ({ node, isExpanded = false, onClick }) => {
  const getStatusColorClass = (status: string) => {
    switch (status) {
      case 'green': return 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]';
      case 'red': return 'bg-red-500 animate-pulse shadow-[0_0_10px_rgba(239,68,68,0.8)]';
      case 'yellow': return 'bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.5)]';
      default: return 'bg-slate-500';
    }
  };

  const getBorderColorClass = (status: string) => {
    switch (status) {
      case 'green': return 'border-emerald-500/30';
      case 'red': return 'border-red-500/50';
      case 'yellow': return 'border-amber-500/30';
      default: return 'border-slate-600';
    }
  };

  return (
    <div 
      className={`relative cursor-pointer transition-all duration-300 ease-in-out bg-slate-900/90 backdrop-blur-sm border ${getBorderColorClass(node.status)} rounded font-sans text-slate-200 hover:bg-slate-800 ${isExpanded ? 'z-50 shadow-2xl scale-105' : 'z-10'}`}
      style={{ width: '240px', minHeight: '80px', boxSizing: 'border-box' }}
      onClick={onClick}
    >
      {/* Header bar - ISA-101 style muted top */}
      <div className="h-2 w-full bg-slate-800 rounded-t flex">
        <div className={`h-full w-full opacity-50 ${getStatusColorClass(node.status).split(' ')[0]}`}></div>
      </div>
      
      <div className="p-3 flex items-start gap-3">
        <div className="p-2 bg-slate-800 border border-slate-700 rounded text-slate-400 shrink-0">
          {getIcon(node.node_type)}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex justify-between items-start">
            <h4 className="text-sm font-bold truncate text-slate-100" title={node.node_label}>
              {node.node_label}
            </h4>
            <div className={`w-3 h-3 rounded-full mt-1 shrink-0 ${getStatusColorClass(node.status)}`} />
          </div>
          <div className="text-xs text-slate-400 uppercase tracking-wider mt-1 font-mono">
            {node.node_type}
          </div>
        </div>
      </div>

      {/* Expanded Content (Progressive Disclosure) */}
      {isExpanded && (
        <div className="px-3 pb-3 pt-2 border-t border-slate-700/50 bg-slate-900">
          <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-2 font-bold">Diagnostics</div>
          <div className="space-y-1.5">
            {Object.entries(node.metadata || {}).map(([k, v]) => (
              <div key={k} className="flex justify-between text-xs font-mono">
                <span className="text-slate-400">{k}:</span>
                <span className="text-cyan-400 truncate ml-2 text-right" title={String(v)}>{String(v)}</span>
              </div>
            ))}
            {(!node.metadata || Object.keys(node.metadata).length === 0) && (
              <div className="text-xs text-slate-500 italic">No diagnostic data</div>
            )}
          </div>
          <button className="mt-3 w-full py-1.5 text-xs bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded text-slate-300 transition-colors uppercase tracking-wider font-bold">
            View Details
          </button>
        </div>
      )}
    </div>
  );
};
