import type { FC } from 'react';

import type { ManufacturingSiteTopology } from '../../types/control-plane';
import { DataFlowEdge } from './DataFlowEdge';
import { TopologyNode } from './TopologyNode';

export interface TopologyMapProps {
  topology: ManufacturingSiteTopology;
}

export const TopologyMap: FC<TopologyMapProps> = ({ topology }) => (
  <article className="card">
    <h3>{topology.site_label}</h3>
    <p className="card-subtitle">{topology.archetype}</p>
    <p className="card-note"><strong>Nodes:</strong> {topology.nodes.length} · <strong>Flows:</strong> {topology.edges.length}</p>
    <h4>Nodes</h4>
    <ul className="list">{topology.nodes.slice(0, 10).map((node) => <TopologyNode key={node.node_id} node={node} />)}</ul>
    <h4>Data flows</h4>
    <ul className="list">{topology.edges.slice(0, 6).map((edge, idx) => <DataFlowEdge key={`${edge.source_label}-${edge.target_label}-${idx}`} edge={edge} />)}</ul>
  </article>
);
