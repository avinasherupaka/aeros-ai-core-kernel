import { useState } from 'react';
import { Bot, FileText, Send, ShieldAlert, Sparkles, X } from 'lucide-react';
import type { AssistantResponse } from '../../types/control-plane';
import { cx } from '../../lib/design';

interface AssistantDrawerProps {
  open: boolean;
  contextLabel?: string | null;
  response: AssistantResponse | null;
  loading?: boolean;
  onClose: () => void;
  onSubmit: (question: string) => void;
  suggestedQueries?: string[];
}

export function AssistantDrawer({
  open,
  contextLabel,
  response,
  loading,
  onClose,
  onSubmit,
  suggestedQueries = [],
}: AssistantDrawerProps) {
  const [question, setQuestion] = useState('');

  const submit = (value: string) => {
    const trimmed = value.trim();
    if (trimmed) {
      onSubmit(trimmed);
      setQuestion('');
    }
  };

  return (
    <div
      className={cx(
        'fixed right-0 top-0 z-40 flex h-full w-80 flex-col border-l border-surface-700 bg-surface-900 shadow-2xl transition-transform duration-200',
        open ? 'translate-x-0' : 'translate-x-full',
      )}
    >
      <div className="flex items-center justify-between border-b border-surface-700 px-4 py-3">
        <div className="flex items-center gap-2">
          <Bot size={16} className="text-biotech-accent" />
          <span className="text-sm font-semibold text-slate-100">MCP Assistant</span>
        </div>
        <button onClick={onClose} className="rounded p-1 text-slate-400 hover:bg-surface-700 hover:text-slate-100">
          <X size={16} />
        </button>
      </div>

      {contextLabel && (
        <div className="border-b border-surface-800 bg-surface-850 px-4 py-2 text-[11px] text-slate-400">
          Context: <span className="font-medium text-slate-200">{contextLabel}</span>
        </div>
      )}

      <div className="flex-1 space-y-3 overflow-y-auto px-4 py-3">
        {suggestedQueries.length > 0 && !response && !loading && (
          <div>
            <div className="mb-2 flex items-center gap-1.5 text-[11px] uppercase tracking-wider text-slate-500">
              <Sparkles size={12} /> Suggested Queries
            </div>
            <div className="space-y-1.5">
              {suggestedQueries.map((query) => (
                <button
                  key={query}
                  onClick={() => submit(query)}
                  className="block w-full rounded border border-surface-600 px-3 py-2 text-left text-xs text-slate-300 hover:border-biotech-accent hover:text-biotech-accent"
                >
                  {query}
                </button>
              ))}
            </div>
          </div>
        )}

        {loading && <div className="text-xs text-biotech-accent">Querying deterministic assistant…</div>}

        {response && (
          <div className="space-y-3">
            <div className="rounded-lg border border-surface-700 bg-surface-850 p-3">
              <div className="mb-1 text-[11px] uppercase tracking-wider text-slate-500">Response</div>
              <p className="whitespace-pre-wrap text-xs leading-relaxed text-slate-200">{response.summary}</p>
            </div>

            {response.deterministic_facts.length > 0 && (
              <div>
                <div className="mb-1 text-[11px] uppercase tracking-wider text-slate-500">Deterministic Facts</div>
                <ul className="space-y-1 text-xs text-slate-300">
                  {response.deterministic_facts.map((fact, index) => (
                    <li key={index} className="flex gap-1.5">
                      <span className="text-status-green">✓</span>
                      {fact}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {response.recommended_actions.length > 0 && (
              <div>
                <div className="mb-1 text-[11px] uppercase tracking-wider text-slate-500">Recommended Actions</div>
                <ul className="space-y-1 text-xs text-slate-300">
                  {response.recommended_actions.map((action, index) => (
                    <li key={index} className="flex gap-1.5">
                      <span className="text-biotech-accent">→</span>
                      {action}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {response.human_approval_required && (
              <div className="flex items-center gap-2 rounded border border-status-yellow/40 bg-status-yellow/10 px-3 py-2 text-xs text-status-yellow">
                <ShieldAlert size={14} /> Human review required before any regulated decision.
              </div>
            )}

            {response.evidence_citations.length > 0 && (
              <div>
                <div className="mb-1 text-[11px] uppercase tracking-wider text-slate-500">Evidence Citations</div>
                <ul className="space-y-1 text-xs text-slate-400">
                  {response.evidence_citations.map((citation, index) => (
                    <li key={index} className="flex items-center gap-1.5">
                      <FileText size={12} className="text-slate-500" />
                      {citation}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="border-t border-surface-700 p-3">
        <div className="flex gap-2">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && submit(question)}
            placeholder="Ask a bounded question…"
            className="flex-1 rounded border border-surface-600 bg-surface-950 px-3 py-2 text-xs text-slate-200 placeholder:text-slate-600 focus:border-biotech-accent focus:outline-none"
          />
          <button onClick={() => submit(question)} className="rounded bg-biotech-accent/20 px-3 text-biotech-accent hover:bg-biotech-accent/30">
            <Send size={14} />
          </button>
        </div>
      </div>
    </div>
  );
}
