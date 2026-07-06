import React from 'react';
import type {
  ConnectorStatusCard as ConnectorStatusCardModel,
  EnterpriseReadinessRollup,
  PersonaWorkflowCard,
  SiteHealthCard as SiteHealthCardModel,
  TrafficLight,
} from '../../types/control-plane';
import { TrafficLightBadge } from '../status/TrafficLightBadge';
import { Activity, AlertTriangle, CheckCircle, Clock, Server, BarChart3, TrendingUp, ShieldAlert, Zap } from 'lucide-react';

export interface DashboardPageProps {
  readiness: EnterpriseReadinessRollup | null;
  sites: SiteHealthCardModel[];
  connectors: ConnectorStatusCardModel[];
  workflow: PersonaWorkflowCard | null;
}

const ProgressBar: React.FC<{ value: number; colorClass: string; label?: string }> = ({ value, colorClass, label }) => (
  <div className="w-full">
    {label && <div className="flex justify-between text-xs mb-1 text-slate-400 font-mono"><span>{label}</span><span>{value}%</span></div>}
    <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden border border-slate-700/50">
      <div className={`h-full ${colorClass} transition-all duration-1000`} style={{ width: `${value}%` }} />
    </div>
  </div>
);

const Sparkline: React.FC<{ data: number[]; color: string }> = ({ data, color }) => {
  const max = Math.max(...data, 1);
  const min = Math.min(...data, 0);
  const range = max - min;
  const width = 100;
  const height = 30;
  const points = data.map((d, i) => `${(i / (data.length - 1)) * width},${height - ((d - min) / range) * height}`).join(' ');
  return (
    <svg width="100%" height="100%" viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none" className="overflow-visible">
      <polyline points={points} fill="none" stroke={color} strokeWidth="2" vectorEffect="non-scaling-stroke" />
    </svg>
  );
};

