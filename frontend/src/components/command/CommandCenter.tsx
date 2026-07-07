import { AlertOctagon, CheckCircle2, CircleDashed, FileText, Lock, Shield } from 'lucide-react';
import type { CommandCenterEvent } from '../../types/control-plane';
import { cx, statusColor, titleCase } from '../../lib/design';
import { Panel, PanelHeader, SectionLabel, ProgressBar, EmptyHint, Badge } from '../ui/primitives';
import { EvidenceGraphView } from '../evidence/EvidenceGraphView';
import { Sparkline } from '../shared/Sparkline';

interface CommandCenterProps {
  event: CommandCenterEvent | null;
  loading?: boolean;
  onOpenDossier?: (eventId: string) => void;
}

const ContextRow = ({ label, value }: { label: string; value: string | number | null | undefined }) => (
  <div className="flex items-center justify-between border-b border-line2 py-1.5 text-xs">
    <span className="text-ink3">{label}</span>
    <span className="font-medium text-ink">{value ?? '—'}</span>
  </div>
);

const actionIcon = (status: string) => {
  if (status === 'done') return <CheckCircle2 size={15} className="text-status-green" />;
  if (status === 'blocked') return <Lock size={15} className="text-status-red" />;
  return <CircleDashed size={15} className="text-status-amber" />;
};

