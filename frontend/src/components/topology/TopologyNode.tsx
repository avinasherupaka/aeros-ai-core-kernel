import type { FC } from 'react';

import type { TopologyNode as TopologyNodeModel } from '../../types/control-plane';
import { TrafficLightBadge } from '../status/TrafficLightBadge';

export interface TopologyNodeProps {
  node: TopologyNodeModel;
}

export const TopologyNode: FC<TopologyNodeProps> = ({ node }) => (
  <li>
    {node.node_label} ({node.node_type}) <TrafficLightBadge status={node.status} />
  </li>
);
