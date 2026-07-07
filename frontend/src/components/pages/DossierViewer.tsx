import type { FC, ReactNode } from 'react';
import type { EventSummary, FullDossier } from '../../types/control-plane';
import { Panel, StatusDot, StatusPill, Badge, ProgressBar, EmptyHint } from '../ui/primitives';
import { cx, statusColor, titleCase, formatNumber } from '../../lib/design';
import { FileText, CheckCircle2, AlertTriangle, MessageSquare } from 'lucide-react';

export interface DossierViewerProps {
  events: EventSummary[];
  dossier: FullDossier | null;
  loading: boolean;
  selectedEventId: string | null;
  onSelect: (eventId: string) => void;
  onAsk: (question: string) => void;
}

export const DossierViewer: FC<DossierViewerProps> = ({ events, dossier, loading, selectedEventId, onSelect, onAsk }) => {
  if (events.length === 0) {
    return <EmptyHint title="No events available" detail="No events to generate dossiers for" icon={<FileText className="h-8 w-8 text-ink3" />} />;
  }

  return (
    <div className="flex h-full gap-4">
      {/* LEFT RAIL: Event selector + Document navigator */}
      <div className="w-[300px] flex flex-col gap-4">
        {/* Events selector */}
        <Panel className="flex-1 flex flex-col min-h-0">
          <div className="border-b border-line px-3 py-2">
            <div className="text-xs font-semibold text-ink2">Events</div>
          </div>
          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {events.map((event) => {
              const isSelected = event.event_id === selectedEventId;
              const sc = statusColor(event.status);
              return (
                <button
                  key={event.event_id}
                  onClick={() => onSelect(event.event_id)}
                  className={cx(
                    'w-full text-left px-2 py-2 rounded border transition-all',
                    isSelected
                      ? 'bg-brand-soft border-brand-ring'
                      : 'bg-panel hover:bg-panel2 border-transparent hover:border-line'
                  )}
                >
                  <div className="flex items-start gap-2">
                    <StatusDot status={event.status} size={8} className="mt-1" />
                    <div className="flex-1 min-w-0">
                      <div className="text-xs font-medium text-ink truncate">{event.parameter}</div>
                      {event.batch_label && (
                        <div className="text-[10px] text-ink3 truncate mt-0.5">Batch {event.batch_label}</div>
                      )}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </Panel>

        {/* Document sections navigator */}
        {dossier && !loading && (
          <Panel className="flex-shrink-0">
            <div className="border-b border-line px-3 py-2">
              <div className="text-xs font-semibold text-ink2">Document Sections</div>
            </div>
            <div className="p-2 space-y-0.5 max-h-[300px] overflow-y-auto">
              {dossier.sections.map((section) => (
                <button
                  key={section.key}
                  onClick={() => {
                    const el = document.getElementById(sectionAnchorId(section.key));
                    el?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                  }}
                  className="w-full text-left px-2 py-1.5 rounded text-[11px] text-ink2 hover:bg-panel2 hover:text-ink transition-colors"
                >
                  {section.title}
                </button>
              ))}
            </div>
          </Panel>
        )}
      </div>

      {/* RIGHT PANE: Dossier document */}
      <div className="flex-1 min-w-0 overflow-y-auto">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="flex items-center gap-2 text-ink3">
              <div className="h-2 w-2 rounded-full bg-brand animate-breathe" />
              <span className="text-sm">Assembling dossier…</span>
            </div>
          </div>
        ) : !dossier ? (
          <EmptyHint
            title="Select an event"
            detail="Choose an event from the left to view its GMP Assurance Dossier"
            icon={<FileText className="h-8 w-8 text-ink3" />}
          />
        ) : (
          <Panel className="p-8 max-w-5xl mx-auto">
            {/* DOSSIER HEADER */}
            <div className="border-b border-line2 pb-6 mb-6">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h1 className="text-2xl font-semibold text-ink">{dossier.title}</h1>
                  <div className="text-sm text-ink2 mt-1">
                    {dossier.batch_label} · {dossier.product_label} · {dossier.site_label}
                  </div>
                </div>
                <StatusPill status={dossier.status} />
              </div>

              <div className="flex items-center gap-3 text-xs text-ink3 mb-4">
                <span>Generated by {dossier.generated_by}</span>
                <Badge tone="neutral">{dossier.artifact_count} artifacts</Badge>
                <Badge tone="brand">Auto-generated GMP dossier</Badge>
              </div>

              <div className="bg-panel2 border border-line rounded-lg p-4 mb-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-xs font-semibold text-ink2">GMP Dossier Readiness</div>
                  <span className="text-xs font-medium text-ink">{dossier.completeness_pct}%</span>
                </div>
                <ProgressBar pct={dossier.completeness_pct} className="mb-2" />
                <div className="text-[10px] text-ink3">
                  {dossier.evidence_present.length} of {dossier.evidence_required.length} required evidence items present
                </div>
              </div>

              {/* Evidence summary strip */}
              <div className="flex flex-wrap gap-1.5 mb-4">
                {dossier.evidence_present.map((item) => (
                  <span key={item} className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] bg-status-green-soft text-status-green border border-status-green-line">
                    <CheckCircle2 className="h-3 w-3" />
                    {item}
                  </span>
                ))}
                {dossier.evidence_missing.map((item) => (
                  <span key={item} className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] bg-status-amber-soft text-status-amber border border-status-amber-line">
                    <AlertTriangle className="h-3 w-3" />
                    {item}
                  </span>
                ))}
              </div>

              <div className="text-xs text-ink3 leading-relaxed mb-4">
                This machine-assembled GMP Assurance Dossier consolidates state-of-control assessment, impact mapping, evidence registers, missing-evidence checklists, and human review placeholders in compliance with SOP requirements. The platform automatically generates audit-ready documentation for each quality event.
              </div>

              <button
                onClick={() => onAsk("What evidence is missing for this dossier?")}
                className="text-xs text-brand hover:text-brand-hover flex items-center gap-1.5 transition-colors"
              >
                <MessageSquare className="h-3.5 w-3.5" />
                Ask Dendrix about this dossier
              </button>
            </div>

            {/* SECTIONS */}
            <div className="space-y-8">
              {dossier.sections.map((section) => (
                <div key={section.key} id={sectionAnchorId(section.key)}>
                  <h2 className="text-lg font-semibold text-ink border-b border-line2 pb-2 mb-3">
                    {section.title}
                  </h2>
                  <div className="text-sm text-ink2">
                    {renderContent(section.content, 0)}
                  </div>
                </div>
              ))}
            </div>
          </Panel>
        )}
      </div>
    </div>
  );
};

