import { useMemo, useState, type FC, type FormEvent } from 'react';

import type { AssistantQueryRequest, AssistantResponse, PersonaType } from '../../types/control-plane';

export interface AssistantPanelProps {
  persona?: PersonaType;
  request?: AssistantQueryRequest;
  response?: AssistantResponse;
  onSubmit?: (request: AssistantQueryRequest) => void;
}

const DEFAULT_PROMPTS = [
  'What are the top release blockers right now?',
  'Summarize connector health and stale feeds.',
  'What should QA prioritize this shift?',
];

export const AssistantPanel: FC<AssistantPanelProps> = ({ persona, request, response, onSubmit }) => {
  const [question, setQuestion] = useState(request?.question ?? '');

  const effectivePersona = useMemo(() => persona ?? request?.persona, [persona, request?.persona]);

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = question.trim();
    if (!trimmed || !onSubmit) {
      return;
    }
    onSubmit({ question: trimmed, persona: effectivePersona });
  };

  return (
    <section className="card">
      <h3 style={{ marginTop: 0 }}>Assistant chat</h3>
      <p style={{ marginTop: 0, color: '#4b5563' }}>
        Grounded operational guidance with citations and human-approval guardrails.
      </p>

      <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        <label htmlFor="assistant-question">Question</label>
        <textarea
          id="assistant-question"
          rows={3}
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask about readiness, blockers, evidence gaps, or next best actions..."
        />
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {DEFAULT_PROMPTS.map((prompt) => (
            <button key={prompt} type="button" className="ghost-button" onClick={() => setQuestion(prompt)}>
              {prompt}
            </button>
          ))}
        </div>
        <button type="submit" className="primary-button">Send question</button>
      </form>

      {response ? (
        <article style={{ marginTop: '1rem', borderTop: '1px solid #e5e7eb', paddingTop: '1rem' }}>
          <p><strong>Summary:</strong> {response.summary}</p>
          <pre className="markdown-box">{response.response_markdown || 'No markdown response provided.'}</pre>
          <ul>
            <li>Human approval required: {response.human_approval_required ? 'Yes' : 'No'}</li>
            <li>GxP decision deferred: {response.gxp_decision_deferred ? 'Yes' : 'No'}</li>
            <li>Safety checks passed: {response.prohibited_content_check_passed ? 'Yes' : 'No'}</li>
          </ul>
          {response.evidence_citations.length ? (
            <>
              <h4 style={{ marginBottom: '0.4rem' }}>Evidence citations</h4>
              <ul>
                {response.evidence_citations.map((citation) => (
                  <li key={citation}>{citation}</li>
                ))}
              </ul>
            </>
          ) : null}
        </article>
      ) : null}
    </section>
  );
};
