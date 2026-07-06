import type { FC } from 'react';

import type { AssetHealthCard as AssetHealthCardModel } from '../../types/control-plane';
import { TrafficLightBadge } from '../status/TrafficLightBadge';

export interface AssetHealthCardProps {
  asset: AssetHealthCardModel;
}

export const AssetHealthCard: FC<AssetHealthCardProps> = ({ asset }) => (
  <article className="card">
    <header className="card-head compact">
      <h4>{asset.asset_label}</h4>
      <TrafficLightBadge status={asset.overall_status} />
    </header>
    <p className="card-subtitle">{asset.domain_path}</p>
    <div className="chip-row">
      <TrafficLightBadge status={asset.equipment_health} label="Equipment" />
      <span className="meta-chip">Maintenance due: {asset.maintenance_due ? 'Yes' : 'No'}</span>
    </div>
  </article>
);
