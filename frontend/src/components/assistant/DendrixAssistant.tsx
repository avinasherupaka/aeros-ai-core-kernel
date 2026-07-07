import { useEffect, useRef, useState } from 'react';
import { Sparkles, X, Send, ShieldCheck, FileText, CornerDownLeft } from 'lucide-react';
import { cx } from '../../lib/design';
import type { AssistantResponse } from '../../types/control-plane';

export interface DendrixAssistantProps {
  open: boolean;
  onToggle: (open: boolean) => void;
  contextLabel: string;
  suggestedQueries: string[];
  response: AssistantResponse | null;
  loading: boolean;
  onSubmit: (question: string) => void;
}

/**
 * Dendrix - the always-available assurance assistant. Renders as a floating
 * launcher bubble on every page and expands into a context-aware chat panel.
 * Answers are deterministic and cited; GxP decisions are always deferred to a human.
 */
export function DendrixAssistant({
  open,
  onToggle,
  contextLabel,
  suggestedQueries,
  response,
  loading,
  onSubmit,
}: DendrixAssistantProps) {
  const [draft, setDraft] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [response, loading]);

  const submit = (question: string) => {
    const q = question.trim();
    if (!q) return;
    onSubmit(q);
    setDraft('');
  };

  return (
    <>
      {/* Launcher bubble */}
      <button
        onClick={() => onToggle(!open)}
        className={cx(
          'fixed bottom-5 right-5 z-40 flex h-13 items-center gap-2 rounded-full px-4 py-3 text-sm font-semibold text-white shadow-float transition',
          'bg-brand hover:bg-brand-hover',
          open && 'scale-95 opacity-0 pointer-events-none',
        )}
        aria-label="Open Dendrix assistant"
      >
        <Sparkles size={18} />
        Ask Dendrix
      </button>

      {/* Panel */}
      <div
        className={cx(
          'fixed bottom-5 right-5 z-50 flex w-[380px] max-w-[calc(100vw-2.5rem)] flex-col overflow-hidden rounded-xl border border-line bg-panel shadow-float transition-all',
          open ? 'pointer-events-auto translate-y-0 opacity-100' : 'pointer-events-none translate-y-4 opacity-0',
        )}
        style={{ height: 'min(620px, calc(100vh - 2.5rem))' }}
      >
        {/* Header */}
        <div className="flex items-center justify-between gap-2 border-b border-line bg-brand px-4 py-3 text-white">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/15">
              <Sparkles size={18} />
            </div>
            <div>
              <div className="text-sm font-semibold leading-tight">Dendrix</div>
              <div className="text-[11px] text-white/70 leading-tight">Assurance assistant</div>
            </div>
          </div>
          <button onClick={() => onToggle(false)} className="rounded p-1 text-white/80 hover:bg-white/15 hover:text-white">
            <X size={16} />
          </button>
        </div>

        {/* Context chip */}
        <div className="flex items-center gap-1.5 border-b border-line bg-brand-soft px-4 py-2 text-[11px] font-medium text-brand">
          <span className="inline-block h-1.5 w-1.5 rounded-full bg-brand" />
          Context: {contextLabel}
        </div>

        {/* Body */}
        <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto px-4 py-3">
          {!response && !loading && (
            <div className="space-y-3">
              <p className="text-xs text-ink3">
                Ask about active deviations, batch release blockers, evidence gaps, or connector health. Answers are
                deterministic and cited — Dendrix never makes the quality decision for you.
              </p>
              <div className="space-y-1.5">
                <div className="text-[11px] font-semibold uppercase tracking-wider text-ink3">Suggested</div>
                {suggestedQueries.map((q) => (
                  <button
                    key={q}
                    onClick={() => submit(q)}
                    className="flex w-full items-center justify-between gap-2 rounded-lg border border-line bg-panel2 px-3 py-2 text-left text-xs text-ink2 transition hover:border-brand-ring hover:bg-brand-soft hover:text-brand"
                  >
                    {q}
                    <CornerDownLeft size={13} className="shrink-0 opacity-50" />
                  </button>
                ))}
              </div>
            </div>
          )}

          {loading && (
            <div className="flex items-center gap-2 text-xs text-ink3">
              <span className="h-2 w-2 animate-breathe rounded-full bg-brand" />
              Analyzing assurance context…
            </div>
          )}

          {response && !loading && (
            <div className="space-y-3">
              <div className="rounded-lg border border-line bg-panel2 px-3 py-2 text-xs text-ink2">
                <div className="mb-1 text-[11px] font-semibold text-ink">{response.summary}</div>
                <div className="whitespace-pre-wrap leading-relaxed text-ink2">{response.response_markdown}</div>
              </div>

              {response.recommended_actions.length > 0 && (
                <div className="space-y-1">
                  <div className="text-[11px] font-semibold uppercase tracking-wider text-ink3">Recommended</div>
                  {response.recommended_actions.map((a, i) => (
                    <div key={i} className="flex items-start gap-1.5 text-xs text-ink2">
                      <span className="mt-0.5 text-brand">→</span>
                      {a}
                    </div>
                  ))}
                </div>
              )}

              {response.evidence_citations.length > 0 && (
                <div className="space-y-1">
                  <div className="text-[11px] font-semibold uppercase tracking-wider text-ink3">Sources</div>
                  {response.evidence_citations.slice(0, 5).map((c, i) => (
                    <div key={i} className="flex items-center gap-1.5 rounded border border-line bg-panel px-2 py-1 text-[11px] text-ink3">
                      <FileText size={11} className="shrink-0 text-ink3" />
                      <span className="truncate">{c}</span>
                    </div>
                  ))}
                </div>
              )}

              {response.human_approval_required && (
                <div className="flex items-center gap-1.5 rounded-lg border border-status-amber-line bg-status-amber-soft px-3 py-2 text-[11px] font-medium text-status-amber">
                  <ShieldCheck size={13} /> Human review required before any release decision.
                </div>
              )}
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t border-line bg-panel p-3">
          <div className="flex items-end gap-2">
            <textarea
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  submit(draft);
                }
              }}
              rows={1}
              placeholder="Ask Dendrix…"
              className="max-h-24 min-h-[38px] flex-1 resize-none rounded-lg border border-line bg-panel2 px-3 py-2 text-xs text-ink placeholder:text-ink3 focus:border-brand-ring focus:outline-none focus:ring-2 focus:ring-brand-ring/40"
            />
            <button
              onClick={() => submit(draft)}
              disabled={!draft.trim() || loading}
              className="flex h-[38px] w-[38px] shrink-0 items-center justify-center rounded-lg bg-brand text-white transition hover:bg-brand-hover disabled:cursor-not-allowed disabled:opacity-40"
            >
              <Send size={15} />
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
