import type { FC } from 'react';

import type { TopologyNode } from '../../types/control-plane';

export interface AutomationPyramidProps {
  nodes: TopologyNode[];
}

export const AutomationPyramid: FC<AutomationPyramidProps> = ({ nodes }) => (
  <div className="card">
    <h4>Automation pyramid</h4>
    <div className="chip-row">
      {nodes.slice(0, 10).map((node) => (
        <span key={node.node_id} className="meta-chip">{node.node_label}</span>
      ))}
    </div>
  </div>
);
