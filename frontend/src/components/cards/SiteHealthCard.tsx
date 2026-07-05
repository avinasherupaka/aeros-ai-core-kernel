import type { FC } from 'react';

import type { SiteHealthCard as SiteHealthCardModel } from '../../types/control-plane';

export interface SiteHealthCardProps {
  site: SiteHealthCardModel;
}

/**
 * Shell component for rendering a manufacturing site health summary card.
 * The final UI can layer traffic-light badges, KPI chips, and drilldowns on top.
 */
export const SiteHealthCard: FC<SiteHealthCardProps> = (_props) => null;
