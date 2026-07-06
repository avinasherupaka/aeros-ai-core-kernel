import type { FC } from 'react';
export interface CAPAQueueItem {
  record_id: string;
  site_label: string;
  summary: string;
  owner: string;
  priority: string;
  status: string;
  due_label: string;
}

export interface CAPATableProps {
  queue: CAPAQueueItem[];
}

export const CAPATable: FC<CAPATableProps> = ({ queue }) => (
  <div className="bg-slate-800 border border-slate-700 rounded-lg overflow-hidden">
    <table className="w-full text-left text-sm text-slate-300">
      <thead className="bg-slate-900/50 text-slate-400 text-xs uppercase tracking-wider">
        <tr>
          <th className="px-6 py-3 font-medium">Record</th>
          <th className="px-6 py-3 font-medium">Site</th>
          <th className="px-6 py-3 font-medium">Summary</th>
          <th className="px-6 py-3 font-medium">Owner</th>
          <th className="px-6 py-3 font-medium">Priority</th>
          <th className="px-6 py-3 font-medium">Status</th>
          <th className="px-6 py-3 font-medium">Due</th>
        </tr>
      </thead>
      <tbody className="divide-y divide-slate-700/50">
        {queue.map((item) => (
          <tr key={item.record_id} className="hover:bg-slate-800/80 transition-colors">
            <td className="px-6 py-4 font-medium text-slate-200">{item.record_id}</td>
            <td className="px-6 py-4">{item.site_label}</td>
            <td className="px-6 py-4">{item.summary}</td>
            <td className="px-6 py-4">{item.owner}</td>
            <td className="px-6 py-4">
              <span className={item.priority === 'High' ? 'text-red-400 font-medium' : ''}>
                {item.priority}
              </span>
            </td>
            <td className="px-6 py-4">{item.status}</td>
            <td className="px-6 py-4">{item.due_label}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);
