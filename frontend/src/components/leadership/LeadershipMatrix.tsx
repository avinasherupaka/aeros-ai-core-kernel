import { useMemo, useState } from 'react';
import { Activity, AlertTriangle, TrendingUp, X } from 'lucide-react';
import type { EnterpriseReadinessRollup, TrafficLight, ReadinessScore } from '../../types/control-plane';
import { cx, statusColor } from '../../lib/design';
import { Panel, PanelHeader, Legend, EmptyHint, StatusDot, Badge } from '../ui/primitives';

interface LeadershipMatrixProps {
  readiness: EnterpriseReadinessRollup | null;
}

interface CellSelection {
  siteLabel: string;
  dimension: string;
  score: ReadinessScore;
}

const dimensionStatus = (dimensions: ReadinessScore[], name: string): ReadinessScore | null => {
  const match = dimensions.find((dim) => dim.dimension.toLowerCase().includes(name.toLowerCase().slice(0, 4)));
  return match ?? null;
};

const Cell = ({ 
  status, 
  scoreData, 
  onClick, 
  isSelected 
}: { 
  status: TrafficLight; 
  scoreData?: ReadinessScore | null;
  onClick?: () => void; 
  isSelected?: boolean;
}) => {
  const sc = statusColor(status);
  const reasons = scoreData?.reason_codes ?? [];
  const tooltipText = reasons.length > 0 ? reasons.join('; ') : sc.label;
  
  return (
    <td className="px-2 py-2 text-center">
      <button
        onClick={onClick}
        disabled={!onClick}
        title={tooltipText}
        className={cx(
          'inline-flex h-7 w-7 items-center justify-center rounded-md border transition-all',
          sc.border, 
          sc.bg,
          onClick && 'cursor-pointer hover:scale-110 hover:shadow-md',
          isSelected && 'ring-2 ring-brand ring-offset-1 ring-offset-panel scale-110'
        )}
      >
        <StatusDot status={status} size={10} />
      </button>
    </td>
  );
};

