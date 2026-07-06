import type { FC } from 'react';

import type { ConnectorStatusCard as ConnectorStatusCardModel } from '../../types/control-plane';
import { SLAIndicator } from '../status/SLAIndicator';
import { TrafficLightBadge } from '../status/TrafficLightBadge';

export interface ConnectorStatusCardProps {
  connector: ConnectorStatusCardModel;
}

export const ConnectorStatusCard: FC<ConnectorStatusCardProps> = ({ connector }) => (
  <article className="card connector-card">
    <header className="card-head compact">
      <h4>{connector.connector_label}</h4>
      <TrafficLightBadge status={connector.status} />
    </header>
    <p className="card-subtitle">{connector.system_type} · Last sync {connector.last_ingestion_label}</p>
    <div className="chip-row">
      <SLAIndicator breached={connector.sla_breach} />
      <TrafficLightBadge status={connector.latency_status} label={connector.latency_ms ? `${connector.latency_ms} ms` : 'Latency n/a'} />
    </div>
    {connector.degradation_reason ? <p className="card-note">{connector.degradation_reason}</p> : null}
  </article>
);
