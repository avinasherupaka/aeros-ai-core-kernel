import type { FC } from 'react';

import type { SiteHealthCard as SiteHealthCardModel } from '../../types/control-plane';
import { TrafficLightBadge } from '../status/TrafficLightBadge';

export interface SiteHealthCardProps {
  site: SiteHealthCardModel;
}

export const SiteHealthCard: FC<SiteHealthCardProps> = ({ site }) => {
  return (
    <article className="card">
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', gap: '0.75rem' }}>
        <div>
          <h3 style={{ margin: 0 }}>{site.site_label}</h3>
          <p style={{ margin: '0.2rem 0 0', color: '#4b5563' }}>{site.archetype}</p>
        </div>
        <TrafficLightBadge status={site.overall_status} label={site.overall_status.toUpperCase()} />
      </header>

      <p style={{ margin: '0.85rem 0 0' }}>{site.business_summary}</p>

      <div className="metric-grid" style={{ marginTop: '0.85rem' }}>
        <div>
          <strong>{site.open_events}</strong>
          <p>Open events</p>
        </div>
        <div>
          <strong>{site.critical_events}</strong>
          <p>Critical events</p>
        </div>
      </div>

      <div style={{ marginTop: '0.85rem', display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
        <TrafficLightBadge status={site.equipment_health} label="Equipment" />
        <TrafficLightBadge status={site.connector_health} label="Connectors" />
        <TrafficLightBadge status={site.data_freshness} label="Freshness" />
        <TrafficLightBadge status={site.evidence_completeness} label="Evidence" />
        <TrafficLightBadge status={site.audit_readiness} label="Audit" />
      </div>

      {site.recommended_action ? (
        <p style={{ marginTop: '0.85rem', borderTop: '1px solid #e5e7eb', paddingTop: '0.85rem' }}>
          <strong>Next action:</strong> {site.recommended_action}
        </p>
      ) : null}
    </article>
  );
};
