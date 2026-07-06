import type { FC } from 'react';
import type { ConnectorStatusCard } from '../../types/control-plane';
import { TrafficLightBadge } from '../status/TrafficLightBadge';

export interface ConnectorTableProps {
  connectors: ConnectorStatusCard[];
}

export const ConnectorTable: FC<ConnectorTableProps> = ({ connectors }) => (
  <div className="bg-slate-800 border border-slate-700 rounded-lg overflow-hidden">
    <table className="w-full text-left text-sm text-slate-300">
      <thead className="bg-slate-900/50 text-slate-400 text-xs uppercase tracking-wider">
        <tr>
          <th className="px-6 py-3 font-medium">Connector</th>
          <th className="px-6 py-3 font-medium">System</th>
          <th className="px-6 py-3 font-medium">Status</th>
          <th className="px-6 py-3 font-medium">Latency</th>
          <th className="px-6 py-3 font-medium">SLA</th>
          <th className="px-6 py-3 font-medium">Action</th>
        </tr>
      </thead>
      <tbody className="divide-y divide-slate-700/50">
        {connectors.map((connector, index) => (
          <tr key={`${connector.connector_label}-${connector.system_type}-${index}`} className="hover:bg-slate-800/80 transition-colors">
            <td className="px-6 py-4 font-medium text-slate-200">{connector.connector_label}</td>
            <td className="px-6 py-4">{connector.system_type}</td>
            <td className="px-6 py-4"><TrafficLightBadge status={connector.status} /></td>
            <td className="px-6 py-4 tabular-nums">{connector.latency_ms ? `${connector.latency_ms} ms` : 'n/a'}</td>
            <td className="px-6 py-4">
              <span className={connector.sla_breach ? 'text-red-400 font-medium' : 'text-slate-400'}>
                {connector.sla_breach ? 'Breach' : 'Within target'}
              </span>
            </td>
            <td className="px-6 py-4 text-slate-400">{connector.recommended_action ?? 'No action needed'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);
