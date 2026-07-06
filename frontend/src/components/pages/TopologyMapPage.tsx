import type { FC } from 'react';

import type { ManufacturingSiteTopology } from '../../types/control-plane';
import { AutomationPyramid } from '../topology/AutomationPyramid';
import { TopologyMap } from '../topology/TopologyMap';

export interface TopologyMapPageProps {
  topology: ManufacturingSiteTopology[];
}

export const TopologyMapPage: FC<TopologyMapPageProps> = ({ topology }) => (
  <section className="stack">
    <h2>Topology Map</h2>
    <div className="grid columns-2">
      {topology.map((siteTopology) => (
        <div key={siteTopology.site_label} className="stack-inner">
          <TopologyMap topology={siteTopology} />
          <AutomationPyramid nodes={siteTopology.automation_pyramid} />
        </div>
      ))}
    </div>
  </section>
);
