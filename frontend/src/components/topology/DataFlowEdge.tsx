import type { FC } from 'react';

import type { DataFlowEdge as DataFlowEdgeModel } from '../../types/control-plane';
import { TrafficLightBadge } from '../status/TrafficLightBadge';

export interface DataFlowEdgeProps {
  edge: DataFlowEdgeModel;
}

export const DataFlowEdge: FC<DataFlowEdgeProps> = ({ edge }) => (
  <li>
    <strong>{edge.source_label}</strong> → <strong>{edge.target_label}</strong>{' '}
    <TrafficLightBadge status={edge.status} label={edge.flow_type} />
  </li>
);