export const DashboardPage: React.FC<DashboardPageProps> = ({ readiness, sites, connectors, workflow }) => {
  if (!workflow) {
    return <div className="text-slate-400 p-8 text-center italic">Waiting for persona workflow context...</div>;
  }

  // --- PLANT OPS VIEW ---
  if (workflow.persona === 'plant_ops') {
    return (
      <div className="space-y-6 font-sans">
        <div className="flex justify-between items-end border-b border-slate-700 pb-4">
          <div>
            <h2 className="text-3xl font-bold text-slate-100 flex items-center tracking-tight">
              <Activity className="w-8 h-8 mr-3 text-emerald-400" />
              Plant Operations Control
            </h2>
            <p className="text-slate-400 mt-1 uppercase tracking-widest text-sm font-semibold">{workflow.primary_objective}</p>
          </div>
          <div className="flex space-x-3">
            {workflow.recommended_actions.map((act, i) => (
              <button key={i} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded shadow-lg shadow-blue-500/20 text-sm uppercase tracking-wider flex items-center transition-colors">
                <Zap className="w-4 h-4 mr-2" />
                {act.action}
              </button>
            ))}
          </div>
        </div>

        {/* Giant Equipment Health Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {workflow.kpis.map((kpi, i) => (
            <div key={i} className="bg-slate-900 border-l-4 border-slate-700 rounded-r shadow-md p-5 relative overflow-hidden group hover:bg-slate-800 transition-colors"
                 style={{ borderLeftColor: kpi.status === 'red' ? '#ef4444' : kpi.status === 'yellow' ? '#f59e0b' : '#10b981' }}>
              <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity">
                <BarChart3 className="w-16 h-16" />
              </div>
              <h3 className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-1">{kpi.label}</h3>
              <div className="flex items-end space-x-3">
                <span className="text-4xl font-black text-slate-100 tracking-tighter">{kpi.value}</span>
              </div>
              <div className="mt-4 h-8 opacity-70">
                {/* Dummy sparkline data for SCADA look */}
                <Sparkline data={[20, 25, 22, 30, 28, 35, kpi.status === 'red' ? 10 : 40]} color={kpi.status === 'red' ? '#ef4444' : kpi.status === 'yellow' ? '#f59e0b' : '#10b981'} />
              </div>
            </div>
          ))}
        </div>

        {/* Active Deviations Table */}
        <div className="bg-slate-900 border border-slate-700 rounded overflow-hidden">
          <div className="bg-slate-800 p-3 border-b border-slate-700 font-bold text-slate-300 uppercase tracking-wider text-sm flex items-center">
            <AlertTriangle className="w-4 h-4 mr-2 text-amber-500" />
            Active Deviations & Alerts
          </div>
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-900/50 text-xs uppercase text-slate-500 font-mono">
              <tr>
                <th className="p-3">Severity</th>
                <th className="p-3">Summary</th>
                <th className="p-3">Owner</th>
                <th className="p-3">SLA / Due</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono">
              {workflow.alerts.map((alert, i) => (
                <tr key={i} className="hover:bg-slate-800/50 transition-colors">
                  <td className="p-3"><TrafficLightBadge status={alert.severity} /></td>
                  <td className="p-3 font-semibold text-slate-200">{alert.summary}</td>
                  <td className="p-3 text-slate-400">{alert.owner}</td>
                  <td className={`p-3 font-bold ${alert.severity === 'red' ? 'text-red-400' : 'text-slate-400'}`}>{alert.dueLabel}</td>
                </tr>
              ))}
              {workflow.alerts.length === 0 && (
                <tr><td colSpan={4} className="p-6 text-center text-slate-500 italic">No active deviations</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  // --- QA MANAGER VIEW ---
  if (workflow.persona === 'qa') {
    return (
      <div className="space-y-6 font-sans">
        <div className="border-b border-slate-700 pb-4">
          <h2 className="text-3xl font-bold text-slate-100 flex items-center tracking-tight">
            <CheckCircle className="w-8 h-8 mr-3 text-blue-400" />
            Quality Assurance Pipeline
          </h2>
          <p className="text-slate-400 mt-1 uppercase tracking-widest text-sm font-semibold">{workflow.primary_objective}</p>
        </div>

        {/* Release Board Metrics (Horizontal bars) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-slate-900 border border-slate-700 p-5 rounded">
            <h3 className="text-sm font-bold text-slate-300 uppercase tracking-widest mb-4 flex items-center">
              <Clock className="w-4 h-4 mr-2 text-slate-400" /> Batch Progress Pipelines
            </h3>
            <div className="space-y-5">
              <ProgressBar value={85} colorClass="bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]" label="Batch 10442-A (Release Pending)" />
              <ProgressBar value={40} colorClass="bg-emerald-500" label="Batch 10443-B (In Production)" />
              <ProgressBar value={12} colorClass="bg-amber-500" label="Batch 10444-C (Dispensing)" />
            </div>
          </div>
          <div className="bg-slate-900 border border-slate-700 p-5 rounded">
            <h3 className="text-sm font-bold text-slate-300 uppercase tracking-widest mb-4">Release Board Metrics</h3>
            <div className="grid grid-cols-2 gap-4">
              {workflow.kpis.map((kpi, i) => (
                <div key={i} className="bg-slate-800 p-3 rounded border border-slate-700/50">
                  <div className="text-xs text-slate-400 uppercase tracking-wider mb-1">{kpi.label}</div>
                  <div className="text-2xl font-light text-slate-100">{kpi.value}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* CAPA Exceptions */}
        <div className="bg-slate-900 border border-slate-700 rounded overflow-hidden">
          <div className="bg-red-900/20 p-3 border-b border-slate-700 font-bold text-slate-300 uppercase tracking-wider text-sm flex items-center">
            <ShieldAlert className="w-4 h-4 mr-2 text-red-400" />
            CAPA Exceptions & Alerts
          </div>
          <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-4">
            {workflow.alerts.map((alert, i) => (
              <div key={i} className="bg-slate-800 border-l-2 border-red-500 p-3 rounded flex flex-col justify-between">
                <div className="font-semibold text-slate-200 text-sm mb-2">{alert.summary}</div>
                <div className="flex justify-between text-xs text-slate-400 font-mono">
                  <span>Owner: {alert.owner}</span>
                  <span className="text-red-400">{alert.dueLabel}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // --- LEADERSHIP VIEW (Enterprise Readiness Rollup) ---
  if (workflow.persona === 'leadership') {
    return (
      <div className="space-y-6 font-sans">
        <div className="border-b border-slate-700 pb-4">
          <h2 className="text-3xl font-bold text-slate-100 flex items-center tracking-tight">
            <TrendingUp className="w-8 h-8 mr-3 text-purple-400" />
            Enterprise Readiness Command Center
          </h2>
          <p className="text-slate-400 mt-1 uppercase tracking-widest text-sm font-semibold">{workflow.primary_objective}</p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {workflow.kpis.map((kpi, i) => (
            <div key={i} className="bg-slate-900 p-4 rounded border border-slate-700 flex flex-col items-center justify-center text-center">
              <span className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-2">{kpi.label}</span>
              <span className={`text-4xl font-black ${kpi.status === 'red' ? 'text-red-400' : kpi.status === 'yellow' ? 'text-amber-400' : 'text-emerald-400'}`}>
                {kpi.value}
              </span>
            </div>
          ))}
        </div>

        {readiness && (
          <div className="bg-slate-900 border border-slate-700 rounded overflow-hidden mt-6">
            <div className="bg-slate-800 p-4 border-b border-slate-700 font-bold text-slate-300 uppercase tracking-wider">
              Site Readiness Rollup Matrix
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300 whitespace-nowrap">
                <thead className="bg-slate-900 text-xs uppercase text-slate-500 font-mono">
                  <tr>
                    <th className="p-4 border-b border-slate-700">Site</th>
                    <th className="p-4 border-b border-slate-700">Status</th>
                    <th className="p-4 border-b border-slate-700">Plant Risk</th>
                    <th className="p-4 border-b border-slate-700">QA Posture</th>
                    <th className="p-4 border-b border-slate-700">Open CAPAs</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800 font-sans">
                  {readiness.sites.map((site, i) => (
                    <tr key={i} className="hover:bg-slate-800/30 transition-colors">
                      <td className="p-4 font-bold text-slate-200">{site.site_label}</td>
                      <td className="p-4"><TrafficLightBadge status={site.overall_status} /></td>
                      <td className="p-4 text-slate-400 max-w-xs truncate" title={site.plant_risk_summary}>{site.plant_risk_summary}</td>
                      <td className="p-4 text-slate-400">{site.qa_release_posture}</td>
                      <td className="p-4 font-mono">
                        <span className={`px-2 py-1 rounded bg-slate-800 ${site.open_capas > 5 ? 'text-red-400 border border-red-500/30' : 'text-slate-300'}`}>
                          {site.open_capas}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    );
  }

  // --- DEFAULT FALLBACK VIEW ---
  return (
    <div className="space-y-6 font-sans">
      <div className="border-b border-slate-700 pb-4">
        <h2 className="text-2xl font-bold text-slate-100 flex items-center">
          <Server className="w-6 h-6 mr-3 text-slate-400" />
          {workflow.persona_label} Workspace
        </h2>
        <p className="text-slate-400 mt-1 uppercase tracking-widest text-xs">{workflow.primary_objective}</p>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {workflow.kpis.map((kpi, i) => (
          <div key={i} className="bg-slate-900 border border-slate-700 p-4 rounded">
            <div className="text-xs text-slate-400 uppercase mb-2">{kpi.label}</div>
            <div className="text-xl text-slate-100">{kpi.value}</div>
          </div>
        ))}
      </div>
    </div>
  );
};
