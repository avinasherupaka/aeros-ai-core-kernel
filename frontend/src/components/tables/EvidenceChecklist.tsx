import type { FC } from 'react';

export interface EvidenceChecklistProps {
  items: string[];
}

export const EvidenceChecklist: FC<EvidenceChecklistProps> = ({ items }) => (
  <ul className="list">
    {items.map((item, index) => (
      <li key={`${item}-${index}`}>{item}</li>
    ))}
  </ul>
);
