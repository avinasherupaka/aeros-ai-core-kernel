import type { FC } from 'react';

import type { ReadinessScore } from '../../types/control-plane';
import { TrafficLightBadge } from '../status/TrafficLightBadge';

export interface ReadinessScoreCardProps {
  score: ReadinessScore;
}

export const ReadinessScoreCard: FC<ReadinessScoreCardProps> = ({ score }) => {
  const formattedScore = typeof score.score_pct === 'number' ? `${score.score_pct}%` : 'n/a';

  return (
  <article className="card readiness-score-card">
    <header className="card-head compact">
      <h4>{score.dimension}</h4>
      <TrafficLightBadge status={score.status} />
    </header>
    <p className="metric-value">{formattedScore}</p>
    {score.reason_codes.length ? (
      <ul className="list compact">
        {score.reason_codes.map((reason) => (
          <li key={reason}>{reason}</li>
        ))}
      </ul>
    ) : null}
  </article>
  );
};
