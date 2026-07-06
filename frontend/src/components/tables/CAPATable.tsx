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
  <div className="card table-wrap">
    <table>
      <thead>
        <tr>
          <th>Record</th>
          <th>Site</th>
          <th>Summary</th>
          <th>Owner</th>
          <th>Priority</th>
          <th>Status</th>
          <th>Due</th>
        </tr>
      </thead>
      <tbody>
        {queue.map((item) => (
          <tr key={item.record_id}>
            <td>{item.record_id}</td>
            <td>{item.site_label}</td>
            <td>{item.summary}</td>
            <td>{item.owner}</td>
            <td>{item.priority}</td>
            <td>{item.status}</td>
            <td>{item.due_label}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);
