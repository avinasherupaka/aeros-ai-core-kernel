import type { FC } from 'react';

export interface EvidenceCitationProps {
  citation: string;
}

export const EvidenceCitation: FC<EvidenceCitationProps> = ({ citation }) => (
  <li className="citation-item">{citation}</li>
);
