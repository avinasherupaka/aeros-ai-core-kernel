import type { FC } from 'react';
import type { DossierReadinessCard as DossierReadinessCardModel } from '../../types/control-plane';
import { DossierReadinessCard } from '../cards/DossierReadinessCard';
import { EvidenceChecklist } from '../tables/EvidenceChecklist';
import { Search } from 'lucide-react';

export interface DossierViewerProps {
  batchId: string;
  dossier: DossierReadinessCardModel | null;
  onBatchChange: (batchId: string) => void;
  onLoad: () => void;
}

export const DossierViewer: FC<DossierViewerProps> = ({ batchId, dossier, onBatchChange, onLoad }) => (
  <div className="flex h-[calc(100vh-12rem)] space-x-6">
    <div className="w-1/3 flex flex-col space-y-6">
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-5">
        <label htmlFor="batch-id" className="block text-sm font-medium text-slate-400 mb-2">Batch ID</label>
        <div className="flex space-x-2">
          <input 
            id="batch-id" 
            value={batchId} 
            onChange={(event) => onBatchChange(event.target.value)} 
            className="flex-1 bg-slate-900 border border-slate-700 rounded-md px-3 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button 
            type="button" 
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium transition-colors flex items-center" 
            onClick={onLoad}
          >
            <Search className="w-4 h-4 mr-2" />
            Load
          </button>
        </div>
      </div>
      
      {dossier ? (
        <div className="flex-1 overflow-y-auto min-h-0 bg-slate-800 border border-slate-700 rounded-lg p-5">
          <h3 className="text-lg font-medium text-slate-200 mb-4">Missing Evidence</h3>
          <EvidenceChecklist items={dossier.missing_evidence} />
        </div>
      ) : null}
    </div>
    
    <div className="flex-1 bg-slate-800 border border-slate-700 rounded-lg overflow-y-auto">
      {dossier ? (
        <div className="p-6">
          <DossierReadinessCard dossier={dossier} />
        </div>
      ) : (
        <div className="h-full flex items-center justify-center text-slate-500">
          Select a batch ID to view dossier details
        </div>
      )}
    </div>
  </div>
);