// --- Helpers ---

function sectionAnchorId(key: string): string {
  return `section-${key.replace(/[^a-z0-9]/gi, '-')}`;
}

function renderContent(value: unknown, depth: number): ReactNode {
  if (depth > 4) return <span className="text-ink3 italic">…</span>;

  if (value === null || value === undefined) {
    return <span className="text-ink3">—</span>;
  }

  if (typeof value === 'string') {
    return <div className="prose prose-sm max-w-none text-ink2 leading-relaxed">{value}</div>;
  }

  if (typeof value === 'number') {
    return <span className="font-mono text-ink">{formatNumber(value, 2)}</span>;
  }

  if (typeof value === 'boolean') {
    return value ? (
      <span className="flex items-center gap-1 text-status-green">
        <StatusDot status="green" size={6} />
        Yes
      </span>
    ) : (
      <span className="text-ink3">No</span>
    );
  }

  if (Array.isArray(value)) {
    if (value.length === 0) {
      return <span className="text-ink3 italic">None</span>;
    }

    // If all items are strings, render as bulleted list
    if (value.every((v) => typeof v === 'string')) {
      return (
        <ul className="list-disc list-inside space-y-1 ml-2">
          {value.map((item, i) => (
            <li key={i} className="text-ink2">{item}</li>
          ))}
        </ul>
      );
    }

    // If all items are objects with same keys, render as table
    if (value.every((v) => typeof v === 'object' && v !== null)) {
      const allKeys = Array.from(new Set(value.flatMap((v) => Object.keys(v as Record<string, unknown>))));
      if (allKeys.length > 0 && allKeys.length <= 6) {
        return (
          <div className="overflow-x-auto">
            <table className="min-w-full text-xs border border-line rounded">
              <thead className="bg-panel2">
                <tr>
                  {allKeys.map((key) => (
                    <th key={key} className="px-3 py-2 text-left text-ink2 font-semibold border-b border-line">
                      {titleCase(key)}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {value.map((row, i) => (
                  <tr key={i} className="border-b border-line last:border-0">
                    {allKeys.map((key) => (
                      <td key={key} className="px-3 py-2 text-ink2">
                        {renderContent((row as Record<string, unknown>)[key], depth + 1)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
      }
    }

    // Otherwise, render as stacked cards
    return (
      <div className="space-y-2">
        {value.slice(0, 50).map((item, i) => (
          <div key={i} className="pl-3 border-l-2 border-line2">
            {renderContent(item, depth + 1)}
          </div>
        ))}
        {value.length > 50 && <div className="text-ink3 italic text-xs">…and {value.length - 50} more</div>}
      </div>
    );
  }

  if (typeof value === 'object') {
    const obj = value as Record<string, unknown>;
    const entries = Object.entries(obj);
    if (entries.length === 0) {
      return <span className="text-ink3 italic">Empty</span>;
    }

    return (
      <dl className="space-y-2">
        {entries.slice(0, 30).map(([key, val]) => (
          <div key={key} className="flex gap-3">
            <dt className="text-xs font-semibold text-ink2 min-w-[140px]">{titleCase(key)}:</dt>
            <dd className="flex-1 min-w-0">{renderContent(val, depth + 1)}</dd>
          </div>
        ))}
        {entries.length > 30 && <div className="text-ink3 italic text-xs">…and {entries.length - 30} more fields</div>}
      </dl>
    );
  }

  return <span className="text-ink3 font-mono text-xs">{String(value)}</span>;
}