export function LeadershipMatrix({ readiness }: LeadershipMatrixProps) {
  const sites = readiness?.sites ?? [];
  const [selectedCell, setSelectedCell] = useState<CellSelection | null>(null);

  const dimensions = useMemo(() => {
    if (sites.length === 0) return [];
    const firstSite = sites[0];
    return firstSite.dimensions.map(d => d.dimension);
  }, [sites]);

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
    return (
      <EmptyHint 
        title="No enterprise readiness data available" 
        detail="Readiness metrics will appear here once sites are configured and reporting."
      />
    );
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
            <Panel key={kpi.label} className="p-4">
              <div className="flex items-center justify-between">
                <span className="text-[11px] uppercase tracking-wider text-ink3">{kpi.label}</span>
                <Icon size={15} className={sc.text} />
              </div>
              <div className={cx('mt-1 text-2xl font-semibold', kpi.status === 'unknown' ? 'text-ink' : sc.text)}>{kpi.value}</div>
            </Panel>
          );
        })}
      </div>

      {/* Heatmap matrix */}
      <Panel className="p-4">
        <div className="mb-4 flex items-center justify-between">
          <div className="text-[11px] font-semibold uppercase tracking-wider text-ink3">Enterprise Readiness Matrix</div>
          <Legend items={[
            { status: 'green', label: 'In control' },
            { status: 'yellow', label: 'At risk / warning' },
            { status: 'red', label: 'Action required' },
            { status: 'unknown', label: 'Not evaluated' },
          ]} />
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-[11px] uppercase tracking-wider text-ink3">
                <th className="px-2 py-2 text-left">Site</th>
                {dimensions.map((dim) => (
                  <th key={dim} className="px-2 py-2 text-center">{dim}</th>
                ))}
                <th className="px-2 py-2 text-center">Overall</th>
              </tr>
            </thead>
            <tbody>
              {sites.map((site) => (
                <tr key={site.site_label} className="border-t border-line">
                  <td className="px-2 py-2 text-left text-sm font-medium text-ink">{site.site_label}</td>
                  {dimensions.map((dim) => {
                    const scoreData = dimensionStatus(site.dimensions, dim);
                    const status = scoreData?.status ?? 'unknown';
                    const isSelected = selectedCell?.siteLabel === site.site_label && selectedCell?.dimension === dim;
                    return (
                      <Cell 
                        key={dim} 
                        status={status} 
                        scoreData={scoreData}
                        isSelected={isSelected}
                        onClick={() => scoreData && setSelectedCell({ siteLabel: site.site_label, dimension: dim, score: scoreData })}
                      />
                    );
                  })}
                  <Cell status={site.overall_status} />
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>

      {/* Detail panel for selected cell */}
      {selectedCell && (
        <Panel className="p-4">
          <div className="flex items-start justify-between mb-3">
            <div>
              <div className="text-sm font-semibold text-ink">{selectedCell.siteLabel} — {selectedCell.dimension}</div>
              <div className="flex items-center gap-2 mt-1">
                <StatusDot status={selectedCell.score.status} size={8} />
                <span className="text-xs text-ink3">{statusColor(selectedCell.score.status).label}</span>
                {selectedCell.score.score_pct != null && (
                  <Badge tone="neutral">{selectedCell.score.score_pct}%</Badge>
                )}
                {selectedCell.score.sla_status && (
                  <Badge tone={selectedCell.score.sla_status === 'compliant' ? 'brand' : 'neutral'}>
                    {selectedCell.score.sla_status}
                  </Badge>
                )}
              </div>
            </div>
            <button 
              onClick={() => setSelectedCell(null)}
              className="text-ink3 hover:text-ink transition-colors"
            >
              <X size={16} />
            </button>
          </div>

          {/* Reason codes */}
          {selectedCell.score.reason_codes.length > 0 && (
            <div className="mb-3">
              <div className="text-[11px] font-semibold uppercase tracking-wider text-ink3 mb-1.5">Reason Codes</div>
              <ul className="space-y-1">
                {selectedCell.score.reason_codes.map((reason, i) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-ink2">
                    <span className="text-ink3">•</span>
                    {reason}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommended actions */}
          {selectedCell.score.recommended_actions.length > 0 && (
            <div className="mb-3">
              <div className="text-[11px] font-semibold uppercase tracking-wider text-ink3 mb-1.5">Recommended Actions</div>
              <ul className="space-y-1">
                {selectedCell.score.recommended_actions.map((action, i) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-ink2">
                    <span className="text-brand font-bold">{i + 1}.</span>
                    {action}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Evidence citations */}
          {selectedCell.score.evidence_citations.length > 0 && (
            <div>
              <div className="text-[11px] font-semibold uppercase tracking-wider text-ink3 mb-1.5">Evidence Citations</div>
              <div className="flex flex-wrap gap-1">
                {selectedCell.score.evidence_citations.map((citation, i) => (
                  <Badge key={i} tone="neutral" className="text-[9px]">{citation}</Badge>
                ))}
              </div>
            </div>
          )}
        </Panel>
      )}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {/* Top risks */}
        <Panel className="p-4">
          <div className="mb-3 text-[11px] font-semibold uppercase tracking-wider text-ink3">Top Enterprise Risks</div>
          {readiness.top_risks.length === 0 ? (
            <p className="text-xs text-ink3">No outstanding enterprise-level risks.</p>
          ) : (
            <ul className="space-y-2">
              {readiness.top_risks.map((risk, index) => (
                <li key={index} className="flex items-start gap-2 text-xs text-ink2">
                  <span className="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-status-red-soft text-[10px] font-bold text-status-red">
                    {index + 1}
                  </span>
                  {risk}
                </li>
              ))}
            </ul>
          )}
        </Panel>

        {/* Release pipeline */}
        <Panel className="p-4">
          <div className="mb-3 text-[11px] font-semibold uppercase tracking-wider text-ink3">Enterprise Release Pipeline</div>
          <div className="grid grid-cols-2 gap-3">
            {releaseStages.map((stage) => (
              <div key={stage.label} className="rounded border border-line bg-panel2 px-3 py-2">
                <div className="text-lg font-semibold text-ink">{stage.count}</div>
                <div className="text-[11px] text-ink3">{stage.label}</div>
              </div>
            ))}
          </div>
          <p className="mt-3 border-t border-line pt-3 text-xs text-ink2">{readiness.enterprise_summary}</p>
        </Panel>
      </div>
    </div>
  );
}
