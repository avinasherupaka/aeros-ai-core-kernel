import type { FC } from 'react';
import type { ManufacturingSiteTopology } from '../../types/control-plane';
import { AutomationPyramid } from '../topology/AutomationPyramid';
import { TopologyMap } from '../topology/TopologyMap';

export interface TopologyMapPageProps {
  topology: ManufacturingSiteTopology[];
}

export const TopologyMapPage: FC<TopologyMapPageProps> = ({ topology }) => (
  <div className="space-y-8">
    <h2 className="text-2xl font-light text-slate-100">Network Topology</h2>
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
      {topology.map((siteTopology) => (
        <div key={siteTopology.site_label} className="flex flex-col space-y-6">
          <TopologyMap topology={siteTopology} />
          <AutomationPyramid nodes={siteTopology.automation_pyramid} />
        </div>
      ))}
    </div>
  </div>
);