export function CommandCenter({ event, loading, onOpenDossier }: CommandCenterProps) {
  if (loading) {
    return (
      <div className="flex h-full items-center justify-center p-8">
        <p className="text-sm text-ink3">Loading command center…</p>
      </div>
    );
  }

  if (!event) {
    return (
      <EmptyHint
        title="No active state-of-control breaches"
        detail="All parameters within validated ranges — system is operating nominally."
        icon={<Shield className="text-status-green" size={40} />}
      />
    );
  }

  const { summary, context, impact, series, series_meta, evidence_graph, dossier, required_actions } = event;
  const sc = statusColor(summary.status);

  // Compute present evidence (required but not missing)
  const presentEvidence = dossier.required_evidence.filter((item) => !dossier.missing_evidence.includes(item));

  return (
    <div className="grid h-full grid-cols-1 gap-3 overflow-hidden p-3 lg:grid-cols-[minmax(0,30%)_minmax(0,70%)]">
      {/* LEFT COLUMN — Event Context, Impact & Control Chart */}
      <div className="flex flex-col gap-3 overflow-y-auto">
        {/* Event Header */}
        <Panel>
          <div className={cx('flex items-center gap-2 border-b px-4 py-3', sc.border, sc.bg)}>
            <AlertOctagon size={18} className={sc.text} />
            <div className="flex-1">
              <div className={cx('text-sm font-bold uppercase tracking-wide', sc.text)}>
                {titleCase(summary.outcome)}
              </div>
              <div className="text-[11px] text-ink3">State of Control Violation</div>
            </div>
          </div>
          <div className="px-4 py-3">
            <ContextRow label="Parameter" value={context.parameter} />
            <ContextRow label="Asset" value={context.asset_label} />
            <ContextRow label="Room" value={context.room_label} />
            <ContextRow label="Batch" value={context.batch_label} />
            <ContextRow label="Product" value={context.product_label} />
            <ContextRow label="Phase" value={context.phase_label} />
            <ContextRow label="Duration" value={context.duration_minutes ? `${context.duration_minutes} min` : null} />
            <ContextRow label="Peak Value" value={context.peak_value != null ? `${context.peak_value}${context.unit ?? ''}` : null} />
            <ContextRow label="Alert Limit" value={context.alert_limit != null ? `${context.alert_limit}${context.unit ?? ''}` : null} />
            <ContextRow label="Action Limit" value={context.action_limit != null ? `${context.action_limit}${context.unit ?? ''}` : null} />
          </div>
        </Panel>

        {/* Impact Assessment */}
        <Panel>
          <PanelHeader title="Impact Assessment" />
          <div className="px-4 py-3">
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className={cx('rounded border px-2 py-1.5', statusColor(impact.risk_level === 'critical' ? 'red' : 'yellow').border, statusColor(impact.risk_level === 'critical' ? 'red' : 'yellow').bg)}>
                <div className="text-ink3">Risk Level</div>
                <div className="font-semibold text-ink">{titleCase(impact.risk_level)}</div>
              </div>
              <div className="rounded border border-line px-2 py-1.5">
                <div className="text-ink3">GxP Impact</div>
                <div className="font-semibold text-ink">{impact.gxp_impact ? 'YES' : 'No'}</div>
              </div>
              <div className="col-span-2 rounded border border-line px-2 py-1.5">
                <div className="text-ink3">CAPA Required</div>
                <div className="font-semibold text-ink">{impact.capa_required ? 'YES — Remediation mandatory' : 'No'}</div>
              </div>
            </div>
            {impact.confidence_score != null && (
              <div className="mt-3 rounded bg-panel2 px-2 py-1.5 text-xs">
                <div className="text-ink3">Confidence: {Math.round(impact.confidence_score * 100)}%</div>
                {impact.confidence_explanation && (
                  <p className="mt-1 text-[11px] italic text-ink2">{impact.confidence_explanation}</p>
                )}
              </div>
            )}
            {impact.quality_risks.length > 0 && (
              <div className="mt-3">
                <SectionLabel>Quality Risks</SectionLabel>
                <ul className="mt-1 space-y-1 text-xs text-ink2">
                  {impact.quality_risks.map((risk, index) => (
                    <li key={index} className="flex gap-1.5">
                      <span className="text-status-red">•</span>
                      {risk}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </Panel>

        {/* Control Chart */}
        <Panel>
          <PanelHeader title="Control Chart" subtitle={series_meta.window_label} />
          <div className="px-3 pb-3 pt-2">
            <Sparkline series={series} meta={series_meta} height={200} />
          </div>
        </Panel>
      </div>

      {/* RIGHT COLUMN — Actions + Dossier strip above the landscape Evidence Graph */}
      <div className="flex min-h-0 flex-col gap-3 overflow-hidden">
        {/* Top strip: Required Actions + GMP Dossier Readiness side by side */}
        <div className="grid shrink-0 grid-cols-1 gap-3 xl:grid-cols-2">
          {/* Required Actions */}
          <Panel>
            <PanelHeader title="Required Actions" />
            <div className="px-4 pb-4 pt-2">
              <ul className="space-y-2">
                {required_actions.map((action, index) => (
                  <li key={index} className="flex items-start gap-2 text-xs text-ink2">
                    <span className="mt-0.5">{actionIcon(action.status)}</span>
                    <span className={cx(action.status === 'blocked' && 'text-status-red')}>{action.label}</span>
                  </li>
                ))}
              </ul>
            </div>
          </Panel>

          {/* GMP Dossier Readiness */}
          <Panel>
            <PanelHeader
              title="GMP Dossier Readiness"
              subtitle="Evidence assembled for release — not batch/process progress"
              right={<Badge tone="neutral">{Math.round(dossier.completeness_pct)}%</Badge>}
            />
            <div className="px-4 pb-4 pt-2">
              <ProgressBar pct={dossier.completeness_pct} className="mb-3" />

              <div className="grid grid-cols-2 gap-3">
                {presentEvidence.length > 0 && (
                  <div>
                    <SectionLabel className="mb-1.5">Present</SectionLabel>
                    <ul className="space-y-1 text-xs">
                      {presentEvidence.slice(0, 4).map((item, i) => (
                        <li key={i} className="flex items-start gap-1.5 text-status-green">
                          <CheckCircle2 size={13} className="mt-0.5 shrink-0" />
                          <span className="truncate" title={item}>{item}</span>
                        </li>
                      ))}
                      {presentEvidence.length > 4 && (
                        <li className="text-ink3">+ {presentEvidence.length - 4} more…</li>
                      )}
                    </ul>
                  </div>
                )}

                {dossier.missing_evidence.length > 0 && (
                  <div>
                    <SectionLabel className="mb-1.5">Missing</SectionLabel>
                    <ul className="space-y-1 text-xs">
                      {dossier.missing_evidence.slice(0, 4).map((item, i) => (
                        <li key={i} className="flex items-start gap-1.5 text-status-amber">
                          <CircleDashed size={13} className="mt-0.5 shrink-0" />
                          <span className="truncate" title={item}>{item}</span>
                        </li>
                      ))}
                      {dossier.missing_evidence.length > 4 && (
                        <li className="text-ink3">+ {dossier.missing_evidence.length - 4} more…</li>
                      )}
                    </ul>
                  </div>
                )}
              </div>

              <button
                onClick={() => onOpenDossier?.(summary.event_id)}
                className="mt-3 flex w-full items-center justify-center gap-2 rounded border border-brand-ring bg-brand-soft px-3 py-2 text-xs font-medium text-brand hover:bg-brand-hover"
              >
                <FileText size={14} />
                View Full Dossier
              </button>
            </div>
          </Panel>
        </div>

        {/* Landscape Evidence Graph — fills remaining height */}
        <div className="min-h-0 flex-1">
          <EvidenceGraphView graph={evidence_graph} />
        </div>
      </div>
    </div>
  );
}
