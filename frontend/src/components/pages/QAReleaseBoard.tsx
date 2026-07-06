import type { FC } from 'react';

import type { DossierReadinessCard as DossierReadinessCardModel, PersonaWorkflowCard } from '../../types/control-plane';
import type { CAPAQueueItem } from '../tables/CAPATable';
import { DossierReadinessCard } from '../cards/DossierReadinessCard';
import { CAPATable } from '../tables/CAPATable';

export interface QAReleaseBoardProps {
  queue: CAPAQueueItem[];
  dossier: DossierReadinessCardModel | null;
  workflow: PersonaWorkflowCard | null;
}

export const QAReleaseBoard: FC<QAReleaseBoardProps> = ({ queue, dossier, workflow }) => (
  <section className="stack">
    <h2>QA Release Board</h2>
    {workflow ? (
      <article className="card qa-banner">
        <h3>{workflow.persona_label}</h3>
        <p>{workflow.primary_objective}</p>
        <p className="card-note">Human approval remains mandatory for release disposition.</p>
      </article>
    ) : null}
    {dossier ? <DossierReadinessCard dossier={dossier} /> : null}
    <h3>CAPA / Deviation Queue</h3>
    <CAPATable queue={queue} />
  </section>
);
