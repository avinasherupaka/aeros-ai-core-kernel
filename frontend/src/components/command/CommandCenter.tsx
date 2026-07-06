import { AlertOctagon, CheckCircle2, CircleDashed, Clock, Lock, Send, ShieldAlert } from 'lucide-react';
import { useState } from 'react';
import type { CommandCenterEvent } from '../../types/control-plane';
import { cx, statusColor } from '../../lib/design';
import { EvidenceGraphView } from '../evidence/EvidenceGraphView';
import { Sparkline } from '../shared/Sparkline';

interface CommandCenterProps {
  event: CommandCenterEvent | null;
  loading?: boolean;
  onAsk?: (question: string) => void;
  onOpenDossier?: () => void;
}

const ContextRow = ({ label, value }: { label: string; value: string | number | null | undefined }) => (
  <div className="flex items-center justify-between border-b border-surface-800 py-1.5 text-xs">
    <span className="text-slate-500">{label}</span>
    <span className="font-medium text-slate-200">{value ?? '—'}</span>
  </div>
);

const actionIcon = (status: string) => {
  if (status === 'done') return <CheckCircle2 size={15} className="text-status-green" />;
  if (status === 'blocked') return <Lock size={15} className="text-status-red" />;
  return <CircleDashed size={15} className="text-status-yellow" />;
};

