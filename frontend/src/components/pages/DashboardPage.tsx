import type { FC } from 'react';

import type {
  ConnectorStatusCard as ConnectorStatusCardModel,
  EnterpriseReadinessRollup,
  PersonaWorkflowCard,
  SiteHealthCard as SiteHealthCardModel,
  TrafficLight,
} from '../../types/control-plane';
import { ConnectorTable } from '../tables/ConnectorTable';
import { TrafficLightBadge } from '../status/TrafficLightBadge';
import { SiteHealthCard } from '../cards/SiteHealthCard';

export interface DashboardPageProps {
  readiness: EnterpriseReadinessRollup | null;
  sites: SiteHealthCardModel[];
  connectors: ConnectorStatusCardModel[];
  workflow: PersonaWorkflowCard | null;
}

export const DashboardPage: FC<DashboardPageProps> = ({ readiness, sites, connectors, workflow }) => {
  const metrics: Array<{ label: string; value: string; status: TrafficLight }> = readiness
    ? [
        { label: 'Overall', value: readiness.overall_status, status: readiness.overall_status },
        { label: 'Sites', value: String(readiness.total_sites), status: readiness.overall_status },
        { label: 'Red', value: String(readiness.red_sites), status: readiness.red_sites ? 'red' : 'green' },
        { label: 'Yellow', value: String(readiness.yellow_sites), status: readiness.yellow_sites ? 'yellow' : 'green' },
        { label: 'Green', value: String(readiness.green_sites), status: readiness.green_sites ? 'green' : 'unknown' },
      ]
    : [];

  return (
    <section className="stack">
      <h2>Enterprise Dashboard</h2>
      {metrics.length ? (
        <div className="metric-grid">
          {metrics.map((metric) => (
            <article key={metric.label} className="card">
              <p className="metric-label">{metric.label}</p>
              <p className="metric-value">{metric.value}</p>
              <TrafficLightBadge status={metric.status} />
            </article>
          ))}
        </div>
      ) : null}

      {readiness ? (
        <article className="card">
          <h3>Enterprise Summary</h3>
          <p>{readiness.enterprise_summary}</p>
          {readiness.top_risks.length ? (
            <ul className="list compact">
              {readiness.top_risks.map((risk) => (
                <li key={risk}>{risk}</li>
              ))}
            </ul>
          ) : null}
        </article>
      ) : null}

      <h3>Site Readiness</h3>
      <div className="grid columns-2">
        {sites.map((site) => (
          <SiteHealthCard key={site.site_id} site={site} />
        ))}
      </div>

      <h3>Connector Health</h3>
      <ConnectorTable connectors={connectors} />

      {workflow ? (
        <article className="card">
          <h3>{workflow.persona_label} Workflow</h3>
          <p>{workflow.primary_objective}</p>
          <div className="metric-grid">
            {workflow.kpis.map((kpi) => (
              <div key={kpi.label}>
                <p className="metric-label">{kpi.label}</p>
                <p className="metric-value">{kpi.value}</p>
                <TrafficLightBadge status={kpi.status} />
              </div>
            ))}
          </div>
          <div className="grid columns-2">
            <div>
              <h4>Active Alerts</h4>
              <ul className="list compact">
                {workflow.alerts.map((alert) => (
                  <li key={alert.summary}>{alert.summary}</li>
                ))}
              </ul>
            </div>
            <div>
              <h4>Recommended Actions</h4>
              <ul className="list compact">
                {workflow.recommended_actions.map((action) => (
                  <li key={action.action}>{action.action}</li>
                ))}
              </ul>
            </div>
          </div>
        </article>
      ) : null}
    </section>
  );
};
