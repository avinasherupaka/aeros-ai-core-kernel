import type { FC } from 'react';

import type { DossierReadinessCard as DossierReadinessCardModel } from '../../types/control-plane';
import { DossierReadinessCard } from '../cards/DossierReadinessCard';
import { EvidenceChecklist } from '../tables/EvidenceChecklist';

export interface DossierViewerProps {
  batchId: string;
  dossier: DossierReadinessCardModel | null;
  onBatchChange: (batchId: string) => void;
  onLoad: () => void;
}

export const DossierViewer: FC<DossierViewerProps> = ({ batchId, dossier, onBatchChange, onLoad }) => (
  <section className="stack">
    <h2>Dossier Viewer</h2>
    <div className="card">
      <label htmlFor="batch-id">Batch ID</label>
      <div className="inline-form">
        <input id="batch-id" value={batchId} onChange={(event) => onBatchChange(event.target.value)} />
        <button type="button" className="primary-button" onClick={onLoad}>Load dossier</button>
      </div>
    </div>
    {dossier ? (
      <>
        <DossierReadinessCard dossier={dossier} />
        <article className="card">
          <h3>Missing Evidence</h3>
          <EvidenceChecklist items={dossier.missing_evidence} />
        </article>
      </>
    ) : null}
  </section>
);
