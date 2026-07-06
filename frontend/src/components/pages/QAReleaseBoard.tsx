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
  <div className="space-y-8">
    <h2 className="text-2xl font-light text-slate-100">QA Release Board</h2>
    
    {workflow ? (
      <article className="bg-slate-800 border border-slate-700 rounded-lg p-6 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-1 h-full bg-blue-500"></div>
        <h3 className="text-lg font-medium text-slate-200 mb-2">{workflow.persona_label}</h3>
        <p className="text-slate-300 mb-4">{workflow.primary_objective}</p>
        <p className="text-sm text-amber-400/90 font-medium">Human approval remains mandatory for release disposition.</p>
      </article>
    ) : null}
    
    {dossier ? <DossierReadinessCard dossier={dossier} /> : null}
    
    <div>
      <h3 className="text-xl font-light text-slate-100 mb-4">CAPA / Deviation Queue</h3>
      <CAPATable queue={queue} />
    </div>
  </div>
);
