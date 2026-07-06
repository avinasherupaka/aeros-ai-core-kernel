import type { FC } from 'react';

import type { ConnectorStatusCard } from '../../types/control-plane';
import { TrafficLightBadge } from '../status/TrafficLightBadge';

export interface ConnectorTableProps {
  connectors: ConnectorStatusCard[];
}

export const ConnectorTable: FC<ConnectorTableProps> = ({ connectors }) => (
  <div className="card table-wrap">
    <table>
      <thead>
        <tr>
          <th>Connector</th>
          <th>System</th>
          <th>Status</th>
          <th>Latency</th>
          <th>SLA</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {connectors.map((connector) => (
          <tr key={connector.connector_label}>
            <td>{connector.connector_label}</td>
            <td>{connector.system_type}</td>
            <td><TrafficLightBadge status={connector.status} /></td>
            <td>{connector.latency_ms ? `${connector.latency_ms} ms` : 'n/a'}</td>
            <td>{connector.sla_breach ? 'Breach' : 'Within target'}</td>
            <td>{connector.recommended_action ?? 'No action needed'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);
