import { useMemo } from 'react';
import { Activity, AlertTriangle, TrendingUp } from 'lucide-react';
import type { EnterpriseReadinessRollup, TrafficLight } from '../../types/control-plane';
import { cx, statusColor } from '../../lib/design';

interface LeadershipMatrixProps {
  readiness: EnterpriseReadinessRollup | null;
}

const DIMENSIONS = ['Equipment', 'Connectors', 'Data', 'Evidence', 'Audit'] as const;

const dimensionStatus = (dimensions: { dimension: string; status: TrafficLight }[], name: string): TrafficLight => {
  const match = dimensions.find((dim) => dim.dimension.toLowerCase().includes(name.toLowerCase().slice(0, 4)));
  return match?.status ?? 'unknown';
};

const Cell = ({ status }: { status: TrafficLight }) => {
  const sc = statusColor(status);
  return (
    <td className="px-2 py-2 text-center">
      <span className={cx('inline-flex h-6 w-6 items-center justify-center rounded-full border', sc.border, sc.bg)}>
        <span className={cx('h-2.5 w-2.5 rounded-full', sc.dot)} />
      </span>
    </td>
  );
};

export function LeadershipMatrix({ readiness }: LeadershipMatrixProps) {
  const sites = readiness?.sites ?? [];

  const releaseStages = useMemo(() => {
    const totalCapas = sites.reduce((sum, site) => sum + (site.open_capas ?? 0), 0);
    const overdue = sites.reduce((sum, site) => sum + (site.overdue_reviews ?? 0), 0);
    return [
      { label: 'In Batch', count: sites.length * 2 },
      { label: 'QA Review', count: Math.max(sites.length, 1) },
      { label: 'CAPA Open', count: totalCapas },
      { label: 'Overdue Reviews', count: overdue },
    ];
  }, [sites]);

  if (!readiness) {
    return <div className="p-8 text-sm text-slate-400">No enterprise readiness data available.</div>;
  }

  return (
    <div className="space-y-4 overflow-y-auto p-3">
      {/* KPI strip */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {[
          { label: 'Total Sites', value: String(readiness.total_sites), status: 'unknown' as TrafficLight, icon: Activity },
          { label: 'Red Sites', value: String(readiness.red_sites), status: 'red' as TrafficLight, icon: AlertTriangle },
          { label: 'Yellow Sites', value: String(readiness.yellow_sites), status: 'yellow' as TrafficLight, icon: AlertTriangle },
          { label: 'Green Sites', value: String(readiness.green_sites), status: 'green' as TrafficLight, icon: TrendingUp },
        ].map((kpi) => {
          const sc = statusColor(kpi.status);
          const Icon = kpi.icon;
          return (
            <div key={kpi.label} className="rounded-lg border border-surface-700 bg-surface-900 p-4">
              <div className="flex items-center justify-between">
                <span className="text-[11px] uppercase tracking-wider text-slate-500">{kpi.label}</span>
                <Icon size={15} className={sc.text} />
              </div>
              <div className={cx('mt-1 text-2xl font-semibold', kpi.status === 'unknown' ? 'text-slate-100' : sc.text)}>{kpi.value}</div>
            </div>
          );
        })}
      </div>

      {/* Heatmap matrix */}
      <div className="rounded-lg border border-surface-700 bg-surface-900 p-4">
        <div className="mb-3 text-[11px] font-semibold uppercase tracking-wider text-slate-500">Enterprise Readiness Matrix</div>
        <table className="w-full">
          <thead>
            <tr className="text-[11px] uppercase tracking-wider text-slate-500">
              <th className="px-2 py-2 text-left">Site</th>
              {DIMENSIONS.map((dim) => (
                <th key={dim} className="px-2 py-2 text-center">{dim}</th>
              ))}
              <th className="px-2 py-2 text-center">Overall</th>
            </tr>
          </thead>
          <tbody>
            {sites.map((site) => (
              <tr key={site.site_label} className="border-t border-surface-800">
                <td className="px-2 py-2 text-left text-sm font-medium text-slate-200">{site.site_label}</td>
                {DIMENSIONS.map((dim) => (
                  <Cell key={dim} status={dimensionStatus(site.dimensions, dim)} />
                ))}
                <Cell status={site.overall_status} />
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {/* Top risks */}
        <div className="rounded-lg border border-surface-700 bg-surface-900 p-4">
          <div className="mb-3 text-[11px] font-semibold uppercase tracking-wider text-slate-500">Top Enterprise Risks</div>
          {readiness.top_risks.length === 0 ? (
            <p className="text-xs text-slate-500">No outstanding enterprise-level risks.</p>
          ) : (
            <ul className="space-y-2">
              {readiness.top_risks.map((risk, index) => (
                <li key={index} className="flex items-start gap-2 text-xs text-slate-300">
                  <span className="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-status-red/20 text-[10px] font-bold text-status-red">
                    {index + 1}
                  </span>
                  {risk}
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Release pipeline */}
        <div className="rounded-lg border border-surface-700 bg-surface-900 p-4">
          <div className="mb-3 text-[11px] font-semibold uppercase tracking-wider text-slate-500">Enterprise Release Pipeline</div>
          <div className="grid grid-cols-2 gap-3">
            {releaseStages.map((stage) => (
              <div key={stage.label} className="rounded border border-surface-700 bg-surface-850 px-3 py-2">
                <div className="text-lg font-semibold text-slate-100">{stage.count}</div>
                <div className="text-[11px] text-slate-500">{stage.label}</div>
              </div>
            ))}
          </div>
          <p className="mt-3 border-t border-surface-800 pt-3 text-xs text-slate-400">{readiness.enterprise_summary}</p>
        </div>
      </div>
    </div>
  );
}
