import type { FC } from 'react';

import type { DossierReadinessCard as DossierReadinessCardModel } from '../../types/control-plane';
import { TrafficLightBadge } from '../status/TrafficLightBadge';

export interface DossierReadinessCardProps {
  dossier: DossierReadinessCardModel;
}

export const DossierReadinessCard: FC<DossierReadinessCardProps> = ({ dossier }) => (
  <article className="card">
    <header className="card-head">
      <div>
        <h3>{dossier.batch_label}</h3>
        <p className="card-subtitle">{dossier.product_label} · {dossier.site_label}</p>
      </div>
      <TrafficLightBadge status={dossier.dossier_status} label="Dossier status" />
    </header>
    <div className="metric-grid">
      <div>
        <p className="metric-label">Completeness</p>
        <p className="metric-value">{dossier.completeness_pct}%</p>
      </div>
      <div>
        <p className="metric-label">Open CAPAs</p>
        <p className="metric-value">{dossier.open_capas}</p>
      </div>
      <div>
        <p className="metric-label">QA review</p>
        <p className="metric-value">{dossier.qa_review_status}</p>
      </div>
      <div>
        <p className="metric-label">Human approval</p>
        <p className="metric-value">{dossier.human_approval_required ? 'Required' : 'Not required'}</p>
      </div>
    </div>
    <p className="card-note"><strong>Recommendation:</strong> {dossier.release_recommendation}</p>
  </article>
);
