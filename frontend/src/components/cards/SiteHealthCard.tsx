import type { FC } from 'react';
import type { SiteHealthCard as SiteHealthCardModel } from '../../types/control-plane';
import { TrafficLightBadge } from '../status/TrafficLightBadge';

export interface SiteHealthCardProps {
  site: SiteHealthCardModel;
}

export const SiteHealthCard: FC<SiteHealthCardProps> = ({ site }) => {
  return (
    <article className="bg-slate-800 border border-slate-700 rounded-lg p-5 flex flex-col h-full">
      <header className="flex justify-between items-start gap-3 mb-4">
        <div>
          <h3 className="text-lg font-medium text-slate-100 m-0">{site.site_label}</h3>
          <p className="text-sm text-slate-400 mt-1">{site.archetype}</p>
        </div>
        <TrafficLightBadge status={site.overall_status} label={site.overall_status.toUpperCase()} />
      </header>

      <p className="text-sm text-slate-300 mb-6 flex-grow">{site.business_summary}</p>

      <div className="grid grid-cols-2 gap-4 mb-6 bg-slate-900/50 p-4 rounded-md border border-slate-700/50">
        <div>
          <strong className="block text-2xl font-light text-slate-200">{site.open_events}</strong>
          <p className="text-xs text-slate-500 uppercase tracking-wider mt-1">Open events</p>
        </div>
        <div>
          <strong className="block text-2xl font-light text-slate-200">{site.critical_events}</strong>
          <p className="text-xs text-slate-500 uppercase tracking-wider mt-1">Critical events</p>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-6">
        <TrafficLightBadge status={site.equipment_health} label="Equipment" />
        <TrafficLightBadge status={site.connector_health} label="Connectors" />
        <TrafficLightBadge status={site.data_freshness} label="Freshness" />
        <TrafficLightBadge status={site.evidence_completeness} label="Evidence" />
        <TrafficLightBadge status={site.audit_readiness} label="Audit" />
      </div>

      {site.recommended_action ? (
        <p className="mt-auto pt-4 border-t border-slate-700 text-sm">
          <strong className="text-slate-400 font-medium mr-2">Next action:</strong>
          <span className="text-slate-200">{site.recommended_action}</span>
        </p>
      ) : null}
    </article>
  );
};