export function CommandCenter({ event, loading, onAsk, onOpenDossier }: CommandCenterProps) {
  const [question, setQuestion] = useState('');

  if (loading) {
    return <div className="p-8 text-sm text-slate-400">Loading command center…</div>;
  }
  if (!event) {
    return (
      <div className="flex h-full items-center justify-center p-8 text-center">
        <div>
          <ShieldAlert className="mx-auto mb-3 text-status-green" size={32} />
          <p className="text-sm text-slate-300">No active state-of-control breaches</p>
          <p className="mt-1 text-xs text-slate-500">All monitored parameters are within validated ranges.</p>
        </div>
      </div>
    );
  }

  const { summary, context, impact, series, evidence_graph, dossier, required_actions } = event;
  const sc = statusColor(summary.status);

  const suggestedQueries = [
    `What is the quality risk for this ${summary.parameter.toLowerCase()} excursion?`,
    'What is blocking batch release?',
    'Show the evidence checklist',
  ];

  return (
    <div className="grid h-full grid-cols-1 gap-3 overflow-hidden p-3 lg:grid-cols-[minmax(0,30%)_minmax(0,42%)_minmax(0,28%)]">
      {/* LEFT — Event Context */}
      <div className="flex flex-col overflow-y-auto rounded-lg border border-surface-700 bg-surface-900">
        <div className={cx('flex items-center gap-2 border-b px-4 py-3', sc.border, sc.bg)}>
          <AlertOctagon size={18} className={sc.text} />
          <div>
            <div className={cx('text-sm font-bold uppercase tracking-wide', sc.text)}>{summary.outcome.replace(/_/g, ' ')}</div>
            <div className="text-[11px] text-slate-400">State of Control Violation</div>
          </div>
        </div>
        <div className="px-4 py-3">
          <ContextRow label="Parameter" value={context.parameter} />
          <ContextRow label="Asset" value={context.asset_label} />
          <ContextRow label="Room" value={context.room_label} />
          <ContextRow label="Duration" value={context.duration_minutes ? `${context.duration_minutes} min` : null} />
          <ContextRow label="Alert Limit" value={context.alert_limit != null ? `${context.alert_limit}${context.unit ?? ''}` : null} />
          <ContextRow label="Action Limit" value={context.action_limit != null ? `${context.action_limit}${context.unit ?? ''}` : null} />
          <ContextRow label="Peak Value" value={context.peak_value != null ? `${context.peak_value}${context.unit ?? ''}` : null} />
          <ContextRow label="Batch" value={context.batch_label} />
          <ContextRow label="Product" value={context.product_label} />
          <ContextRow label="Phase" value={context.phase_label} />
        </div>

        <div className="border-t border-surface-800 px-4 py-3">
          <div className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-500">Impact Assessment</div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className={cx('rounded border px-2 py-1.5', statusColor(impact.risk_level === 'critical' ? 'red' : 'yellow').border)}>
              <div className="text-slate-500">Risk Level</div>
              <div className="font-semibold text-slate-100">{impact.risk_level.toUpperCase()}</div>
            </div>
            <div className="rounded border border-surface-700 px-2 py-1.5">
              <div className="text-slate-500">GxP Impact</div>
              <div className="font-semibold text-slate-100">{impact.gxp_impact ? 'YES — Product at Risk' : 'No'}</div>
            </div>
          </div>
          {impact.quality_risks.length > 0 && (
            <ul className="mt-2 space-y-1 text-xs text-slate-400">
              {impact.quality_risks.slice(0, 4).map((risk, index) => (
                <li key={index} className="flex gap-1.5">
                  <span className="text-status-red">•</span>
                  {risk}
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="mt-auto border-t border-surface-800 px-4 py-3">
          <div className="mb-1 flex items-center justify-between text-[11px] font-semibold uppercase tracking-wider text-slate-500">
            <span>Time Series</span>
            <span>60 min window</span>
          </div>
          <Sparkline data={series} limit={context.alert_limit} actionLimit={context.action_limit} />
        </div>
      </div>

      {/* CENTER — Evidence Graph */}
      <div className="min-h-[420px] overflow-hidden rounded-lg">
        <EvidenceGraphView graph={evidence_graph} completenessPct={dossier.completeness_pct} />
      </div>

      {/* RIGHT — Action Panel */}
      <div className="flex flex-col gap-3 overflow-y-auto">
        <div className="rounded-lg border border-surface-700 bg-surface-900 p-4">
          <div className="mb-3 text-[11px] font-semibold uppercase tracking-wider text-slate-500">Required Actions</div>
          <ul className="space-y-2">
            {required_actions.map((action, index) => (
              <li key={index} className="flex items-center gap-2 text-xs text-slate-300">
                {actionIcon(action.status)}
                <span className={cx(action.status === 'blocked' && 'text-status-red')}>{action.label}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="rounded-lg border border-surface-700 bg-surface-900 p-4">
          <div className="mb-2 flex items-center justify-between text-[11px] font-semibold uppercase tracking-wider text-slate-500">
            <span>Dossier Completeness</span>
            <span className="text-slate-300">{Math.round(dossier.completeness_pct)}%</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-surface-700">
            <div
              className={cx('h-full rounded-full', dossier.completeness_pct >= 90 ? 'bg-status-green' : dossier.completeness_pct >= 60 ? 'bg-status-yellow' : 'bg-status-red')}
              style={{ width: `${Math.min(dossier.completeness_pct, 100)}%` }}
            />
          </div>
          {dossier.missing_evidence.length > 0 && (
            <div className="mt-2 text-xs text-slate-500">
              Missing: <span className="text-slate-300">{dossier.missing_evidence.slice(0, 3).join(' · ')}</span>
            </div>
          )}
        </div>

        <div className="flex flex-1 flex-col rounded-lg border border-surface-700 bg-surface-900 p-4">
          <div className="mb-2 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
            <Clock size={12} /> MCP Assistant
          </div>
          <div className="mb-2 flex flex-wrap gap-1.5">
            {suggestedQueries.map((query) => (
              <button
                key={query}
                onClick={() => onAsk?.(query)}
                className="rounded-full border border-surface-600 px-2.5 py-1 text-[11px] text-slate-300 hover:border-biotech-accent hover:text-biotech-accent"
              >
                {query}
              </button>
            ))}
          </div>
          <div className="mt-auto flex gap-2">
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && question.trim()) {
                  onAsk?.(question.trim());
                  setQuestion('');
                }
              }}
              placeholder="Ask about this event…"
              className="flex-1 rounded border border-surface-600 bg-surface-950 px-3 py-2 text-xs text-slate-200 placeholder:text-slate-600 focus:border-biotech-accent focus:outline-none"
            />
            <button
              onClick={() => {
                if (question.trim()) {
                  onAsk?.(question.trim());
                  setQuestion('');
                }
              }}
              className="rounded bg-biotech-accent/20 px-3 text-biotech-accent hover:bg-biotech-accent/30"
            >
              <Send size={14} />
            </button>
          </div>
          <button
            onClick={onOpenDossier}
            className="mt-2 rounded border border-surface-600 px-3 py-2 text-xs font-medium text-slate-300 hover:border-biotech-accent hover:text-biotech-accent"
          >
            View Full Dossier
          </button>
        </div>
      </div>
    </div>
  );
}
